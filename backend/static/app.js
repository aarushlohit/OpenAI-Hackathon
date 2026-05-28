/* ============================================================
   HERMES-X — Frontend Application Logic
   Conversational investigation interface
   ============================================================ */

'use strict';

// ── State ──────────────────────────────────────────────────
let attachedImage = null; // { file, dataUrl, mimeType }
let isInvestigating = false;
let currentHermesMessageEl = null;
let agentResults = {}; // Collects all agent data for tech panel

// ── DOM refs ───────────────────────────────────────────────
const $ = (id) => document.getElementById(id);

// ── Init ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setupTextarea();
  setupImageUpload();
  setupDragDrop();
  setupKeyboardShortcuts();
  checkHealth();
});

function setupTextarea() {
  const ta = $('messageInput');
  ta.addEventListener('input', () => {
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 200) + 'px';
  });
}

function setupKeyboardShortcuts() {
  $('messageInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendInvestigation();
    }
  });
}

function setupImageUpload() {
  const input = $('imageUpload');
  input.addEventListener('change', () => {
    if (input.files[0]) attachImageFile(input.files[0]);
  });
}

function setupDragDrop() {
  const overlay = $('dragOverlay');
  let dragDepth = 0;

  document.addEventListener('dragenter', (e) => {
    if (e.dataTransfer?.types.includes('Files')) {
      dragDepth++;
      overlay.classList.add('active');
    }
  });

  document.addEventListener('dragleave', () => {
    dragDepth--;
    if (dragDepth <= 0) {
      dragDepth = 0;
      overlay.classList.remove('active');
    }
  });

  document.addEventListener('dragover', (e) => e.preventDefault());

  document.addEventListener('drop', (e) => {
    e.preventDefault();
    dragDepth = 0;
    overlay.classList.remove('active');
    const file = e.dataTransfer?.files[0];
    if (file && file.type.startsWith('image/')) attachImageFile(file);
  });
}

function attachImageFile(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    attachedImage = { file, dataUrl: e.target.result, mimeType: file.type };
    $('previewImg').src = e.target.result;
    $('imagePreview').style.display = 'block';
  };
  reader.readAsDataURL(file);
}

function removeImage() {
  attachedImage = null;
  $('imagePreview').style.display = 'none';
  $('imageUpload').value = '';
  $('previewImg').src = '';
}

// ── Health Check ───────────────────────────────────────────
async function checkHealth() {
  try {
    const r = await fetch('/health');
    if (r.ok) setStatus('Ready', 'ok');
    else setStatus('Degraded', 'error');
  } catch {
    setStatus('Offline', 'error');
  }
}

function setStatus(text, state) {
  $('statusText').textContent = text;
  const dot = $('statusDot');
  dot.className = 'status-dot';
  if (state === 'loading') dot.classList.add('loading');
  if (state === 'error') dot.classList.add('error');
}

// ── Example fills ──────────────────────────────────────────
function fillExample(type) {
  const examples = {
    telegram: `Hi! We found your profile on LinkedIn and would love to offer you a position at TechCorp. 
The interview is waived for top candidates like you. 
Onboarding is done exclusively via Telegram (@recruiter_techcorp). 
A refundable security deposit of ₹4,500 via UPI is required to confirm your position. 
Please respond within 24 hours or the offer will be given to another candidate.`,
    domain: `Please complete your onboarding at: https://onboard.googles.xyz/careers
Your offer letter has been sent. Log in at micros0ft-careers.com with your details.
For verification, send your documents to hr@amaz0n-jobs.net`,
    google: `Hi! I'm a recruiter at Google (careers.google.com). We came across your profile and would like to schedule a technical interview for a Software Engineer position.
The process involves 3 rounds: coding screen, system design, and a team fit interview with the hiring manager. All interviews are conducted over Google Meet.
No fees or deposits are required at any stage. Can you share your availability for next week?`
  };

  const ta = $('messageInput');
  ta.value = examples[type] || '';
  ta.dispatchEvent(new Event('input'));
  ta.focus();
}

// ── New Investigation ──────────────────────────────────────
function startNewInvestigation() {
  $('conversationView').style.display = 'none';
  $('welcomeView').style.display = 'flex';
  $('messagesContainer').innerHTML = '';
  $('messageInput').value = '';
  $('messageInput').style.height = 'auto';
  removeImage();
  agentResults = {};
  currentHermesMessageEl = null;

  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  $('newInvestigationBtn').classList.add('active');
}

function showPlaceholder(name) {
  showConversation();
  const mc = $('messagesContainer');
  mc.innerHTML = '';
  const el = document.createElement('div');
  el.className = 'placeholder-message';
  el.textContent = `${name} — coming soon.`;
  mc.appendChild(el);
}

