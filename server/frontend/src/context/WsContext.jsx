import { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from './AuthContext';

const WebSocketContext = createContext(null);

const WS_URL = 'wss://...';

export const WebSocketProvider = ({ children }) => {
    const { user } = useAuth();
    const [isConnected, setIsConnected] = useState(false);

    const wsRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);
    const listenersRef = useRef(new Map());

    useEffect(() => {
        if (!user) {
            if (wsRef.current) wsRef.current.close();
            return;
        }

        const connect = () => {
            const ws = new WebSocket(WS_URL);
            wsRef.current = ws;

            ws.onopen = () => {
                //console.log('WebSocket connesso');
                setIsConnected(true);
            };

            ws.onmessage = (event) => {
                //console.log("New messagge from websocket! ", event.data);
                try {
                    const message = JSON.parse(event.data);
                    const { event: eventName, payload } = message;

                    if (eventName && listenersRef.current.has(eventName)) {
                        listenersRef.current.get(eventName).forEach((callback) => {
                            callback(payload);
                        });
                    }
                } catch (err) {
                    console.error('Errore parsing messaggio WebSocket:', err);
                }
            };

            ws.onclose = () => {
                console.warn('WebSocket disconnesso. Riconnessione tra 3 secondi...');
                setIsConnected(false);
                reconnectTimeoutRef.current = setTimeout(connect, 3000);
            };

            ws.onerror = (error) => {
                console.error('Errore WebSocket:', error);
                ws.close();
            };
        };

        connect();

        return () => {
            clearTimeout(reconnectTimeoutRef.current);
            if (wsRef.current) {
                wsRef.current.onclose = null;
                wsRef.current.close();
            }
        };
    }, [user]);

    const subscribe = useCallback((eventName, callback) => {
        if (!listenersRef.current.has(eventName)) {
            listenersRef.current.set(eventName, new Set());
        }

        listenersRef.current.get(eventName).add(callback);

        return () => {
            const eventListeners = listenersRef.current.get(eventName);
            if (eventListeners) {
                eventListeners.delete(callback);
                if (eventListeners.size === 0) listenersRef.current.delete(eventName);
            }
        };
    }, []);

    const sendMessage = useCallback((data) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(data));
            return true;
        }
        
        console.warn('WebSocket non connesso. Impossibile inviare:', data);
        return false;
    }, []);

    return (
        <WebSocketContext.Provider value={{ isConnected, subscribe, sendMessage }}>
        {children}
        </WebSocketContext.Provider>
    );
    };

    export const useWebSocket = () => {
        const context = useContext(WebSocketContext);
        if (!context) {
            throw new Error("useWebSocket deve essere usato all'interno di un WebSocketProvider");
        }
    return context;
};