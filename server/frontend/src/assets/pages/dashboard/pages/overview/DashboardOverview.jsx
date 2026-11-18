import { useEffect, useState } from 'react';

import { useEmergencies } from '../../../../../context/EmergencyContext';
import { getAllPatients } from '../../../../../api/patientsService';
import { useWebSocket } from '../../../../../context/WsContext';

import { WS_EVENTS_INGOING } from '../../../../../constants/wsEvents';

import patients from './assets/css/dashboardOverview.module.css';

import DashboardOverviewTotals from "./assets/DashboardOverviewTotals";
import DashboardOverviewPatients from "./assets/DashboardOverviewPatients";

export default function DashboardOverview() {
    const TELEMETRY_STORAGE_KEY = 'patients_telemetry';

    const [patientsList, setPatientsList] = useState([]);
    const { activeEmergencies, getEmergencyTypeInfo } = useEmergencies()

    const { subscribe } = useWebSocket();

    const EMERGENCY_CARD_CLASS = [
        {
            id: -1,
            class: patients.blue
        },
        {
            id: 1,
            class: patients.red
        },
        {
            id: 2,
            class: patients.red
        },
        {
            id: 3,
            class: patients.red
        },
        {
            id: 4,
            class: patients.yellow
        },
    ];

    useEffect(() => {
        const fetchPatients = async () => {
            try {
                const data = await getAllPatients();

                let cachedTelemetry = {};
                try {
                    cachedTelemetry = JSON.parse(localStorage.getItem(TELEMETRY_STORAGE_KEY) || '{}');
                } catch (parseError) {
                    console.error("Errore nella lettura del localStorage:", parseError);
                }

                const mergedPatients = data.map((patient) => ({
                    ...patient,
                    ...(cachedTelemetry[patient.id] || {}),
                }));

                setPatientsList(mergedPatients);
            } catch (error) {
                console.error("Errore nel recupero dei pazienti:", error);
            }
        };

        fetchPatients();
    }, []);

    useEffect(() => {
        const unsubDeviceUpdate = subscribe(WS_EVENTS_INGOING.DEVICE_UPDATE, (data) => {
            const patientId = data.patient.id;
            const telemetry = {
                bpm: Number(data.bpm),
                battery: Number(data.battery),
                steps: Number(data.steps),
                emergency: data.emergency === '1' || data.emergency === 1,
                fall: data.fall === '1' || data.fall === 1,
                updatedAt: new Date().toISOString(),
            };

            setPatientsList((prevList) =>
                prevList.map((patient) =>
                    patient.id === patientId
                        ? { ...patient, ...telemetry }
                        : patient
                )
            );

            try {
                const cached = JSON.parse(localStorage.getItem(TELEMETRY_STORAGE_KEY) || '{}');
                cached[patientId] = telemetry;
                localStorage.setItem(TELEMETRY_STORAGE_KEY, JSON.stringify(cached));
            } catch (err) {
                console.error('Errore salvataggio telemetria su localStorage:', err);
            }
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

    const getEmergencyTypeClass = (typeId) => {
        return (
            EMERGENCY_CARD_CLASS.find((item) => item.id === Number(typeId)) || {
                id: typeId,
                class: patients.blue
            }
        );
    };

    return (
        <>
            <DashboardOverviewTotals patientsList={patientsList} activeEmergencies={activeEmergencies}></DashboardOverviewTotals>
            <DashboardOverviewPatients patientsList={patientsList} getPatientEmergency={getPatientEmergency} getEmergencyTypeInfo={getEmergencyTypeInfo} getEmergencyTypeClass={getEmergencyTypeClass}></DashboardOverviewPatients>
        </>
    );
}