function showConversation() {
  $('welcomeView').style.display = 'none';
  $('conversationView').style.display = 'flex';
}

// ── Send Investigation ─────────────────────────────────────
async function sendInvestigation() {
  if (isInvestigating) return;

  const text = $('messageInput').value.trim();
  if (!text && !attachedImage) return;

  isInvestigating = true;
  $('sendBtn').disabled = true;
  setStatus('Investigating…', 'loading');

  // Show conversation view
  showConversation();

  // Render user message
  renderUserMessage(text, attachedImage?.dataUrl);

  // Clear input
  $('messageInput').value = '';
  $('messageInput').style.height = 'auto';
  const imageToSend = attachedImage;
  removeImage();

  // Start hermes message with progress steps
  agentResults = {};
  currentHermesMessageEl = renderHermesProgress();

  // Build form data
  const formData = new FormData();
  formData.append('text', text);
  if (imageToSend) {
    formData.append('image', imageToSend.file);
  }

  // Connect SSE
  try {
    const response = await fetch('/investigate', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split('\n\n');
      buffer = events.pop(); // Keep incomplete event

      for (const eventStr of events) {
        if (!eventStr.trim()) continue;
        parseSSEEvent(eventStr);
      }
    }
  } catch (err) {
    renderError(`Investigation failed: ${err.message}`);
  } finally {
    isInvestigating = false;
    $('sendBtn').disabled = false;
    setStatus('Ready', 'ok');
    scrollToBottom();
  }
}

// ── SSE Parsing ────────────────────────────────────────────
function parseSSEEvent(raw) {
  let eventType = 'message';
  let dataStr = '';

  for (const line of raw.split('\n')) {
    if (line.startsWith('event: ')) eventType = line.slice(7).trim();
    else if (line.startsWith('data: ')) dataStr = line.slice(6).trim();
  }

  if (!dataStr) return;

  let data;
  try { data = JSON.parse(dataStr); } catch { return; }

  switch (eventType) {
    case 'progress':
      updateProgressStep(data.step, data.message);
      break;
    case 'agent_result':
      agentResults[data.agent] = data.result;
      markStepDone(data.agent);
      break;
    case 'verdict':
      agentResults = { ...agentResults, ...data.technical };
      renderVerdict(data.consensus, data.technical);
      break;
    case 'error':
      renderError(data.message);
      break;
    case 'done':
      break;
  }

  scrollToBottom();
}

// ── Render helpers ─────────────────────────────────────────
function renderUserMessage(text, imageDataUrl) {
  const mc = $('messagesContainer');
  const el = document.createElement('div');
  el.className = 'message user';

  let html = '';
  if (text) html += `<div class="user-bubble">${escapeHtml(text)}</div>`;
  if (imageDataUrl) html += `<img class="user-image" src="${imageDataUrl}" alt="Attached image" />`;

  el.innerHTML = html;
  mc.appendChild(el);
  scrollToBottom();
}

function renderHermesProgress() {
  const mc = $('messagesContainer');
  const el = document.createElement('div');
  el.className = 'message hermes';

  el.innerHTML = `
    <div class="hermes-avatar">
      <div class="avatar-icon">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
        </svg>
      </div>
      <span class="avatar-name">Hermes</span>
    </div>
    <div class="hermes-content">
      <div class="progress-steps" id="progressSteps">
        ${renderStep('behavior', 'Analyzing onboarding flow…', 'wait')}
        ${renderStep('osint', 'Verifying company legitimacy…', 'wait')}
        ${renderStep('domain', 'Checking domain trust…', 'wait')}
        ${renderStep('consensus', 'Running consensus analysis…', 'wait')}
      </div>
    </div>
  `;

  mc.appendChild(el);
  return el;
}

function renderStep(id, label, state) {
  const icon = state === 'wait'
    ? `<div class="step-wait"></div>`
    : state === 'spin'
      ? `<div class="step-spinner"></div>`
      : `<div class="step-check">✓</div>`;

  return `<div class="progress-step ${state === 'spin' ? 'active' : ''} ${state === 'done' ? 'done' : ''}" id="step-${id}">
    ${icon}
    <span>${label}</span>
  </div>`;
}

const STEP_LABELS = {
  behavior: 'Analyzing onboarding flow and communication patterns…',
  osint: 'Verifying company legitimacy and recruiter claims…',
  domain: 'Checking domain trust and typo-squatting indicators…',
  image: 'Analyzing attached image for fraud indicators…',
  consensus: 'Running consensus analysis and forming final verdict…',
};

