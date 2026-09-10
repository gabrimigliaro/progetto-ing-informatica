import { useState } from 'react';
import { Outlet } from 'react-router-dom';

import DashboardHeader from './assets/header/Header';
import DashboardAside from './assets/aside/Aside';

import styles from './assets/general/dashboard.module.css';

export default function Dashboard() {
    const [isAsideOpen, setIsAsideOpen] = useState(false);

    return (
        <main className='relative'>
            <DashboardHeader setIsOpen={setIsAsideOpen}></DashboardHeader>
            <DashboardAside isOpen={isAsideOpen} setIsOpen={setIsAsideOpen}></DashboardAside>

            <div className={`${styles.wrapper}`}>
                <Outlet />
            </div>
        </main>
    );
}