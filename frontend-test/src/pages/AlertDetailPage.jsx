import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

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

// ── SVG Risk Gauge ────────────────────────────────────────────────────────────
function RiskGauge({ score, band }) {
  const color = BAND_COLOR[band] || "#888";
  const radius = 70;
  const stroke = 10;
  const cx = 90, cy = 90;
  const startAngle = -210;
  const sweepAngle = 240;
  const angle = startAngle + (sweepAngle * score) / 100;
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

  const needleX = cx + (radius - 4) * Math.cos(toRad(angle));
  const needleY = cy + (radius - 4) * Math.sin(toRad(angle));

  return (
    <svg width={180} height={130} style={{ display: "block", margin: "0 auto" }}>
      {/* Track */}
      <path d={arcPath(startAngle, sweepAngle)} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={stroke} strokeLinecap="round" />
      {/* Fill */}
      <path d={arcPath(startAngle, sweepAngle * score / 100)} fill="none" stroke={color}
        strokeWidth={stroke} strokeLinecap="round"
        style={{ filter: `drop-shadow(0 0 6px ${color}88)` }} />
      {/* Needle dot */}
      <circle cx={needleX} cy={needleY} r={5} fill={color} style={{ filter: `drop-shadow(0 0 8px ${color})` }} />
      {/* Center score */}
      <text x={cx} y={cy + 6} textAnchor="middle" fill={color}
        fontSize={24} fontWeight={700} fontFamily="'Courier New',monospace">
        {score.toFixed(0)}
      </text>
      <text x={cx} y={cy + 22} textAnchor="middle" fill="rgba(223,240,251,0.4)"
        fontSize={9} letterSpacing={2} fontFamily="'Courier New',monospace">
        RISK SCORE
      </text>
    </svg>
  );
}

