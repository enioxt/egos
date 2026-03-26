/**
 * Mycelium Integration Layer for EGOS Commons
 * Connects frontend events to the Mycelium Reference Graph and Event Bus.
 */

export interface MyceliumEvent {
  type: string;
  source: string;
  payload: Record<string, any>;
  timestamp: string;
}

export const emitMyceliumEvent = async (type: string, payload: Record<string, any>) => {
  try {
    const event: MyceliumEvent = {
        type,
        source: 'egos_commons_frontend',
        payload,
        timestamp: new Date().toISOString()
    };
    
    // In production, syncs with backend Mycelium Event Bus (agents/runtime/event-bus.ts projection)
    console.log('[Mycelium Sync] Event Emitted:', event);
    
    const endpoint = import.meta.env.VITE_MYCELIUM_URL;
    if (endpoint) {
      await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(event)
      });
    }
  } catch (error) {
    console.warn('[Mycelium Sync] Failed to emit event:', error);
  }
};
