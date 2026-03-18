import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { TRIDENT_API_BASE } from "../config";

const BAND_COLOR = { CRITICAL: "#EF4444", HIGH: "#F97316", MEDIUM: "#EAB308", LOW: "#10B981" };
const BAND_BG    = { CRITICAL: "rgba(239,68,68,0.10)", HIGH: "rgba(249,115,22,0.10)", MEDIUM: "rgba(234,179,8,0.08)", LOW: "rgba(16,185,129,0.08)" };
const BAND_ICON  = { CRITICAL: "🚨", HIGH: "⚠️", MEDIUM: "🔶", LOW: "✅" };
const ACTION_COLOR = { BLOCK: "#EF4444", ESCALATE: "#F97316", WARN: "#EAB308", VERIFY: "#10B981" };

const MODULE_LABELS = {
  phishing: "Phishing", url_detection: "URL Detection", ai_text: "AI Text",
  credential_exposure: "Credentials", prompt_injection: "Prompt Injection",
  malware: "Malware", campaign_graph: "Campaign Graph", fusion_model: "Fusion Model",
  shap_explainer: "SHAP Explainer"
};

// ── SVG Risk Arc ────────────────────────────────────────────────────────────
function RiskArc({ score, band }) {
  const color = BAND_COLOR[band] || "#888";
  const radius = 60;
  const stroke = 8;
  const cx = 80, cy = 80;
  const startAngle = 140;
  const sweepAngle = 260; // Progress arc sweep
  const toRad = (deg) => (deg * Math.PI) / 180;

  const arcPath = (start, sweep) => {
    const s = toRad(start);
    const e = toRad(start + sweep);
    const x1 = cx + radius * Math.cos(s);
    const y1 = cy + radius * Math.sin(s);
    const x2 = cx + radius * Math.cos(e);
    const y2 = cy + radius * Math.sin(e);
    const large = sweep > 180 ? 1 : 0;
    return `M ${x1} ${y1} A ${radius} ${radius} 0 ${large} 1 ${x2} ${y2}`;
  };

  return (
    <div style={{ position: "relative", width: 160, height: 130, margin: "0 auto" }}>
      <svg width={160} height={160} viewBox="0 0 160 160">
        {/* Background track */}
        <path d={arcPath(140, 260)} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth={stroke} strokeLinecap="round" />
        {/* Progress Arc */}
        <path d={arcPath(140, (260 * score) / 100)} fill="none" stroke={color}
          strokeWidth={stroke} strokeLinecap="round"
          style={{ filter: `drop-shadow(0 0 8px ${color}66)`, transition: "stroke-dasharray 1s ease" }} />
      </svg>
      <div style={{
        position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)",
        textAlign: "center", marginTop: 5
      }}>
        <div style={{ fontSize: "2.2rem", fontWeight: 800, color: "#fff", lineHeight: 1 }}>{score.toFixed(0)}</div>
        <div style={{ fontSize: "0.7rem", color: "rgba(223,240,251,0.4)", letterSpacing: 1, marginTop: 2 }}>/ 100</div>
      </div>
    </div>
  );
}

