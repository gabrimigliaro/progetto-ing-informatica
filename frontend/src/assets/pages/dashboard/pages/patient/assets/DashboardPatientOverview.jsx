import styles from '../../../../../ui/cards/cards.module.css';
import CardAlert from '../../../../../ui/cards-alerts/card-alerts';

export default function DashboardPatientOverview({ patientData }) {
    return (
        <div className={`${styles.patientOverviewCards} flex row-flex`} style={{gap: 15, marginTop: 25}}>
            <div className={`${styles.patientOverviewCard}`}>
                <div className={`${styles.top}`}>
                    <div className={`${styles.identification}`}>
                        <div className={`${styles.user} center`}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="5"></circle><path d="M20 21a8 8 0 0 0-16 0"></path></svg>
                        </div>

                        <div className={`${styles.name}`}>
                            <h2 className='font-semi-bold text-lg'>{patientData.name}</h2>
                            <p className='monospace text-xs text-little-dark'>{patientData.id}</p>
                        </div>
                    </div>

                    <CardAlert type={patientData.status}></CardAlert>
                </div>

                <div className={`${styles.bottom}`}>
                    <div className={`${styles.info}`}>
                        <dt className='text-xs text-little-dark'>Referente</dt>
                        <dd className='text-sm font-medium'>{patientData.referente}</dd>
                    </div>

                    <div className={`${styles.info}`}>
                        <dt className='text-xs text-little-dark'>Posizione</dt>
                        <dd className='text-sm font-medium flex align-center' style={{gap: 5}}>
                            <svg style={{width: 12, height: 12}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"></path><circle cx="12" cy="10" r="3"></circle></svg>
                            
                            {patientData.position}
                        </dd>
                    </div>
                </div>
            </div>

            <div className={`${styles.patientHeartCard} ${styles.red}`}>
                <p className='text-sm text-little-dark'>Battiti attuali</p>

                <div className={`${styles.heart}`}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"></path></svg>
                
                    <strong className='monospace' style={{fontSize: "2.25rem"}}>{patientData.heartRate} <span className='uppercase font-default text-xs text-little-dark'>bpm</span></strong>
                </div>

                <p className='text-xs text-little-dark'>Segnale ricevuto adesso dall’orologio connesso.</p>
            </div>
        </div>
    );
}