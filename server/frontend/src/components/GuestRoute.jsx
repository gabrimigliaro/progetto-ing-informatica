import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function GuestRoute({ redirectTo = "/dashboard" }) {
    const { user, loading } = useAuth();

    if (loading) {
        return <div>Caricamento...</div>;
    }

    if (user) {
        return <Navigate to={redirectTo} replace />;
    }

    return <Outlet />;
}