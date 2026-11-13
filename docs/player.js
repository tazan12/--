/* DJ Letter: autonomous silent films + one serialized radio audio element. */
(() => {
  'use strict';
  const stories = window.DJ_EPISODES;
  const $ = id => document.getElementById(id);
  if (!Array.isArray(stories) || stories.length !== 12) {
    $('stageStatus').textContent = '이야기 정보를 불러오지 못했습니다. 페이지를 새로 열어 주세요.';
    return;
  }
  const RELEASE = '20261114-natural1';
  const pad = n => String(n).padStart(2, '0');
  const mediaPath = (kind, n, ext) => `./assets/${kind}/ep${pad(n + 1)}.${ext}?v=${RELEASE}`;
  const clock = n => Number.isFinite(n) && n >= 0 ? `${Math.floor(n / 60)}:${pad(Math.floor(n % 60))}` : '0:00';
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  const audio = $('programAudio');
  const films = [$('film'), $('filmNext')];
  const scenes = ['달빛이 머무는 밤', '꽃잎이 흔들리는 오후', '창가에 내리는 비', '흰 꽃의 작은 인사', '별빛이 흐르는 호수', '분홍빛 꽃바람', '해변에 닿는 파도', '산과 아침 구름', '저녁빛을 담은 바다', '햇살 가득한 초원', '눈 내리는 겨울 숲', '느리게 지나가는 구름'];
  let index = 0, filter = '전체', phase = 'idle', wanted = false, ticket = 0;
  let transition = 0, fade = 0, loadTimer = 0, toastTimer = 0, fallbackUsed = false;
  let volume = 0.75, videoEpoch = 0, front = 0, swapTimer = 0, swapping = false;
  let inView = true, videoFailed = false, still = reduce.matches, motionOverride = false;
  const attempts = new WeakMap();
  const labels = {playing: '풍경이 흐르고 있어요', loading: '풍경을 준비하고 있어요', blocked: '화면을 터치하면 풍경이 이어집니다', still: '고요한 풍경 · 정지 화면', paused: '풍경을 잠시 쉬어 둡니다', error: '연결을 확인하는 동안 풍경 사진을 보여드립니다'};
  try {
    const saved = localStorage.getItem('dj-letter-still');
    if (saved !== null) { still = saved === '1'; motionOverride = true; }
    const savedVolume = Number(localStorage.getItem('dj-letter-volume'));
    if (localStorage.getItem('dj-letter-volume') !== null && Number.isFinite(savedVolume)) volume = Math.max(0, Math.min(1, savedVolume));
    $('note').value = localStorage.getItem('dj-letter-personal-note') || localStorage.getItem('dj-letter-note') || '';
  } catch (_) { /* Storage restrictions do not stop playback. */ }
  $('still').checked = still;
  $('volume').value = Math.round(volume * 100);
  audio.preload = 'none'; audio.volume = volume;
  films.forEach(v => {
    v.muted = true; v.defaultMuted = true; v.volume = 0; v.playsInline = true;
    v.controls = false; v.loop = true; v.setAttribute('muted', '');
    v.setAttribute('playsinline', ''); v.setAttribute('webkit-playsinline', '');
  });
  function toast(text) {
    clearTimeout(toastTimer); $('toast').textContent = text; $('toast').hidden = !text;
    if (text) toastTimer = setTimeout(() => { $('toast').hidden = true; }, 7000);
  }
  function filmStatus(state) {
    $('filmState').textContent = labels[state];
    $('stage').dataset.filmState = state;
    $('filmFallback').hidden = state !== 'error';
  }
  const canAnimate = () => !still && !document.hidden && inView && !videoFailed;
  function endSwap() {
    clearTimeout(swapTimer); swapTimer = 0; swapping = false;
    films.forEach((v, i) => { v.classList.toggle('is-front', i === front); if (i !== front) v.pause(); });
  }
  function pauseFilms() {
    videoEpoch++; endSwap(); films.forEach(v => v.pause());
    filmStatus(still ? 'still' : 'paused');
  }
  function playFilm(v = films[front]) {
    if (!canAnimate() || !v.paused || attempts.has(v)) return;
    const epoch = videoEpoch;
    const marker = {};
    attempts.set(v, marker);
    v.muted = true; v.defaultMuted = true;
    const request = v.play();
    Promise.resolve(request).then(() => {
      if (epoch !== videoEpoch || !canAnimate()) { if (!canAnimate()) v.pause(); return; }
      if (v === films[front] && !v.paused) filmStatus('playing');
    }).catch(err => {
      if (epoch !== videoEpoch || err.name === 'AbortError') return;
      if (v === films[front]) filmStatus(err.name === 'NotAllowedError' ? 'blocked' : 'error');
    }).finally(() => { if (attempts.get(v) === marker) attempts.delete(v); });
  }
  function setFilm() {
    videoEpoch++; endSwap(); videoFailed = false; front = 0;
    const poster = mediaPath('films', index, 'webp');
    $('filmWindow').style.backgroundImage = `url("${poster}")`;
    $('filmSceneName').textContent = scenes[index];
    $('filmFallback').href = mediaPath('films', index, 'mp4');
    films.forEach((v, i) => {
      v.pause(); attempts.delete(v); v.classList.toggle('is-front', i === 0);
      v.poster = poster; v.preload = i === 0 ? 'auto' : 'metadata';
      v.src = mediaPath('films', index, 'mp4'); v.load();
    });
    filmStatus(still ? 'still' : 'loading');
    playFilm();
  }
  function crossfade() {
    const old = films[front];
    if (!canAnimate() || swapping || old.paused || !Number.isFinite(old.duration) || old.duration < 3 || old.duration - old.currentTime > 0.85) return;
    const nextIndex = 1 - front, next = films[nextIndex], epoch = videoEpoch;
    if (next.readyState < 2) return; // Native loop remains the safe fallback.
    swapping = true;
    try { next.currentTime = 0; } catch (_) { swapping = false; return; }
    next.play().then(() => {
      if (epoch !== videoEpoch || !canAnimate()) { next.pause(); swapping = false; return; }
      next.classList.add('is-front'); old.classList.remove('is-front'); front = nextIndex;
      swapTimer = setTimeout(() => {
        if (epoch !== videoEpoch) return;
        old.pause(); try { old.currentTime = 0; } catch (_) {}
        swapping = false; swapTimer = 0;
      }, 700);
    }).catch(() => { swapping = false; });
  }
  films.forEach(v => {
    v.addEventListener('canplay', () => { if (v === films[front]) playFilm(); });
    v.addEventListener('playing', () => { if (v === films[front] && canAnimate()) filmStatus('playing'); });
    v.addEventListener('timeupdate', () => { if (v === films[front]) crossfade(); });
    v.addEventListener('waiting', () => { if (v === films[front] && canAnimate()) filmStatus('loading'); });
    v.addEventListener('error', () => {
      if (v !== films[front]) return;
      videoFailed = true; films.forEach(x => x.pause()); filmStatus('error');
    });
  });
  function retryFilm() {
    if (videoFailed) return;
    if (canAnimate()) playFilm();
  }
  // Recover muted autoplay on real user gestures; no video play button is required.
  document.addEventListener('pointerdown', retryFilm, {passive: true});
  document.addEventListener('touchend', retryFilm, {passive: true});
  document.addEventListener('keydown', retryFilm);
  document.addEventListener('visibilitychange', () => { if (document.hidden) pauseFilms(); else retryFilm(); });
  window.addEventListener('pageshow', retryFilm);
  window.addEventListener('online', () => { if (videoFailed) setFilm(); else retryFilm(); });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(entries => {
      inView = entries[0].isIntersecting;
      if (inView) retryFilm(); else pauseFilms();
    }, {threshold: 0.01}).observe($('filmWindow'));
  }
  $('still').addEventListener('change', () => {
    still = $('still').checked; motionOverride = true;
    try { localStorage.setItem('dj-letter-still', still ? '1' : '0'); } catch (_) {}
    if (still) pauseFilms(); else { videoFailed = false; filmStatus('loading'); playFilm(); }
  });
  reduce.addEventListener?.('change', e => {
    if (motionOverride) return;
    still = e.matches; $('still').checked = still;
    if (still) pauseFilms(); else retryFilm();
  });
  function clearAudioTimers() {
    clearTimeout(transition); clearInterval(fade); clearTimeout(loadTimer);
    transition = fade = loadTimer = 0;
  }
  function invalidateAudio() {
    ticket++; wanted = false; clearAudioTimers(); audio.pause();
  }
  function audioStatus(text) { $('stageStatus').textContent = text; }
  function updateControls() {
    const active = (wanted && !audio.paused) || (wanted && phase === 'transition');
    $('stagePlay').textContent = active ? 'Ⅱ' : '▶';
    $('stagePlay').setAttribute('aria-label', active ? '낭독·음악 일시정지' : '낭독·음악 듣기');
    $('phaseLabel').textContent = phase === 'dj' ? 'DJ의 편지' : phase === 'music' ? '클래식 감상' : phase === 'transition' ? '음악으로 이어지는 쉼' : '편지와 음악';
    const known = Number.isFinite(audio.duration) && audio.duration > 0 && (phase === 'dj' || phase === 'music');
    $('seek').disabled = !known;
    $('clock').textContent = known ? clock(audio.currentTime) : '0:00';
    $('duration').textContent = known ? clock(audio.duration) : '0:00';
    $('seek').value = known ? Math.round(1000 * audio.currentTime / audio.duration) : 0;
    $('seek').setAttribute('aria-valuetext', `${$('clock').textContent} / ${$('duration').textContent}`);
  }
  function originalMusicURL(url) {
    const match = url.match(/^(https:\/\/upload\.wikimedia\.org\/wikipedia\/commons)\/transcoded\/([^/]+\/[^/]+\/[^/]+)\/[^/]+$/);
    return match ? `${match[1]}/${match[2]}` : '';
  }
  function playProgram() {
    const expected = ticket, expectedPhase = phase;
    wanted = true;
    clearTimeout(loadTimer);
    loadTimer = setTimeout(() => {
      if (ticket === expected && wanted && audio.readyState < 2) audioStatus('연결이 느립니다. 준비되는 대로 이어서 들려드립니다.');
    }, 12000);
    const request = audio.play(); // Remains inside the user gesture when started manually.
    Promise.resolve(request).then(() => {
      if (ticket !== expected || phase !== expectedPhase || !wanted) return;
      clearTimeout(loadTimer);
      audioStatus(phase === 'dj' ? '남성 DJ가 편지를 읽어 드리고 있어요.' : '이제 음악 곁에 편안히 머물러 보세요.');
      updateControls();
    }).catch(err => {
      if (ticket !== expected || !wanted || err.name === 'AbortError') return;
      clearTimeout(loadTimer);
      if (err.name === 'NotAllowedError') {
        wanted = false; audioStatus('소리를 들으려면 낭독·음악 버튼을 한 번 눌러 주세요.'); updateControls();
      } else if (phase === 'music') handleMusicError();
      else { wanted = false; audioStatus('낭독을 불러오지 못했습니다. 듣기 버튼으로 다시 시도할 수 있습니다.'); updateControls(); }
    });
    updateControls(); retryFilm();
  }
  function startNarration() {
    invalidateAudio(); phase = 'dj'; fallbackUsed = false;
    $('musicSource').hidden = true; audio.src = mediaPath('voice', index, 'mp3');
    audio.volume = volume; audioStatus('오늘의 편지를 준비합니다.'); playProgram();
  }
  function beginMusic() {
    invalidateAudio(); phase = 'music'; fallbackUsed = false;
    $('musicSource').hidden = true; audio.src = stories[index].src; audio.volume = volume;
    audioStatus('클래식 연주를 준비합니다.'); playProgram();
  }
  function handleMusicError() {
    if (phase !== 'music') return;
    const fallback = originalMusicURL(stories[index].src);
    if (!fallbackUsed && fallback && audio.src !== fallback) {
      fallbackUsed = true; ticket++; clearTimeout(loadTimer);
      audio.src = fallback; audioStatus('같은 연주의 원본 음원으로 연결합니다.'); playProgram(); return;
    }
    clearAudioTimers(); wanted = false;
    $('musicSource').href = stories[index].src; $('musicSource').hidden = false;
    audioStatus('원본 음악 서버의 연결이 원활하지 않습니다. 아래 원본 링크에서 확인해 주세요.'); updateControls();
  }
  function queueMusic() {
    clearTimeout(transition);
    const expected = ticket;
    transition = setTimeout(() => { if (wanted && phase === 'transition' && expected === ticket) beginMusic(); }, 1800);
  }
  function toggleProgram() {
    if (phase === 'idle' || phase === 'complete') { startNarration(); return; }
    if (phase === 'transition') {
      wanted = !wanted; clearTimeout(transition);
      audioStatus(wanted ? '잠시 숨을 고르고, 음악을 맞이합니다.' : '음악으로 넘어가기 전, 잠시 멈췄습니다.');
      if (wanted) queueMusic(); updateControls(); return;
    }
    if (wanted || !audio.paused) {
      invalidateAudio(); audioStatus(phase === 'dj' ? '편지를 잠시 멈췄습니다.' : '음악을 잠시 멈췄습니다.'); updateControls();
    } else playProgram();
  }
  audio.addEventListener('ended', () => {
    clearAudioTimers();
    if (phase === 'dj') {
      phase = 'transition'; wanted = true; audioStatus('잠시 숨을 고르고, 음악을 맞이합니다.'); queueMusic();
    } else if (phase === 'music') {
      phase = 'complete'; wanted = false; audioStatus('음악이 끝났습니다. 남은 여운을 천천히 느껴 보세요.');
    }
    updateControls();
  });
  audio.addEventListener('error', () => {
    if (phase === 'music') handleMusicError();
    else if (phase === 'dj') { clearAudioTimers(); wanted = false; audioStatus('낭독 파일을 불러오지 못했습니다. 연결을 확인한 뒤 다시 들어 주세요.'); updateControls(); }
  });
  ['timeupdate', 'durationchange', 'loadedmetadata', 'playing', 'pause'].forEach(name => audio.addEventListener(name, updateControls));
  $('seek').addEventListener('input', () => {
    if (Number.isFinite(audio.duration) && audio.duration > 0 && !audio.seeking) {
      audio.currentTime = audio.duration * Number($('seek').value) / 1000; updateControls();
    }
  });
  $('volume').addEventListener('input', () => {
    volume = Number($('volume').value) / 100; audio.volume = volume;
    try { localStorage.setItem('dj-letter-volume', String(volume)); } catch (_) {}
  });
  const moods = ['전체', '사랑', '그리움', '위로', '휴식', '회복', '고요', '상실', '기억', '동행'];
  function renderMoods() {
    $('moods').replaceChildren(...moods.map(m => {
      const button = document.createElement('button'); button.type = 'button'; button.textContent = m;
      button.className = m === filter ? 'selected' : ''; button.setAttribute('aria-pressed', String(m === filter));
      button.onclick = () => { filter = m; renderMoods(); renderCards(); }; return button;
    }));
  }
  function renderCards() {
    $('cards').replaceChildren(...stories.map((story, i) => ({story, i})).filter(x => filter === '전체' || x.story.mood === filter).map(({story, i}) => {
      const card = document.createElement('button'); card.type = 'button';
      card.className = 'dj-card' + (i === index ? ' active' : ''); card.dataset.episode = String(i + 1);
      card.setAttribute('aria-pressed', String(i === index)); card.setAttribute('aria-label', `${i + 1}편 ${story.title}, ${story.music}`);
      const art = document.createElement('div'); art.className = 'dj-card-art';
      const img = document.createElement('img'); img.loading = 'lazy'; img.decoding = 'async';
      img.alt = scenes[i]; img.src = mediaPath('films', i, 'webp');
      const ep = document.createElement('span'); ep.textContent = `EP. ${pad(i + 1)}`; art.append(img, ep);
      const body = document.createElement('div'); body.className = 'dj-card-copy';
      [['small', `${story.composer} · ${story.mood}`], ['strong', story.title], ['span', story.music]].forEach(([tag, text]) => {
        const el = document.createElement(tag); el.textContent = text; body.append(el);
      });
      card.append(art, body);
      card.onclick = () => {
        const continueListening = wanted; setEpisode(i);
        $('stage').scrollIntoView({behavior: reduce.matches ? 'instant' : 'smooth', block: 'center'});
        if (continueListening) startNarration();
      };
      return card;
    }));
  }
  function setEpisode(i) {
    invalidateAudio(); phase = 'idle'; fallbackUsed = false;
    index = (i + stories.length) % stories.length;
    audio.removeAttribute('src'); audio.load();
    const story = stories[index];
    $('stageTitle').textContent = story.title; $('stageEpisode').textContent = `LETTER ${pad(index + 1)} / 12`;
    $('stageMusic').textContent = `${story.composer} · ${story.music}`;
    $('readerTitle').textContent = story.title; $('readerMood').textContent = `${story.mood}에 관한 이야기`; $('readerText').textContent = story.story;
    $('musicSource').hidden = true; audioStatus('편지를 듣고, 음악을 맞이할 준비가 되었습니다.');
    updateControls(); setFilm(); renderCards(); toast('');
  }
  $('mainPlay').onclick = startNarration; $('readerPlay').onclick = startNarration;
  $('stagePlay').onclick = toggleProgram; $('musicOnly').onclick = beginMusic;
  $('stageNext').onclick = () => { const resume = wanted; setEpisode(index + 1); if (resume) startNarration(); };
  $('wide').onclick = () => {
    const wide = $('listen').classList.toggle('is-wide');
    $('wide').textContent = wide ? '기본 화면' : '넓게 감상'; $('wide').setAttribute('aria-pressed', String(wide));
    retryFilm();
  };
  $('noteSave').onclick = () => {
    try { localStorage.setItem('dj-letter-personal-note', $('note').value); toast('이 브라우저에 편지를 보관했습니다.'); }
    catch (_) { toast('브라우저 저장이 제한되어 있습니다. 편지를 따로 보관해 주세요.'); }
  };
  setEpisode(0); renderMoods();
})();
