/**
 * AuthPanel — Glassmorphism Sign In / Sign Up panel
 *
 * Self-contained. Drop anywhere over a dark background.
 * Fonts (Cinzel + Rajdhani) are injected via a <style> tag — no extra <link> needed.
 *
 * Props: none  — all state is internal.
 * Emitted events: none yet (wire onSignIn / onSignUp props when backend is ready).
 */
import { useState, useEffect, useRef } from 'react';

// ─── SVG Brand Icons ────────────────────────────────────────────────────────────

function GoogleIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M43.611 20.083H42V20H24v8h11.303C33.654 32.657 29.332 36 24 36c-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z" fill="#FFC107"/>
      <path d="M6.306 14.691l6.571 4.819C14.655 15.108 19.01 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 16.318 4 9.656 8.337 6.306 14.691z" fill="#FF3D00"/>
      <path d="M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238C29.211 35.091 26.715 36 24 36c-5.312 0-9.822-3.506-11.387-8.318l-6.508 5.017C9.37 39.566 16.202 44 24 44z" fill="#4CAF50"/>
      <path d="M43.611 20.083H42V20H24v8h11.303a12.04 12.04 0 01-4.087 5.571l.003-.002 6.19 5.238C36.971 39.801 44 34.5 44 24c0-1.341-.138-2.65-.389-3.917z" fill="#1976D2"/>
    </svg>
  );
}

function TridentIcon() {
  return (
    <svg width="52" height="52" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M24 4 L24 44 M14 4 L14 16 M34 4 L34 16 M10 4 L18 12 M30 4 L38 12 M18 12 Q24 20 30 12 M14 16 Q24 24 34 16"
        stroke="rgba(190,225,255,0.75)"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <path d="M10 4 C 10 4 10 8 14 8 C 18 8 18 4 18 4" stroke="rgba(190,225,255,0.75)" strokeWidth="2" strokeLinecap="round" fill="none"/>
      <path d="M30 4 C 30 4 30 8 34 8 C 38 8 38 4 38 4" stroke="rgba(190,225,255,0.75)" strokeWidth="2" strokeLinecap="round" fill="none"/>
    </svg>
  );
}

// ─── CSS: fonts + keyframe animations (injected once into <head>) ───────────────

const KEYFRAME_CSS = `
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Rajdhani:wght@400;500;600;700&display=swap');

  @keyframes panelIn {
    from { opacity: 0; transform: translateY(14px) scale(0.98); }
    to   { opacity: 1; transform: translateY(0)    scale(1);    }
  }
  @keyframes contentIn {
    from { opacity: 0; transform: translateY(6px); }
    to   { opacity: 1; transform: translateY(0);   }
  }
  @keyframes contentOut {
    from { opacity: 1; transform: translateY(0); }
    to   { opacity: 0; transform: translateY(6px); }
  }
`;

// ─── Sub-components ─────────────────────────────────────────────────────────────

/** Labeled glass input with focus-state transitions. */
function Field({ label, type = 'text', value, onChange, placeholder }) {
  const [focused, setFocused] = useState(false);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <label style={{
        fontFamily: "'Rajdhani', sans-serif",
        fontSize: '12px',
        fontWeight: 600,
        letterSpacing: '0.14em',
        textTransform: 'uppercase',
        color: focused ? 'rgba(190,225,255,0.75)' : 'rgba(180,210,255,0.45)',
        transition: 'color 0.2s',
      }}>
        {label}
      </label>
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        style={{
          fontFamily: "'Rajdhani', sans-serif",
          fontSize: '17px',
          fontWeight: 500,
          color: 'rgba(225,242,255,0.92)',
          background: focused ? 'rgba(255,255,255,0.07)' : 'rgba(255,255,255,0.03)',
          border: `1px solid ${focused ? 'rgba(200,225,255,0.28)' : 'rgba(255,255,255,0.09)'}`,
          borderRadius: '10px',
          padding: '15px 18px',
          outline: 'none',
          transition: 'all 0.2s',
          width: '100%',
          boxSizing: 'border-box',
        }}
        onMouseEnter={e => { if (!focused) e.target.style.background = 'rgba(255,255,255,0.05)'; }}
        onMouseLeave={e => { if (!focused) e.target.style.background = 'rgba(255,255,255,0.03)'; }}
      />
    </div>
  );
}

/** Icon-only OAuth provider button. */
function OAuthBtn({ children, label }) {
  const [hovered, setHovered] = useState(false);
  return (
    <button
      aria-label={label}
      title={label}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: hovered ? 'rgba(255,255,255,0.09)' : 'rgba(255,255,255,0.04)',
        border: '1px solid rgba(255,255,255,0.09)',
        borderRadius: '10px',
        padding: '18px 0',
        cursor: 'pointer',
        transition: 'all 0.2s',
        outline: 'none',
      }}
    >
      {children}
    </button>
  );
}

