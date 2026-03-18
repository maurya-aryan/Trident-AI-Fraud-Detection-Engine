/**
 * useAlerts Hook
 *
 * Custom React hook for managing alerts state with automatic polling.
 *
 * Features:
 * - Fetches alerts from API with optional bucket filtering
 * - Automatic polling with configurable interval
 * - Loading and error state management
 * - Manual refetch capability
 *
 * Usage:
 *   const { alerts, loading, error, refetch } = useAlerts({ bucket: 'CRITICAL', limit: 50 });
 */
import { useState, useEffect, useCallback } from 'react';
import { fetchAlerts } from '../lib/api';
import { ALERT_POLL_INTERVAL } from '../constants';

export function useAlerts({
  bucket = null,
  limit = 100,
  offset = 0,
  pollInterval = ALERT_POLL_INTERVAL,
  autoPoll = true,
} = {}) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [total, setTotal] = useState(0);

  const loadAlerts = useCallback(async () => {
    try {
      setError(null);
      const response = await fetchAlerts({ bucket, limit, offset });

      setAlerts(response.alerts || []);
      setTotal(response.total || 0);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load alerts:', err);
      setError(err.message || 'Failed to load alerts');
      setLoading(false);
    }
  }, [bucket, limit, offset]);

  // Initial load
  useEffect(() => {
    loadAlerts();
  }, [loadAlerts]);

  // Auto-polling
  useEffect(() => {
    if (!autoPoll || pollInterval <= 0) return;

    const intervalId = setInterval(() => {
      loadAlerts();
    }, pollInterval);

    return () => clearInterval(intervalId);
  }, [autoPoll, pollInterval, loadAlerts]);

  return {
    alerts,
    loading,
    error,
    total,
    refetch: loadAlerts,
  };
}

/**
 * useAlertStats Hook
 *
 * Fetches and manages alert statistics.
 *
 * Usage:
 *   const { stats, loading, error } = useAlertStats();
 */
export function useAlertStats({ pollInterval = ALERT_POLL_INTERVAL, autoPoll = false } = {}) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadStats = useCallback(async () => {
    try {
      setError(null);
      const { fetchAlertStats } = await import('../lib/api');
      const response = await fetchAlertStats();
      setStats(response);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load alert stats:', err);
      setError(err.message || 'Failed to load alert stats');
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadStats();
  }, [loadStats]);

  // Auto-polling (optional)
  useEffect(() => {
    if (!autoPoll || pollInterval <= 0) return;

    const intervalId = setInterval(() => {
      loadStats();
    }, pollInterval);

    return () => clearInterval(intervalId);
  }, [autoPoll, pollInterval, loadStats]);

  return {
    stats,
    loading,
    error,
    refetch: loadStats,
  };
}
