"""JARVIS Dashboard HTML."""

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, interactive-widget=resizes-content">
<title>J.A.R.V.I.S.</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
:root{--bg:#08080c;--surface:#111118;--surface2:#1a1a25;--surface3:#222230;--border:#ffffff08;--border2:#ffffff12;--cl:#d4a574;--cl2:#e8c4a0;--cl-dim:#d4a57435;--cl-glow:#d4a57418;--green:#34d399;--yellow:#fbbf24;--red:#ef4444;--text:#eae6e1;--text2:#9a9590;--text3:#5a5550}
*{box-sizing:border-box;margin:0;padding:0}
html{height:100%;overflow:hidden}
body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--text);height:100vh;height:100dvh;display:flex;flex-direction:column;overflow:hidden}
body::before{content:'';position:fixed;top:-40%;left:-40%;width:180%;height:180%;background:radial-gradient(ellipse at 50% 20%,var(--cl-glow) 0%,transparent 60%);pointer-events:none;z-index:0}
.top{position:relative;z-index:10;height:52px;min-height:52px;background:var(--surface);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 16px}
.top-left{display:flex;align-items:center;gap:10px}
.logo{width:30px;height:30px;background:linear-gradient(135deg,var(--cl),#c08050);border-radius:9px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:15px;color:#0a0a0f}
.top-title{font-weight:600;font-size:14px;letter-spacing:-.3px}
.top-sub{font-size:10px;color:var(--text2)}
.online{display:flex;align-items:center;gap:5px;font-size:11px;font-weight:500;color:var(--green);background:#34d39910;border:1px solid #34d39925;padding:4px 10px;border-radius:16px}
.online i{width:5px;height:5px;border-radius:50%;background:var(--green);animation:blink 2s ease infinite}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
.stats{display:flex;gap:6px;padding:12px 14px 6px;position:relative;z-index:1}
.st{flex:1;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:10px 8px;text-align:center}
.st b{display:block;font-size:20px;font-weight:700;color:var(--cl)}
.st span{font-size:9px;color:var(--text2);text-transform:uppercase;letter-spacing:.6px}
.scroll{flex:1;overflow-y:auto;overflow-x:hidden;padding:10px 14px 14px;position:relative;z-index:1;-webkit-overflow-scrolling:touch}
.empty{text-align:center;padding:50px 20px}
.empty-ico{width:56px;height:56px;margin:0 auto 14px;background:var(--surface2);border:1px solid var(--border2);border-radius:18px;display:flex;align-items:center;justify-content:center}
.empty h3{font-size:15px;font-weight:600;margin-bottom:4px}
.empty p{font-size:12px;color:var(--text2);line-height:1.5}

/* Cards */
.card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:14px;margin-bottom:8px}
.card.new{animation:up .35s ease}
@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.card-head{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px}
.card-prompt{font-size:13px;font-weight:500;flex:1;margin-right:8px;line-height:1.4}
.badge{font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;padding:3px 8px;border-radius:12px;white-space:nowrap}
.badge.running{background:#fbbf2415;color:var(--yellow);border:1px solid #fbbf2425}
.badge.done{background:#34d39915;color:var(--green);border:1px solid #34d39925}
.badge.error,.badge.stopped{background:#ef444415;color:var(--red);border:1px solid #ef444425}
.dots{display:flex;gap:4px;padding:4px 0}
.dots i{width:5px;height:5px;border-radius:50%;background:var(--cl-dim);animation:dot 1.2s ease infinite}
.dots i:nth-child(2){animation-delay:.15s}.dots i:nth-child(3){animation-delay:.3s}
@keyframes dot{0%,80%,100%{transform:scale(.5);opacity:.3}40%{transform:scale(1);opacity:1}}
.card-stage{font-size:11px;color:var(--yellow);padding:4px 0;display:flex;align-items:center;gap:6px}
.card-stage .ic{font-size:13px}
.card-elapsed{font-size:10px;color:var(--text3);padding:2px 0}
.card-res{font-size:12px;line-height:1.6;color:var(--text2);background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:10px 12px;max-height:250px;overflow-y:auto;white-space:pre-wrap;word-break:break-word}
.card-time{font-size:9px;color:var(--text3);margin-top:6px}
.stop-btn{font-family:'Inter',sans-serif;font-size:10px;font-weight:600;padding:4px 12px;border-radius:10px;border:1px solid #ef444440;background:#ef444418;color:var(--red);cursor:pointer;margin-top:6px}
.stop-btn:active{background:#ef444430}

/* Permission card */
.perm-card{background:#fbbf2410;border:1px solid #fbbf2430;border-radius:14px;padding:14px;margin-bottom:8px;animation:up .35s ease}
.perm-title{font-size:13px;font-weight:600;color:var(--yellow);margin-bottom:6px;display:flex;align-items:center;gap:6px}
.perm-desc{font-size:12px;color:var(--text2);margin-bottom:10px;line-height:1.5;background:var(--bg);border-radius:8px;padding:8px 10px;white-space:pre-wrap;word-break:break-word;max-height:150px;overflow-y:auto}
.perm-btns{display:flex;gap:8px}
.perm-btn{flex:1;font-family:'Inter',sans-serif;font-size:13px;font-weight:600;padding:10px;border-radius:12px;border:none;cursor:pointer}
.perm-yes{background:var(--green);color:#0a0a0f}
.perm-no{background:var(--red);color:#fff}
.perm-btn:active{transform:scale(.96)}

/* Input */
.input-wrap{position:relative;z-index:50;padding:8px 12px;padding-bottom:max(8px,env(safe-area-inset-bottom));background:linear-gradient(to top,var(--bg) 60%,transparent)}
.input-box{background:var(--surface);border:1px solid var(--border2);border-radius:18px;padding:5px;display:flex;align-items:flex-end;gap:0;box-shadow:0 -2px 30px #00000050,0 0 60px var(--cl-glow);transition:border-color .3s}
.input-box:focus-within{border-color:var(--cl-dim)}
textarea.inp{flex:1;background:none;border:none;outline:none;color:var(--text);font-family:'Inter',sans-serif;font-size:15px;padding:9px 12px;min-height:38px;max-height:100px;resize:none;line-height:1.45}
textarea.inp::placeholder{color:var(--text3)}
.btns{display:flex;gap:3px;padding-bottom:1px}
.b{width:38px;height:38px;border-radius:13px;border:none;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:all .15s}
.b svg{width:17px;height:17px}
.b-mic{background:var(--surface2);color:var(--text2)}
.b-send{background:var(--cl);color:#0a0a0f}
.b-send:active{transform:scale(.93)}
.b-send:disabled{background:var(--surface2);color:var(--text3)}

/* Voice overlay */
.vo{position:fixed;inset:0;z-index:1000;background:var(--bg);display:none;flex-direction:column;opacity:0;transition:opacity .3s ease}
.vo.open{display:flex;opacity:1}
.vo-top{padding:16px;display:flex;justify-content:space-between;align-items:center}
.vo-close{width:36px;height:36px;border-radius:12px;background:var(--surface2);border:1px solid var(--border2);display:flex;align-items:center;justify-content:center;cursor:pointer;color:var(--text2)}
.vo-close svg{width:16px;height:16px}
.vo-center{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px}
.orb-wrap{position:relative;width:160px;height:160px}
.orb{width:160px;height:160px;border-radius:50%;background:radial-gradient(circle at 40% 35%,var(--cl2),var(--cl),#a07050);box-shadow:0 0 60px var(--cl-dim),0 0 120px var(--cl-glow);cursor:pointer;-webkit-tap-highlight-color:transparent;position:relative;z-index:10;touch-action:manipulation;transition:all .5s ease}
.orb.listening{animation:orbPulse 2s ease infinite;box-shadow:0 0 80px #d4a57450,0 0 160px #d4a57425}
.orb.speaking{animation:orbSpeak .6s ease infinite;box-shadow:0 0 100px #34d39940,0 0 180px #34d39920;background:radial-gradient(circle at 40% 35%,#a0e8c8,var(--green),#20a070)}
@keyframes orbPulse{0%,100%{transform:scale(1)}50%{transform:scale(1.08)}}
@keyframes orbSpeak{0%,100%{transform:scale(1)}50%{transform:scale(1.05)}}
.ring{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:160px;height:160px;border-radius:50%;border:1px solid var(--cl-dim);opacity:0;pointer-events:none}
.listening .ring{animation:ringPulse 2.5s ease infinite}
.ring:nth-child(2){animation-delay:.5s!important}.ring:nth-child(3){animation-delay:1s!important}
@keyframes ringPulse{0%{transform:translate(-50%,-50%) scale(1);opacity:.5}100%{transform:translate(-50%,-50%) scale(2);opacity:0}}
.vo-status{font-size:14px;font-weight:500;color:var(--text2);min-height:20px;text-align:center;padding:0 20px}
.vo-transcript{font-size:18px;font-weight:600;text-align:center;max-width:85%;min-height:28px;line-height:1.4}
.vo-response{font-size:13px;text-align:center;color:var(--text2);max-width:85%;min-height:20px;line-height:1.5;max-height:120px;overflow-y:auto}
.vo-bottom{padding:16px;display:flex;flex-direction:column;gap:8px;align-items:center}
.vo-voice-row{display:flex;gap:6px;flex-wrap:wrap;justify-content:center}
.vo-vbtn{font-family:'Inter',sans-serif;font-size:11px;font-weight:500;padding:6px 14px;border-radius:20px;border:1px solid var(--border2);background:var(--surface);color:var(--text2);cursor:pointer}
.vo-vbtn.sel{background:var(--cl);color:#0a0a0f;border-color:var(--cl)}
.vo-send{font-family:'Inter',sans-serif;font-size:14px;font-weight:600;padding:12px 40px;border-radius:16px;border:none;background:var(--cl);color:#0a0a0f;cursor:pointer;margin-top:4px}
.vo-send:active{transform:scale(.95)}
.vo-send:disabled{background:var(--surface2);color:var(--text3)}
.mic-error{display:none;background:#ef444420;border:1px solid #ef444440;border-radius:12px;padding:12px 16px;margin:0 16px;font-size:12px;color:var(--red);line-height:1.5;text-align:center}
.mic-error.show{display:block}
::-webkit-scrollbar{width:3px}::-webkit-scrollbar-track{background:transparent}::-webkit-scrollbar-thumb{background:var(--text3);border-radius:3px}
</style>
</head>
<body>

<div class="top">
  <div class="top-left"><div class="logo">J</div><div><div class="top-title">J.A.R.V.I.S.</div><div class="top-sub">MacBook Pro &bull; AI Assistant</div></div></div>
  <div class="online"><i></i>Online</div>
</div>
<div class="stats">
  <div class="st"><b id="sT">0</b><span>Tasks</span></div>
  <div class="st"><b id="sD">0</b><span>Done</span></div>
  <div class="st"><b id="sR">0</b><span>Active</span></div>
</div>
<div class="scroll" id="scroll"></div>

<div class="input-wrap" id="inputWrap">
  <div class="input-box">
    <textarea class="inp" id="inp" placeholder="Wydaj polecenie, Szefie..." rows="1" oninput="resizeTA(this)"></textarea>
    <div class="btns">
      <button class="b b-mic" onclick="openVoice()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/><path d="M19 10v2a7 7 0 01-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg></button>
      <button class="b b-send" id="sendBtn" onclick="send()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg></button>
    </div>
  </div>
</div>

<!-- Voice overlay -->
<div class="vo" id="vo">
  <div class="vo-top"><div style="font-weight:600;font-size:14px">J.A.R.V.I.S. Voice</div><div class="vo-close" onclick="closeVoice()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></div></div>
  <div class="mic-error" id="micError"></div>
  <div class="vo-center">
    <div class="orb-wrap" id="orbWrap"><div class="orb" id="orb"></div><div class="ring"></div><div class="ring"></div><div class="ring"></div></div>
    <div class="vo-status" id="voSt">Dotknij aby mowic, Szefie</div>
    <div class="vo-transcript" id="voTx"></div>
    <div class="vo-response" id="voRes"></div>
  </div>
  <div class="vo-bottom">
    <div style="font-size:11px;color:var(--text3);margin-bottom:2px">Glos odpowiedzi:</div>
    <div class="vo-voice-row" id="voiceRow"></div>
    <button class="vo-send" id="voSend" onclick="voiceSend()" disabled>Wyslij polecenie</button>
  </div>
</div>

<script>
// ═══ VIEWPORT ═══
if(window.visualViewport){const w=document.getElementById('inputWrap'),b=document.body;function onVP(){const v=window.visualViewport,d=window.innerHeight-v.height;if(d>50){b.style.height=v.height+'px';w.style.paddingBottom='8px'}else{b.style.height='100dvh';w.style.paddingBottom=''}document.getElementById('scroll').scrollTop=999999}window.visualViewport.addEventListener('resize',onVP);window.visualViewport.addEventListener('scroll',onVP)}
function resizeTA(el){el.style.height='auto';el.style.height=Math.min(el.scrollHeight,100)+'px'}
function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML}
function ago(ts){const d=Math.floor(Date.now()/1000-ts);if(d<60)return'teraz';if(d<3600)return Math.floor(d/60)+'m temu';return Math.floor(d/3600)+'h temu'}

// ═══ SEND ═══
async function send(text){const ta=document.getElementById('inp');const p=text||ta.value.trim();if(!p)return;document.getElementById('sendBtn').disabled=true;try{await fetch('/send',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'prompt='+encodeURIComponent(p)});if(!text){ta.value='';ta.style.height='auto'}poll()}catch(e){}document.getElementById('sendBtn').disabled=false}
document.getElementById('inp').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send()}});
async function stopJob(id){try{await fetch('/stop',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'id='+id});poll()}catch(e){}}
async function respondPerm(id,allow){try{await fetch('/perm',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:id,allow:allow})});poll()}catch(e){}}

// ═══ SMART POLL (no flicker) ═══
let lastData='';
const stageIcons={'Bash':'&#9654;','Edit':'&#9998;','Write':'&#128196;','Read':'&#128065;','Glob':'&#128269;','Grep':'&#128270;','thinking':'&#129504;','default':'&#9881;'};

function renderCard(j){
  const cls=j.status;
  const bdg=cls==='running'?'Pracuje...':cls==='done'?'Gotowe':cls==='stopped'?'Stop':'Blad';
  let h='<div class="card-head"><div class="card-prompt">'+esc(j.prompt)+'</div><div class="badge '+cls+'">'+bdg+'</div></div>';
  if(cls==='running'){
    h+='<div class="dots"><i></i><i></i><i></i></div>';
    if(j.stage){
      const ico=stageIcons[j.stage_tool]||stageIcons['default'];
      h+='<div class="card-stage"><span class="ic">'+ico+'</span>'+esc(j.stage)+'</div>';
    }
    if(j.elapsed)h+='<div class="card-elapsed">'+esc(j.elapsed)+'</div>';
    h+='<button class="stop-btn" onclick="stopJob('+j.id+')">Zatrzymaj</button>';
  }
  if(j.result)h+='<div class="card-res">'+esc(j.result)+'</div>';
  if(j.started)h+='<div class="card-time">'+ago(j.started)+'</div>';
  return h;
}

function renderPerm(p){
  return '<div class="perm-title">&#9888; Pytanie o pozwolenie</div>'
    +'<div class="perm-desc">'+esc(p.desc)+'</div>'
    +'<div class="perm-btns">'
    +'<button class="perm-btn perm-yes" onclick="respondPerm('+p.id+',true)">Tak, zrob to</button>'
    +'<button class="perm-btn perm-no" onclick="respondPerm('+p.id+',false)">Nie, anuluj</button>'
    +'</div>';
}

async function poll(){
  try{
    const [jr,pr]=await Promise.all([fetch('/jobs').then(r=>r.json()),fetch('/perms').then(r=>r.json())]);
    const newData=JSON.stringify(jr)+JSON.stringify(pr);
    if(newData===lastData)return; // no change = no DOM update
    lastData=newData;

    let t=jr.length,d=0,rn=0;
    jr.forEach(j=>{if(j.status==='done')d++;if(j.status==='running')rn++});
    document.getElementById('sT').textContent=t;
    document.getElementById('sD').textContent=d;
    document.getElementById('sR').textContent=rn;

    const el=document.getElementById('scroll');

    if(!jr.length&&!pr.length){
      el.innerHTML='<div class="empty"><div class="empty-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="26" height="26"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg></div><h3>Do uslug, Szefie</h3><p>Powiedz lub napisz polecenie.<br>Wykonam je na Twoim Macu.</p></div>';
      return;
    }

    // Build map of existing cards
    const existing={};
    el.querySelectorAll('[data-id]').forEach(c=>existing[c.dataset.id]=c);

    // Render permissions first, then jobs
    const ids=[];
    for(const p of pr){
      const did='perm-'+p.id;ids.push(did);
      const html=renderPerm(p);
      if(existing[did]){
        if(existing[did].innerHTML!==html)existing[did].innerHTML=html;
      }else{
        const div=document.createElement('div');div.className='perm-card';div.dataset.id=did;div.innerHTML=html;
        el.insertBefore(div,el.firstChild);
      }
    }
    for(const j of jr){
      const did='job-'+j.id;ids.push(did);
      const html=renderCard(j);
      if(existing[did]){
        if(existing[did].innerHTML!==html)existing[did].innerHTML=html;
      }else{
        const div=document.createElement('div');div.className='card new';div.dataset.id=did;div.innerHTML=html;
        el.appendChild(div);
        setTimeout(()=>div.classList.remove('new'),400);
      }
    }
    // Remove stale cards
    el.querySelectorAll('[data-id]').forEach(c=>{if(!ids.includes(c.dataset.id))c.remove()});

    // Voice: speak newly done jobs
    for(const j of jr){
      if(j.status==='done'&&!j._spoken&&voiceOpen){
        j._spoken=true;speakResult(j.result);
      }
    }
  }catch(e){}
}
setInterval(poll,1500);poll();

// ═══ VOICE ═══
let voiceOpen=false,recognition=null,isListening=false,selectedVoice=null,voices=[];
const hasSR=('webkitSpeechRecognition' in window||'SpeechRecognition' in window);
function loadVoices(){voices=speechSynthesis.getVoices();const row=document.getElementById('voiceRow');if(!voices.length)return;const picks=[];const want=['Google','Samantha','Daniel','Zosia','Anna','Paulina','Monika','Alex','Karen','Tessa'];for(const v of voices){if(want.some(w=>v.name.includes(w)))picks.push(v)}if(!picks.length)picks.push(...voices.filter(v=>v.lang.startsWith('pl')));if(!picks.length)picks.push(...voices.slice(0,6));row.innerHTML='';picks.slice(0,8).forEach((v,i)=>{const btn=document.createElement('button');btn.className='vo-vbtn'+(i===0?' sel':'');btn.textContent=v.name.replace('Google ','').replace('Microsoft ','').split('(')[0].trim();btn.onclick=()=>{selectedVoice=v;row.querySelectorAll('.vo-vbtn').forEach(b=>b.classList.remove('sel'));btn.classList.add('sel')};row.appendChild(btn);if(i===0)selectedVoice=v})}
speechSynthesis.onvoiceschanged=loadVoices;loadVoices();
function showMicError(m){const e=document.getElementById('micError');e.innerHTML=m;e.classList.add('show')}
function hideMicError(){document.getElementById('micError').classList.remove('show')}
function openVoice(){voiceOpen=true;document.getElementById('vo').classList.add('open');hideMicError();document.getElementById('voTx').dataset.final='';if(!hasSR){showMicError('Brak wsparcia mowy w przegladarce');return}if(!window.isSecureContext){showMicError('Mikrofon wymaga HTTPS.<br>chrome://flags > insecure origins > '+location.origin);return}setTimeout(()=>startListening(),300)}
function closeVoice(){voiceOpen=false;stopListening();speechSynthesis.cancel();document.getElementById('vo').classList.remove('open');document.getElementById('voTx').textContent='';document.getElementById('voRes').textContent='';hideMicError()}
function toggleListening(){if(isListening)stopListening();else startListening()}
(function(){const orb=document.getElementById('orb');let t=false;orb.addEventListener('touchstart',function(e){e.preventDefault();e.stopPropagation();t=true;toggleListening()},{passive:false,capture:true});orb.addEventListener('click',function(e){e.preventDefault();if(t){t=false;return}toggleListening()},{capture:true})})();
function startListening(){if(!hasSR)return;hideMicError();const SR=window.SpeechRecognition||window.webkitSpeechRecognition;recognition=new SR();recognition.lang='pl-PL';recognition.interimResults=true;recognition.continuous=false;
recognition.onstart=()=>{isListening=true;document.getElementById('orb').classList.add('listening');document.getElementById('orbWrap').classList.add('listening');document.getElementById('voSt').textContent='Slucham...'};
recognition.onresult=(e)=>{let text='';for(let i=e.resultIndex;i<e.results.length;i++)text+=e.results[i][0].transcript;const prev=document.getElementById('voTx').dataset.final||'';const last=e.results[e.results.length-1];if(last.isFinal){const nf=prev+(prev?' ':'')+last[0].transcript;document.getElementById('voTx').dataset.final=nf;document.getElementById('voTx').textContent=nf;document.getElementById('voSend').disabled=false}else{document.getElementById('voTx').textContent=prev+(prev?' ':'')+text}};
recognition.onerror=(e)=>{if(e.error==='not-allowed'){showMicError('Mikrofon zablokowany — zezwol w ustawieniach');stopListening();return}if(e.error!=='no-speech'&&e.error!=='aborted')stopListening()};
recognition.onend=()=>{if(isListening)try{setTimeout(()=>{if(isListening)recognition.start()},100)}catch(e){}};
try{recognition.start()}catch(e){showMicError('Blad mikrofonu: '+e.message)}}
function stopListening(){isListening=false;if(recognition)try{recognition.stop()}catch(e){}document.getElementById('orb').classList.remove('listening','speaking');document.getElementById('orbWrap').classList.remove('listening');document.getElementById('voSt').textContent='Dotknij aby mowic, Szefie'}
function speakResult(text){speechSynthesis.cancel();const orb=document.getElementById('orb');orb.classList.remove('listening');orb.classList.add('speaking');document.getElementById('orbWrap').classList.remove('listening');document.getElementById('voSt').textContent='Odpowiadam...';document.getElementById('voRes').textContent=text;const utt=new SpeechSynthesisUtterance(text);utt.lang='pl-PL';if(selectedVoice)utt.voice=selectedVoice;utt.rate=1.05;utt.onend=()=>{orb.classList.remove('speaking');document.getElementById('voSt').textContent='Gotowe, Szefie. Czekam na rozkazy dalej'};speechSynthesis.speak(utt)}
async function voiceSend(){const tx=document.getElementById('voTx').textContent.trim();if(!tx)return;stopListening();document.getElementById('voSt').textContent='Wysylam...';document.getElementById('voSend').disabled=true;document.getElementById('voRes').textContent='';document.getElementById('voTx').dataset.final='';try{await fetch('/send',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:'prompt='+encodeURIComponent(tx)});document.getElementById('voSt').textContent='Claude pracuje...';poll();waitForResult(tx)}catch(e){document.getElementById('voSt').textContent='Blad polaczenia'}}
function waitForResult(prompt){const check=setInterval(async()=>{try{const r=await fetch('/jobs');const jobs=await r.json();const m=jobs.find(j=>j.prompt===prompt&&j.status!=='running');if(m){clearInterval(check);poll();if(m.result){speakResult(m.result);document.getElementById('voTx').textContent=''}}}catch(e){}},2000)}
</script>
</body>
</html>"""
