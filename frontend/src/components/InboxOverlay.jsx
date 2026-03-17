import { useState } from 'react';
import { interceptedEmails } from '../data/mockEmails';
import ThreatInspector from './ThreatInspector';
import useScrollLock from '../hooks/useScrollLock';

export default function InboxOverlay({ isOpen, onClose }) {
  const [selectedEmail, setSelectedEmail] = useState(null);
  const { lock, unlock } = useScrollLock();

  // Lock/unlock scroll
  if (isOpen) lock();
  else unlock();

  if (!isOpen) return null;

  const handleClose = () => {
    setSelectedEmail(null);
    unlock();
    onClose();
  };

  return (
    <div className="inbox-overlay">
      <div className="inbox-backdrop" onClick={handleClose} />
      <div className="inbox-container">
        <div className="inbox-header">
          <div className="inbox-header-left">
            <span className="inbox-icon">📧</span>
            <h2>TRIDENT Intercepted Inbox</h2>
          </div>
          <button className="inbox-close" onClick={handleClose}>✕</button>
        </div>

        {selectedEmail ? (
          <ThreatInspector email={selectedEmail} onBack={() => setSelectedEmail(null)} />
        ) : (
          <div className="inbox-list">
            {interceptedEmails.map((email) => (
              <div
                key={email.id}
                className={`inbox-item inbox-item-${email.classification.toLowerCase()}`}
                onClick={() => setSelectedEmail(email)}
              >
                <div className="inbox-item-header">
                  <span className="inbox-sender">{email.sender}</span>
                  <span className={`inbox-badge badge-${email.classification.toLowerCase()}`}>
                    {email.classification}
                  </span>
                </div>
                <div className="inbox-subject">{email.subject}</div>
                <div className="inbox-risk">
                  <div className="risk-bar-track">
                    <div
                      className="risk-bar-fill"
                      style={{
                        width: `${email.riskScore}%`,
                        backgroundColor: email.riskScore > 75 ? '#ff4444' : email.riskScore > 40 ? '#ffaa00' : '#44ff88',
                      }}
                    />
                  </div>
                  <span className="risk-score-label">{email.riskScore}%</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
