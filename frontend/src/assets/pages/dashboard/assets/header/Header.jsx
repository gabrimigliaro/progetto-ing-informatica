import { useLocation } from 'react-router-dom';

import styles from './assets/header.module.css';

export default function DashboardHeader({ setIsOpen }) {
    const location = useLocation();

    const getPageTitle = (path) => {
        switch (path) {
        case '/':
        case '/dashboard':
            return {title: 'Dashboard', subtitle: 'Panoramica dei pazienti assegnati'};
        case '/dashboard/emergencies':
            return {title: 'Emergenze attuali', subtitle: 'Segnalazioni da gestire in tempo reale'};
        case '/dashboard/devices':
            return {title: 'Dispositivi', subtitle: 'Richieste di collegamento alla rete'};
        case '/dashboard/associations':
            return {title: 'Operatori e pazienti', subtitle: 'Gestisci le assegnazioni di monitoraggio'};
        case '/dashboard/settings':
            return {title: 'Impostazioni', subtitle: 'Sicurezza e gestione dell’account'};
        default:
            return 'Pagina non trovata';
        }
    };

    return (
        <header className={`${styles.dashboardHeader} flex flex-row align-center`}>
            <button className={`${styles.dashboardHeaderOpenAsideButton}`} onClick={() => setIsOpen(true)}>
                <svg style={{width: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M4 5h16"></path><path d="M4 12h16"></path><path d="M4 19h16"></path></svg>
            </button>

            <div className='flex flex-column' style={{marginLeft: 32, gap: 3}}>
                <h1 className='text-dark text-xl font-semi-bold'>{getPageTitle(location.pathname).title}</h1>
                <p className='text-little-dark text-sm'>{getPageTitle(location.pathname).subtitle}</p>
            </div>

            <div className={`${styles.system} flex flex-row align-center absolute`} style={{gap: 5, right: 32}}>
                <div className="circle" style={{backgroundColor: "oklch(0.596 0.145 163.225006)", width: 8, minWidth: 8, height: 8}}></div>
                <span className='text-little-dark text-xs'>Sistema operativo</span>
            </div>
        </header>
    );
}