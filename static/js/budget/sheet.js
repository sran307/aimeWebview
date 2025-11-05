(function(){
  function getCSRF() {
    const token = document.querySelector('meta[name="csrf-token"]');
    return token ? token.content : null;
  }

  function debounce(fn, wait){
    let t;
    return function(...args){
      clearTimeout(t);
      t = setTimeout(()=>fn.apply(this,args), wait);
    };
  }

  function setStatus(text){
    const el = document.getElementById('status');
    if(el) el.textContent = text;
  }

  async function loadSheet() {
    setStatus('Loading sheet...');
    const res = await fetch(window.SHEETS_INIT.loadUrl, { credentials: 'same-origin' });
    if(!res.ok) { setStatus('Failed to load sheet'); return; }
    const data = await res.json();
    const cells = data.cells || {};
    document.querySelectorAll('.cell').forEach(td=>{
      const key = td.dataset.row + ":" + td.dataset.col;
      if(cells[key]){
        td.textContent = cells[key].value;
        td.dataset.version = cells[key].version;
      } else {
        td.textContent = '';
        td.dataset.version = 0;
      }
    });
    setStatus('Loaded');
  }

  async function saveCellRequest(sheetId, row, col, value, version) {
    try {
      const res = await fetch(window.SHEETS_INIT.saveUrl, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRF()
        },
        body: JSON.stringify({sheet_id: sheetId, row, col, value, version})
      });

      if(res.status === 409){
        // conflict
        const data = await res.json();
        return {status: 'conflict', server_value: data.server_value, server_version: data.server_version};
      }

      if(!res.ok){
        const t = await res.text();
        return {status: 'error', text: t};
      }
      const data = await res.json();
      return data;
    } catch(e){
      return {status: 'error', text: e.message};
    }
  }

  function attachAutosave() {
    const saveDebounced = debounce(async (td) => {
      td.classList.remove('editing');
      setStatus('Saving...');
      const sheetId = td.dataset.sheet;
      const row = td.dataset.row;
      const col = td.dataset.col;
      const value = td.textContent;
      const version = parseInt(td.dataset.version || 0);
      const res = await saveCellRequest(sheetId, row, col, value, version);
      if(res.status === 'ok'){
        td.dataset.version = res.version;
        setStatus('Saved');
      } else if(res.status === 'conflict'){
        // simple client behavior: accept server value
        td.textContent = res.server_value;
        td.dataset.version = res.server_version;
        setStatus('Conflict: server value loaded');
      } else {
        setStatus('Save error: ' + (res.text || JSON.stringify(res)));
      }
    }, 600);

    document.querySelectorAll('.cell').forEach(td=>{
      td.addEventListener('input', function(){
        td.classList.add('editing');
        saveDebounced(td);
      });
      td.addEventListener('focus', ()=> td.classList.add('editing'));
      td.addEventListener('blur', ()=> { td.classList.remove('editing'); saveDebounced(td); });
    });
  }

  // init
  document.addEventListener('DOMContentLoaded', function(){
    loadSheet().then(()=> attachAutosave());
  });

})();
