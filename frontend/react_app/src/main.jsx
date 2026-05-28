import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Search, History as HistoryIcon, Bookmark, ShieldAlert, Settings as SettingsIcon, Image as ImageIcon, Send, X, Shield, Activity, Globe, Eye } from 'lucide-react';
import './styles.css';

const STORAGE = {
  history: 'hermes.history.v1',
  saved: 'hermes.savedReports.v1',
};

const steps = [
  ['thinking', 'Thinking'],
  ['pondering', 'Pondering'],
  ['agents', 'Launching agents'],
  ['image', 'Image forensics'],
  ['behavior', 'Behavior'],
  ['osint', 'OSINT'],
  ['domain', 'Domain intelligence'],
  ['web', 'Web reputation'],
  ['consensus', 'Risk synthesis'],
  ['opencode', 'AI Reasoning'],
];

function App() {
  const [view, setView] = useState('new');
  const [status, setStatus] = useState('Ready');
  const [text, setText] = useState('');
  const [imagePath, setImagePath] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [messages, setMessages] = useState([]);
  const [progress, setProgress] = useState({});
  const [technical, setTechnical] = useState({});
  const [verdict, setVerdict] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [history, setHistory] = useState([]);
  const [savedReports, setSavedReports] = useState([]);
  const scrollRef = useRef(null);

  useEffect(() => {
    loadCollections();
    fetch('/health')
      .then((r) => r.json())
      .then((data) => setStatus(data.mongodb ? 'MongoDB armed' : 'Local mode'))
      .catch(() => setStatus('Offline'));
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages, progress, verdict, view]);

  async function loadCollections() {
    const localHistory = readLocal(STORAGE.history);
    const localSaved = readLocal(STORAGE.saved);
    try {
      const [h, s] = await Promise.all([
        fetch('/api/history').then((r) => r.json()),
        fetch('/api/reports').then((r) => r.json()),
      ]);
      setHistory(h.items?.length ? h.items : localHistory);
      setSavedReports(s.items?.length ? s.items : localSaved);
    } catch {
      setHistory(localHistory);
      setSavedReports(localSaved);
    }
  }

  function onImage(file) {
    setImageFile(file);
    setImagePreview(file ? URL.createObjectURL(file) : '');
  }

  async function investigate() {
    if (isRunning || (!text.trim() && !imageFile && !imagePath.trim())) return;
    setView('new');
    setIsRunning(true);
    setStatus('Investigating');
    setMessages([{ role: 'user', text: text || imagePath, image: imagePreview }]);
    setProgress({});
    setTechnical({});
    setVerdict(null);

    const form = new FormData();
    form.append('text', text);
    if (imagePath.trim()) form.append('image_path', imagePath.trim());
    if (imageFile) form.append('image', imageFile);
    setText('');
    setImagePath('');
    setImageFile(null);
    setImagePreview('');

    try {
      const response = await fetch('/investigate', { method: 'POST', body: form });
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split('\n\n');
        buffer = chunks.pop();
        for (const chunk of chunks) parseEvent(chunk);
      }
    } catch (error) {
      setMessages((items) => [...items, { role: 'system', error: `Investigation failed: ${error.message}` }]);
    } finally {
      setIsRunning(false);
      setStatus('Ready');
      loadCollections();
    }
  }

  function parseEvent(raw) {
    let type = 'message';
    let data = '';
    for (const line of raw.split('\n')) {
      if (line.startsWith('event: ')) type = line.slice(7).trim();
      if (line.startsWith('data: ')) data = line.slice(6).trim();
    }
    if (!data) return;
    const payload = JSON.parse(data);
    if (type === 'progress') {
      setProgress((current) => ({ ...current, [payload.step]: { state: 'active', message: payload.message } }));
    }
    if (type === 'agent_result') {
      setTechnical((current) => ({ ...current, [payload.agent]: payload.result }));
      setProgress((current) => ({
        ...current,
        [payload.agent]: { ...(current[payload.agent] || {}), state: 'done' },
      }));
    }
    if (type === 'verdict') {
      setVerdict(payload);
      const record = reportFromVerdict(payload);
      writeLocal(STORAGE.history, [record, ...readLocal(STORAGE.history)].slice(0, 50));
    }
    if (type === 'error') {
      setMessages((items) => [...items, { role: 'system', error: payload.message }]);
    }
  }

  async function saveCurrentReport() {
    if (!verdict) return;
    const record = reportFromVerdict(verdict);
    writeLocal(STORAGE.saved, [record, ...readLocal(STORAGE.saved).filter((item) => item.id !== record.id)]);
    try {
      await fetch('/api/reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(record),
      });
    } catch {
      // Local fallback already saved.
    }
    await loadCollections();
    setView('saved');
  }

  const threatFeed = useMemo(() => buildThreatFeed(history), [history]);

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark"><Shield size={24} /></div>
          <span>
            Detective Hermes
            <small>Agentic fraud lab</small>
          </span>
        </div>
        <Nav view={view} setView={setView} />
        <div className="runtime"><span />{status}</div>
      </aside>

      <main className="main">
        <section ref={scrollRef} className="scroll-region">
          {view === 'new' && (
            <InvestigationView
              messages={messages}
              progress={progress}
              technical={technical}
              verdict={verdict}
              onSave={saveCurrentReport}
            />
          )}
          {view === 'history' && <ReportList title="History" reports={history} empty="No investigations yet." />}
          {view === 'saved' && <ReportList title="Saved Reports" reports={savedReports} empty="No saved reports yet." />}
          {view === 'feed' && <ThreatFeed feed={threatFeed} />}
          {view === 'settings' && <Settings onClear={() => { localStorage.clear(); loadCollections(); }} />}
        </section>

        <section className="composer-wrap">
          {imagePreview && (
            <div className="preview">
              <img src={imagePreview} alt="Attached evidence" />
              <button onClick={() => onImage(null)}><X size={16} /></button>
            </div>
          )}
          <div className="composer">
            <textarea
              value={text}
              onChange={(event) => {
                setText(event.target.value);
                event.target.style.height = 'auto';
                event.target.style.height = Math.min(event.target.scrollHeight, 200) + 'px';
              }}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault();
                  investigate();
                }
              }}
              placeholder="Paste recruiter text, offer details, suspicious URLs, or attach an offer-letter image"
              rows={1}
            />
            <div className="composer-bottom">
              <div className="actions">
                <label title="Attach image">
                  <ImageIcon size={20} />
                  <input type="file" accept="image/*" onChange={(event) => onImage(event.target.files?.[0] || null)} />
                </label>
              </div>
              <button className="send-btn" disabled={isRunning || (!text.trim() && !imageFile && !imagePath.trim())} onClick={investigate}>
                {isRunning ? '...' : <Send size={18} />}
              </button>
            </div>
            <input
              className="path-input"
              value={imagePath}
              onChange={(event) => setImagePath(event.target.value)}
              placeholder="Optional server image path, e.g. /home/aarush/offer-letter.png"
            />
          </div>
        </section>
      </main>
    </div>
  );
}

