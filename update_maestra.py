#!/usr/bin/env python3
"""Best-effort: baja la maestra vigente del CM Emergencia desde la página de
ChileCompra y regenera data/productos.json. Si algo falla, no rompe el flujo
(el dashboard mantiene la versión anterior / la semilla embebida)."""
import re, sys, os, datetime, urllib.request
import parse_maestra

PAGE = "https://www.chilecompra.cl/informacion-de-compras-publicas-ante-emergencias/"

def get(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": "senapred-robot"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read() if binary else r.read().decode("utf-8", "replace")

def main():
    html = get(PAGE)
    # buscar el EMERGENCIAS.xlsx vigente (prioriza el de "maestras-emergencia")
    urls = re.findall(r'https://[^"\']*EMERGENCIAS\.xlsx', html)
    urls = [u.replace("&amp;", "&") for u in urls]
    pref = [u for u in urls if "maestras-emergencia" in u] or urls
    if not pref:
        print("No encontré la maestra EMERGENCIAS.xlsx en la página."); return 1
    url = pref[0]
    print("Maestra:", url)
    xlsx = "EMERGENCIAS.xlsx"
    open(xlsx, "wb").write(get(url, binary=True))
    hoy = datetime.date.today().isoformat()
    o, sz = parse_maestra.parse(xlsx, "data/productos.json", actualizado=hoy)
    print(f"✔ productos.json: {len(o['items'])} productos · {sz/1024:.0f} KB")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("Aviso: no se pudo actualizar la maestra:", e)
        sys.exit(0)   # no romper el flujo
