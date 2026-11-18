import { Link } from 'react-router-dom';

import styles from '../../../../../ui/cards/cards.module.css';

export default function DashboardEmergenciesToRisolve({ activeEmergenciesList, getEmergencyTypeInfo, resolveEmergency }) {
    return (
        <div className='flex flex-column' style={{gap: 10, paddingBottom: 35}}>
            {activeEmergenciesList.map((emergency) => (
                <div key={emergency.id} className={`${styles.emergenciesCard} ${getEmergencyTypeInfo(emergency.type).class}`}>
                    <div className={`${styles.left} flex`} style={{alignItems: "center", gap: 15}}>
                        <span className={`${styles.icon} flex center`}>
                            {getEmergencyTypeInfo(emergency.type).icon}
                        </span>

                        <div className='flex flex-column'>
                            <p className='font-semi-bold'>{getEmergencyTypeInfo(emergency.type).label}</p>
                            <p className='text-sm text-little-dark' style={{marginTop: 2}}><Link to={`/dashboard/patient/${emergency.patient.id}`} className='font-medium hov-underlined' style={{color: "var(--primary)"}}>{emergency.patient.name} {emergency.patient.surname}</Link> <span className='monospace'>• PZ-{emergency.patient.id}</span></p>
                            <p className='flex flex-row text-sm text-little-dark' style={{gap: 5, marginTop: 5}}>
                                <svg style={{width: 16, height: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"></path><circle cx="12" cy="10" r="3"></circle></svg>
                                Stanza 4, primo piano
                            </p>
                        </div>
                    </div>

                    <div className={`${styles.right} flex flex-row`} style={{gap: 15}}>
                        <p className='monospace text-xxl font-semi-bold' style={{whiteSpace: "nowrap",}}>{emergency.bpm ?? "--"} <span className='uppercase default-font text-xs text-little-dark' style={{marginLeft: -9}}>bpm</span></p>
                        <button onClick={() => resolveEmergency(emergency.id)} className='primary-btn' style={{gap: 10, whiteSpace: "nowrap", boxShadow: "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.1) 0px 1px 3px 0px, rgba(0, 0, 0, 0.1) 0px 1px 2px -1px"}}>
                            <svg style={{width: 16, height: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"></path></svg>
                            Segna come risolta
                        </button>
                    </div>
                </div>
            ))}
        </div>
    );
}