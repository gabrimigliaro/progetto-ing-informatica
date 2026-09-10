import { useState } from 'react';
import { Outlet } from 'react-router-dom';

import DashboardHeader from './assets/header/Header';
import DashboardAside from './assets/aside/Aside';

export default function Dashboard() {
    const [isAsideOpen, setIsAsideOpen] = useState(false);

    return (
        <main>
            <DashboardHeader setIsOpen={setIsAsideOpen}></DashboardHeader>
            <DashboardAside isOpen={isAsideOpen} setIsOpen={setIsAsideOpen}></DashboardAside>
            <Outlet />
        </main>
    );
}