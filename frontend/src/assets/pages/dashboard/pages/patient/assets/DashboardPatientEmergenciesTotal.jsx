import styles from '../../../../../ui/cards/cards.module.css';

export default function DashboardPatientEmergenciesTotal({ patientData }) {
    return (
        <div className={`${styles.patientEmergenciesTotal} flex`} style={{gap: 15}}>
            <div className={`${styles.card}`}>
                <p className='text-sm text-little-dark'>Caduta rilevata</p>
                <p className='monospace text-xxl font-semi-bold'>1</p>
            </div>

            <div className={`${styles.card}`}>
                <p className='text-sm text-little-dark'>Battiti troppo alti</p>
                <p className='monospace text-xxl font-semi-bold'>0</p>
            </div>

            <div className={`${styles.card}`}>
                <p className='text-sm text-little-dark'>Battiti troppo bassi</p>
                <p className='monospace text-xxl font-semi-bold'>1</p>
            </div>

            <div className={`${styles.card}`}>
                <p className='text-sm text-little-dark'>Supporto richiesto</p>
                <p className='monospace text-xxl font-semi-bold'>1</p>
            </div>
        </div>
    );
}