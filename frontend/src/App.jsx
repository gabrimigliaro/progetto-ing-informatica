import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
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
            <Routes>
                <Route path="/dashboard" element={<Dashboard />} >
                    <Route index element={<DashboardOverview />} />

                    <Route path="associations" element={<DashboardAssociations />} />
                    <Route path="devices" element={<DashboardDevices />} />
                    <Route path="settings" element={<DashboardSettings />} />
                    <Route path="emergencies" element={<DashboardEmergencies />} />

                    <Route path="patient/:patientSlug" element={<DashboardPatient />} />
                </Route>

                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                <Route path="*" element={<NotFound />} />
            </Routes>
        </BrowserRouter>
    );
}