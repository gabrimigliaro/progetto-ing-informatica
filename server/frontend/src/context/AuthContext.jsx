import { createContext, useContext, useState, useEffect } from 'react';
import { loginUser, logoutUser, getCurrentUser, deleteCurrentUser } from '../api/authService';
import api from '../api/axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const userData = await getCurrentUser();
                setUser(userData);
            } catch (error) {
                setUser(null);
            } finally {
                setLoading(false);
            }
        };
        checkAuth();
    }, []);

    const login = async (email, password) => {
        await loginUser({ email, password });
        const userData = await getCurrentUser();

        setUser(userData);
        return userData;
    };

    const logout = async () => {
        try {
            if ('serviceWorker' in navigator) {
                const reg = await navigator.serviceWorker.getRegistration('/sw.js');
                const sub = await reg?.pushManager.getSubscription();
                if (sub) {
                    await api.post('/push/unsubscribe', { endpoint: sub.endpoint });
                    await sub.unsubscribe();
                }
            }
        } catch (err) {
            console.warn('Pulizia push durante logout fallita:', err);
        } 

        try {
            await logoutUser();
        } finally {
            setUser(null);
        }
    };

    const deleteUser = async () => {
        try {
            await deleteCurrentUser();
        } finally {
            setUser(null);
        }
    };

    return (
        <AuthContext.Provider value={{ user, login, logout, deleteUser, loading }}>
            {!loading && children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth deve essere utilizzato all\'interno di un AuthProvider');
    }
    return context;
};