/** Full-width primary action button. */
function CTAButton({ label }) {
  const [hovered, setHovered] = useState(false);
  return (
    <button
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        width: '100%',
        fontFamily: "'Rajdhani', sans-serif",
        fontSize: '16px',
        fontWeight: 700,
        letterSpacing: '0.22em',
        textTransform: 'uppercase',
        color: 'rgba(225,242,255,0.88)',
        background: hovered ? 'rgba(255,255,255,0.11)' : 'rgba(255,255,255,0.07)',
        border: `1px solid ${hovered ? 'rgba(255,255,255,0.22)' : 'rgba(255,255,255,0.14)'}`,
        borderRadius: '12px',
        padding: '18px',
        cursor: 'pointer',
        transition: 'all 0.2s',
        boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.08), 0 4px 16px rgba(0,0,0,0.18)',
        outline: 'none',
      }}
    >
      {label}
    </button>
  );
}

// ─── Main export ────────────────────────────────────────────────────────────────

export default function AuthPanel() {
  // ── Tab state ──────────────────────────────────────────────────────────────
  const [tab, setTab]                   = useState('signin'); // 'signin' | 'signup'
  const [contentVisible, setContentVisible] = useState(true);
  const [displayedTab, setDisplayedTab] = useState('signin');
  const pendingTabRef                   = useRef(null);

  // ── Sign-in fields ─────────────────────────────────────────────────────────
  const [siEmail, setSiEmail]       = useState('');
  const [siPassword, setSiPassword] = useState('');

  // ── Sign-up fields ─────────────────────────────────────────────────────────
  const [suName, setSuName]         = useState('');
  const [suEmail, setSuEmail]       = useState('');
  const [suPassword, setSuPassword] = useState('');
  const [suConfirm, setSuConfirm]   = useState('');

  // ── Tab switch: fade out → swap → fade in ──────────────────────────────────
  function handleTabSwitch(next) {
    if (next === tab) return;
    pendingTabRef.current = next;
    setContentVisible(false);
    setTab(next);
  }

  useEffect(() => {
    if (!contentVisible) {
      const t = setTimeout(() => {
        setDisplayedTab(pendingTabRef.current ?? tab);
        setContentVisible(true);
      }, 160);
      return () => clearTimeout(t);
    }
  }, [contentVisible, tab]);

  const isSignIn = displayedTab === 'signin';

  // ── Render ─────────────────────────────────────────────────────────────────
  return (
    <>
      <style>{KEYFRAME_CSS}</style>

      {/* ── Glass panel ───────────────────────────────────────────────────── */}
      <div style={{
        width: '100%',
        maxWidth: '860px',
        minHeight: '92vh',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: '24px',
        background: 'rgba(255,255,255,0.05)',
        backdropFilter: 'blur(36px) saturate(1.8)',
        WebkitBackdropFilter: 'blur(36px) saturate(1.8)',
        border: '1px solid rgba(255,255,255,0.1)',
        boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.08), 0 24px 64px rgba(0,0,0,0.4), 0 4px 16px rgba(0,0,0,0.2)',
        animation: 'panelIn 550ms cubic-bezier(0.16,1,0.3,1) both',
        overflow: 'hidden',
      }}>

        {/* ── Tab row ───────────────────────────────────────────────────────── */}
        <div style={{
          display: 'flex',
          background: 'rgba(0,0,0,0.12)',
          borderBottom: '1px solid rgba(255,255,255,0.07)',
        }}>
          {['signin', 'signup'].map(t => {
            const active = tab === t;
            return (
              <button
                key={t}
                onClick={() => handleTabSwitch(t)}
                style={{
                  flex: 1,
                  fontFamily: "'Rajdhani', sans-serif",
                  fontSize: '15px',
                  fontWeight: 600,
                  letterSpacing: '0.18em',
                  textTransform: 'uppercase',
                  color: 'rgba(225,242,255,0.92)',
                  opacity: active ? 1 : 0.32,
                  background: 'transparent',
                  border: 'none',
                  borderBottom: active ? '1.5px solid rgba(190,225,255,0.65)' : '1.5px solid transparent',
                  padding: '20px 0',
                  cursor: 'pointer',
                  transition: 'opacity 0.2s, border-color 0.2s',
                  outline: 'none',
                }}
              >
                {t === 'signin' ? 'Sign In' : 'Sign Up'}
              </button>
            );
          })}
        </div>

        {/* ── Body ──────────────────────────────────────────────────────────── */}
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          padding: '32px 36px 40px',
        }}>
          {/* Content capped at readable width, centered inside the wide panel */}
          <div style={{ width: '100%', maxWidth: '600px', margin: '0 auto' }}>

            {/* Logo */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '44px', gap: '12px' }}>
              <TridentIcon />
              <span style={{ fontFamily: "'Cinzel', serif", fontSize: '28px', fontWeight: 700, letterSpacing: '0.12em', color: 'rgba(225,242,255,0.95)' }}>
                TRIDENT
              </span>
              <span style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: '12px', fontWeight: 500, letterSpacing: '0.32em', textTransform: 'uppercase', color: 'rgba(150,185,220,0.45)' }}>
                AI Fraud Detection Engine
              </span>
            </div>

            {/* Animated content block (fades on tab switch) */}
            <div style={{ animation: contentVisible ? 'contentIn 280ms cubic-bezier(0.16,1,0.3,1) both' : 'contentOut 160ms ease both' }}>

              {/* Heading */}
              <div style={{ marginBottom: '32px' }}>
                <h2 style={{ fontFamily: "'Cinzel', serif", fontSize: '34px', fontWeight: 700, color: 'rgba(225,242,255,0.95)', margin: '0 0 10px' }}>
                  {isSignIn ? 'Welcome Back' : 'Create Account'}
                </h2>
                <p style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: '15px', fontWeight: 500, letterSpacing: '0.04em', color: 'rgba(150,185,220,0.45)', margin: 0 }}>
                  {isSignIn ? 'Access your threat intelligence dashboard' : 'Join the fraud detection network'}
                </p>
              </div>

              {/* Fields */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', marginBottom: '30px' }}>
                {isSignIn ? (
                  <>
                    <Field label="Email Address" type="email"    value={siEmail}    onChange={e => setSiEmail(e.target.value)}    placeholder="analyst@trident.io" />
                    <div>
                      <Field label="Password"      type="password" value={siPassword} onChange={e => setSiPassword(e.target.value)} placeholder="••••••••••" />
                      <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '7px' }}>
                        <button style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: '13px', fontWeight: 500, letterSpacing: '0.06em', color: 'rgba(150,185,220,0.38)', background: 'transparent', border: 'none', cursor: 'pointer', padding: 0, outline: 'none' }}>
                          Forgot password?
                        </button>
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    <Field label="Full Name"        type="text"     value={suName}     onChange={e => setSuName(e.target.value)}     placeholder="Agent Name" />
                    <Field label="Email Address"    type="email"    value={suEmail}    onChange={e => setSuEmail(e.target.value)}    placeholder="analyst@trident.io" />
                    <Field label="Create Password"  type="password" value={suPassword} onChange={e => setSuPassword(e.target.value)} placeholder="••••••••••" />
                    <Field label="Confirm Password" type="password" value={suConfirm}  onChange={e => setSuConfirm(e.target.value)}  placeholder="••••••••••" />
                  </>
                )}
              </div>

              {/* CTA */}
              <div style={{ marginBottom: '32px' }}>
                <CTAButton label={isSignIn ? 'Sign In' : 'Sign Up'} />
              </div>

              {/* Divider */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
                <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.07)' }} />
                <span style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: '12px', fontWeight: 500, letterSpacing: '0.16em', textTransform: 'uppercase', color: 'rgba(150,185,220,0.3)', whiteSpace: 'nowrap' }}>
                  Connect with
                </span>
                <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.07)' }} />
              </div>

              {/* Google OAuth */}
              <div style={{ display: 'flex', gap: '14px', marginBottom: '36px' }}>
                <OAuthBtn label="Continue with Google"><GoogleIcon /></OAuthBtn>
              </div>

              {/* Switch tab */}
              <p style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: '14px', fontWeight: 500, letterSpacing: '0.04em', color: 'rgba(150,185,220,0.38)', textAlign: 'center', margin: 0 }}>
                {isSignIn ? "Don't have an account? " : 'Already have an account? '}
                <button
                  onClick={() => handleTabSwitch(isSignIn ? 'signup' : 'signin')}
                  style={{ fontFamily: "'Rajdhani', sans-serif", fontSize: '14px', fontWeight: 600, color: 'rgba(180,220,255,0.7)', background: 'transparent', border: 'none', borderBottom: '1px solid rgba(180,220,255,0.4)', padding: '0 0 1px', cursor: 'pointer', outline: 'none', letterSpacing: '0.04em' }}
                >
                  {isSignIn ? 'Sign up' : 'Sign in'}
                </button>
              </p>

            </div>{/* end animated block */}
          </div>{/* end content wrapper */}
        </div>{/* end body */}
      </div>{/* end glass panel */}
    </>
  );
}
