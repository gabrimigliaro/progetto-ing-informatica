import styles from '../../../../../ui/cards/cards.module.css';

export default function DashboardOverviewTotals() {
    return (
        <div className={`${styles.cards}`}>
            <div className={`${styles.card}`}>
                <p className='text-sm text-little-dark'>Pazienti monitorati</p>
                <span className='monospace text-xxl font-semi-bold'>6</span>
            </div>

            <div className={`${styles.card} ${styles.red}`}>
                <p className='text-sm text-little-dark'>Emergenze attive</p>
                <span className={'monospace text-xxl font-semi-bold'} id='num'>3</span>
            </div>
        </div>
    );
}