import { useEffect } from 'react';
import { useParams, Link, useOutletContext } from 'react-router-dom';

import DashboardPatientOverview from './assets/DashboardPatientOverview';
import DashboardPatientEmergenciesTotal from './assets/DashboardPatientEmergenciesTotal';
import DashboardPatientEmergenciesHistory from './assets/DashboardPatientEmergenciesHistory';

const mockPatients = {
    'mario-rossi': {
        name: 'Mario Rossi',
        id: 'PZ-041',
        position: 'Stanza 1, primo piano',
        heartRate: 72,
        status: 'support',
        referente: 'Giulia Moretti',
    },
};

export default function DashboardPatient() {
    const { patientSlug } = useParams();
    const { setCustomHeader } = useOutletContext();

    const patient = mockPatients[patientSlug];

    useEffect(() => {
        if (patient) {
            setCustomHeader({
                title: patient.name,
                subtitle: "Scheda del paziente",
            });
        } else {
            setCustomHeader({
                title: 'Ospite non trovato',
                subtitle: 'Verificare la correttezza del link inserito',
            });
        }

        return () => setCustomHeader(null);
    }, [patient, setCustomHeader]);

    if (!patient) {
        return (
            <div>
                <h2>Paziente non trovato</h2>
                <Link to="/dashboard">← Torna alla lista ospiti</Link>
            </div>
        );
    }

    return (
        <>
            <Link to="/dashboard" className="text-sm text-little-dark flex align-center" style={{gap: 10, width: "fit-content"}}>
                <svg style={{width: 16, height: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="m12 19-7-7 7-7"></path><path d="M19 12H5"></path></svg>
                Torna alla dashboard
            </Link>

            <DashboardPatientOverview patientData={patient}></DashboardPatientOverview>

            <div className='flex flex-column' style={{marginTop: 35}}>
                <div className='flex flex-column' style={{gap: 3}}>
                    <h2 className='text-lg font-semi-bold'>Storico eventi</h2>
                    <p className='text-sm text-little-dark'>Cadute, battiti anomali e richieste di aiuto registrate.</p>
                </div>

                <DashboardPatientEmergenciesTotal patientData={patient}></DashboardPatientEmergenciesTotal>
                <DashboardPatientEmergenciesHistory patientData={patient}></DashboardPatientEmergenciesHistory>
            </div>
        </>
    );
}