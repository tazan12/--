/* Routing tests use a fake audio element; live media is verified separately in a browser. */
const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
function setup(){
 const elements=new Map(),timers=new Map();let seq=0;
 class Element{
  constructor(){this.attrs={};this.listeners={};this.children=[];this.textContent='';this.hidden=false;this.value='';this.classList={toggle:()=>false};}
  setAttribute(k,v){this.attrs[k]=String(v)}getAttribute(k){return this.attrs[k]??null}removeAttribute(k){delete this.attrs[k]}
  append(...v){this.children.push(...v)}replaceChildren(...v){this.children=v}scrollIntoView(){}
  addEventListener(k,f){(this.listeners[k]??=[]).push(f)}dispatchEvent(e){for(const f of this.listeners[e.type]||[])f(e)}
 }
 class Audio extends Element{
  constructor(){super();this.paused=true;this.readyState=4;this.currentTime=0;this.duration=30;this.volume=.75;this.ended=false;this.error=null;this.requests=[];this.pending=false;}
  set src(v){this.attrs.src=v;this.currentTime=0;this.error=null;this.ended=false}get src(){return this.attrs.src||''}
  play(){this.requests.push(this.src);if(this.rejectNext){const e=this.rejectNext;this.rejectNext=null;return Promise.reject(e)}this.paused=false;this.dispatchEvent({type:'playing'});return this.pending?new Promise(r=>this.release=r):Promise.resolve()}
  pause(){this.paused=true;this.dispatchEvent({type:'pause'})}load(){this.currentTime=0}finish(){this.paused=true;this.ended=true;this.dispatchEvent({type:'ended'})}
 }
 const audio=new Audio();elements.set('programAudio',audio);
 const $=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id)};
 const episodes=Array.from({length:12},(_,i)=>({title:'편지 '+i,composer:'작곡가',music:'작품 '+i,mood:'고요',story:'기록',src:`https://example.invalid/music-${i}.mp3`}));
 const win={DJ_EPISODES:episodes,DJ_SCENERY:{setEpisode(){},resume(){},userStart(){}},matchMedia:()=>({matches:false}),dispatchEvent(){}};
 const ctx=vm.createContext({window:win,document:{getElementById:$,createElement:()=>new Element()},localStorage:{getItem:()=>null,setItem(){}},Event:class{constructor(type){this.type=type}},setTimeout:(f,ms)=>{timers.set(++seq,{f,ms});return seq},clearTimeout:id=>timers.delete(id),setInterval:(f,ms)=>{timers.set(++seq,{f,ms});return seq},clearInterval:id=>timers.delete(id),console});
 vm.runInContext(fs.readFileSync(path.resolve(__dirname,'../docs/player.js'),'utf8'),ctx);
 return {api:win.DJ_PLAYER,audio,$,episodes,timers};
}
const settle=()=>new Promise(resolve=>setImmediate(resolve));
test('journal entry interrupts narration and plays only the actual classical source',async()=>{const {api,audio,episodes}=setup();api.select(0,true);assert.match(audio.src,/assets\/voice/);api.journal(true,true);await settle();assert.equal(audio.src,episodes[0].src);assert.equal(api.state().phase,'music');assert.equal(api.state().playing,true);assert.equal(api.state().journalMode,true);api.pause()});
test('journal off cancels playback; changing track while off remains silent',async()=>{const {api,audio}=setup();api.journal(true,true);api.journal(true,false);const count=audio.requests.length;api.music(6,false);await settle();assert.equal(audio.paused,true);assert.equal(api.state().wanted,false);assert.equal(api.state().episode,6);assert.equal(audio.requests.length,count);api.pause()});
test('every replay route is narration-free while the journal context is active',async()=>{const {api,audio,$,episodes}=setup();api.journal(true,true);audio.requests=[];api.music(8,true);$('mainPlay').onclick();$('readerPlay').onclick();api.select(10,true);await settle();assert.ok(audio.requests.length>0);assert.ok(audio.requests.every(x=>!x.includes('/voice/')));assert.equal(audio.src,episodes[10].src);api.pause()});
test('explicit journal off prevents an already queued narration handoff',async()=>{const {api,audio,timers}=setup();api.select(0,true);await settle();audio.finish();assert.equal(api.state().phase,'transition');api.journal(true,false);for(const {f,ms} of [...timers.values()])if(ms===1800)f();await settle();assert.equal(audio.paused,true);assert.equal(api.state().wanted,false);api.pause()});
test('return to listening retains the original DJ narration behavior',async()=>{const {api,audio}=setup();api.journal(true,false);api.journal(false);api.select(4,true);await settle();assert.equal(api.state().journalMode,false);assert.equal(api.state().phase,'dj');assert.match(audio.src,/voice\/ep05\.mp3/);api.pause()});
test('a pending play promise cannot undo a later journal off action',async()=>{const {api,audio}=setup();audio.pending=true;api.journal(true,true);api.journal(true,false);audio.release();await settle();assert.equal(audio.paused,true);assert.equal(api.state().wanted,false);api.pause()});
test('browser audio denial remains paused and can be explicitly retried without narration',async()=>{const {api,audio,episodes}=setup();audio.rejectNext=Object.assign(new Error('gesture required'),{name:'NotAllowedError'});api.journal(true,true);await settle();assert.equal(api.state().wanted,false);assert.equal(audio.paused,true);api.music(3,true);await settle();assert.equal(audio.src,episodes[3].src);assert.equal(api.state().playing,true);api.pause()});