function Nav({ view, setView }) {
  const items = [
    ['new', 'New Investigation', <Search size={18} />],
    ['history', 'History', <HistoryIcon size={18} />],
    ['saved', 'Saved Reports', <Bookmark size={18} />],
    ['feed', 'Threat Feed', <ShieldAlert size={18} />],
    ['settings', 'Settings', <SettingsIcon size={18} />]
  ];
  return <nav>{items.map(([id, label, icon]) => <button key={id} className={view === id ? 'active' : ''} onClick={() => setView(id)}>{icon} {label}</button>)}</nav>;
}

function InvestigationView({ messages, progress, technical, verdict, onSave }) {
  if (!messages.length) return (
    <div className="welcome">
      <div className="hero-kicker"><ShieldAlert size={14} /> Detective Hermes Agent</div>
      <h1>Offer-letter forensics with live reputation intelligence.</h1>
      <p>Upload an offer image or paste recruiter text. Hermes extracts the company, launches specialist agents, searches Glassdoor, AmbitionBox, Reddit, and public scam reports, then produces an evidence-backed verdict.</p>
      <div className="hero-grid">
        <div><strong><ImageIcon size={18} style={{marginBottom: 4, color: 'var(--accent)'}} /> Vision OCR</strong><span>Pollinations image extraction</span></div>
        <div><strong><Globe size={18} style={{marginBottom: 4, color: 'var(--success)'}} /> Web OSINT</strong><span>Glassdoor, AmbitionBox, Reddit</span></div>
        <div><strong><Activity size={18} style={{marginBottom: 4, color: 'var(--warning)'}} /> Deep Review</strong><span>OpenCode API synthesis</span></div>
      </div>
    </div>
  );
  return (
    <div className="conversation">
      {messages.map((message, index) => (
        <div key={index} className={`message ${message.role}`}>
          {message.text && <div className="bubble">{message.text}</div>}
          {message.image && <img className="evidence-img" src={message.image} alt="Evidence" />}
          {message.error && <div className="error">{message.error}</div>}
        </div>
      ))}
      {!verdict && <Progress progress={progress} />}
      {verdict && <Verdict verdict={verdict} technical={technical} onSave={onSave} />}
    </div>
  );
}

function Progress({ progress }) {
  return (
    <div className="progress-card">
      {steps.map(([id, label]) => {
        const item = progress[id];
        return <div key={id} className={`step ${item?.state || ''}`}><span />{item?.message || label}</div>;
      })}
    </div>
  );
}

