import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { DeviceProvider } from './context/DeviceContext';
import { EmergencyProvider } from './context/EmergencyContext.jsx';
import { WebSocketProvider } from './context/WsContext.jsx';

import GuestRoute from './components/GuestRoute';
import ProtectedRoute from './components/ProtectedRoute';

import Dashboard from './assets/pages/dashboard/Dashboard';
import DashboardOverview from './assets/pages/dashboard/pages/overview/DashboardOverview.jsx';
import DashboardAssociations from './assets/pages/dashboard/pages/associations/DashboardAssociations';
import DashboardDevices from './assets/pages/dashboard/pages/devices/DashboardDevices';
import DashboardSettings from './assets/pages/dashboard/pages/settings/DashboardSettings';
import DashboardEmergencies from './assets/pages/dashboard/pages/emergencies/DashboardEmergencies.jsx';
import DashboardPatient from './assets/pages/dashboard/pages/patient/DashboardPatient.jsx';

import Login from './assets/pages/login/Login';
import Register from './assets/pages/register/Register';

import NotFound from './assets/pages/errors/404/404';

export default function App() {
    return (
        <BrowserRouter>
            <AuthProvider>
                <WebSocketProvider>
                    <DeviceProvider>
                        <EmergencyProvider>
                            <Routes>
                                <Route path="/" element={<Navigate to="/dashboard" replace />} />

                                <Route element={<ProtectedRoute />}>
                                    <Route path="/dashboard" element={<Dashboard />} >
                                        <Route index element={<DashboardOverview />} />

                                        <Route path="associations" element={<DashboardAssociations />} />
                                        <Route path="devices" element={<DashboardDevices />} />
                                        <Route path="settings" element={<DashboardSettings />} />
                                        <Route path="emergencies" element={<DashboardEmergencies />} />

                                        <Route path="patient/:patientSlug" element={<DashboardPatient />} />
                                    </Route>
                                </Route>

                                <Route element={<GuestRoute />}>
                                    <Route path="/login" element={<Login />} />
                                    <Route path="/register" element={<Register />} />
                                </Route>

                                <Route path="*" element={<NotFound />} />
                            </Routes>
                        </EmergencyProvider>
                    </DeviceProvider>
                </WebSocketProvider>
            </AuthProvider>
        </BrowserRouter>
    );
}