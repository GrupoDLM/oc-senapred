#!/usr/bin/env python3
"""Robot del Centro de Mando SENAPRED.
Corre en GitHub Actions: consulta Mercado Público (sin límites de navegador),
trae TODAS las OC de SENAPRED a DLM/VENTIA con su detalle, y arma data/ocs.json
que el dashboard lee al instante. Acumula histórico (merge con lo ya guardado).

Uso:
  python robot.py --days 45                 # incremental (últimos 45 días) — para el schedule
  python robot.py --from 2026-01-01         # backfill del histórico — una vez a mano
Env:
  MP_TICKET  ticket de la API (si no, usa el por defecto)
"""
import os, sys, json, time, argparse, datetime, urllib.request, urllib.parse

API = "https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json"
TICKET = os.environ.get("MP_TICKET") or "E52E2BA2-07D2-4BE6-846C-C4DEFC7F839D"
PROVIDERS = [("1769987", "DLM"), ("1895894", "VENTIA")]
SENAPRED_ORG = "7180"
SEN_UNITS = {"1078078", "758"}
PAUSE = float(os.environ.get("MP_PAUSE", "0.8"))   # segundos entre llamadas
MAXTRIES = 8

def cl(v): return "" if v is None else v

def fetch(url, tries=MAXTRIES):
    for i in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "senapred-robot"})
            with urllib.request.urlopen(req, timeout=40) as r:
                if r.status == 200:
                    data = json.loads(r.read().decode("utf-8", "replace"))
                    time.sleep(PAUSE)
                    return data
        except Exception as e:
            code = getattr(e, "code", None)
            if code not in (429, 500, 502, 503, 504, None):
                # error no recuperable
                time.sleep(PAUSE); return None
        time.sleep(PAUSE * i)   # backoff creciente
    return None

def ddmmyyyy(d): return d.strftime("%d%m%Y")

def parse_detail(oc):
    c = oc.get("Comprador") or {}
    F = oc.get("Fechas") or {}
    items = []
    for it in ((oc.get("Items") or {}).get("Listado") or []):
        items.append({"prod": cl(it.get("Producto")), "esp": cl(it.get("EspecificacionComprador")),
                      "cant": it.get("Cantidad"), "un": cl(it.get("Unidad")), "mon": cl(it.get("Moneda")),
                      "pu": it.get("PrecioNeto"), "tot": it.get("Total")})
    return {"estado": cl(oc.get("Estado")), "estadoCod": oc.get("CodigoEstado"),
            "lic": cl(oc.get("CodigoLicitacion")), "descripcion": cl(oc.get("Descripcion")),
            "fEnvio": cl(F.get("FechaEnvio")), "fAcept": cl(F.get("FechaAceptacion")),
            "organismo": cl(c.get("NombreOrganismo")), "codOrg": str(cl(c.get("CodigoOrganismo"))),
            "unidad": cl(c.get("NombreUnidad")), "cDir": cl(c.get("DireccionUnidad")),
            "cComuna": cl(c.get("ComunaUnidad")), "cRegion": cl(c.get("RegionUnidad")),
            "cContacto": cl(c.get("NombreContacto")), "cMail": cl(c.get("MailContacto")),
            "cFono": cl(c.get("FonoContacto")), "moneda": cl(oc.get("TipoMoneda")),
            "neto": oc.get("TotalNeto"), "iva": oc.get("Impuestos"), "total": oc.get("Total"),
            "formaPago": cl(oc.get("FormaPago")), "items": items}

def is_senapred(det, codigo):
    if str(det.get("codOrg") or "") == SENAPRED_ORG: return True
    return (codigo.split("-")[0] if codigo else "") in SEN_UNITS

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=45)
    ap.add_argument("--from", dest="dfrom", default=None)
    ap.add_argument("--out", default="data/ocs.json")
    args = ap.parse_args()

    today = datetime.date.today()
    if args.dfrom:
        d0 = datetime.datetime.strptime(args.dfrom, "%Y-%m-%d").date()
    else:
        d0 = today - datetime.timedelta(days=args.days - 1)
    days = [d0 + datetime.timedelta(days=i) for i in range((today - d0).days + 1)]
    print(f"Rango: {d0} .. {today}  ({len(days)} días)")

    # cargar acumulado previo
    prev = {"ocs": [], "det": {}}
    if os.path.exists(args.out):
        try: prev = json.load(open(args.out, encoding="utf-8"))
        except Exception: pass
    det = dict(prev.get("det") or {})
    ocs_map = {o["codigo"]: o for o in (prev.get("ocs") or [])}

    # 1) listados por día/proveedor -> set de códigos con su empresa
    found = {}   # codigo -> {empresa, estadoCod, nombre, fecha(dia)}
    for k, d in enumerate(days):
        for pcode, pname in PROVIDERS:
            url = f"{API}?fecha={ddmmyyyy(d)}&CodigoProveedor={pcode}&ticket={TICKET}"
            j = fetch(url)
            if j is None:
                print(f"  ! fallo listado {d} {pname}")
                continue
            for o in (j.get("Listado") or []):
                found[o.get("Codigo")] = {"empresa": pname, "estadoCod": o.get("CodigoEstado"),
                                          "nombre": cl(o.get("Nombre")), "dia": d.isoformat()}
        if (k + 1) % 10 == 0:
            print(f"  listados {k+1}/{len(days)} días · {len(found)} OC candidatas")

    # 2) detalle de las que faltan o cambiaron de estado; filtrar SENAPRED
    codigos = list(found.keys())
    kept = 0; fetched = 0
    for i, codigo in enumerate(codigos):
        f = found[codigo]
        cached = det.get(codigo)
        if cached and cached.get("estadoCod") == f["estadoCod"] and codigo in ocs_map:
            continue  # ya lo tenemos y no cambió
        url = f"{API}?codigo={urllib.parse.quote(codigo)}&ticket={TICKET}"
        j = fetch(url); fetched += 1
        if not j or not (j.get("Listado") or []):
            print(f"  ! sin detalle {codigo}")
            continue
        dd = parse_detail(j["Listado"][0])
        if not is_senapred(dd, codigo):
            # no es SENAPRED: lo sacamos si estaba
            det.pop(codigo, None); ocs_map.pop(codigo, None); continue
        det[codigo] = dd
        fecha = (dd.get("fEnvio") or f["dia"])[:10]
        ocs_map[codigo] = {"codigo": codigo, "empresa": f["empresa"], "fecha": fecha,
                           "estadoCod": dd.get("estadoCod"), "nombre": f["nombre"]}
        kept += 1
        if fetched % 20 == 0:
            print(f"  detalle {i+1}/{len(codigos)} · {kept} SENAPRED nuevas/actualizadas")

    # 3) mantener en ocs solo las que están en det (SENAPRED)
    ocs = [o for o in ocs_map.values() if o["codigo"] in det]
    ocs.sort(key=lambda o: o.get("fecha", ""), reverse=True)
    out = {"savedAt": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
           "ocs": ocs, "det": det}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(out, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    kb = os.path.getsize(args.out) / 1024
    print(f"✔ {len(ocs)} OC de SENAPRED en total · {kept} nuevas/actualizadas esta corrida · {kb:.0f} KB → {args.out}")

if __name__ == "__main__":
    main()
