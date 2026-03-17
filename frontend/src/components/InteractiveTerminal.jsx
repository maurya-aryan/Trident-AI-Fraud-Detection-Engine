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

  const bufferRef = useRef([]);

  const appendLine = useCallback((text, type = 'info') => {
    const now = new Date();
    const ts = now.toTimeString().split(' ')[0];
    bufferRef.current.push({ text, type, timestamp: ts });
  }, []);

  // Buffered Output Typewriter Effect
  useEffect(() => {
    const interval = setInterval(() => {
      if (bufferRef.current.length > 0) {
        const nextLine = bufferRef.current.shift();
        setLines((prev) => [...prev.slice(-400), nextLine]);
        
        // Auto-scroll
        if (terminalBodyRef.current) {
          terminalBodyRef.current.scrollTop = terminalBodyRef.current.scrollHeight;
        }
      }
    }, 180);
    return () => clearInterval(interval);
  }, []);

  // Uptime Counter
  const [uptime, setUptime] = useState(0);
  useEffect(() => {
    const timer = setInterval(() => setUptime((prev) => prev + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatUptime = (sec) => {
    const h = String(Math.floor(sec / 3600)).padStart(2, '0');
    const m = String(Math.floor((sec % 3600) / 60)).padStart(2, '0');
    const s = String(sec % 60).padStart(2, '0');
    return `${h}:${m}:${s}`;
  };

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

  const bootRanRef = useRef(false);

  // Typewriter sequence on mount (poller stopped)
  useEffect(() => {
    if (bootRanRef.current) return;
    bootRanRef.current = true;

    if (!isRunning) {
      const messages = [
        "Initializing TRIDENT engine...",
        "Loading detection modules... 9/9",
        "IMAP interface ready",
        "poller stopped (exit=n/a)"
      ];
      messages.forEach((text, i) => {
        setTimeout(() => appendLine(text, 'detail'), i * 300);
      });
    }
  }, []);

  return (
    <div className="flex flex-col md:flex-row items-stretch justify-between gap-12 md:gap-[72px] max-w-[1200px] mx-auto w-full px-6 pt-[120px] pb-[100px]">
      <style>{`
        @keyframes pulse-glow {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
        @keyframes cursor-blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0; }
        }
        @keyframes static-scanlines {
          0% { background-position: 0 0; }
          100% { background-position: 0 100%; }
        }
        .scanline-overlay::after {
          content: '';
          position: absolute;
          inset: 0;
          pointer-events: none;
          background-image: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(0,0,0,0.12) 2px,
            rgba(0,0,0,0.12) 4px
          );
          z-index: 2;
        }
        .terminal-scroll::-webkit-scrollbar {
          width: 4px;
        }
        .terminal-scroll::-webkit-scrollbar-track {
          background: transparent;
        }
        .terminal-scroll::-webkit-scrollbar-thumb {
          background: rgba(0,245,255,0.2);
          border-radius: 4px;
        }
      `}</style>

      {/* LEFT COLUMN: Mission briefing / dashboard panel */}
      <div className="w-full md:w-[38%] flex flex-col justify-center text-center md:text-left order-2 md:order-1 pt-12">
        <h2 className="text-4xl md:text-[64px] font-black tracking-tighter uppercase mb-[20px] leading-none">
          <span className="block italic text-white">Live</span>
          <span className="block italic text-blue-500">Detection</span>
        </h2>
        <p className="text-blue-200/60 font-mono text-[15px] max-w-sm md:mx-0 mx-auto leading-[1.8] mb-[32px]">
          Interact with the live TRIDENT engine. Execute analysis to see multi-modal signals processed in real-time.
        </p>

        {/* SYSTEM STATUS PANEL */}
        <div className="p-6 rounded-lg border border-cyan-400/12 bg-cyan-400/[0.03] backdrop-blur-sm w-full max-w-sm mx-auto md:mx-0">
          <h4 className="font-mono text-[10px] tracking-[0.15em] text-cyan-400/50 mb-[16px]">SYSTEM STATUS</h4>
          <div className="flex flex-col gap-2">
            <div className="flex justify-between items-center text-[13px] font-mono py-[10px]">
              <span className="text-white/40">IMAP SERVER</span>
              <span className={`flex items-center gap-1.5 ${mailboxStatus.connected ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
                <span className={`w-2 h-2 rounded-full ${mailboxStatus.connected ? 'bg-[#00ff88]' : 'bg-[#ff4444]'} animate-[pulse-glow_2s_infinite]`} />
                {mailboxStatus.connected ? 'CONNECTED' : 'DISCONNECTED'}
              </span>
            </div>
            <div className="flex justify-between items-center text-[13px] font-mono py-[10px]">
              <span className="text-white/40">POLLER</span>
              <span className={`flex items-center gap-1.5 ${isRunning ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
                <span className={`w-2 h-2 rounded-full ${isRunning ? 'bg-[#00ff88]' : 'bg-[#ff4444]'} animate-[pulse-glow_2s_infinite]`} />
                {isRunning ? 'RUNNING' : 'STOPPED'}
              </span>
            </div>
            <div className="flex justify-between items-center text-[13px] font-mono py-[10px]">
              <span className="text-white/40">STREAM</span>
              <span className={`flex items-center gap-1.5 ${connected ? 'text-[#00ff88]' : 'text-[#ff4444]'}`}>
                <span className={`w-2 h-2 rounded-full ${connected ? 'bg-[#00ff88]' : 'bg-[#ff4444]'} animate-[pulse-glow_2s_infinite]`} />
                {connected ? 'ACTIVE' : 'INACTIVE'}
              </span>
            </div>
          </div>
        </div>

        {/* Thin Divider */}
        <div className="w-full max-w-sm h-[1px] bg-cyan-400/10 mt-[28px] mb-[24px] mx-auto md:mx-0" />

        {/* Descriptive bullet items list text */}
        <div className="space-y-2 text-[13px] leading-[2.2] font-mono text-white/35 flex flex-col items-center md:items-start tracking-wider">
          <p>› Connect your Gmail account via OAuth</p>
          <p>› Start the IMAP poller to scan inbox</p>
          <p>› Monitor real-time detection logs on right</p>
        </div>
      </div>

      {/* RIGHT COLUMN: Terminal Window Area list framing panel */}
      <div className="w-full md:w-[62%] flex flex-col items-center order-1 md:order-2">
        <div className="w-full rounded-xl border border-cyan-400/18 bg-[#080d18] shadow-[0_0_0_1px_rgba(0,245,255,0.05),0_20px_60px_rgba(0,0,0,0.6),0_0_80px_rgba(0,245,255,0.04)] overflow-hidden relative">
          
          {/* HEADER BAR */}
          <div className="h-[52px] bg-[#111827] border-b border-cyan-400/12 px-4 flex items-center justify-between z-10">
            <div className="flex items-center">
              <span className="w-[14px] h-[14px] rounded-full bg-[#ff5f57] mr-1.5 shadow-[0_0_6px_rgba(255,95,87,0.6)]" />
              <span className="w-[14px] h-[14px] rounded-full bg-[#febc2e] mr-1.5 shadow-[0_0_6px_rgba(254,188,46,0.5)]" />
              <span className="w-[14px] h-[14px] rounded-full bg-[#28c840] shadow-[0_0_6px_rgba(40,200,64,0.5)]" />
            </div>
            
            <div className="flex items-center gap-2 font-mono text-[13px] font-medium text-white/60 tracking-wider">
              <span>TRIDENT IMAP Poller — Live Logs</span>
              <div className="flex items-center gap-1 text-red-500 select-none ml-2">
                <span className="animate-[pulse-glow_1.5s_infinite] font-black text-red-600">●</span>
                <span className="text-[12px] tracking-wide">REC</span>
              </div>
            </div>

            <span className={`inline-flex items-center gap-1 px-[14px] py-[5px] rounded-full border border border-green-500/25 bg-green-500/10 text-green-400 text-[12px] font-mono shadow-[0_0_10px_rgba(0,255,0,0.04)]`}>
              <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
              stream connected
            </span>
          </div>

          {/* TERMINAL BODY with scanline grid opacity layer overlay */}
          <div className="relative h-[380px] overflow-y-auto terminal-scroll p-[20px] font-mono text-[14px] text-slate-200 border-l-[3px] border-cyan-400/35 scanline-overlay" ref={terminalBodyRef}>
            <div className="absolute top-0 left-0 w-[200px] h-[200px] bg-[radial-gradient(circle_at_10%_10%,_rgba(0,245,255,0.05),_transparent_70%)] pointer-events-none z-0" />

            <div className="relative z-10 flex flex-col gap-[4px] leading-[1.7]">
              {lines.map((line, i) => {
                const textLower = line.text.toLowerCase();
                const isError = textLower.includes("stopped") || textLower.includes("failed") || textLower.includes("error") || line.type === 'error';
                const isSuccess = textLower.includes("connected") || textLower.includes("started") || textLower.includes("ok") || line.type === 'success';

                let textColor = "text-slate-200";
                if (isError) textColor = "text-[#ff6b6b]";
                if (isSuccess) textColor = "text-[#00ff88]";

                return (
                  <div key={i} className="flex items-baseline break-all tracking-wide min-h-[1.1rem]">
                    <span className="text-cyan-400/40 select-none mr-2 font-light">[{line.timestamp}]</span>
                    <span className="text-cyan-400/80 mr-1.5 select-none font-bold">&gt;</span>
                    <span className={`${textColor} font-light`}>
                      {line.text}
                    </span>
                  </div>
                );
              })}
              
              {/* Blinking Cursor */}
              <div className="inline-block w-[6px] h-[16px] bg-cyan-400/80 animate-[cursor-blink_1s_infinite] ml-1 self-center" style={{ verticalAlign: 'middle' }} />
            </div>
          </div>

          {/* Bottom status stats strip */}
          <div className="h-[36px] bg-cyan-400/[0.03] border-t border-cyan-400/10 flex items-center justify-between px-[20px] font-mono text-[11px] text-cyan-400/40 tracking-wider">
            <span>TRIDENT v2.1.0 — IMAP MODULE</span>
            <span>UPTIME: {formatUptime(uptime)}</span>
            <span>LINES: {lines.length}</span>
          </div>
        </div>

        {/* Action Buttons Row underlying wrapper layout absolute anchors frames */}
        <div className="w-full flex flex-col gap-3 mt-[20px]">
          
          {mailboxStatus.connected ? (
            <div className="flex items-center justify-between px-4 h-[54px] rounded-[10px] border border-green-500/25 bg-green-950/20 font-mono text-[14px] text-green-400">
              <span>● Connected: {mailboxStatus.email}</span>
              <button className="text-red-400 underline hover:text-red-300" onClick={handleDisconnect}>[Disconnect]</button>
            </div>
          ) : (
            <button 
              className="w-full h-[54px] rounded-[10px] border border-white/15 bg-white/5 backdrop-blur-sm flex items-center px-6 gap-3 font-mono text-[14px] text-white/80 transition-all duration-300 hover:border-blue-500/50 hover:bg-blue-500/10 hover:shadow-[0_0_20px_rgba(66,133,244,0.1)] group"
              onClick={handleConnectGoogle}
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.1c-.22-.66-.35-1.36-.35-2.1s.13-1.44.35-2.1V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l3.66-2.84z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.66l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              <span>CONNECT GMAIL</span>
              <span className="ml-auto text-white/20 select-none">OAuth 2.0</span>
            </button>
          )}

          <div className="flex gap-[14px]">
            <button 
              className={`flex-[1] h-[54px] rounded-[10px] border border-cyan-400/30 bg-cyan-400/10 font-mono text-[14px] text-cyan-300 tracking-wider flex items-center justify-center gap-1.5 transition-all duration-300 hover:bg-cyan-400/20 hover:border-cyan-400/60 hover:shadow-[0_0_24px_rgba(0,245,255,0.15)] ${
                isStarting || isRunning ? 'opacity-40 cursor-not-allowed bg-cyan-950/20 border-cyan-400/10 inline-flex' : ''
              }`}
              onClick={startPoller}
              disabled={isStarting || isRunning}
            >
              {isStarting ? '⏳ STARTING…' : isRunning ? '▶ RUNNING' : '▶ START POLLER'}
            </button>

            <button 
              className={`flex-[0.4] h-[54px] rounded-[10px] border border-red-500/20 bg-transparent font-mono text-[14px] text-red-500/40 tracking-wider flex items-center justify-center gap-1.5 transition-all duration-300 ${
                isRunning ? 'border-red-500/60 text-red-500 bg-red-500/10 hover:bg-red-500/20 hover:shadow-[0_0_24px_rgba(255,0,0,0.15)]' : 'cursor-not-allowed'
              }`}
              onClick={stopPoller}
              disabled={isStopping || !isRunning}
            >
              {isStopping ? '⏳ STOPPING…' : '■ STOP'}
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}
