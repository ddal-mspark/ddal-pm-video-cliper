const el = (id) => document.getElementById(id);
let uploaded = null; // server filename
let downloadUrl = null;

function setEnabled(element, enabled) {
  element.disabled = !enabled;
  element.classList.toggle('disabled', !enabled);
}

el('uploadBtn').addEventListener('click', () => el('file').click());

el('file').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  el('fileInfo').textContent = `${file.name} — ${(file.size/1e6).toFixed(1)} MB`;
  el('player').src = URL.createObjectURL(file);
  const form = new FormData();
  form.append('file', file);
  const res = await fetch('/upload', { method: 'POST', body: form });
  const j = await res.json();
  if (!j.ok) { alert('Upload failed'); return; }
  uploaded = j.filename;
  setEnabled(el('process'), true);
});

function updateTaskUI() {
  const val = document.querySelector('input[name="task"]:checked').value;
  const isGif  = (val === 'vgif');
  const isDeid = (val === 'deid');
  document.getElementById('deidBox')?.classList.toggle('hidden', !isDeid);
  document.getElementById('gifQualityRow')?.classList.toggle('hidden', !isGif);
}

// 라디오 변경 시 반영
document.querySelectorAll('input[name="task"]').forEach(r => {
  r.addEventListener('change', updateTaskUI);
});

document.querySelector('.logs').removeAttribute('open'); 

function isTimeLike(s) {
  if (!s) return false;
  s = String(s).trim();
  // allow plain seconds like "30" or hh:mm:ss / mm:ss
  if (/^\d+$/.test(s)) return true;
  if (/^\d{1,2}:\d{2}(?:[:]\d{2})?$/.test(s)) return true;
  return false;
}

function normalizeTimeField(s) {
  if (!s) return null;
  s = String(s).trim();
  if (s === "") return null;
  // plain integer seconds -> keep as number string
  if (/^\d+$/.test(s)) return s;
  // mm:ss or hh:mm:ss -> normalize to hh:mm:ss if needed
  if (/^\d{1,2}:\d{2}$/.test(s)) {
    // mm:ss -> convert to 00:mm:ss
    return `00:${s}`;
  }
  if (/^\d{1,2}:\d{2}:\d{2}$/.test(s)) {
    return s;
  }
  return null; // invalid
}

el('process').addEventListener('click', async () => {
  if (!uploaded) return alert('Upload a video first');

  el('logs').textContent = 'Processing...';
  setEnabled(el('download'), false);
  downloadUrl = null;

  const isGif = document.querySelector('input[name="task"]:checked').value === 'vgif';
  const gifQuality = isGif ? document.getElementById('gifQuality').value : 'custom';
  const fpsValue = document.getElementById('fps').value;
  const payload = {
    filename: uploaded,
    task: document.querySelector('input[name="task"]:checked').value,
    resolution: document.getElementById('resolution').value || null,
    fps: fpsValue === 'default' ? null : Number(fpsValue),
    mute: document.getElementById('mute').checked,
    deid_args: document.getElementById('deidArgs')?.value || null,
    gif_quality: gifQuality,
    start_time: (isTimeLike(document.getElementById('startTime').value) ? normalizeTimeField(document.getElementById('startTime').value) : null),
    duration: (isTimeLike(document.getElementById('duration').value) ? normalizeTimeField(document.getElementById('duration').value) : null),    
  };

  const res = await fetch('/process', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  const j = await res.json();
  if (!j.ok) {
    el('logs').textContent = (j.detail || j.error || 'failed');
    return;
  }
  el('logs').textContent = (j.stderr || '') + '\n' + (j.stdout || '');
  downloadUrl = j.download_url;
  setEnabled(el('download'), true);
});

el('download').addEventListener('click', () => {
  if (downloadUrl) {
    window.open(downloadUrl, '_blank');
  }
});

document.addEventListener('DOMContentLoaded', () => {
  updateTaskUI();
  // 기본 접힘 유지하고 싶으면 여기에서 닫아두기
  document.querySelector('.logs')?.removeAttribute('open');
});

document.getElementById('gifQuality')?.addEventListener('change', (e) => {
  const q = e.target.value;
  if (q === 'tiny')   { el('resolution').value = '360'; el('fps').value = '10'; }
  if (q === 'small')  { el('resolution').value = '480'; el('fps').value = '10'; }
  if (q === 'medium') { el('resolution').value = '640'; el('fps').value = '12'; }
  if (q === 'high')   { el('resolution').value = '720'; el('fps').value = '15'; }
});