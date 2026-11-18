import { Link } from 'react-router-dom';

import { formatDateTime } from '../../../../../../utils/formatTime'

import styles from '../../../../../ui/lists/lists.module.css';

export default function DashboardEmergenciesResolved({ resolvedEmergenciesList, getEmergencyTypeInfo }) {
    return (
        <div style={{width: "100%", paddingBottom: 35}}>
            <h2 className='text-lg font-semi-bold'>Emergenze risolte</h2>

            <div className={`${styles.list}`} style={{marginTop: 15}}>
                {resolvedEmergenciesList.map((emergency) => (
                    <div key={emergency.id} className={`${styles.item}`}>
                        <div className={`${styles.details}`}>
                            <p className='text-sm font-medium'>{getEmergencyTypeInfo(emergency.type).label} · <Link to={`/dashboard/patient/${emergency.patient.id}`} className='text-primary hov-underlined'>{emergency.patient.name} {emergency.patient.surname}</Link></p>
                            <p className='text-sm text-little-dark'>Stanza 1, primo piano</p>
                        </div>

                        <span className='flex text-xs font-medium text-green' style={{whiteSpace: "nowrap", alignItems: "center", gap: 5}}>
                            <svg style={{width: 16, height: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"></path></svg>
                            Da {emergency.resolver.name} {emergency.resolver.surname} il {formatDateTime(emergency.resolved_at)}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}