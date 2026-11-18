import styles from '../../../../../ui/cards/cards.module.css';

export default function DashboardOverviewTotals({ patientsList, activeEmergencies }) {
    return (
        <div className={`${styles.cards}`}>
            <div className={`${styles.card}`}>
                <p className='text-sm text-little-dark'>Pazienti monitorati</p>
                <span className='monospace text-xxl font-semi-bold'>{patientsList.length}</span>
            </div>

            <div className={`${styles.card} ${styles.red}`}>
                <p className='text-sm text-little-dark'>Emergenze attive</p>
                <span className={'monospace text-xxl font-semi-bold'} id='num'>{activeEmergencies.length}</span>
            </div>
        </div>
    );
}