import patientStyle from './css/dashboardPatient.module.css';
import styles from '../../../../../ui/lists/lists.module.css';

export default function DashboardPatientEmergenciesHistory({ patientData }) {
    return (
        <div className={`${patientStyle.patientEmergenciesHistory} ${styles.list} flex`}>
            <div className={`${styles.item}`}>
                <div className={`${styles.details}`}>
                    <p className='text-sm font-medium'>Caduta rilevata</p>
                    <p className='text-sm text-little-dark'>Caduta rilevata dall'orologio in corridoio</p>
                </div>

                <span className='monospace text-xs text-little-dark' style={{whiteSpace: "nowrap"}}>09/09/2026 13:02</span>
            </div>

            <div className={`${styles.item}`}>
                <div className={`${styles.details}`}>
                    <p className='text-sm font-medium'>Caduta rilevata</p>
                    <p className='text-sm text-little-dark'>Caduta rilevata dall'orologio in corridoioCaduta rilevata dall'orologio in corridoioCaduta rilevata dall'orologio in corridoioCaduta rilevata dall'orologio in corridoioCaduta rilevata dall'orologio in corridoioCaduta rilevata dall'orologio in corridoioCaduta rilevata dall'orologio in corridoioCaduta rilevata dall'orologio in corridoioCaduta rilevata dall'orologio in corridoio</p>
                </div>

                <span className='monospace text-xs text-little-dark' style={{whiteSpace: "nowrap"}}>09/09/2026 13:02</span>
            </div>

            <div className={`${styles.item}`}>
                <div className={`${styles.details}`}>
                    <p className='text-sm font-medium'>Caduta rilevata</p>
                    <p className='text-sm text-little-dark'>Caduta rilevata dall'orologio in corridoio</p>
                </div>

                <span className='monospace text-xs text-little-dark' style={{whiteSpace: "nowrap"}}>09/09/2026 13:02</span>
            </div>
        </div>
    );
}