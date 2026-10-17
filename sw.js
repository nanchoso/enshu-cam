// 電波がないときも開けるように、ページと地図の部品を端末に保存しておく
const CACHE = "enshu-v1";
const PRECACHE = [
  "./",
  "index.html",
  "checklist.html",
  "report.html",
  "data/places.json",
  "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css",
  "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// 自分のサイトと Leaflet だけを扱う。カメラ画像や投稿の保存先には手を出さない
self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const ours = url.origin === self.location.origin;
  const leaflet = url.href.startsWith("https://cdnjs.cloudflare.com/ajax/libs/leaflet/");
  if (!ours && !leaflet) return;

  // まずネットから取り、取れなければ保存しておいたものを返す
  event.respondWith(
    fetch(req)
      .then((res) => {
        if (res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      })
      .catch(() => caches.match(req, { ignoreSearch: true }).then((hit) => hit || caches.match("index.html")))
  );
});
