import { useState, useEffect, useMemo } from 'react';
import { useParams, Link, useOutletContext } from 'react-router-dom';

import { getPatientById, getActiveAssociations } from '../../../../../api/patientsService'
import { useEmergencies, EMERGENCY_TYPES } from '../../../../../context/EmergencyContext';

import { useWebSocket } from '../../../../../context/WsContext';

import { WS_EVENTS_INGOING } from '../../../../../constants/wsEvents';

import DashboardPatientOverview from './assets/DashboardPatientOverview';
import DashboardPatientEmergenciesTotal from './assets/DashboardPatientEmergenciesTotal';
import DashboardPatientEmergenciesHistory from './assets/DashboardPatientEmergenciesHistory';

export default function DashboardPatient() {
    const TELEMETRY_STORAGE_KEY = 'patients_telemetry';

    const { patientSlug } = useParams();
    const { setCustomHeader } = useOutletContext();
    const { activeEmergencies, emergenciesList, getEmergencyTypeInfo } = useEmergencies();

    const { subscribe } = useWebSocket();

    const [patient, setPatient] = useState(null);
    const [bpm, setBpm] = useState("--")

    const patientId = useMemo(() => {
        if (!patientSlug) return null;
        const parts = patientSlug.split('-');
        return Number(parts[parts.length - 1]);
    }, [patientSlug]);

    const patientEmergencies = useMemo(() => {
        return emergenciesList.filter(
            (emergency) => emergency.p_id === Number(patientId)
        );
    }, [emergenciesList, patientId]);

    useEffect(() => {
        if (!patientId || isNaN(patientId)) return;

        const fetchPatientDetails = async () => {
            try {
                const [patientData, associations] = await Promise.all([getPatientById(patientId), getActiveAssociations()]);

                const activeDevice = associations.find((a) => a.patient.id === patientId);
                patientData.device = activeDevice?.device || null;

                setPatient(patientData);

                const cachedTelemetry = JSON.parse(localStorage.getItem(TELEMETRY_STORAGE_KEY) || '{}');
                setBpm(cachedTelemetry[patientData.id]?.bpm ?? null);
            } catch (err) {}
        };

        fetchPatientDetails();
    }, [patientId]);

    useEffect(() => {
        if (patient) {
            setCustomHeader({title: `${patient.name} ${patient.surname}`, subtitle: "Scheda del paziente"});
        } else {
            setCustomHeader({title: 'Ospite non trovato', subtitle: 'Verificare la correttezza del link inserito'});
        }

        return () => setCustomHeader(null);
    }, [patient, setCustomHeader]);

    useEffect(() => {
        const unsubDeviceUpdate = subscribe(WS_EVENTS_INGOING.DEVICE_UPDATE, (data) => {
            if (!data.patient) return;

            const incomingPatientId = data.patient.id;
            const telemetry = {
                bpm: Number(data.bpm),
                battery: Number(data.battery),
                steps: Number(data.steps),
                emergency: data.emergency === '1' || data.emergency === 1,
                fall: data.fall === '1' || data.fall === 1,
                updatedAt: new Date().toISOString(),
            };

            try {
                const cached = JSON.parse(localStorage.getItem(TELEMETRY_STORAGE_KEY) || '{}');
                cached[incomingPatientId] = telemetry;
                localStorage.setItem(TELEMETRY_STORAGE_KEY, JSON.stringify(cached));
            } catch (err) {
                console.error('Errore salvataggio telemetria su localStorage:', err);
            }

            setBpm(telemetry.bpm);
        });

        return () => {
            unsubDeviceUpdate();
        };
    }, [subscribe]);

    const getPatientEmergency = (patientId) => {
        const emergency = activeEmergencies.find((emergency) => emergency.p_id === Number(patientId));

        if (emergency != null) return emergency
        else return -1
    }

    const filterEmergenciesByType = (emergenciesList, typeId) => {
        return emergenciesList.filter((emergency) => emergency.type === Number(typeId));
    };

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

            <DashboardPatientOverview patientData={patient} getEmergencyTypeInfo={getEmergencyTypeInfo} getPatientEmergency={getPatientEmergency} bpm={bpm}></DashboardPatientOverview>

            <div className='flex flex-column' style={{marginTop: 35}}>
                <div className='flex flex-column' style={{gap: 3}}>
                    <h2 className='text-lg font-semi-bold'>Storico eventi</h2>
                    <p className='text-sm text-little-dark'>Cadute, battiti anomali e richieste di aiuto registrate.</p>
                </div>

                <DashboardPatientEmergenciesTotal patientEmergencies={patientEmergencies} filterEmergenciesByType={filterEmergenciesByType}></DashboardPatientEmergenciesTotal>
                <DashboardPatientEmergenciesHistory patientData={patient} patientEmergencies={patientEmergencies} getEmergencyTypeInfo={getEmergencyTypeInfo}></DashboardPatientEmergenciesHistory>
            </div>
        </>
    );
}