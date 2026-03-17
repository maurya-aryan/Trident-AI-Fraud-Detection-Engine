import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

const BAND_COLOR  = { CRITICAL: "#EF4444", HIGH: "#F97316", MEDIUM: "#EAB308", LOW: "#10B981" };
const BAND_BG     = { CRITICAL: "rgba(239,68,68,0.10)", HIGH: "rgba(249,115,22,0.10)", MEDIUM: "rgba(234,179,8,0.08)", LOW: "rgba(16,185,129,0.08)" };
const BAND_ICON   = { CRITICAL: "🚨", HIGH: "⚠️", MEDIUM: "🔶", LOW: "✅" };
const FRAUD_BANDS = new Set(["CRITICAL", "HIGH", "MEDIUM"]);
const SAFE_BANDS  = new Set(["LOW"]);

export default function AlertsPage() {
  const { bucket } = useParams();
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const isFraud = bucket === "fraud";
  const allowedBands = isFraud ? FRAUD_BANDS : SAFE_BANDS;
  const title = isFraud ? "FRAUD ALERTS" : "SAFE ALERTS";
  const subtitle = isFraud ? "HIGH · MEDIUM · CRITICAL" : "LOW RISK";
  const accentColor = isFraud ? "#EF4444" : "#10B981";
  const emptyMsg = isFraud ? "No fraud alerts at this time." : "No safe mail classified yet.";

  useEffect(() => {
    setLoading(true);
    fetch("/api/alerts?limit=50")
      .then(r => {
        if (!r.ok) throw new Error(`API error: ${r.status}`);
        return r.json();
      })
      .then(data => {
        const all = data.alerts || [];
        const filtered = all
          .map((entry, idx) => ({ entry, originalIdx: idx }))
          .filter(({ entry }) => allowedBands.has((entry.alert?.risk_band || "LOW").toUpperCase()));
        setAlerts(filtered);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, [bucket]);

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
        padding: "0 32px",
        height: 60,
        display: "flex", alignItems: "center", justifyContent: "space-between"
      }}>
        <button
          onClick={() => navigate("/")}
          style={{
            background: "none", border: "1px solid rgba(0,212,255,0.25)",
            color: "#00d4ff", fontFamily: "'Courier New', monospace",
            fontSize: "0.75rem", letterSpacing: "1.5px", padding: "6px 18px",
            borderRadius: 6, cursor: "pointer", transition: "all 0.2s"
          }}
          onMouseEnter={e => e.currentTarget.style.background = "rgba(0,212,255,0.1)"}
          onMouseLeave={e => e.currentTarget.style.background = "none"}
        >
          ← BACK TO FUNNEL
        </button>

        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 6, height: 6, borderRadius: "50%", background: accentColor, boxShadow: `0 0 8px ${accentColor}` }} />
          <span style={{ fontSize: "0.7rem", letterSpacing: "2px", color: "rgba(223,240,251,0.5)" }}>
            TRIDENT · ALERT DASHBOARD
          </span>
        </div>
      </div>

      {/* Page Title */}
      <div style={{ padding: "48px 32px 32px", maxWidth: 900, margin: "0 auto" }}>
        <div style={{ marginBottom: 6, fontSize: "0.65rem", letterSpacing: "3px", color: "rgba(223,240,251,0.35)" }}>
          CLASSIFIED ·  {subtitle}
        </div>
        <h1 style={{
          fontSize: "clamp(2rem, 5vw, 3.2rem)", fontWeight: 300,
          letterSpacing: "0.15em", color: accentColor,
          textShadow: `0 0 40px ${accentColor}55`,
          margin: 0, lineHeight: 1
        }}>
          {title}
        </h1>
        <div style={{ marginTop: 12, width: 48, height: 2, background: `linear-gradient(90deg, ${accentColor}, transparent)` }} />
      </div>

      {/* Content */}
      <div style={{ maxWidth: 900, margin: "0 auto", padding: "0 32px" }}>
        {loading && (
          <div style={{ textAlign: "center", padding: "80px 0", color: "rgba(0,212,255,0.5)", letterSpacing: "2px", fontSize: "0.8rem" }}>
            FETCHING ALERTS...
          </div>
        )}

        {error && (
          <div style={{
            background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.25)",
            borderRadius: 10, padding: "20px 24px", color: "#EF4444",
            fontSize: "0.8rem", letterSpacing: "1px"
          }}>
            ⚠ API UNREACHABLE — {error}
            <br />
            <span style={{ color: "rgba(239,68,68,0.6)", fontSize: "0.7rem" }}>Make sure FastAPI is running on port 8000</span>
          </div>
        )}

        {!loading && !error && alerts.length === 0 && (
          <div style={{ textAlign: "center", padding: "80px 0" }}>
            <div style={{ fontSize: "3rem", marginBottom: 16 }}>{isFraud ? "🚫" : "✅"}</div>
            <div style={{ color: "rgba(223,240,251,0.35)", letterSpacing: "2px", fontSize: "0.8rem" }}>{emptyMsg}</div>
          </div>
        )}

        {!loading && !error && alerts.map(({ entry, originalIdx }) => {
          const rec     = entry.alert || {};
          const band    = (rec.risk_band || "LOW").toUpperCase();
          const score   = rec.risk_score ?? 0;
          const subj    = rec.subject || "(no subject)";
          const sender  = rec.sender  || "(unknown)";
          const ts      = entry.received_at || "";
          const color   = BAND_COLOR[band]  || "#888";
          const bg      = BAND_BG[band]     || "rgba(100,100,100,0.05)";
          const icon    = BAND_ICON[band]   || "❓";

          return (
            <div
              key={originalIdx}
              style={{
                display: "flex", alignItems: "stretch", gap: 0,
                marginBottom: 14, borderRadius: 12,
                border: `1px solid ${color}28`,
                overflow: "hidden"
              }}
            >
              {/* Card body */}
              <div style={{
                flex: 1, background: bg,
                padding: "18px 22px",
                display: "flex", alignItems: "center", gap: 18
              }}>
                <div style={{ fontSize: "1.8rem", lineHeight: 1, flexShrink: 0 }}>{icon}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 6, flexWrap: "wrap" }}>
                    <span style={{
                      background: `${color}22`, color, padding: "3px 12px",
                      borderRadius: 6, fontSize: "0.65rem", fontWeight: 700, letterSpacing: "0.5px"
                    }}>{band}</span>
                    <span style={{ color, fontSize: "1rem", fontWeight: 700 }}>{score.toFixed(0)}/100</span>
                    <span style={{ color: "rgba(223,240,251,0.85)", fontSize: "0.9rem", fontWeight: 600,
                      overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", maxWidth: 340 }}>
                      {subj}
                    </span>
                  </div>
                  <div style={{ fontSize: "0.75rem", color: "rgba(100,148,193,0.8)" }}>
                    <span style={{ color: "rgba(91,196,239,0.7)" }}>From:</span> {sender}
                    &nbsp;·&nbsp;
                    <span style={{ color: "rgba(91,196,239,0.7)" }}>At:</span> {ts}
                  </div>
                </div>
              </div>

              {/* View button */}
              <button
                onClick={() => navigate(`/alerts/${bucket}/${originalIdx}`)}
                style={{
                  background: `${color}18`, border: "none",
                  borderLeft: `1px solid ${color}28`,
                  color, fontFamily: "'Courier New', monospace",
                  fontSize: "0.72rem", letterSpacing: "1.5px",
                  padding: "0 24px", cursor: "pointer",
                  transition: "background 0.2s", flexShrink: 0,
                  fontWeight: 700
                }}
                onMouseEnter={e => e.currentTarget.style.background = `${color}32`}
                onMouseLeave={e => e.currentTarget.style.background = `${color}18`}
              >
                ▶ VIEW
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