function updateProgressStep(stepId, message) {
  const el = document.getElementById(`step-${stepId}`);
  if (!el) {
    // Add new step (e.g. image)
    const steps = document.getElementById('progressSteps');
    if (steps) {
      const newStep = document.createElement('div');
      newStep.innerHTML = renderStep(stepId, message || STEP_LABELS[stepId] || message, 'spin');
      steps.insertBefore(newStep.firstElementChild, steps.lastElementChild);
    }
    return;
  }

  el.className = 'progress-step active';
  el.innerHTML = `<div class="step-spinner"></div><span>${message || STEP_LABELS[stepId]}</span>`;
}

function markStepDone(stepId) {
  const el = document.getElementById(`step-${stepId}`);
  if (!el) return;
  const label = el.querySelector('span')?.textContent || STEP_LABELS[stepId] || stepId;
  el.className = 'progress-step done';
  el.innerHTML = `<div class="step-check">✓</div><span>${label.replace('…', '')}</span>`;
}

function renderVerdict(consensus, technical) {
  if (!currentHermesMessageEl) return;

  const content = currentHermesMessageEl.querySelector('.hermes-content');
  if (!content) return;

  const verdict = consensus.verdict || 'UNKNOWN';
  const tier = verdictTier(verdict);
  const confidence = consensus.confidence || 50;

  // Build why_flagged list
  const flagged = (consensus.why_flagged || []).map(s =>
    `<div class="verdict-list-item">${escapeHtml(s)}</div>`
  ).join('');

  const safeSignals = (consensus.safe_signals || []).map(s =>
    `<div class="verdict-list-item">${escapeHtml(s)}</div>`
  ).join('');

  const verdictHtml = `
    <div class="verdict-card verdict-${tier}">
      <div class="verdict-header">
        <div>
          <div class="verdict-badge badge-${tier}">${verdict}</div>
          <div class="verdict-headline" style="margin-top:10px">${escapeHtml(consensus.headline || verdict)}</div>
        </div>
      </div>

      <div class="verdict-body">
        ${flagged ? `
        <div class="verdict-section">
          <div class="verdict-section-title">Why this was flagged</div>
          <div class="verdict-list">${flagged}</div>
        </div>` : ''}

        ${safeSignals ? `
        <div class="verdict-section">
          <div class="verdict-section-title">Reassuring signals</div>
          <div class="verdict-list">${safeSignals}</div>
        </div>` : ''}

        ${consensus.recommendation ? `
        <div class="verdict-section">
          <div class="verdict-section-title">Recommendation</div>
          <div class="verdict-recommendation rec-${tier}">${escapeHtml(consensus.recommendation)}</div>
        </div>` : ''}
      </div>

      <div class="verdict-meta">
        <div class="confidence-bar-wrapper">
          <span class="confidence-label">Confidence</span>
          <div class="confidence-bar">
            <div class="confidence-fill fill-${tier}" style="width:${confidence}%"></div>
          </div>
          <span class="confidence-pct">${confidence}%</span>
        </div>
        <div class="reasoned-by">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          Reasoned by NVIDIA NIM
        </div>
      </div>
    </div>

    <div class="tech-toggle">
      <button class="tech-toggle-btn" onclick="toggleTechPanel(this)" aria-expanded="false">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
        View Technical Analysis
      </button>
      <div class="tech-panel" id="techPanel-${Date.now()}">
        ${buildTechPanel(technical, consensus)}
      </div>
    </div>
  `;

  content.innerHTML = verdictHtml;
}