// ── Module Score Bars ─────────────────────────────────────────────────────────
function ModuleBars({ scores }) {
  if (!scores || Object.keys(scores).length === 0) return (
    <div style={{ color: "rgba(223,240,251,0.3)", fontSize: "0.75rem", textAlign: "center", padding: "20px 0" }}>
      No module data
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {Object.entries(scores).sort(([, a], [, b]) => b - a).map(([mod, val]) => {
        const pct = Math.min(100, Math.max(0, val));
        const color = pct >= 75 ? "#EF4444" : pct >= 50 ? "#F97316" : pct >= 25 ? "#EAB308" : "#10B981";
        return (
          <div key={mod}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
              <span style={{ fontSize: "0.7rem", color: "rgba(91,196,239,0.8)", letterSpacing: "0.5px" }}>
                {MODULE_LABELS[mod] || mod}
              </span>
              <span style={{ fontSize: "0.7rem", color, fontWeight: 700 }}>{pct.toFixed(0)}</span>
            </div>
            <div style={{ height: 5, borderRadius: 3, background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
              <div style={{
                height: "100%", width: `${pct}%`, borderRadius: 3,
                background: `linear-gradient(90deg, ${color}88, ${color})`,
                boxShadow: `0 0 8px ${color}55`,
                transition: "width 0.6s ease"
              }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ── Radar Chart ───────────────────────────────────────────────────────────────
function RadarChart({ scores }) {
  const entries = Object.entries(scores || {}).slice(0, 8);
  if (entries.length < 3) return null;

  const cx = 110, cy = 110, r = 80;
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
      {/* Grid rings */}
      {[0.25, 0.5, 0.75, 1].map((f) => (
        <polygon key={f}
          points={poly(outline.map((_, i) => {
            const a = (2 * Math.PI * i) / n - Math.PI / 2;
            return { x: cx + r * f * Math.cos(a), y: cy + r * f * Math.sin(a) };
          }))}
          fill="none" stroke="rgba(0,212,255,0.08)" strokeWidth={1}
        />
      ))}
      {/* Spokes */}
      {outline.map((p, i) => (
        <line key={i} x1={cx} y1={cy} x2={p.x} y2={p.y} stroke="rgba(0,212,255,0.08)" strokeWidth={1} />
      ))}
      {/* Data area */}
      <polygon points={poly(points)} fill="rgba(0,212,255,0.1)" stroke="#00d4ff" strokeWidth={1.5}
        style={{ filter: "drop-shadow(0 0 6px rgba(0,212,255,0.3))" }} />
      {/* Labels */}
      {outline.map((p, i) => {
        const [mod] = entries[i];
        const lx = cx + (r + 16) * Math.cos((2 * Math.PI * i) / n - Math.PI / 2);
        const ly = cy + (r + 16) * Math.sin((2 * Math.PI * i) / n - Math.PI / 2);
        return (
          <text key={i} x={lx} y={ly} textAnchor="middle" dominantBaseline="middle"
            fill="rgba(91,196,239,0.7)" fontSize={8} fontFamily="'Courier New',monospace">
            {(MODULE_LABELS[mod] || mod).split(" ")[0].toUpperCase()}
          </text>
        );
      })}
    </svg>
  );
}

// ── Main Component ────────────────────────────────────────────────────────────
export default function AlertDetailPage() {
  const { bucket, id } = useParams();
  const navigate = useNavigate();
  const [alert, setAlert] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [debugOpen, setDebugOpen] = useState(false);

  const isFraud = bucket === "fraud";
  const accentColor = isFraud ? "#EF4444" : "#10B981";

  useEffect(() => {
    fetch("/api/alerts?limit=50")
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
  const topFactors = tr.top_factors  || rec.top_factors  || [];
  const explanation = tr.explanation || rec.explanation || "";
  const bandColor  = BAND_COLOR[band] || "#888";
  const bandBg     = BAND_BG[band]    || "rgba(100,100,100,0.05)";
  const bandIcon   = BAND_ICON[band]  || "❓";
  const actionColor = ACTION_COLOR[action] || "#888";

  return (
    <div style={{
      minHeight: "100vh",
      background: "radial-gradient(ellipse 80% 50% at 50% 0%, #050f1e 0%, #020810 60%, #000 100%)",
      color: "#dff0fb",
      fontFamily: "'Courier New', monospace",
      padding: "0 0 80px 0"
    }}>
      {/* Header */}
      <div style={{
        position: "sticky", top: 0, zIndex: 100,
        background: "rgba(2,8,16,0.85)",
        backdropFilter: "blur(20px)",
        borderBottom: "1px solid rgba(0,212,255,0.12)",
        padding: "0 32px", height: 60,
        display: "flex", alignItems: "center", justifyContent: "space-between"
      }}>
        <button
          onClick={() => navigate(`/alerts/${bucket}`)}
          style={{
            background: "none", border: "1px solid rgba(0,212,255,0.25)",
            color: "#00d4ff", fontFamily: "'Courier New', monospace",
            fontSize: "0.75rem", letterSpacing: "1.5px", padding: "6px 18px",
            borderRadius: 6, cursor: "pointer", transition: "all 0.2s"
          }}
          onMouseEnter={e => e.currentTarget.style.background = "rgba(0,212,255,0.1)"}
          onMouseLeave={e => e.currentTarget.style.background = "none"}
        >
          ← BACK TO {isFraud ? "FRAUD" : "SAFE"} ALERTS
        </button>

        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 6, height: 6, borderRadius: "50%", background: accentColor, boxShadow: `0 0 8px ${accentColor}` }} />
          <span style={{ fontSize: "0.7rem", letterSpacing: "2px", color: "rgba(223,240,251,0.5)" }}>
            TRIDENT · ALERT ANALYSIS
          </span>
        </div>
      </div>

      {/* Loading / Error states */}
      {loading && (
        <div style={{ textAlign: "center", padding: "120px 0", color: "rgba(0,212,255,0.5)", letterSpacing: "2px", fontSize: "0.8rem" }}>
          LOADING ANALYSIS...
        </div>
      )}
      {error && (
        <div style={{ maxWidth: 900, margin: "40px auto", padding: "0 32px" }}>
          <div style={{ background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.25)", borderRadius: 10, padding: "20px 24px", color: "#EF4444", fontSize: "0.8rem" }}>
            ⚠ {error}
          </div>
        </div>
      )}

      {/* Content */}
      {!loading && !error && alert && (
        <div style={{ maxWidth: 1100, margin: "0 auto", padding: "40px 32px 0" }}>

          {/* Subject + band badge */}
          <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 32, flexWrap: "wrap" }}>
            <span style={{ fontSize: "1.4rem" }}>{bandIcon}</span>
            <span style={{
              background: `${bandColor}22`, color: bandColor,
              padding: "4px 14px", borderRadius: 6,
              fontSize: "0.65rem", fontWeight: 700, letterSpacing: "1px"
            }}>{band}</span>
            <span style={{
              background: `${actionColor}18`, color: actionColor,
              padding: "4px 14px", borderRadius: 6,
              fontSize: "0.65rem", fontWeight: 700, letterSpacing: "1px",
              border: `1px solid ${actionColor}33`
            }}>{action}</span>
            <span style={{ fontSize: "1rem", fontWeight: 700, color: "#dff0fb", flex: 1 }}>{subject}</span>
          </div>

          {/* Two-column layout */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>

            {/* LEFT — Email message */}
            <div style={{
              background: "rgba(3,13,28,0.7)",
              border: `1px solid rgba(14,165,233,0.18)`,
              borderLeft: `2px solid rgba(14,165,233,0.4)`,
              borderRadius: 14,
              padding: "24px 24px"
            }}>
              <div style={{ fontSize: "0.6rem", letterSpacing: "3px", color: "rgba(91,196,239,0.5)", marginBottom: 16 }}>
                EMAIL MESSAGE
              </div>
              <div style={{ fontSize: "1rem", fontWeight: 700, marginBottom: 10, color: "#dff0fb" }}>{subject}</div>
              <div style={{ fontSize: "0.72rem", color: "rgba(100,148,193,0.8)", marginBottom: 18 }}>
                <span style={{ color: "rgba(91,196,239,0.7)" }}>From:</span> {sender}
                &nbsp;·&nbsp;
                <span style={{ color: "rgba(91,196,239,0.7)" }}>At:</span> {ts}
              </div>
              <div style={{
                background: "rgba(0,0,0,0.4)", borderRadius: 10,
                padding: 18, border: "1px solid rgba(14,150,210,0.10)",
                maxHeight: "50vh", overflowY: "auto"
              }}>
                <pre style={{
                  fontFamily: "'Courier New', monospace",
                  fontSize: "0.8rem", color: "rgba(224,242,254,0.9)",
                  lineHeight: 1.7, whiteSpace: "pre-wrap", margin: 0
                }}>
                  {body || "(No message content available)"}
                </pre>
              </div>
            </div>

            {/* RIGHT — Analysis */}
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              <div style={{ fontSize: "0.6rem", letterSpacing: "3px", color: "rgba(91,196,239,0.5)" }}>
                TRIDENT ANALYSIS
              </div>

              {/* Gauge + band info */}
              <div style={{
                background: bandBg,
                border: `1px solid ${bandColor}28`,
                borderRadius: 14, padding: "24px 20px",
                textAlign: "center"
              }}>
                <RiskGauge score={score} band={band} />
                {tr.confidence != null && (
                  <div style={{ fontSize: "0.7rem", color: "rgba(223,240,251,0.4)", marginTop: 6, letterSpacing: "1px" }}>
                    CONFIDENCE: {(tr.confidence * 100).toFixed(0)}%
                  </div>
                )}
                {tr.processing_time_ms != null && (
                  <div style={{ fontSize: "0.65rem", color: "rgba(223,240,251,0.3)", letterSpacing: "1px" }}>
                    PROCESSED IN {tr.processing_time_ms.toFixed(0)} ms
                  </div>
                )}
              </div>

              {/* Module scores */}
              {Object.keys(modules).length > 0 && (
                <div style={{
                  background: "rgba(3,13,28,0.7)",
                  border: "1px solid rgba(14,165,233,0.12)",
                  borderRadius: 14, padding: "20px 20px"
                }}>
                  <div style={{ fontSize: "0.6rem", letterSpacing: "3px", color: "rgba(91,196,239,0.5)", marginBottom: 14 }}>
                    MODULE SCORES
                  </div>
                  <ModuleBars scores={modules} />
                </div>
              )}

              {/* Top factors */}
              {topFactors.length > 0 && (
                <div style={{
                  background: "rgba(3,13,28,0.7)",
                  border: "1px solid rgba(14,165,233,0.12)",
                  borderRadius: 14, padding: "20px 20px"
                }}>
                  <div style={{ fontSize: "0.6rem", letterSpacing: "3px", color: "rgba(91,196,239,0.5)", marginBottom: 14 }}>
                    TOP RISK FACTORS
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                    {topFactors.map((f, i) => (
                      <div key={i} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <div style={{ width: 6, height: 6, borderRadius: "50%", background: bandColor, flexShrink: 0 }} />
                        <span style={{ fontSize: "0.78rem", color: "rgba(223,240,251,0.8)" }}>{f}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Explanation — full width */}
          {explanation && (
            <div style={{
              marginTop: 24,
              background: "rgba(3,13,28,0.7)",
              border: "1px solid rgba(14,165,233,0.12)",
              borderRadius: 14, padding: "20px 24px"
            }}>
              <div style={{ fontSize: "0.6rem", letterSpacing: "3px", color: "rgba(91,196,239,0.5)", marginBottom: 10 }}>
                EXPLANATION
              </div>
              <p style={{ fontSize: "0.82rem", lineHeight: 1.8, color: "rgba(223,240,251,0.75)", margin: 0 }}>
                {explanation}
              </p>
            </div>
          )}

          {/* Radar chart — full width */}
          {Object.keys(modules).length >= 3 && (
            <div style={{
              marginTop: 24,
              background: "rgba(3,13,28,0.7)",
              border: "1px solid rgba(14,165,233,0.12)",
              borderRadius: 14, padding: "20px 24px",
              textAlign: "center"
            }}>
              <div style={{ fontSize: "0.6rem", letterSpacing: "3px", color: "rgba(91,196,239,0.5)", marginBottom: 16 }}>
                MODULE RADAR
              </div>
              <RadarChart scores={modules} />
            </div>
          )}

          {/* Debug expander */}
          <div style={{ marginTop: 24 }}>
            <button
              onClick={() => setDebugOpen(o => !o)}
              style={{
                background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)",
                color: "rgba(223,240,251,0.4)", fontFamily: "'Courier New', monospace",
                fontSize: "0.7rem", letterSpacing: "1.5px", padding: "8px 20px",
                borderRadius: 8, cursor: "pointer", width: "100%", textAlign: "left"
              }}
            >
              {debugOpen ? "▾" : "▸"} ADVANCED / DEBUG INFO
            </button>
            {debugOpen && (
              <pre style={{
                marginTop: 8, background: "rgba(0,0,0,0.5)",
                border: "1px solid rgba(255,255,255,0.06)",
                borderRadius: 10, padding: 20,
                fontSize: "0.7rem", color: "rgba(223,240,251,0.6)",
                overflowX: "auto", lineHeight: 1.6
              }}>
                {JSON.stringify(alert, null, 2)}
              </pre>
            )}
          </div>

        </div>
      )}
    </div>
  );
}
