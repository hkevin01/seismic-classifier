/**
 * WebSocket service for real-time seismic data streaming
 * Implements reconnection logic and buffered data handling
 */

import React from "react";

export interface SeismicDataMessage {
  type: "waveform" | "event" | "status" | "alert";
  timestamp: string;
  data: any;
  station?: string;
  metadata?: Record<string, any>;
}

export interface ConnectionStatus {
  connected: boolean;
  lastMessage: string | null;
  reconnectAttempts: number;
  latency: number;
}

export class WebSocketService {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectTimeout: number | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;
  private messageBuffer: SeismicDataMessage[] = [];
  private maxBufferSize = 1000;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();
  private connectionStatus: ConnectionStatus = {
    connected: false,
    lastMessage: null,
    reconnectAttempts: 0,
    latency: 0,
  };

  constructor(url: string) {
    this.url = url;
    this.initializeEventTypes();
  }

  private initializeEventTypes(): void {
    const eventTypes = ["waveform", "event", "status", "alert", "connection"];
    eventTypes.forEach((type) => {
      this.listeners.set(type, new Set());
    });
  }

  /**
   * Connect to the WebSocket server
   */
  public connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log("WebSocket already connected");
      return;
    }

    try {
      console.log(`Connecting to WebSocket: ${this.url}`);
      this.ws = new WebSocket(this.url);
      this.setupEventHandlers();
    } catch (error) {
      console.error("Failed to create WebSocket connection:", error);
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from the WebSocket server
   */
  public disconnect(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      this.ws.close(1000, "Client disconnect");
      this.ws = null;
    }

    this.updateConnectionStatus(false);
  }

  /**
   * Send a message to the server
   */
  public sendMessage(message: any): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const timestamp = new Date().toISOString();
      const wrappedMessage = { ...message, timestamp };
      this.ws.send(JSON.stringify(wrappedMessage));
    } else {
      console.warn("WebSocket not connected. Message not sent:", message);
    }
  }

  /**
   * Subscribe to specific message types
   */
  public subscribe(eventType: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }

    this.listeners.get(eventType)!.add(callback);

    // Return unsubscribe function
    return () => {
      this.listeners.get(eventType)?.delete(callback);
    };
  }

  /**
   * Get current connection status
   */
  public getStatus(): ConnectionStatus {
    return { ...this.connectionStatus };
  }

  /**
   * Get buffered messages
   */
  public getBufferedMessages(): SeismicDataMessage[] {
    return [...this.messageBuffer];
  }

  /**
   * Clear message buffer
   */
  public clearBuffer(): void {
    this.messageBuffer = [];
  }

  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log("WebSocket connected");
      this.reconnectAttempts = 0;
      this.updateConnectionStatus(true);
      this.notifyListeners("connection", { status: "connected" });
    };

    this.ws.onmessage = (event) => {
      try {
        const message: SeismicDataMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    this.ws.onclose = (event) => {
      console.log("WebSocket closed:", event.code, event.reason);
      this.updateConnectionStatus(false);
      this.notifyListeners("connection", { status: "disconnected", code: event.code });

      if (event.code !== 1000) {
        // Not a normal closure
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      this.notifyListeners("connection", { status: "error", error });
    };
  }

  private handleMessage(message: SeismicDataMessage): void {
    // Update latency calculation
    if (message.timestamp) {
      const latency = Date.now() - new Date(message.timestamp).getTime();
      this.connectionStatus.latency = latency;
    }

    // Buffer management
    this.addToBuffer(message);

    // Notify listeners
    this.notifyListeners(message.type, message.data);
    this.connectionStatus.lastMessage = message.timestamp;
  }

  private addToBuffer(message: SeismicDataMessage): void {
    this.messageBuffer.push(message);

    // Maintain buffer size
    if (this.messageBuffer.length > this.maxBufferSize) {
      this.messageBuffer.shift(); // Remove oldest message
    }
  }

  private notifyListeners(eventType: string, data: any): void {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      listeners.forEach((callback) => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in ${eventType} listener:`, error);
        }
      });
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error("Max reconnection attempts reached");
      this.notifyListeners("connection", { status: "failed", reason: "max_attempts" });
      return;
    }

    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts); // Exponential backoff
    this.reconnectAttempts++;
    this.connectionStatus.reconnectAttempts = this.reconnectAttempts;

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

    this.reconnectTimeout = setTimeout(() => {
      this.connect();
    }, delay);
  }

  private updateConnectionStatus(connected: boolean): void {
    this.connectionStatus.connected = connected;
    if (!connected) {
      this.connectionStatus.latency = 0;
    }
  }
}

// Singleton instance for global use
let websocketService: WebSocketService | null = null;

export const getWebSocketService = (url?: string): WebSocketService => {
  if (!websocketService && url) {
    websocketService = new WebSocketService(url);
  } else if (!websocketService) {
    throw new Error("WebSocket service not initialized. Provide URL on first call.");
  }
  return websocketService;
};

// React hook for easy integration
export const useWebSocket = (url: string, eventType?: string) => {
  const [connectionStatus, setConnectionStatus] = React.useState<ConnectionStatus>({
    connected: false,
    lastMessage: null,
    reconnectAttempts: 0,
    latency: 0,
  });
  const [lastMessage, setLastMessage] = React.useState<any>(null);

  React.useEffect(() => {
    const ws = getWebSocketService(url);

    // Subscribe to connection status changes
    const unsubscribeConnection = ws.subscribe("connection", (_status) => {
      setConnectionStatus(ws.getStatus());
    });

    // Subscribe to specific event type if provided
    let unsubscribeEvents: (() => void) | undefined;
    if (eventType) {
      unsubscribeEvents = ws.subscribe(eventType, (data) => {
        setLastMessage({ type: eventType, data, timestamp: new Date().toISOString() });
      });
    }

    // Connect
    ws.connect();

    // Cleanup on unmount
    return () => {
      unsubscribeConnection();
      unsubscribeEvents?.();
    };
  }, [url, eventType]);

  return {
    connectionStatus,
    lastMessage,
    sendMessage: (message: any) => getWebSocketService().sendMessage(message),
    subscribe: (type: string, callback: (data: any) => void) =>
      getWebSocketService().subscribe(type, callback),
  };
};

export default WebSocketService;
