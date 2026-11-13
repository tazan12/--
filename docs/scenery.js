/* DJ Letter: one native decoder; genuine footage fallback when video is blocked. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const video = $('film'), image = $('filmMotion'), surface = $('filmWindow');
  if (!video || !image || !surface) return;
  const RELEASE = '20261114-stable3';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  let episode = 0, epoch = 0, still = false, explicitStill = false;
  let mode = 'loading', pending = false, failed = false, retries = 0;
  let lastProgress = performance.now(), lastTime = -1, frameCount = 0, callback = 0;
  let motionURL = '', posterURL = '', startedAt = 0;
  const path = ext => `./assets/films/ep${String(episode + 1).padStart(2, '0')}.${ext}?v=${RELEASE}`;
  const desired = () => !still && !document.hidden;
  // An obsolete stored still flag must never silently disable a new release.
  try { localStorage.removeItem('dj-letter-still'); } catch (_) {}
  $('still').checked = still;
  video.muted = video.defaultMuted = true;
  video.volume = 0; video.playsInline = true; video.loop = true; video.controls = false;
  video.setAttribute('muted', ''); video.setAttribute('playsinline', '');
  video.setAttribute('webkit-playsinline', '');
  function status(next) {
    mode = next; surface.dataset.playback = next;
    const text = {
      loading: '풍경을 준비하고 있어요', video: '실사 풍경이 흐르고 있어요',
      compatible: '실사 풍경 · 호환 재생', still: '정지 화면 · 감상 설정에서 변경',
      hidden: '화면으로 돌아오면 이어집니다', error: '풍경 연결을 다시 확인하고 있어요'
    }[next];
    if ($('filmState').textContent !== text) $('filmState').textContent = text;
    $('stage').dataset.filmState = next;
    $('filmFallback').hidden = next !== 'error';
  }
  function stopMotionImage() {
    image.hidden = true;
    image.removeAttribute('src');
  }
  function fallback() {
    if (!desired()) return;
    surface.classList.remove('native-visible');
    image.hidden = false;
    if (image.getAttribute('src') !== motionURL) {
      status('loading'); image.src = motionURL;
    } else if (image.complete && image.naturalWidth) status('compatible');
  }
  image.addEventListener('load', () => {
    if (!desired() || image.hidden || image.getAttribute('src') !== motionURL) return;
    if (mode !== 'video') status('compatible');
  });
  image.addEventListener('error', () => {
    if (!desired() || image.hidden) return;
    image.hidden = true; status('error');
  });
  function progress() {
    if (!desired() || video.paused || video.readyState < 2) return;
    lastProgress = performance.now();
    if (frameCount >= 2 || video.currentTime > 0.08) {
      failed = false; surface.classList.add('native-visible');
      if (!image.hidden) stopMotionImage();
      status('video');
    }
  }
  function observeFrames(token) {
    if (!video.requestVideoFrameCallback) return;
    callback = video.requestVideoFrameCallback((_now, metadata) => {
      if (token !== epoch) return;
      if (metadata.mediaTime !== lastTime) { lastTime = metadata.mediaTime; frameCount++; progress(); }
      observeFrames(token);
    });
  }
  function playNative() {
    if (!desired() || failed || pending || !video.paused) return;
    const token = epoch; pending = true;
    let promise;
    try { video.muted = true; promise = video.play(); }
    catch (_) { pending = false; fallback(); return; }
    Promise.resolve(promise).then(() => {
      if (token !== epoch) return;
      // A resolved play() is NOT proof that visible frames are advancing.
      if (!desired()) video.pause();
    }).catch(error => {
      if (token !== epoch || !desired() || error.name === 'AbortError') return;
      fallback();
    }).finally(() => { if (token === epoch) pending = false; });
  }
  function pause() {
    video.pause(); stopMotionImage(); surface.classList.remove('native-visible');
    status(still ? 'still' : 'hidden');
  }
  function resume() {
    if (!desired()) return;
    if (failed) fallback(); else playNative();
  }
  function userStart() {
    // Listening is an explicit interaction. Honor a still choice made this session,
    // but do not let OS/obsolete saved defaults permanently lock the scenery.
    if (!explicitStill) { still = false; $('still').checked = false; }
    resume();
  }
  function setEpisode(index, label) {
    epoch++; episode = index; pending = false; failed = false; retries = 0;
    video.pause();
    if (callback && video.cancelVideoFrameCallback) video.cancelVideoFrameCallback(callback);
    stopMotionImage(); surface.classList.remove('native-visible');
    frameCount = 0; lastTime = -1; startedAt = lastProgress = performance.now();
    posterURL = path('webp'); motionURL = path('motion.webp');
    surface.style.backgroundImage = `url("${posterURL}")`;
    video.poster = posterURL; video.src = path('compat.mp4'); video.load();
    $('filmSceneName').textContent = label;
    $('filmFallback').href = path('compat.mp4');
    status(still ? 'still' : 'loading'); observeFrames(epoch); resume();
  }
  video.addEventListener('loadeddata', resume);
  video.addEventListener('canplay', resume);
  video.addEventListener('error', () => { failed = true; pending = false; fallback(); });
  video.addEventListener('timeupdate', () => {
    if (!video.requestVideoFrameCallback && video.currentTime !== lastTime) {
      lastTime = video.currentTime; frameCount++; progress();
    }
  });
  // This is deliberately independent of the native play promise, which can hang.
  setInterval(() => {
    if (!desired()) return;
    const now = performance.now();
    if (now - lastProgress > 2200) {
      fallback();
      if (!failed && !pending && retries < 2 && now - startedAt > 4500 * (retries + 1)) {
        retries++; playNative();
      }
    }
  }, 800);
  document.addEventListener('pointerdown', resume, {passive: true});
  document.addEventListener('touchend', resume, {passive: true});
  document.addEventListener('keydown', resume);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) pause(); else { lastProgress = performance.now(); resume(); }
  });
  window.addEventListener('pageshow', resume);
  window.addEventListener('online', () => { failed = false; retries = 0; video.load(); resume(); });
  $('still').addEventListener('change', () => {
    still = $('still').checked; explicitStill = still;
    if (still) pause(); else { lastProgress = performance.now(); resume(); }
  });
  // Reduced-motion is respected for UI transitions in CSS. The requested
  // content plays automatically; only an explicit session choice pauses it.
  window.DJ_SCENERY = {
    setEpisode, resume, userStart,
    report: () => ({release: RELEASE, episode: episode + 1, mode, still,
      videoTime: video.currentTime, frameCount, ready: video.readyState,
      paused: video.paused, compatibilityVisible: !image.hidden,
      compatibilityLoaded: image.complete && image.naturalWidth > 0,
      error: video.error?.message || null})
  };
})();
