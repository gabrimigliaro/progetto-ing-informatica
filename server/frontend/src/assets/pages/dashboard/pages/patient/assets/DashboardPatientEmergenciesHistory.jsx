import patientStyle from './css/dashboardPatient.module.css';
import styles from '../../../../../ui/lists/lists.module.css';

import { formatDateTime } from '../../../../../../utils/formatTime'

export default function DashboardPatientEmergenciesHistory({ patientEmergencies, getEmergencyTypeInfo }) {
    return (
        <div className={`${patientStyle.patientEmergenciesHistory} ${styles.list} flex`}>
            {patientEmergencies.map((emergency) => (
                <div key={emergency.id} className={`${styles.item}`}>
                    <div className={`${styles.details}`}>
                        <p className='text-sm font-medium'>{getEmergencyTypeInfo(emergency.type).label}</p>
                        <p className='text-sm text-little-dark'>{getEmergencyTypeInfo(emergency.type).label} dall'orologio</p>
                    </div>

                    <span className='monospace text-xs text-little-dark' style={{whiteSpace: "nowrap"}}>{formatDateTime(emergency.created_at)}</span>
                </div>
            ))}
        </div>
    );
}