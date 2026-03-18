/**
 * useSSE Hook
 *
 * Custom React hook for managing Server-Sent Events (EventSource) connections.
 *
 * Features:
 * - Automatic connection management
 * - Message handling with type filtering
 * - Connection state tracking
 * - Automatic cleanup on unmount
 * - Error handling and reconnection
 *
 * Usage:
 *   const { messages, connected, error } = useSSE('/poller/stream', {
 *     onMessage: (data) => console.log('Received:', data),
 *     onError: (err) => console.error('SSE Error:', err),
 *   });
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import { API_URL } from '../constants';

export function useSSE(endpoint, { onMessage = null, onError = null, autoConnect = true } = {}) {
  const [messages, setMessages] = useState([]);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState(null);

  const eventSourceRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connect = useCallback(() => {
    if (eventSourceRef.current) {
      console.warn('EventSource already connected');
      return;
    }

    const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;

    try {
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        console.log('SSE connection established:', endpoint);
        setConnected(true);
        setError(null);
      };

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          // Add to messages array
          setMessages((prev) => [...prev, data]);

          // Call external handler if provided
          if (onMessage) {
            onMessage(data);
          }
        } catch (err) {
          console.error('Failed to parse SSE message:', err);
        }
      };

      eventSource.onerror = (err) => {
        console.error('SSE connection error:', err);
        setConnected(false);
        setError('Connection lost');

        // Call external error handler
        if (onError) {
          onError(err);
        }

        // Close and attempt reconnection after delay
        disconnect();

        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting SSE reconnection...');
          connect();
        }, 5000);
      };
    } catch (err) {
      console.error('Failed to create EventSource:', err);
      setError(err.message);
      setConnected(false);

      if (onError) {
        onError(err);
      }
    }
  }, [endpoint, onMessage, onError]);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setConnected(false);
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    // Cleanup on unmount
    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    messages,
    connected,
    error,
    connect,
    disconnect,
    clearMessages,
  };
}

/**
 * usePollerStream Hook
 *
 * Specialized hook for the IMAP poller stream endpoint.
 *
 * Usage:
 *   const { status, logs, connected } = usePollerStream();
 */
export function usePollerStream() {
  const [status, setStatus] = useState('stopped');
  const [logs, setLogs] = useState([]);
  const [pid, setPid] = useState(null);

  const handleMessage = useCallback((data) => {
    if (data.type === 'status') {
      setStatus(data.data);
      if (data.pid) setPid(data.pid);
    } else if (data.type === 'line') {
      setLogs((prev) => [...prev, data.data]);
    }
  }, []);

  const { connected, error, connect, disconnect } = useSSE('/poller/stream', {
    onMessage: handleMessage,
    autoConnect: true,
  });

  const clearLogs = useCallback(() => {
    setLogs([]);
  }, []);

  return {
    status,
    logs,
    pid,
    connected,
    error,
    connect,
    disconnect,
    clearLogs,
  };
}
