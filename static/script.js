async function updateStatus(){
  const res = await fetch('/status');
  const data = await res.json();
  document.getElementById('free').textContent = data.free;
  document.getElementById('occ').textContent = data.occupied;
  document.getElementById('tot').textContent = data.total;
}
setInterval(updateStatus,1000);

function switchCam(){
  const sel = document.getElementById('camSelect');
  const formData = new FormData();
  formData.append('camera', sel.value);
  fetch('/switch',{method:'POST',body:formData});
  document.getElementById('stream').src='/video_feed?cache='+Date.now();
}
