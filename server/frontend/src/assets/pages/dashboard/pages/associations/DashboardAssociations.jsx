import { useEffect, useState, useCallback, useMemo } from 'react';
import { addPatient, getAllPatients, createAssociation, getActiveAssociations } from '../../../../../api/patientsService';
import { useDevices } from '../../../../../context/DeviceContext';

import cards from '../../../../ui/cards/cards.module.css'
import Alert from '../../../../ui/alerts/alerts';

import DashboardAssociationsPatient from "./assets/DashboardAssociationsPatient";
import DashboardAssociationsPatientDevice from "./assets/DashboardAssociationsPatientDevice";

export default function DashboardAssociations() {
    const [alert, setAlert] = useState(null);
    const [patientsList, setPatientList] = useState([])
    const [associationsList, setAssociationsList] = useState([])

    const { connectedList } = useDevices();

    const handleAddPatient = async (patientData) => {
        try {
            const patientAdded = await addPatient(patientData);

            setPatientList((prev) => [...prev, patientAdded]);

            setAlert({ type: 'success', text: `Paziente ${patientData.name} ${patientData.surname} creato con successo.` });
        } catch (err) {
            const errorMsg = err.response?.data?.detail || err.message;
            setAlert({ type: 'error', text: `Non è stato possibile creare il paziente: ${errorMsg}` });
        }

        setTimeout(function() {
			setAlert(null)
		}, 5000)
    };

    const handleCreateAssociation = async (associationData) => {
        try {
            const associationAdded = await createAssociation(associationData)

            setAssociationsList((prev) => [...prev, associationAdded]);

            setAlert({ type: 'success', text: 'Associazione creata con successo.' });
        } catch (err) {
            const errorMsg = err.response?.data?.detail || err.message;
            setAlert({ type: 'error', text: `Non è stato possibile creare la associazione: ${errorMsg}` });
        }

        setTimeout(function() {
			setAlert(null)
		}, 5000)
    };

    const availablePatients = useMemo(() => {
        const busyPatientIds = new Set(associationsList.map((assoc) => assoc.p_id));
        return patientsList.filter((patient) => !busyPatientIds.has(patient.id));
    }, [patientsList, associationsList]);

    const availableDevices = useMemo(() => {
        const busyDeviceIds = new Set(associationsList.map((assoc) => assoc.d_id));
        return connectedList.filter((device) => !busyDeviceIds.has(device.id));
    }, [connectedList, associationsList]);

    const fetchPatients = useCallback(async () => {
        try {
            const [patients, associations] = await Promise.all([
                getAllPatients(), 
                getActiveAssociations()
            ]);

            setPatientList(patients);
            setAssociationsList(associations);
        } catch (error) {
            console.error("Errore durante il caricamento di pazienti e associazioni:", error);
        }
    }, []);

    useEffect(() => {
        fetchPatients()
    }, [fetchPatients])

    return (
        <>
            <div className={`${cards.cards} ${cards.associationsCards}`} style={{paddingBottom: 35}}>
                <DashboardAssociationsPatient addPatient={handleAddPatient} />
                <DashboardAssociationsPatientDevice devicesList={availableDevices} patientsList={availablePatients} associationsList={associationsList} createAssociation={handleCreateAssociation} />
            </div>

             {alert && <Alert type={alert.type} text={alert.text} />}
        </>
    );
}