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

  useEffect(() => {
    connectStream();
    return () => disconnectStream();
  }, [connectStream, disconnectStream]);

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

      <div className="terminal-footer bg-black/40 p-4 border-t border-white/5 flex gap-4">
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
