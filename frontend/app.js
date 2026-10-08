const $ = (selector) => document.querySelector(selector);

async function request(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok && response.status !== 204) throw new Error(`Request failed (${response.status})`);
  return response.status === 204 ? null : response.json();
}

function setConnection(online) {
  const label = $('#connectionText');
  if (label) label.textContent = online ? 'API online' : 'API unavailable';
  const pulse = document.querySelector('.pulse');
  if (pulse && !online) pulse.style.background = '#d96b59';
}

function renderResults(items = []) {
  const body = $('#resultsBody');
  if (!body) return;
  if (!items.length) { body.innerHTML = '<tr><td colspan="4" class="table-empty">Run a scan to populate control checks.</td></tr>'; return; }
  body.innerHTML = items.map((item) => `<tr><td>${escapeHtml(item.category || 'General')}<br><span class="muted">${escapeHtml(item.label || '')}</span></td><td>${escapeHtml(item.value || 'Not detected')}</td><td><span class="status-badge ${item.compliant ? 'status-pass' : 'status-fail'}">${item.compliant ? 'Passed' : 'Review'}</span></td><td class="recommendation">${escapeHtml(item.suggestion || 'No action required.')}</td></tr>`).join('');
}

function renderScan(scan, items, counts) {
  const passed = counts?.passed || 0;
  const total = counts?.total || items?.length || 0;
  const failed = counts?.failed || Math.max(total - passed, 0);
  const score = total ? Math.round((passed / total) * 100) : 0;
  $('#emptyState')?.classList.add('hidden');
  $('#summaryState')?.classList.remove('hidden');
  $('#scoreText').textContent = score >= 80 ? 'Healthy posture' : 'Needs attention';
  $('#scoreValue').textContent = `${score}%`;
  $('#scoreMeter').style.width = `${score}%`;
  $('#summaryText').textContent = scan?.ai_summary || 'Assessment complete. Review the controls below for next steps.';
  $('#passedCount').textContent = passed;
  $('#failedCount').textContent = failed;
  $('#totalCount').textContent = total;
  $('#lastUpdated').textContent = scan?.created_at ? `Assessed ${formatDate(scan.created_at)}` : 'Assessment complete';
  renderResults(items);
}

async function loadLatest() {
  try {
    const data = await request('/api/latest');
    setConnection(true);
    if (data?.scan) renderScan(data.scan, data.items, data.counts);
    const history = await request('/api/history');
    if ($('#scanCount')) $('#scanCount').textContent = history?.scans?.length || 0;
  } catch (error) { setConnection(false); console.error(error); }
}

async function submitScan(event) {
  event.preventDefault();
  const message = $('#formMessage'); const button = $('#buttonText');
  message.textContent = 'Analyzing snapshot...'; button.textContent = 'Working';
  try {
    const data = await request('/api/submit', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ raw_output: $('#rawOutput').value }) });
    renderScan({ ai_summary: data.summary }, data.items, { total: data.items.length, passed: data.items.filter((item) => item.compliant).length });
    message.textContent = 'Assessment saved to history'; $('#rawOutput').value = '';
  } catch (error) { message.textContent = 'Could not complete assessment'; console.error(error); }
  button.textContent = 'Analyze snapshot';
}

async function loadHistory() {
  try {
    const data = await request('/api/history'); const body = $('#historyBody');
    if (!body) return;
    if (!data?.scans?.length) { body.innerHTML = '<tr><td colspan="4" class="table-empty">No assessments archived yet.</td></tr>'; return; }
    body.innerHTML = data.scans.map((scan) => `<tr><td><span class="scan-id">SCAN-${String(scan.id).padStart(4, '0')}</span></td><td>${formatDate(scan.created_at)}</td><td class="history-summary">${escapeHtml(scan.ai_summary || 'No summary available.')}</td><td><a class="open-link" href="/?scan=${scan.id}">View ↗</a></td></tr>`).join('');
  } catch (error) { const body = $('#historyBody'); if (body) body.innerHTML = '<tr><td colspan="4" class="table-empty">Archive unavailable.</td></tr>'; console.error(error); }
}

function formatDate(value) { return new Date(value).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }); }
function escapeHtml(value) { return String(value).replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character])); }

document.addEventListener('DOMContentLoaded', () => { $('#scanForm')?.addEventListener('submit', submitScan); loadLatest(); loadHistory(); });