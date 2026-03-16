import { useState, useRef, useCallback } from 'react';
import { terminalLogs } from '../data/terminalLogs';

const API_URL = 'http://localhost:8000';

export default function InteractiveTerminal() {
  const [lines, setLines] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [showLive, setShowLive] = useState(false);
  const [liveResult, setLiveResult] = useState(null);
  const terminalBodyRef = useRef(null);

  const scrollToBottom = () => {
    if (terminalBodyRef.current) {
      terminalBodyRef.current.scrollTop = terminalBodyRef.current.scrollHeight;
    }
  };

  const typewriterPlay = useCallback(async () => {
    if (isRunning) return;
    setIsRunning(true);
    setLines([]);
    setLiveResult(null);

    for (let i = 0; i < terminalLogs.length; i++) {
      const log = terminalLogs[i];
      await new Promise((r) => setTimeout(r, log.type === 'blank' ? 80 : log.type === 'separator' ? 120 : 55));
      setLines((prev) => [...prev, log]);

      // Auto-scroll
      setTimeout(scrollToBottom, 10);
    }

    // Red flash effect
    document.body.classList.add('threat-flash');
    setTimeout(() => document.body.classList.remove('threat-flash'), 600);

    // Now try live API call
    setShowLive(true);
    try {
      const res = await fetch(`${API_URL}/detect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email_text: "Dear User, We detected unauthorized access. Click here immediately to secure your account. password=Bank@123!",
          sender: "security-alert@amaz0n-verify.com",
          url: "http://fake-bank.xyz/verify",
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setLiveResult(data);
      }
    } catch {
      // Backend may not be running — that's OK for demo
    }

    setIsRunning(false);
  }, [isRunning]);

  const getLineClass = (type) => {
    const map = {
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
    };
    return map[type] || '';
  };

  return (
    <div className="terminal-container">
      <div className="terminal-chrome">
        <div className="terminal-dots">
          <span className="dot dot-red" />
          <span className="dot dot-yellow" />
          <span className="dot dot-green" />
        </div>
        <span className="terminal-title">TRIDENT Detection Engine v1.0.0</span>
      </div>

      <div className="terminal-body" ref={terminalBodyRef}>
        {lines.length === 0 && !isRunning && (
          <div className="terminal-idle">
            <p className="term-info">🔎 TRIDENT v1.0.0 — Ready</p>
            <p className="term-detail">   9 detection modules loaded</p>
            <p className="term-detail">   Awaiting signal for analysis...</p>
          </div>
        )}

        {lines.map((line, i) => (
          <div key={i} className={`term-line ${getLineClass(line.type)}`}>
            {line.text}
          </div>
        ))}

        {showLive && liveResult && (
          <div className="live-result">
            <div className="term-separator">═══════════════ LIVE API RESPONSE ═══════════════</div>
            <div className="term-info">📡 Backend responded with live detection:</div>
            <div className="term-result">   Risk Score: {liveResult.risk_score?.toFixed(1)}</div>
            <div className="term-critical">   Risk Band:  {liveResult.risk_band}</div>
            <div className="term-result">   Action:     {liveResult.recommended_action}</div>
            {liveResult.top_factors?.map((f, i) => (
              <div key={i} className="term-shap">   {i + 1}. {f}</div>
            ))}
          </div>
        )}
      </div>

      <div className="terminal-footer">
        <button
          className={`execute-btn ${isRunning ? 'executing' : ''}`}
          onClick={typewriterPlay}
          disabled={isRunning}
        >
          {isRunning ? '⏳ ANALYZING...' : '[ EXECUTE ]'}
        </button>
      </div>
    </div>
  );
}
