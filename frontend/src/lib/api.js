/**
 * TRIDENT API Client
 *
 * Centralized API calls for all backend endpoints.
 * All fetch() calls should go through this module.
 */
import { API_URL, ENDPOINTS } from '../constants';

/**
 * Base fetch wrapper with error handling
 */
async function apiFetch(endpoint, options = {}) {
  const url = `${API_URL}${endpoint}`;
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  const response = await fetch(url, { ...defaultOptions, ...options });

  if (!response.ok) {
    const error = new Error(`API Error: ${response.statusText}`);
    error.status = response.status;
    error.response = response;
    throw error;
  }

  // Handle empty responses
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return await response.json();
  }

  return response;
}

// ============================================================================
// Detection Endpoints
// ============================================================================

/**
 * Full fraud detection pipeline
 */
export async function detectEmail(payload) {
  return apiFetch(ENDPOINTS.DETECT, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/**
 * Analyze email text only
 */
export async function analyzeEmail(text) {
  return apiFetch(`${ENDPOINTS.ANALYZE_EMAIL}?text=${encodeURIComponent(text)}`, {
    method: 'POST',
  });
}

/**
 * Analyze a single URL
 */
export async function analyzeURL(url) {
  return apiFetch(`${ENDPOINTS.ANALYZE_URL}?url=${encodeURIComponent(url)}`, {
    method: 'POST',
  });
}

/**
 * Scan uploaded file for malware
 */
export async function scanFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  return apiFetch(ENDPOINTS.SCAN_FILE, {
    method: 'POST',
    body: formData,
    headers: {}, // Let browser set Content-Type for FormData
  });
}

/**
 * Check text for exposed credentials
 */
export async function checkCredentials(text) {
  return apiFetch(`${ENDPOINTS.CHECK_CREDENTIALS}?text=${encodeURIComponent(text)}`, {
    method: 'POST',
  });
}

/**
 * Check text for prompt injection
 */
export async function checkInjection(text) {
  return apiFetch(`${ENDPOINTS.CHECK_INJECTION}?text=${encodeURIComponent(text)}`, {
    method: 'POST',
  });
}

// ============================================================================
// Alert Endpoints
// ============================================================================

/**
 * Fetch alerts with optional filtering
 */
export async function fetchAlerts({ bucket = null, limit = 100, offset = 0 } = {}) {
  const params = new URLSearchParams({ limit, offset });
  if (bucket) params.append('bucket', bucket);

  return apiFetch(`${ENDPOINTS.ALERTS}?${params}`);
}

/**
 * Fetch a specific alert by ID
 */
export async function fetchAlertById(id) {
  return apiFetch(`${ENDPOINTS.ALERTS}/${id}`);
}

/**
 * Push a new alert (used by poller)
 */
export async function pushAlert(alert) {
  return apiFetch(ENDPOINTS.ALERTS, {
    method: 'POST',
    body: JSON.stringify(alert),
  });
}

/**
 * Get alert statistics
 */
export async function fetchAlertStats() {
  return apiFetch(ENDPOINTS.ALERTS_STATS);
}

/**
 * Clear all alerts
 */
export async function clearAlerts() {
  return apiFetch(ENDPOINTS.ALERTS, {
    method: 'DELETE',
  });
}

// ============================================================================
// Campaign Graph Endpoints
// ============================================================================

/**
 * Get current campaign correlation status
 */
export async function fetchCampaignStatus() {
  return apiFetch(ENDPOINTS.CAMPAIGN_STATUS);
}

/**
 * Reset the campaign graph
 */
export async function resetCampaignGraph() {
  return apiFetch(ENDPOINTS.RESET_GRAPH, {
    method: 'POST',
  });
}

// ============================================================================
// Authentication Endpoints
// ============================================================================

/**
 * Start Google OAuth flow
 */
export async function startGoogleAuth(ownerId, redirectFrontend = null) {
  const params = new URLSearchParams({ owner_id: ownerId });
  if (redirectFrontend) params.append('redirect_frontend', redirectFrontend);

  const response = await apiFetch(`${ENDPOINTS.AUTH_GOOGLE_START}?${params}`);
  return response;
}

/**
 * Connect mailbox with basic authentication
 */
export async function connectBasicAuth(credentials) {
  return apiFetch(ENDPOINTS.AUTH_CONNECT_BASIC, {
    method: 'POST',
    body: JSON.stringify(credentials),
  });
}

/**
 * Disconnect mailbox
 */
export async function disconnectMailbox(ownerId) {
  return apiFetch(ENDPOINTS.AUTH_DISCONNECT, {
    method: 'POST',
    body: JSON.stringify({ owner_id: ownerId }),
  });
}

// ============================================================================
// Poller Endpoints
// ============================================================================

/**
 * Start the IMAP poller
 */
export async function startPoller(envOverrides = {}) {
  return apiFetch(ENDPOINTS.POLLER_START, {
    method: 'POST',
    body: JSON.stringify({ env_overrides: envOverrides }),
  });
}

/**
 * Stop the IMAP poller
 */
export async function stopPoller() {
  return apiFetch(ENDPOINTS.POLLER_STOP, {
    method: 'POST',
  });
}

/**
 * Get poller stream (SSE)
 */
export function getPollerStream() {
  return new EventSource(`${API_URL}${ENDPOINTS.POLLER_STREAM}`);
}

// ============================================================================
// System Endpoints
// ============================================================================

/**
 * Health check
 */
export async function checkHealth() {
  return apiFetch(ENDPOINTS.HEALTH);
}
