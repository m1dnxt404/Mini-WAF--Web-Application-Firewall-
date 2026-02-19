import { useCallback, useEffect, useRef, useState } from "react";
import type { LogEntry } from "../lib/api";

const WS_URL = import.meta.env.VITE_WAF_WS_URL ?? `ws://${window.location.hostname}:8000`;
const MAX_MESSAGES = 100;
const RECONNECT_DELAY_MS = 3000;

export function useWebSocket() {
  const [messages, setMessages] = useState<LogEntry[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const pausedRef = useRef(false);
  const [paused, setPausedState] = useState(false);

  const setPaused = useCallback((value: boolean) => {
    pausedRef.current = value;
    setPausedState(value);
  }, []);

  useEffect(() => {
    let timeout: ReturnType<typeof setTimeout>;

    function connect() {
      const ws = new WebSocket(`${WS_URL}/ws/logs`);
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);

      ws.onmessage = (event: MessageEvent) => {
        if (pausedRef.current) return;
        try {
          const payload = JSON.parse(event.data as string) as {
            type: string;
            data: LogEntry;
          };
          if (payload.type === "new_log") {
            setMessages((prev) => [payload.data, ...prev].slice(0, MAX_MESSAGES));
          }
        } catch {
          // ignore malformed messages
        }
      };

      ws.onclose = () => {
        setConnected(false);
        timeout = setTimeout(connect, RECONNECT_DELAY_MS);
      };

      ws.onerror = () => ws.close();
    }

    connect();

    return () => {
      clearTimeout(timeout);
      wsRef.current?.close();
    };
  }, []);

  return { messages, connected, paused, setPaused };
}
