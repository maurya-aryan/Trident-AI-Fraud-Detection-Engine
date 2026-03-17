import { useState, useCallback, useEffect } from 'react';

const API_URL = 'http://localhost:8000';

export default function ConnectMailbox() {
    const [mode, setMode] = useState('oauth');         // 'oauth' | 'basic'
    const [status, setStatus] = useState('idle');       // 'idle' | 'loading' | 'connected' | 'error'
    const [message, setMessage] = useState('');
    const [connectedEmail, setConnectedEmail] = useState('');

    // App-password form state
    const [email, setEmail] = useState('');
    const [host, setHost] = useState('imap.gmail.com');
    const [password, setPassword] = useState('');

    // Check URL params for OAuth callback redirect
    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        if (params.get('connected') === '1') {
            const emailParam = params.get('email') || '';
            setStatus('connected');
            setConnectedEmail(decodeURIComponent(emailParam));
            setMessage(`Connected via Google OAuth${emailParam ? ` as ${decodeURIComponent(emailParam)}` : ''}`);
            // Clean URL
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    }, []);

    const handleOAuth = useCallback(async () => {
        setStatus('loading');
        setMessage('');
        try {
            const res = await fetch(
                `${API_URL}/auth/google/start?owner_id=default&redirect_frontend=${encodeURIComponent(window.location.origin + window.location.pathname)}`
            );
            if (!res.ok) {
                const detail = await res.text();
                throw new Error(detail);
            }
            const data = await res.json();
            // Open Google consent in same tab (will redirect back)
            window.location.href = data.auth_url;
        } catch (err) {
            setStatus('error');
            setMessage(`OAuth start failed: ${err.message || err}`);
        }
    }, []);

    const handleBasicConnect = useCallback(async (e) => {
        e.preventDefault();
        if (!email || !password) {
            setMessage('Email and password are required');
            return;
        }
        setStatus('loading');
        setMessage('');
        try {
            const res = await fetch(`${API_URL}/connect/basic`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ owner_id: 'default', provider: 'basic', email, host, password }),
            });
            if (!res.ok) {
                const detail = await res.text();
                throw new Error(detail);
            }
            setStatus('connected');
            setConnectedEmail(email);
            setMessage(`Credentials stored for ${email}`);
            setPassword('');
        } catch (err) {
            setStatus('error');
            setMessage(`Failed: ${err.message || err}`);
        }
    }, [email, host, password]);

    const handleTestConnection = useCallback(async () => {
        setMessage('Testing connection…');
        try {
            const res = await fetch(`${API_URL}/poller/connect-test`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify('default'),
            });
            const data = await res.json();
            if (data.success) {
                setMessage(`✅ ${data.message} (${data.inbox_count} messages in INBOX)`);
            } else {
                setMessage(`❌ ${data.message}`);
            }
        } catch (err) {
            setMessage(`Test error: ${err.message || err}`);
        }
    }, []);

    const handleDisconnect = useCallback(async () => {
        try {
            const res = await fetch(`${API_URL}/auth/disconnect`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify('default'),
            });
            if (res.ok) {
                setStatus('idle');
                setConnectedEmail('');
                setMessage('Disconnected — credentials deleted');
            }
        } catch (err) {
            setMessage(`Disconnect error: ${err.message || err}`);
        }
    }, []);

    return (
        <div className="connect-mailbox bg-[#0c0e14] border border-accent/20 rounded-xl overflow-hidden shadow-[0_0_60px_rgba(0,214,255,0.05)] w-full mb-6">
            {/* Header */}
            <div className="bg-white/5 border-b border-white/5 px-6 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <span className="text-accent text-lg">📬</span>
                    <span className="font-mono text-sm text-white/70 font-semibold tracking-wide">
                        CONNECT MAILBOX
                    </span>
                </div>
                {status === 'connected' && (
                    <span className="text-xs font-mono text-green-400 flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse inline-block" />
                        {connectedEmail || 'connected'}
                    </span>
                )}
            </div>

            <div className="p-6">
                {/* Connected state */}
                {status === 'connected' ? (
                    <div className="space-y-4">
                        <p className="text-green-400/80 font-mono text-sm">{message}</p>
                        <p className="text-white/40 text-xs font-mono">
                            Your credentials are stored encrypted on the server. You can test the connection or disconnect below.
                        </p>
                        <div className="flex gap-3">
                            <button
                                onClick={handleTestConnection}
                                className="px-4 py-2 font-mono text-sm border border-accent text-accent hover:bg-accent/10 transition-colors"
                            >
                                [ TEST CONNECTION ]
                            </button>
                            <button
                                onClick={handleDisconnect}
                                className="px-4 py-2 font-mono text-sm border border-red-500/60 text-red-400 hover:bg-red-500/10 transition-colors"
                            >
                                [ DISCONNECT ]
                            </button>
                        </div>
                    </div>
                ) : (
                    <>
                        {/* Mode tabs */}
                        <div className="flex gap-1 mb-6">
                            <button
                                onClick={() => setMode('oauth')}
                                className={`px-4 py-2 font-mono text-xs border transition-colors ${mode === 'oauth'
                                        ? 'border-accent text-accent bg-accent/10'
                                        : 'border-white/10 text-white/40 hover:text-white/60'
                                    }`}
                            >
                                GOOGLE OAUTH
                            </button>
                            <button
                                onClick={() => setMode('basic')}
                                className={`px-4 py-2 font-mono text-xs border transition-colors ${mode === 'basic'
                                        ? 'border-accent text-accent bg-accent/10'
                                        : 'border-white/10 text-white/40 hover:text-white/60'
                                    }`}
                            >
                                APP PASSWORD
                            </button>
                        </div>

                        {/* OAuth mode */}
                        {mode === 'oauth' && (
                            <div className="space-y-4">
                                <p className="text-white/40 text-xs font-mono leading-relaxed">
                                    Sign in with Google to grant IMAP access via OAuth2. Your tokens are stored encrypted and can be revoked at any time.
                                </p>
                                <button
                                    onClick={handleOAuth}
                                    disabled={status === 'loading'}
                                    className={`flex items-center gap-3 px-5 py-3 rounded border font-mono text-sm transition-colors ${status === 'loading'
                                            ? 'border-white/10 text-white/30 cursor-wait'
                                            : 'border-white/20 text-white/80 hover:bg-white/5 hover:border-white/30'
                                        }`}
                                >
                                    <svg className="w-5 h-5" viewBox="0 0 24 24">
                                        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" />
                                        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                                        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                                    </svg>
                                    {status === 'loading' ? 'Redirecting…' : 'Connect with Google'}
                                </button>
                            </div>
                        )}

                        {/* App Password mode */}
                        {mode === 'basic' && (
                            <form onSubmit={handleBasicConnect} className="space-y-3">
                                <p className="text-white/40 text-xs font-mono leading-relaxed">
                                    For providers without OAuth or when using an App Password. Credentials are encrypted at rest.
                                </p>
                                <input
                                    type="email"
                                    placeholder="Email address"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full bg-black/40 border border-white/10 text-white/80 font-mono text-sm px-4 py-2.5 rounded focus:border-accent/50 focus:outline-none transition-colors placeholder-white/20"
                                />
                                <input
                                    type="text"
                                    placeholder="IMAP Host (default: imap.gmail.com)"
                                    value={host}
                                    onChange={(e) => setHost(e.target.value)}
                                    className="w-full bg-black/40 border border-white/10 text-white/80 font-mono text-sm px-4 py-2.5 rounded focus:border-accent/50 focus:outline-none transition-colors placeholder-white/20"
                                />
                                <input
                                    type="password"
                                    placeholder="App Password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-black/40 border border-white/10 text-white/80 font-mono text-sm px-4 py-2.5 rounded focus:border-accent/50 focus:outline-none transition-colors placeholder-white/20"
                                />
                                <button
                                    type="submit"
                                    disabled={status === 'loading'}
                                    className={`px-5 py-2.5 font-mono text-sm border transition-colors ${status === 'loading'
                                            ? 'border-accent/30 text-accent/30 cursor-wait'
                                            : 'border-accent text-accent hover:bg-accent/10'
                                        }`}
                                >
                                    {status === 'loading' ? '⏳ SAVING…' : '[ SAVE & CONNECT ]'}
                                </button>
                            </form>
                        )}
                    </>
                )}

                {/* Status message */}
                {message && status !== 'connected' && (
                    <p className={`mt-4 font-mono text-xs ${status === 'error' ? 'text-red-400' : 'text-white/50'
                        }`}>
                        {message}
                    </p>
                )}
            </div>
        </div>
    );
}
