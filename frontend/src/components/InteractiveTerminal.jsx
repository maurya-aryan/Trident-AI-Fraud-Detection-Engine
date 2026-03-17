import { useState, useRef, useCallback, useEffect } from 'react';

const API_URL = 'http://localhost:8000';

const lineClass = (type) => ({
  command: 'term-command',
  info: 'term-info',
  module: 'term-module',
  detail: 'term-detail',
  result: 'term-result',
  warning: 'term-warning',
  critical: 'term-critical',
  separator: 'term-separator',
  bar: 'term-bar',
  shap: 'term-shap',
  success: 'term-success',
  blank: 'term-blank',
  status: 'term-info',
  error: 'term-critical',
})[type] || '';

export default function InteractiveTerminal() {
  const [lines, setLines] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [isStopping, setIsStopping] = useState(false);
  const [connected, setConnected] = useState(false);
  const [mailboxStatus, setMailboxStatus] = useState({ connected: false, email: '' });
  const [ownerId] = useState('default');
  const terminalBodyRef = useRef(null);
  const eventSourceRef = useRef(null);

  const appendLine = useCallback((text, type = 'info') => {
    setLines((prev) => [...prev.slice(-400), { text, type }]);
    requestAnimationFrame(() => {
      if (terminalBodyRef.current) {
        terminalBodyRef.current.scrollTop = terminalBodyRef.current.scrollHeight;
      }
    });
  }, []);

  const connectStream = useCallback(() => {
    if (eventSourceRef.current) return;
    const es = new EventSource(`${API_URL}/poller/stream`);
    eventSourceRef.current = es;

    es.onopen = () => setConnected(true);
    es.onerror = () => {
      setConnected(false);
      // Close to prevent infinite auto-retry spam when backend is down
      es.close();
      eventSourceRef.current = null;
    };

    es.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === 'line') {
          appendLine(msg.data, 'detail');
        } else if (msg.type === 'status') {
          if (msg.data === 'started') {
            setIsRunning(true);
            appendLine(`poller started (pid=${msg.pid ?? 'n/a'})`, 'status');
          } else if (msg.data === 'stopped') {
            setIsRunning(false);
            appendLine(`poller stopped (exit=${msg.exit_code ?? 'n/a'})`, 'status');
          } else {
            appendLine(`poller status: ${msg.data}`, 'status');
            setIsRunning(msg.data === 'running');
          }
        }
      } catch (err) {
        console.error('SSE parse error', err);
      }
    };
  }, [appendLine]);

  const disconnectStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setConnected(false);
    }
  }, []);

  const startPoller = useCallback(async () => {
    if (isStarting) return;
    setIsStarting(true);
    setLines([]); // Clear logs on restart
    try {
      connectStream();
      const res = await fetch(`${API_URL}/poller/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ env_overrides: {} }),
      });
      if (!res.ok) {
        const detail = await res.text();
        appendLine(`start failed: ${detail}`, 'error');
        return;
      }
      const data = await res.json();
      setIsRunning(Boolean(data.running));
      appendLine(`starting poller (pid=${data.pid ?? 'n/a'})`, 'status');
    } catch (err) {
      appendLine(`start error: ${err}`, 'error');
    } finally {
      setIsStarting(false);
    }
  }, [appendLine, connectStream, isStarting]);

  const stopPoller = useCallback(async () => {
    if (isStopping) return;
    setIsStopping(true);
    try {
      const res = await fetch(`${API_URL}/poller/stop`, { method: 'POST' });
      if (!res.ok) {
        const detail = await res.text();
        appendLine(`stop failed: ${detail}`, 'error');
        return;
      }
      appendLine('stopping poller...', 'status');
      setIsRunning(false);
    } catch (err) {
      appendLine(`stop error: ${err}`, 'error');
    } finally {
      setIsStopping(false);
    }
  }, [appendLine, isStopping]);

  const checkMailboxStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/auth/status?owner_id=${ownerId}`);
      if (res.ok) {
        const data = await res.json();
        setMailboxStatus(data);
      }
    } catch (err) {
      console.error('Failed to fetch mailbox status', err);
    }
  }, [ownerId]);

  const handleConnectGoogle = useCallback(() => {
    const returnUrl = window.location.origin + window.location.pathname;
    window.location.href = `${API_URL}/auth/google/start?owner_id=${ownerId}&redirect_frontend=${encodeURIComponent(returnUrl)}`;
  }, [ownerId]);

  const handleDisconnect = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/auth/disconnect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ owner_id: ownerId }),
      });
      if (res.ok) {
        appendLine('Mailbox disconnected.', 'info');
        checkMailboxStatus();
      }
    } catch (err) {
      appendLine(`Disconnect error: ${err}`, 'error');
    }
  }, [appendLine, checkMailboxStatus, ownerId]);

  useEffect(() => {
    connectStream();
    checkMailboxStatus();

    // Check URL params for success message
    const params = new URLSearchParams(window.location.search);
    if (params.get('connected') === 'google') {
        appendLine('Google Mailbox connected successfully!', 'success');
        // Clear param without reload
        window.history.replaceState({}, document.title, window.location.pathname);
    }

    return () => disconnectStream();
  }, [connectStream, disconnectStream, checkMailboxStatus, appendLine]);

  return (
    <div className="terminal-container bg-[#0c0e14] border border-accent/20 rounded-xl overflow-hidden shadow-[0_0_60px_rgba(0,214,255,0.05)] w-full w-full flex flex-col">
      <div className="terminal-chrome bg-white/5 border-b border-white/5 px-4 py-3 flex items-center gap-2">
        <div className="terminal-dots flex gap-2">
          <span className="dot dot-red w-3 h-3 rounded-full bg-red-500/80" />
          <span className="dot dot-yellow w-3 h-3 rounded-full bg-yellow-500/80" />
          <span className="dot dot-green w-3 h-3 rounded-full bg-green-500/80" />
        </div>
        <span className="terminal-title ml-4 text-xs font-mono text-white/40">TRIDENT IMAP Poller — Live Logs</span>
        <span className={`terminal-status ml-auto text-xs ${connected ? 'text-green-400' : 'text-red-400'}`}>
          {connected ? 'stream connected' : 'stream disconnected'}
        </span>
      </div>

      <div className="terminal-body p-6 font-mono text-sm leading-relaxed h-[400px] overflow-y-auto flex flex-col" ref={terminalBodyRef}>
        {lines.length === 0 && !isRunning && (
          <div className="terminal-idle">
            <p className="term-info">�️ Live terminal ready</p>
            <p className="term-detail">Start the poller to stream IMAP logs here.</p>
            <p className="term-detail">Env vars are inherited from the backend process.</p>
          </div>
        )}

        {lines.map((line, i) => (
          <div key={i} className={`term-line text-white/80 leading-relaxed min-h-[1.5rem] break-all ${lineClass(line.type)}`}>
            {line.text}
          </div>
        ))}
      </div>

      <div className="terminal-footer bg-black/40 p-4 border-t border-white/5 flex gap-4 items-center flex-wrap">
        {mailboxStatus.connected ? (
          <div className="flex items-center gap-2 mr-auto">
            <span className="text-xs font-mono text-green-400">● Mailbox Connected: {mailboxStatus.email}</span>
            <button
              className="text-xs font-mono text-red-400 underline hover:text-red-300"
              onClick={handleDisconnect}
            >
              [Disconnect]
            </button>
          </div>
        ) : (
          <button
            className="execute-btn px-4 py-2 font-mono text-sm border border-blue-500 text-blue-400 hover:bg-blue-500/10 mr-auto flex items-center gap-2"
            onClick={handleConnectGoogle}
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.1c-.22-.66-.35-1.36-.35-2.1s.13-1.44.35-2.1V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l3.66-2.84z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.66l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            Connect Gmail
          </button>
        )}

        <button
          className={`execute-btn px-4 py-2 font-mono text-sm border transition-colors ${
            isStarting ? 'border-accent/40 text-accent/40 cursor-not-allowed' : 
            isRunning ? 'border-green-500/40 text-green-500 bg-green-500/10 cursor-default' : 
            'border-accent text-accent hover:bg-accent/10'
          }`}
          onClick={startPoller}
          disabled={isStarting || isRunning}
        >
          {isStarting ? '⏳ STARTING…' : isRunning ? '▶ RUNNING' : '[ START POLLER ]'}
        </button>
        <button
          className={`execute-btn danger px-4 py-2 font-mono text-sm border transition-colors ${
            isStopping || !isRunning ? 'border-red-500/20 text-red-500/40 cursor-not-allowed' : 
            'border-red-500 text-red-500 hover:bg-red-500/10'
          }`}
          onClick={stopPoller}
          disabled={isStopping || !isRunning}
        >
          {isStopping ? '⏳ STOPPING…' : '[ STOP ]'}
        </button>
      </div>
    </div>
  );
}
