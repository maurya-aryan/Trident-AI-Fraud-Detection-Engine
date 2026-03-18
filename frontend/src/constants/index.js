/**
 * TRIDENT Frontend Constants
 *
 * Centralized configuration and constants for the frontend application.
 */

// API Configuration
export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Risk Band Thresholds
export const RISK_BANDS = {
  CRITICAL: { min: 76, max: 100, color: '#ff0000' },
  HIGH: { min: 51, max: 75, color: '#ff6600' },
  MEDIUM: { min: 21, max: 50, color: '#ffaa00' },
  LOW: { min: 0, max: 20, color: '#00ff00' },
};

// Risk Band Names
export const RISK_BUCKET_NAMES = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

// Alert Polling Interval (ms)
export const ALERT_POLL_INTERVAL = 5000;

// API Endpoints (relative to API_URL)
export const ENDPOINTS = {
  // Detection
  DETECT: '/detect',
  ANALYZE_EMAIL: '/analyze-email',
  ANALYZE_URL: '/analyze-url',
  SCAN_FILE: '/scan-file',
  CHECK_CREDENTIALS: '/check-credentials',
  CHECK_INJECTION: '/check-injection',

  // Alerts
  ALERTS: '/alerts',
  ALERTS_STATS: '/alerts/stats',

  // Campaign
  CAMPAIGN_STATUS: '/campaign-status',
  RESET_GRAPH: '/reset-graph',

  // Auth
  AUTH_GOOGLE_START: '/auth/google/start',
  AUTH_GOOGLE_CALLBACK: '/auth/google/callback',
  AUTH_CONNECT_BASIC: '/auth/connect/basic',
  AUTH_DISCONNECT: '/auth/disconnect',

  // Poller
  POLLER_START: '/poller/start',
  POLLER_STOP: '/poller/stop',
  POLLER_STREAM: '/poller/stream',

  // System
  HEALTH: '/health',
};

// Animation Durations (ms)
export const ANIMATION = {
  FAST: 200,
  NORMAL: 400,
  SLOW: 800,
};

// Module Names
export const MODULES = {
  AI_TEXT: 'ai_text_detection',
  PHISHING: 'email_phishing',
  URL: 'url_detection',
  MALWARE: 'malware_scanner',
  CREDENTIALS: 'credential_exposure',
  INJECTION: 'prompt_injection',
  CAMPAIGN: 'campaign_graph',
  SHAP: 'shap_explainer',
};
