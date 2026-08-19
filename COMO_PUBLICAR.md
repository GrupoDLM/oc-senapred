# Publicar el Dashboard OC SENAPRED en GitHub Pages

Esto deja el dashboard en un **link fijo** (ej: `https://tuusuario.github.io/oc-senapred/`)
que todo el equipo puede abrir, guardar como favorito e **instalar en el escritorio como app**.
Cuando hagamos mejoras, se reemplaza el archivo y **el link sigue siendo el mismo** (no más versiones nuevas).

## Qué archivos van juntos
Todos estos deben ir en la misma carpeta / repositorio:

- `index.html` ........ el dashboard (la app)
- `manifest.webmanifest` ... datos de la app (nombre, ícono)
- `sw.js` .............. hace que la app sea instalable y se actualice sola
- `icon-192.png` ...... ícono
- `icon-512.png` ...... ícono

## Paso a paso (una sola vez)

1. Entra a https://github.com y crea una cuenta gratis (o inicia sesión).
2. Arriba a la derecha, botón **"+" → New repository**.
   - Repository name: `oc-senapred` (o el que quieras).
   - Déjalo **Public** (el archivo no tiene datos sensibles; los costos y márgenes
     se guardan solo en el navegador de cada persona, no en el archivo).
   - Click **Create repository**.
3. En la página del repo nuevo, click **"uploading an existing file"**
   (o pestaña **Add file → Upload files**).
4. **Arrastra los 5 archivos** de la carpeta a la zona de carga y click **Commit changes**.
5. Ve a **Settings** (del repo) → menú izquierdo **Pages**.
   - En "Build and deployment" → Source: **Deploy from a branch**.
   - Branch: **main** / carpeta **/(root)** → **Save**.
6. Espera ~1 minuto y refresca. Arriba aparecerá:
   **"Your site is live at https://tuusuario.github.io/oc-senapred/"**
   → ese es el link para todo el equipo. ✅

## Guardar como favorito
Abre el link en Chrome → estrella ⭐ en la barra de direcciones → Guardar.

## Instalar en el escritorio (como app con su propio ícono)
En Chrome o Edge, con el link abierto:
- Aparece un ícono de **instalar** (una pantallita con una flecha ⤓) al final de la barra
  de direcciones → click → **Instalar**.
- O bien: menú **⋮ → Guardar y compartir → Instalar página como aplicación…**
- Queda en el escritorio / menú inicio y se abre en su propia ventana, como una app normal.

## Cuando hagamos mejoras
Yo te entrego un `index.html` nuevo. Para actualizar:
- En el repo → click en `index.html` → ícono de lápiz ✏️ → borra todo y pega el nuevo,
  **o** usa **Add file → Upload files** y sube el `index.html` nuevo (reemplaza al anterior).
- En segundos, el mismo link muestra la versión actualizada para todos.
  (La app se auto-actualiza: al reabrirla trae la última versión.)

## Importante sobre los datos del equipo
- Las **OC de Mercado Público** se cargan en vivo: son iguales para todos.
- Los **datos internos** (costos, estados, pedidos, guías, facturas) se guardan en el
  navegador de **cada persona**. Para compartirlos entre ustedes, usen los botones
  **Descargar Excel / Importar Excel**.
- Si más adelante quieren que TODO el equipo edite los mismos datos en tiempo real,
  eso requiere una base de datos compartida — es un paso aparte que puedo proponerte.