// ── SHAP Contributions (CSS Bars) ─────────────────────────────────────────────
function ShapContributions({ factors, color }) {
  if (!factors || factors.length === 0) {
    return (
      <div style={{ color: "rgba(255,255,255,0.2)", fontSize: "0.7rem", textAlign: "center", padding: "10px 0" }}>
        No factor analysis data available
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {factors.sort((a, b) => b.value - a.value).map((f, i) => {
        const val = Math.min(100, Math.max(0, f.value));
        const magnitudeColor = val > 50 ? "#EF4444" : val > 20 ? "#EAB308" : "#2DD4BF";

        return (
          <div key={i}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
              <span style={{ fontSize: "0.72rem", color: "rgba(255,255,255,0.6)", fontWeight: 500 }}>{f.name}</span>
              <span style={{ fontSize: "0.72rem", color: magnitudeColor, fontWeight: 700 }}>{val.toFixed(1)}%</span>
            </div>
            <div style={{ height: 6, background: "rgba(255,255,255,0.03)", borderRadius: 3, overflow: "hidden" }}>
              <div style={{
                height: "100%", width: `${val}%`, background: magnitudeColor,
                borderRadius: 2, transition: "width 0.8s ease-out",
                boxShadow: `0 0 10px ${magnitudeColor}33`
              }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ── Radar Chart (Cleaned up) ───────────────────────────────────────────────────
function RadarChart({ scores }) {
  const entries = Object.entries(scores || {}).slice(0, 8);
  if (entries.length < 3) return null;

  const cx = 110, cy = 110, r = 70;
  const n = entries.length;
  const points = entries.map(([, val], i) => {
    const angle = (2 * Math.PI * i) / n - Math.PI / 2;
    const dist = (r * Math.min(100, Math.max(0, val))) / 100;
    return { x: cx + dist * Math.cos(angle), y: cy + dist * Math.sin(angle) };
  });
  const outline = entries.map((_, i) => {
    const angle = (2 * Math.PI * i) / n - Math.PI / 2;
    return { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
  });

  const poly = (pts) => pts.map(p => `${p.x},${p.y}`).join(" ");

  return (
    <svg width={220} height={220} style={{ display: "block", margin: "0 auto" }}>
      {[0.25, 0.5, 0.75, 1].map((f) => (
        <polygon key={f}
          points={poly(outline.map((_, i) => {
            const a = (2 * Math.PI * i) / n - Math.PI / 2;
            return { x: cx + r * f * Math.cos(a), y: cy + r * f * Math.sin(a) };
          }))}
          fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth={1}
        />
      ))}
      <polygon points={poly(points)} fill="rgba(0,212,255,0.15)" stroke="#00d4ff" strokeWidth={2}
        style={{ filter: "drop-shadow(0 0 10px rgba(0,212,255,0.2))" }} />
      {outline.map((p, i) => {
        const [mod] = entries[i];
        const label = (MODULE_LABELS[mod] || mod).slice(0, 10).toUpperCase();
        const lx = cx + (r + 18) * Math.cos((2 * Math.PI * i) / n - Math.PI / 2);
        const ly = cy + (r + 18) * Math.sin((2 * Math.PI * i) / n - Math.PI / 2);
        return (
          <text key={i} x={lx} y={ly} textAnchor="middle" dominantBaseline="middle"
            fill="rgba(223,240,251,0.4)" fontSize={7} fontWeight={700} fontFamily="'Inter', sans-serif">
            {label}
          </text>
        );
      })}
    </svg>
  );
}

export default function AlertDetailPage() {
  const { bucket, id } = useParams();
  const navigate = useNavigate();
  const [alert, setAlert] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const isFraud = bucket === "fraud";
  const accentColor = isFraud ? "#EF4444" : "#10B981";

  useEffect(() => {
    fetch(`${TRIDENT_API_BASE}/alerts?limit=50`)
      .then(r => {
        if (!r.ok) throw new Error(`API error: ${r.status}`);
        return r.json();
      })
      .then(data => {
        const all = data.alerts || [];
        const idx = parseInt(id, 10);
        if (isNaN(idx) || idx < 0 || idx >= all.length) throw new Error("Alert not found");
        setAlert(all[idx]);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  const rec        = alert?.alert    || {};
  const tr         = rec.trident_result || {};
  const band       = (rec.risk_band  || tr.risk_band  || "LOW").toUpperCase();
  const score      = rec.risk_score  ?? tr.risk_score  ?? 0;
  const action     = rec.recommended_action || tr.recommended_action || "VERIFY";
  const sender     = rec.sender      || "(unknown)";
  const subject    = rec.subject     || "(no subject)";
  const body       = rec.email_text  || rec.snippet   || "";
  const ts         = alert?.received_at || "";
  const modules    = tr.module_scores || rec.module_scores || {};
  const topFactors  = tr.feature_importance 
    ? Object.entries(tr.feature_importance).map(([name, value]) => ({ name, value }))
    : (tr.top_factors || rec.top_factors || []).map(f => ({ name: f, value: 0 }));
  const bandColor  = BAND_COLOR[band] || "#888";
  const actionColor = ACTION_COLOR[action] || "#888";

  const cleanBody = body.replace(/https?:\/\/\S{60,}/g, '[link]');

  return (
    <div style={{
      minHeight: "100vh",
      background: "#03070b",
      color: "#dff0fb",
      fontFamily: "'Inter', sans-serif",
      paddingBottom: 80
    }}>
      {/* ── Sub-Header ───────────────────────────────────────────────────── */}
      <div style={{
        position: "sticky", top: 0, zIndex: 100,
        background: "rgba(3,7,11,0.92)",
        backdropFilter: "blur(20px)",
        borderBottom: "1px solid rgba(255,255,255,0.06)",
        padding: "0 32px", height: 56,
        display: "flex", alignItems: "center", justifyContent: "space-between"
      }}>
        <button
          onClick={() => navigate(`/alerts/${bucket}`)}
          style={{
            background: "none", border: "1px solid rgba(255,255,255,0.15)",
            color: "rgba(255,255,255,0.6)", fontFamily: "'Courier New', monospace",
            fontSize: "0.7rem", letterSpacing: "1.2px", padding: "5px 14px",
            borderRadius: 5, cursor: "pointer", transition: "all 0.2s"
          }}
          onMouseEnter={e => {
            e.currentTarget.style.background = "rgba(255,255,255,0.05)";
            e.currentTarget.style.color = "#fff";
          }}
          onMouseLeave={e => {
            e.currentTarget.style.background = "none";
            e.currentTarget.style.color = "rgba(255,255,255,0.6)";
          }}
        >
          ← BACK TO FRAUD ALERTS
        </button>

        <span style={{ fontSize: "0.65rem", letterSpacing: "2.5px", color: "rgba(255,255,255,0.3)", fontWeight: 700 }}>
          TRIDENT · <span style={{ color: "#dff0fb" }}>ALERT ANALYSIS</span>
        </span>
      </div>

      {loading && (
        <div style={{ textAlign: "center", padding: "120px 0", color: "rgba(255,255,255,0.3)", letterSpacing: "2px", fontSize: "0.8rem" }}>
          LOADING ANALYSIS DATA...
        </div>
      )}

      {error && (
        <div style={{ maxWidth: 1200, margin: "40px auto", padding: "0 32px" }}>
          <div style={{ background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.25)", borderRadius: 10, padding: "20px 24px", color: "#EF4444", fontSize: "0.8rem" }}>
            ⚠ {error}
          </div>
        </div>
      )}

      {!loading && !error && alert && (
        <div style={{ maxWidth: 1300, margin: "0 auto", padding: "32px" }}>

          {/* ── Top Hero Row ──────────────────────────────────────────────── */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 32, gap: 20 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <h1 style={{ fontSize: "1.4rem", fontWeight: 800, color: "#fff", margin: 0, letterSpacing: "-0.02em" }}>{subject}</h1>
              <span style={{
                background: `${bandColor}1A`, color: bandColor, padding: "3px 10px", borderRadius: 4,
                fontSize: "0.6rem", fontWeight: 800, letterSpacing: "1px", border: `1px solid ${bandColor}44`
              }}>{band}</span>
            </div>
            <button style={{
              background: "#F97316", color: "#000", border: "none", padding: "8px 20px",
              borderRadius: 6, fontSize: "0.75rem", fontWeight: 800, letterSpacing: "1px",
              cursor: "pointer", boxShadow: "0 4px 14px rgba(249,115,22,0.3)"
            }}>ESCALATE ALERT</button>
          </div>

          <div style={{ display: "flex", width: "100%", overflow: "hidden", gap: 32, height: "calc(100vh - 140px)" }}>

            {/* LEFT — Email Viewer (60%) */}
            <div style={{ width: "60%", minWidth: 0, overflowY: "auto", display: "flex", flexDirection: "column", gap: 16, height: "100%", paddingRight: 8 }}>
              <div style={{ fontSize: "0.62rem", letterSpacing: "3px", color: "rgba(255,255,255,0.4)", fontWeight: 700 }}>
                EMAIL MESSAGE
              </div>

              <div style={{
                background: "#fdfdfd", color: "#1a1c21", borderRadius: 16, overflow: "hidden",
                boxShadow: "0 20px 40px rgba(0,0,0,0.4)", display: "flex", flexDirection: "column"
              }}>
                {/* Email Header */}
                <div style={{ padding: "32px 32px 24px", borderBottom: "1px solid #f0f0f0" }}>
                   <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
                      <h2 style={{ fontSize: "1.25rem", fontWeight: 700, margin: 0, flex: 1 }}>{subject}</h2>
                      <div style={{ display: "flex", gap: 8 }}>
                         <span style={{ background: "#fef2f2", color: "#dc2626", border: "1px solid #fee2e2", padding: "2px 8px", borderRadius: 4, fontSize: "0.6rem", fontWeight: 800 }}>HIGH</span>
                         <span style={{ background: "#fff7ed", color: "#c2410c", border: "1px solid #ffedd5", padding: "2px 8px", borderRadius: 4, fontSize: "0.6rem", fontWeight: 800 }}>ESCALATE</span>
                      </div>
                   </div>

                   <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                      <div style={{ width: 40, height: 40, borderRadius: 20, background: "#f0f2f5", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, color: "#475569" }}>
                        {sender.charAt(0).toUpperCase()}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: "0.9rem", fontWeight: 700 }}>{sender.split("<")[0].trim()}</div>
                        <div style={{ fontSize: "0.75rem", color: "#64748b" }}>
                          {sender.includes("<") ? sender.match(/<(.+?)>/)?.[1] : sender}
                        </div>
                      </div>
                      <div style={{ fontSize: "0.72rem", color: "#94a3b8" }}>{ts}</div>
                   </div>
                </div>

                {/* Email Body */}
                <div style={{ padding: "32px", minHeight: 300, overflow: "hidden" }}>
                   <div style={{
                     fontSize: "0.95rem", color: "#334155", lineHeight: 1.6, whiteSpace: "pre-wrap",
                     wordBreak: "break-word", overflowWrap: "break-word", fontFamily: "'Inter', sans-serif",
                     overflow: "hidden"
                   }}>
                     {cleanBody || "(No message content available)"}
                   </div>

                   {/* Long Link Mock/Example to show truncation */}
                   <div style={{ marginTop: 40, paddingTop: 24, borderTop: "1px solid #f1f5f9" }}>
                      <div style={{ fontSize: "0.7rem", color: "#94a3b8", marginBottom: 8, fontWeight: 700, letterSpacing: 0.5 }}>SUSPICIOUS URL DETECTED:</div>
                      <div style={{
                        background: "#fff1f2", color: "#e11d48", padding: "8px 12px", borderRadius: 6,
                        fontSize: "0.75rem", fontFamily: "monospace", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                        border: "1px solid #ffe4e6"
                      }}>
                        https://secure-login-update-auth-v2.trident-security-validation-node-8821.io/auth/login?session_id=992817726351&redirect_uri=app_home_dashboard_production_version
                      </div>
                   </div>
                </div>
              </div>
            </div>

            {/* RIGHT — Analysis Panel (40%) */}
            <div style={{ width: "40%", minWidth: 0, overflowY: "auto", display: "flex", flexDirection: "column", gap: 24, height: "100%", paddingRight: 8 }}>

              {/* Risk Score Card */}
              <div style={{
                background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 16, padding: "32px 24px", display: "flex", flexDirection: "column", alignItems: "center"
              }}>
                <div style={{ alignSelf: "flex-start", fontSize: "0.62rem", letterSpacing: "3px", color: "rgba(255,255,255,0.35)", fontWeight: 700, marginBottom: 24 }}>
                  THREAT MAGNITUDE
                </div>
                <RiskArc score={score} band={band} />
                <div style={{
                   background: `${bandColor}1A`, color: bandColor, padding: "5px 16px", borderRadius: 20,
                   fontSize: "0.65rem", fontWeight: 800, letterSpacing: "1.5px", marginTop: 20, border: `1px solid ${bandColor}33`
                }}>
                  {band} SEVERITY
                </div>
              </div>

              {/* SHAP Contributions */}
              <div style={{
                background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 16, padding: "28px 24px"
              }}>
                <div style={{ fontSize: "0.62rem", letterSpacing: "3px", color: "rgba(255,255,255,0.35)", fontWeight: 700, marginBottom: 20 }}>
                  SHAP CONTRIBUTIONS
                </div>
                <ShapContributions factors={topFactors} color={bandColor} />
              </div>

              {/* Module Radar */}
              <div style={{
                background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 16, padding: "28px 24px"
              }}>
                <div style={{ fontSize: "0.62rem", letterSpacing: "3px", color: "rgba(255,255,255,0.35)", fontWeight: 700, marginBottom: 24 }}>
                   MODULE RADAR
                </div>
                <div style={{ background: "rgba(0,0,0,0.2)", borderRadius: 12, padding: "10px", border: "1px solid rgba(255,255,255,0.03)" }}>
                  <RadarChart scores={modules} />
                </div>
              </div>

            </div>
          </div>

        </div>
      )}
    </div>
  );
}
