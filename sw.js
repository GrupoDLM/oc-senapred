/* Service worker del Dashboard OC SENAPRED.
   Estrategia: "network-first" para los archivos propios (así SIEMPRE ves la
   última versión cuando hay internet), con respaldo desde caché si estás sin
   conexión. Las llamadas a Mercado Público y a la librería de Excel (otro
   dominio) NO se interceptan: van directo a la red como siempre. */
const CACHE = "oc-dashboard-v1";
const SHELL = ["./", "./index.html", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png"];

self.addEventListener("install", (e) => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL).catch(() => {})));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  let url;
  try { url = new URL(req.url); } catch (_) { return; }
  // Solo gestionamos archivos de nuestro propio origen (la app).
  if (url.origin !== self.location.origin) return; // API MP / CDN → red normal
  if (req.method !== "GET") return;
  e.respondWith(
    fetch(req)
      .then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
        return res;
      })
      .catch(() => caches.match(req).then((m) => m || caches.match("./index.html")))
  );
});
