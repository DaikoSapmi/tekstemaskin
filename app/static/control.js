// app/static/control.js
(function(){
  const $ = (sel, root=document) => root.querySelector(sel);

  const statusEl = $('#status');
  const startBtn = $('#btnStart');
  const stopBtn  = $('#btnStop');
  const afterBtn = $('#btnAfter');
  const summBtn  = $('#btnSumm');
  const liveEl   = $('#liveText');
  const chromaEl = $('#chromaText');

  function setStatus(msg){ if(statusEl) statusEl.textContent = msg; }
  function toggle(run){ if(startBtn && stopBtn){ startBtn.disabled = run; stopBtn.disabled = !run; } }

  if(startBtn){
    startBtn.addEventListener('click', async () => {
      try{
        setStatus('Starter…');
        const res = await fetch('/start', {method:'POST'});
        const js = await res.json();
        if(js.status === 'started' || js.status === 'already_running'){
          toggle(true); setStatus('I gang');
        }else{ setStatus('Kunne ikke starte (' + (js.status||'ukjent') + ')'); }
      }catch(err){ setStatus('Feil ved start'); console.error(err); }
    });
  }

  if(stopBtn){
    stopBtn.addEventListener('click', async () => {
      try{
        setStatus('Stopper…');
        const res = await fetch('/stop', {method:'POST'});
        const js = await res.json();
        if(js.status === 'stopped'){
          toggle(false); setStatus('Stoppet');
        }else{ setStatus('Ikke i gang (' + (js.status||'ukjent') + ')'); }
      }catch(err){ setStatus('Feil ved stopp'); console.error(err); }
    });
  }

  if(afterBtn){
    afterBtn.addEventListener('click', async () => {
      try{
        setStatus('Starter transkribering av storfil…');
        // Vi venter ikke på svaret her, status kommer via WebSocket
        fetch('/after', {method:'POST'});
      }catch(err){ setStatus('Feil ved transkribering'); console.error(err); }
    });
  }

  if(summBtn){
    summBtn.addEventListener('click', async () => {
      try{
        setStatus('Lager møtereferat…');
        const res = await fetch('/summarize', {method:'POST'});
        const js = await res.json();
        if(js.status === 'ok'){
          setStatus('Referat klart. Starter nedlasting...');
          // Denne URL-en vil nå tvinge nedlasting
          window.location.href = '/download/md';
        }else{
          setStatus('Kunne ikke lage referat: ' + (js.message || 'Ukjent feil'));
        }
      }catch(err){ setStatus('Feil ved referat'); console.error(err); }
    });
  }

  // WebSocket for live segmenter og status
  if(liveEl || chromaEl || statusEl){
    connectWS();
  }

  function connectWS(){
    const proto = location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${proto}://${location.host}/ws`);
    ws.onmessage = (ev) => {
      try{
        const msg = JSON.parse(ev.data);
        
        if(msg.type === 'segments'){
          const text = msg.items.map(it => it.text).filter(Boolean).join(' ').trim();
          if(!text) return;
          if(liveEl){
            const div = document.createElement('div');
            div.textContent = text;
            liveEl.appendChild(div);
            const box = liveEl.parentElement; if(box) box.scrollTop = box.scrollHeight;
          }
          if(chromaEl){ chromaEl.textContent = text; }
        }

        if(msg.type === 'status'){
          setStatus(msg.text); // Oppdaterer status-vinduet
        }
      }catch(e){ /* ignore */ }
    };
    ws.onclose = () => setTimeout(connectWS, 1500);
  }
})();