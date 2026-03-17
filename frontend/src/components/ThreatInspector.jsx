import { shapData } from '../data/shapValues';

export default function ThreatInspector({ email, onBack }) {
  const maxAbsValue = Math.max(...shapData.features.map(f => Math.abs(f.value)));

  return (
    <div className="threat-inspector">
      <button className="inspector-back" onClick={onBack}>← Back to Inbox</button>

      <div className="inspector-header">
        <div className="inspector-risk-gauge">
          <svg viewBox="0 0 120 120" className="risk-gauge-svg">
            <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="8" />
            <circle
              cx="60" cy="60" r="52" fill="none"
              stroke={email.riskScore > 75 ? '#ff4444' : email.riskScore > 40 ? '#ffaa00' : '#44ff88'}
              strokeWidth="8"
              strokeDasharray={`${(email.riskScore / 100) * 327} 327`}
              strokeLinecap="round"
              transform="rotate(-90 60 60)"
              className="risk-gauge-arc"
            />
            <text x="60" y="55" textAnchor="middle" fill="white" fontSize="24" fontWeight="700">
              {email.riskScore}
            </text>
            <text x="60" y="72" textAnchor="middle" fill="rgba(255,255,255,0.5)" fontSize="10">
              RISK SCORE
            </text>
          </svg>
        </div>
        <div className="inspector-meta">
          <span className={`inspector-badge badge-${email.classification.toLowerCase()}`}>
            {email.classification}
          </span>
          <h3>{email.subject}</h3>
          <p className="inspector-sender">From: {email.sender}</p>
          <p className="inspector-id">Event: {email.id}</p>
        </div>
      </div>

      <div className="inspector-body">
        <h4>Email Body</h4>
        <div className="email-body-content" dangerouslySetInnerHTML={{ __html: email.body }} />
      </div>

      <div className="inspector-shap">
        <h4>🧠 SHAP Feature Contributions</h4>
        <div className="shap-chart">
          {shapData.features.map((feat, i) => {
            const barWidth = (Math.abs(feat.value) / maxAbsValue) * 100;
            const isNeg = feat.impact === 'negative';
            return (
              <div key={i} className="shap-row">
                <span className="shap-label">{feat.name}</span>
                <div className="shap-bar-container">
                  <div
                    className={`shap-bar ${isNeg ? 'shap-bar-neg' : 'shap-bar-pos'}`}
                    style={{ width: `${barWidth}%` }}
                  />
                </div>
                <span className="shap-value">
                  {feat.value > 0 ? '+' : ''}{feat.value.toFixed(2)}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