function Verdict({ verdict, technical, onSave }) {
  const consensus = verdict.consensus || {};
  const tier = tierFor(consensus.verdict);
  return (
    <div className={`verdict ${tier}`}>
      <div className="verdict-top">
        <strong>{consensus.verdict || 'UNKNOWN'}</strong>
        <span>{Number(consensus.confidence) || 0}% confidence</span>
      </div>
      <h2>{consensus.headline || consensus.verdict}</h2>
      <p>{consensus.recommendation}</p>
      <button onClick={onSave}>Save Report</button>
      <details>
        <summary>Technical analysis</summary>
        <Tech technical={verdict.technical || technical} consensus={consensus} />
      </details>
    </div>
  );
}

function Tech({ technical = {}, consensus = {} }) {
  return (
    <div className="tech">
      <TechBlock title="Pollinations Image Extraction" data={technical.image} />
      <TechBlock title="Behavior Agent" data={technical.behavior} />
      <TechBlock title="Domain Agent" data={technical.domain} />
      <TechBlock title="Web Reputation: Glassdoor, AmbitionBox, Reddit" data={technical.web} />
      <TechBlock title="AI REASONING" data={technical.opencode} />
      <TechBlock title="Consensus" data={consensus} />
    </div>
  );
}

function TechBlock({ title, data }) {
  if (!data) return null;
  return (
    <section className="tech-block">
      <h3>{title}</h3>
      {data.company_name && <p><b>Company:</b> {data.company_name}</p>}
      {data.company && <p><b>Company:</b> {data.company}</p>}
      {data.conclusion && <p><b>Conclusion:</b> {data.conclusion}</p>}
      {data.scam_conclusion && <p><b>Image conclusion:</b> {data.scam_conclusion}</p>}
      {data.summary && <p>{data.summary}</p>}
      {data.extracted_text && <pre>{data.extracted_text}</pre>}
      {data.sources_checked && data.sources_checked.map((source, index) => <p key={index}><b>{source.source}:</b> {source.finding || source.status}</p>)}
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </section>
  );
}

function ReportList({ title, reports, empty }) {
  return (
    <div className="panel">
      <h1>{title}</h1>
      {!reports.length && <p className="muted">{empty}</p>}
      {reports.map((report) => <article key={report.id} className="report"><b>{report.verdict}</b><h3>{report.title}</h3><p>{report.company}</p><small>{report.created_at || report.createdAt}</small></article>)}
    </div>
  );
}

function ThreatFeed({ feed }) {
  return (
    <div className="panel grid">
      <section><h1>Recurring Signals</h1>{feed.signals.map(([s, c]) => <p key={s}>{s} <b>{c}</b></p>)}</section>
      <section><h1>Flagged Domains</h1>{feed.domains.map(([s, c]) => <p key={s}>{s} <b>{c}</b></p>)}</section>
    </div>
  );
}

function Settings({ onClear }) {
  return (
    <div className="panel">
      <h1>Settings</h1>
      <p>MongoDB is enabled when the backend has MONGODB_URI set.</p>
      <p>Project name: Detective Hermes Agent</p>
      <button className="danger" onClick={onClear}>Clear local browser data</button>
    </div>
  );
}

function reportFromVerdict(payload) {
  const technical = payload.technical || {};
  const consensus = payload.consensus || {};
  return {
    id: payload.id || `case-${Date.now()}`,
    created_at: new Date().toISOString(),
    title: consensus.headline || consensus.verdict || 'Investigation',
    company: technical.image?.company_name || technical.web?.company || technical.opencode?.company || 'Unknown company',
    verdict: consensus.verdict || 'UNKNOWN',
    confidence: consensus.confidence || 0,
    recommendation: consensus.recommendation || '',
    summary: consensus.reasoning || '',
    technical,
  };
}

function buildThreatFeed(history) {
  const signals = new Map();
  const domains = new Map();
  history.forEach((report) => {
    const tech = report.technical || {};
    [...(tech.behavior?.signals || []), ...(tech.image?.red_flags || []), ...(tech.web?.scam_signals || [])].forEach((s) => signals.set(s, (signals.get(s) || 0) + 1));
    (tech.domain?.domains_found || []).forEach((d) => domains.set(d.domain, (domains.get(d.domain) || 0) + 1));
  });
  return {
    signals: [...signals.entries()].sort((a, b) => b[1] - a[1]).slice(0, 15),
    domains: [...domains.entries()].sort((a, b) => b[1] - a[1]).slice(0, 15),
  };
}

function readLocal(key) {
  try { return JSON.parse(localStorage.getItem(key)) || []; } catch { return []; }
}

function writeLocal(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

function tierFor(verdict = '') {
  const value = verdict.toUpperCase();
  if (value.includes('CRITICAL')) return 'critical';
  if (value.includes('HIGH')) return 'high';
  if (value.includes('MEDIUM')) return 'medium';
  if (value.includes('LOW')) return 'low';
  return 'safe';
}

createRoot(document.getElementById('root')).render(<App />);
