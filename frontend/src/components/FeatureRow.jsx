import features from '../data/features.json';

export default function FeatureRow() {
  return (
    <div className="feature-rows">
      {features.map((feat, i) => (
        <div className="feature-row" key={i} style={{ animationDelay: `${i * 0.1}s` }}>
          <span className="feature-icon">{feat.icon}</span>
          <div className="feature-text">
            <h3>{feat.title}</h3>
            <p>{feat.description}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
