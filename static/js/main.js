/* ============================================================
   InkCheck — main.js
   ============================================================ */
document.addEventListener('DOMContentLoaded', () => {

  const fileInput   = document.getElementById('fileInput');
  const uploadZone  = document.getElementById('uploadZone');
  const uploadForm  = document.getElementById('uploadForm');
  const overlay     = document.getElementById('processingOverlay');
  const defaultView = document.getElementById('uploadDefault');
  const previewView = document.getElementById('uploadPreview');
  const previewImg  = document.getElementById('previewImg');
  const previewName = document.getElementById('previewName');
  const previewSize = document.getElementById('previewSize');

  if (fileInput) fileInput.addEventListener('change', handleFile);

  function handleFile() {
    const file = this.files[0];
    if (!file) return;
    if (defaultView) defaultView.style.display = 'none';
    if (previewView) previewView.style.display = 'block';
    const reader = new FileReader();
    reader.onload = e => { if (previewImg) previewImg.src = e.target.result; };
    reader.readAsDataURL(file);
    if (previewName) previewName.textContent = file.name;
    if (previewSize) previewSize.textContent = fmtBytes(file.size);
  }

  function fmtBytes(b) {
    if (b < 1024)    return b + ' B';
    if (b < 1048576) return (b / 1024).toFixed(1) + ' KB';
    return (b / 1048576).toFixed(1) + ' MB';
  }

  if (uploadZone) {
    ['dragenter','dragover'].forEach(ev => {
      uploadZone.addEventListener(ev, e => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
    });
    ['dragleave','drop'].forEach(ev => {
      uploadZone.addEventListener(ev, e => { e.preventDefault(); uploadZone.classList.remove('drag-over'); });
    });
    uploadZone.addEventListener('drop', e => {
      if (e.dataTransfer.files.length > 0 && fileInput) {
        fileInput.files = e.dataTransfer.files;
        handleFile.call(fileInput);
      }
    });
  }

  if (uploadForm && overlay) {
    uploadForm.addEventListener('submit', () => {
      if (fileInput && fileInput.files.length === 0) return;
      overlay.classList.add('active');
      cycleMessages();
    });
  }

  const msgs = [
    'Preprocessing image…','Normalizing pixel values…',
    'Loading CNN model weights…','Extracting feature maps…',
    'Running deep inference…','Scoring signature patterns…','Generating verdict…'
  ];

  function cycleMessages() {
    const el = document.getElementById('procLabel');
    if (!el) return;
    let i = 0; el.textContent = msgs[0];
    setInterval(() => {
      i = (i + 1) % msgs.length;
      el.style.opacity = '0';
      setTimeout(() => { el.textContent = msgs[i]; el.style.opacity = '1'; }, 220);
    }, 1100);
  }

  const confFill  = document.getElementById('confFill');
  const confCount = document.getElementById('confCount');
  if (confFill) {
    const tw = parseFloat(confFill.dataset.width || 0);
    setTimeout(() => { confFill.style.width = tw + '%'; }, 500);
  }
  if (confCount) {
    const target = parseFloat(confCount.dataset.target || 0);
    let cur = 0; const step = target / 70;
    const t = setInterval(() => {
      cur = Math.min(cur + step, target);
      confCount.textContent = cur.toFixed(1) + '%';
      if (cur >= target) clearInterval(t);
    }, 20);
  }

  document.querySelectorAll('.field-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const inp = btn.closest('.field-wrap').querySelector('input');
      if (!inp) return;
      const show = inp.type === 'password';
      inp.type = show ? 'text' : 'password';
      btn.innerHTML = show
        ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`
        : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
    });
  });

  document.querySelectorAll('.flash-alert').forEach(alert => {
    const btn = alert.querySelector('.flash-close');
    if (btn) btn.addEventListener('click', () => dismiss(alert));
    setTimeout(() => dismiss(alert), 5500);
  });

  function dismiss(el) {
    if (!el || !el.parentNode) return;
    el.style.transition = 'opacity .4s ease, transform .4s ease';
    el.style.opacity = '0'; el.style.transform = 'translateY(-4px)';
    setTimeout(() => { if(el.parentNode) el.remove(); }, 420);
  }

});