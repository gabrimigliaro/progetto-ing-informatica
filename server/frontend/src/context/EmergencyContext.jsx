import { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';
import { useAuth } from './AuthContext';
import { useWebSocket } from './WsContext';
import { getAllEmergencies, resolveEmergency } from '../api/emergenciesService';

import { WS_EVENTS_INGOING } from '../constants/wsEvents';

import CardAlert from '../assets/ui/cards-alerts/card-alerts';
import styles from '../assets/ui/cards/cards.module.css';

const EmergencyContext = createContext(null);

export const EMERGENCY_TYPES = [
        {
            id: 1,
            label: 'Caduta rilevata',
            class: styles.red,
            icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>,
            badge: <CardAlert type={"fall"} />
        },
        {
            id: 2,
            label: 'Battiti troppo alti',
            class: styles.red,
            icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>,
            badge: <CardAlert type={"heartBeatH"} />
        },
        {
            id: 3,
            label: 'Battiti troppo bassi',
            class: styles.red,
            icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>,
            badge: <CardAlert type={"heartBeatL"} />
        },
        {
            id: 4,
            label: 'Supporto richiesto',
            class: styles.yellow,
            icon: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><path d="m4.93 4.93 4.24 4.24"></path><path d="m14.83 9.17 4.24-4.24"></path><path d="m14.83 14.83 4.24 4.24"></path><path d="m9.17 14.83-4.24 4.24"></path><circle cx="12" cy="12" r="4"></circle></svg>,
            badge: <CardAlert type={"support"} />
        },
];

export const EmergencyProvider = ({ children }) => {
    const { user } = useAuth();
    const { subscribe } = useWebSocket();
    const [emergenciesList, setEmergenciesList] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchEmergencies = useCallback(async (silent = false) => {
        if (!silent) setLoading(true);

        try {
            const data = await getAllEmergencies();
            setEmergenciesList(data);
        } catch (error) {
            console.error("Errore durante il caricamento delle emergenze:", error);
        } finally {
            if (!silent) setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (!user) {
            setEmergenciesList([]);
            return;
        }

        fetchEmergencies();
    }, [user, fetchEmergencies]);

    useEffect(() => {
        const unsubscribe = subscribe(WS_EVENTS_INGOING.NEW_EMERGENCY, (newEmergency) => {
            setEmergenciesList((prev) => {
                if (prev.some((e) => e.id === newEmergency.id)) return prev;
                return [newEmergency, ...prev];
            });
        });

        return unsubscribe;
    }, [subscribe]);

    const activeEmergencies = useMemo(
        () => emergenciesList.filter((e) => !e.resolved),
        [emergenciesList]
    );

    const resolvedEmergencies = useMemo(
        () => emergenciesList.filter((e) => e.resolved),
        [emergenciesList]
    );

    const unresolvedCount = activeEmergencies.length;

    const handleResolveEmergency = async (emergencyId) => {
        const updatedEmergency = await resolveEmergency(emergencyId);

        setEmergenciesList((prev) =>
        prev.map((item) => (item.id === emergencyId ? updatedEmergency : item))
        );

        return updatedEmergency;
    };

    const getEmergencyTypeInfo = (typeId) => {
        return (
            EMERGENCY_TYPES.find((item) => item.id === Number(typeId)) || {
                id: typeId,
                label: 'Stable',
                class: 'low',
                badge: <CardAlert type={"stable"} />
            }
        );
    };

    return (
        <EmergencyContext.Provider value={{emergenciesList, activeEmergencies, resolvedEmergencies, unresolvedCount, loading, fetchEmergencies, handleResolveEmergency, getEmergencyTypeInfo}}>
            {children}
        </EmergencyContext.Provider>
    );
};

export const useEmergencies = () => {
    const context = useContext(EmergencyContext);
    
    if (!context) {
        throw new Error("useEmergencies deve essere usato all'interno di un EmergencyProvider");
    }
    return context;
};