function buildTechPanel(technical, consensus) {
  const sections = [];

  // Behavior
  if (technical?.behavior) {
    const b = technical.behavior;
    const signals = (b.signals || []).map(s => `<span class="tech-tag">${escapeHtml(s)}</span>`).join('');
    sections.push(`
      <div class="tech-section">
        <div class="tech-section-title">
          Behavior Agent
          <span class="tech-latency">${b.latency_ms ? b.latency_ms + 'ms' : ''}</span>
        </div>
        <div class="tech-content">
          <span class="risk-score-pill badge-${verdictTier(scoreToVerdict(b.risk_score))}">Score: ${b.risk_score}/100</span>
          <div style="margin-top:8px">${signals || '<span style="color:var(--text-muted)">No signals</span>'}</div>
          ${b.reasoning ? `<div style="margin-top:8px;color:var(--text-muted)">${escapeHtml(b.reasoning)}</div>` : ''}
        </div>
      </div>
    `);
  }

  // OSINT
  if (technical?.osint) {
    const o = technical.osint;
    const findings = (o.key_findings || []).map(f => `<span class="tech-tag">${escapeHtml(f)}</span>`).join('');
    sections.push(`
      <div class="tech-section">
        <div class="tech-section-title">
          OSINT Agent
          <span class="tech-latency">${o.latency_ms ? o.latency_ms + 'ms' : ''}</span>
        </div>
        <div class="tech-content">
          <span class="risk-score-pill badge-${verdictTier(scoreToVerdict(o.risk_score))}">Score: ${o.risk_score}/100</span>
          ${o.company_legitimacy ? `<div style="margin-top:8px"><strong>Company:</strong> ${escapeHtml(o.company_legitimacy)}</div>` : ''}
          ${o.onboarding_assessment ? `<div><strong>Onboarding:</strong> ${escapeHtml(o.onboarding_assessment)}</div>` : ''}
          <div style="margin-top:8px">${findings}</div>
        </div>
      </div>
    `);
  }

  // Domain
  if (technical?.domain) {
    const d = technical.domain;
    const domainTags = (d.domains_found || []).map(dom =>
      `<span class="tech-tag" style="border-color:${riskColor(dom.risk_level)}">${escapeHtml(dom.domain)} · ${dom.risk_level}</span>`
    ).join('');
    sections.push(`
      <div class="tech-section">
        <div class="tech-section-title">
          Domain Intelligence
          <span class="tech-latency">deterministic</span>
        </div>
        <div class="tech-content">
          <span class="risk-score-pill badge-${verdictTier(scoreToVerdict(d.risk_score))}">Score: ${d.risk_score}/100</span>
          <div style="margin-top:8px">${domainTags || '<span style="color:var(--text-muted)">No domains extracted</span>'}</div>
          ${d.summary ? `<div style="margin-top:8px;color:var(--text-muted)">${escapeHtml(d.summary)}</div>` : ''}
        </div>
      </div>
    `);
  }

  // Image
  if (technical?.image?.analysis) {
    sections.push(`
      <div class="tech-section">
        <div class="tech-section-title">Image Analysis</div>
        <div class="tech-content">${escapeHtml(technical.image.analysis)}</div>
      </div>
    `);
  }

  // Consensus reasoning
  if (consensus?.reasoning) {
    sections.push(`
      <div class="tech-section">
        <div class="tech-section-title">
          Consensus Reasoning
          <span class="tech-latency">${consensus.latency_ms ? consensus.latency_ms + 'ms' : ''}</span>
        </div>
        <div class="tech-content">${escapeHtml(consensus.reasoning)}</div>
      </div>
    `);
  }

  return sections.join('') || '<div class="tech-section"><div class="tech-content" style="color:var(--text-muted)">No technical data available.</div></div>';
}

function toggleTechPanel(btn) {
  const panel = btn.nextElementSibling;
  const isOpen = panel.classList.contains('visible');
  panel.classList.toggle('visible', !isOpen);
  btn.classList.toggle('open', !isOpen);
  btn.setAttribute('aria-expanded', !isOpen);
  btn.querySelector('span') || (btn.lastChild.textContent = isOpen ? ' View Technical Analysis' : ' Hide Technical Analysis');
}

function renderError(msg) {
  if (!currentHermesMessageEl) return;
  const content = currentHermesMessageEl.querySelector('.hermes-content');
  if (content) {
    content.innerHTML = `<div class="error-message">⚠ ${escapeHtml(msg)}</div>`;
  }
}

// ── Verdict helpers ────────────────────────────────────────
function verdictTier(verdict) {
  if (!verdict) return 'medium';
  const v = verdict.toUpperCase();
  if (v === 'SAFE') return 'safe';
  if (v.includes('LOW')) return 'low';
  if (v.includes('MEDIUM')) return 'medium';
  if (v.includes('HIGH')) return 'high';
  if (v.includes('CRITICAL')) return 'critical';
  return 'medium';
}

function scoreToVerdict(score) {
  if (score < 20) return 'SAFE';
  if (score < 40) return 'LOW RISK';
  if (score < 55) return 'MEDIUM RISK';
  if (score < 75) return 'HIGH RISK';
  return 'CRITICAL';
}

function riskColor(level) {
  const map = { low: 'var(--safe)', medium: 'var(--medium)', high: 'var(--high)', critical: 'var(--critical)' };
  return map[level] || 'var(--border)';
}

// ── Utilities ──────────────────────────────────────────────
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function scrollToBottom() {
  const cv = $('conversationView');
  if (cv) cv.scrollTop = cv.scrollHeight;
}

// ── Sidebar toggle ─────────────────────────────────────────
$('sidebarToggle') && $('sidebarToggle').addEventListener('click', () => {
  const sidebar = document.querySelector('.sidebar');
  if (window.innerWidth <= 768) {
    sidebar.classList.toggle('mobile-open');
  } else {
    sidebar.classList.toggle('collapsed');
  }
});
