import { NavLink, Link } from 'react-router-dom';

import styles from './assets/aside.module.css';

export default function DashboardAside({ isOpen, setIsOpen }) {
    const sidebarLinks = [
    {
        id: 'dashboard',
        label: 'Dashboard',
        path: '/dashboard',
        badgeCount: 0,
        icon: <svg style={{width: 16, minWidth: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"></path></svg>,
        exact: true,
    },
    {
        id: 'patients',
        label: 'Emergenze',
        path: '/dashboard/emergencies',
        badgeCount: 3,
        icon: <svg style={{width: 16, minWidth: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
    },
    {
        id: 'devices',
        label: 'Dispositivi',
        path: '/dashboard/devices',
        badgeCount: 1,
        icon: <svg style={{width: 16, minWidth: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M9 17H7A5 5 0 0 1 7 7h2"></path><path d="M15 7h2a5 5 0 1 1 0 10h-2"></path><line x1="8" x2="16" y1="12" y2="12"></line></svg>
    },
    {
        id: 'operators',
        label: 'Operatori',
        path: '/dashboard/associations',
        badgeCount: 0,
        icon: <svg style={{width: 16, minWidth: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M9 17H7A5 5 0 0 1 7 7h2"></path><path d="M15 7h2a5 5 0 1 1 0 10h-2"></path><line x1="8" x2="16" y1="12" y2="12"></line></svg>
    },
    {
        id: 'settings',
        label: 'Impostazioni',
        path: '/dashboard/settings',
        badgeCount: 0,
        icon: <svg style={{width: 16, minWidth: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915"></path><circle cx="12" cy="12" r="3"></circle></svg>
    },
    ];

    return (
        <>
            <div onClick={() => setIsOpen(false)} className={`${isOpen ? styles.open : `${styles.closed} no-clickable`} block w-full h-full ${styles.backdrop}`}></div>

            <aside className={`fixed top-0 flex flex-column h-full ${styles.asideNav} ${isOpen && styles.open}`} style={{width: 256, backgroundColor: "#FFF", borderRight: "solid 1px var(--border)"}}>
                <button onClick={() => setIsOpen(false)} className={`absolute ${styles.asideCross}`} style={{border: "none", backgroundColor: "transparent", right: 10, top: 10}}>
                    <svg style={{width: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M18 6 6 18"></path><path d="m6 6 12 12"></path></svg>
                </button>
                
                <nav className='flex flex-column align-center' style={{width: "100%", marginTop: 50}}>
                    {sidebarLinks.map((item) => (
                        <NavLink
                            key={item.id}
                            to={item.path}
                            end={item.exact}
                            onClick={() => setIsOpen(false)}
                            style={({ isActive }) => ({
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'flex-start',
                                padding: '0px 12px',
                                borderRadius: '6px',
                                height: 44,
                                textDecoration: 'none',
                                backgroundColor: isActive ? 'var(--primary-bg)' : 'transparent',
                                width: "80%",
                                gap: 10,
                            })}

                            className={({ isActive }) => `${isActive ? "text-primary" : "text-little-dark"} text-sm font-medium`}
                        >
                            
                            {item.icon}

                            <span style={{width: "100%"}}>{item.label}</span>

                            {item.badgeCount > 0 && (
                            <span style={{
                                    backgroundColor: '#ef4444',
                                    color: 'white',
                                    fontSize: '0.75rem',
                                    fontWeight: 'bold',
                                    padding: '2px 8px',
                                    borderRadius: '12px'
                            }}>
                                {item.badgeCount}
                            </span>
                            )}
                        </NavLink>
                    ))}
                </nav>

                <div className='flex flex-column absolute align-center' style={{bottom: 25, width: "100%", gap: 15}}>
                    <div className='flex align-center' style={{gap: 10, width: "80%", paddingTop: 16, borderTop: "solid 1px var(--border)"}}>
                        <div className='circle flex center' style={{backgroundColor: 'var(--fourth)', width: 36, minWidth: 36}}>
                            <span className='text-dark font-semi-bold text-xs'>GM</span>
                        </div>

                        <div className='flex flex-column'>
                            <p className='text-sm font-medium'>Gabriele Migliaro</p>
                            <p className='text-xs text-little-dark'>Operatore sanitario</p>
                        </div>
                    </div>

                    <Link to="/login" style={{width: "75%"}}>
                        <button className='flex align-center text-little-dark text-sm font-medium' style={{width: "100%", backgroundColor: "transparent", border: "none", gap: 7}}>
                            <svg style={{width: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m16 17 5-5-5-5"></path><path d="M21 12H9"></path><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path></svg>

                            Esci
                        </button>
                    </Link>
                </div>
            </aside>
        </>
    );
}