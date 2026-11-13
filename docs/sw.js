/* DJ Letter offline shell. Diary data stays in localStorage, never in requests. */
'use strict';
const VERSION='mind-20261114-1',CACHE='dj-letter-shell-'+VERSION;
const SHELL=['./','./index.html','./player.css?v='+VERSION,'./episodes.js?v='+VERSION,'./scenery.js?v='+VERSION,'./player.js?v='+VERSION,'./mind-journal.css?v='+VERSION,'./mind-store.js?v='+VERSION,'./mind-journal.js?v='+VERSION,'./manifest.webmanifest','./assets/app-icon-192.png','./assets/app-icon-512.png','./video-sources.html'];
self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(SHELL))));
self.addEventListener('activate',event=>event.waitUntil((async()=>{for(const name of await caches.keys())if(name.startsWith('dj-letter-shell-')&&name!==CACHE)await caches.delete(name);await self.clients.claim();})()));
// Do not force reload/skipWaiting while someone is writing. A new version activates
// after existing windows close; unsaved diary text is never discarded by an update.
self.addEventListener('fetch',event=>{
 const request=event.request,url=new URL(request.url),scope=new URL(self.registration.scope);
 if(request.method!=='GET'||url.origin!==scope.origin||!url.pathname.startsWith(scope.pathname)||request.headers.has('range'))return;
 if(/\.(mp4|mp3|ogg|wav)$/i.test(url.pathname)||url.pathname.endsWith('.motion.webp'))return;
 if(request.mode==='navigate'){
  event.respondWith((async()=>{try{const response=await fetch(request);if(response.ok){const cache=await caches.open(CACHE);await cache.put('./index.html',response.clone());}return response;}catch(_){return await caches.match('./index.html')||Response.error();}})());return;
 }
 const file=url.pathname.slice(scope.pathname.length);
 const shellFile=/^(player|episodes|scenery|mind-store|mind-journal)\.(js|css)$/.test(file)||file==='manifest.webmanifest'||file.startsWith('assets/app-icon-');
 const poster=/^assets\/films\/ep\d{2}\.webp$/.test(file);
 if(!shellFile&&!poster)return;
 event.respondWith((async()=>{const cache=await caches.open(CACHE);const key=poster?new Request(new URL(file,scope).href):request;const saved=await cache.match(key);if(saved)return saved;try{const response=await fetch(request);if(response.ok&&response.type==='basic')await cache.put(key,response.clone());return response;}catch(_){return Response.error();}})());
});
