import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { getConnectedDevices, getPendingDevices, connectDevice, refuseDevice } from '../api/devicesService';
import { useWebSocket } from './WsContext';

const DeviceContext = createContext(null);

export const DeviceProvider = ({ children }) => {
    const [connectedList, setConnectedList] = useState([]);
    const [pendingList, setPendingList] = useState([]);
    const [loading, setLoading] = useState(true);

    const { subscribe } = useWebSocket();

    const fetchDevices = useCallback(async () => {
        setLoading(true);
        try {
            const [connected, pending] = await Promise.all([getConnectedDevices(), getPendingDevices()]);

            setConnectedList(connected);
            setPendingList(pending);
        } catch (error) {
            console.error("Errore durante il caricamento dei dispositivi:", error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchDevices();
    }, [fetchDevices]);

    useEffect(() => {
        const unsubPending = subscribe('NEW_DEVICE', (newDevice) => {
            setPendingList((prev) => {
                if (prev.some((d) => d.id === newDevice.id)) return prev;
                return [...prev, newDevice];
            });
        });

        return () => {
            unsubPending();
        };
    }, [subscribe]);

    const handleConnect = async (deviceId) => {
        const updatedDevice = await connectDevice(deviceId);
        
        setPendingList((prev) => prev.filter((d) => d.id !== deviceId));
        setConnectedList((prev) => [...prev, updatedDevice]);
        
        return updatedDevice;
    };

    const handleRefuse = async (deviceId) => {
        await refuseDevice(deviceId);
        
        setPendingList((prev) => prev.filter((d) => d.id !== deviceId));
    };

    return (
        <DeviceContext.Provider 
        value={{ 
            connectedList, 
            pendingList, 
            loading, 
            fetchDevices, 
            handleConnect, 
            handleRefuse 
        }}
        >
        {children}
        </DeviceContext.Provider>
    );
    };

    export const useDevices = () => {
    const context = useContext(DeviceContext);
    if (!context) {
        throw new Error("useDevices deve essere usato all'interno di un DeviceProvider");
    }
    return context;
};