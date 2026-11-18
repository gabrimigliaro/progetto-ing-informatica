import { useState, useEffect, useCallback } from 'react';

import { useDevices } from '../../../../../context/DeviceContext';
import { useWebSocket } from '../../../../../context/WsContext';

import { getActiveAssociations } from '../../../../../api/patientsService';
import { WS_EVENTS_OUTGOING } from '../../../../../constants/wsEvents';

import DashboardDevicesResearch from './assets/DashboardDevicesResearch';
import DashboardDevicesActive from './assets/DashboardDevicesActive';

import Alert from '../../../../ui/alerts/alerts';

export default function DashboardDevices() {
    const { connectedList, pendingList, handleConnect, handleRefuse } = useDevices();
    const [associationsList, setAssociationsList] = useState([])

    const { isConnected, sendMessage } = useWebSocket();

    const [alert, setAlert] = useState(null);

    const fetchPatients = useCallback(async () => {
        try {
            const associations = await getActiveAssociations()

            setAssociationsList(associations);
        } catch (error) {
            console.error("Errore durante il caricamento di pazienti e associazioni:", error);
        }
    }, []);

    useEffect(() => {
        fetchPatients()
    }, [fetchPatients])

    const getPatientNameByDeviceId = (associationsList, deviceId) => {
        const association = associationsList.find((item) => item.d_id === deviceId && item.is_active);

        if (!association || !association.patient) {
            return "Nessuno";
        }

        return `${association.patient.name} ${association.patient.surname}`;
    };

    const onConnect = async (deviceId, deviceMacAddress) => {
        try {
            await handleConnect(deviceId);

            sendMessage({
                event: WS_EVENTS_OUTGOING.DEVICE_CONNECTED,
                payload: {
                    device_id: deviceId,
                    mac_address: deviceMacAddress
                }
            });

            setAlert({ type: 'success', text: 'Dispositivo connesso con successo.' });
        } catch (err) {
			setAlert({ type: 'error', text: 'Errore nella connessione del dispositivo.'});
		}
        
        setTimeout(function() {
			setAlert(null)
		}, 5000)
    };

    const onRefuse = async (deviceId) => {
        try {
            await handleRefuse(deviceId);
            setAlert({ type: 'success', text: 'Dispositivo rifiutato con successo.' });
        } catch (err) {
			setAlert({ type: 'error', text: 'Errore nel rifiuto del dispositivo.'});
		}
        
        setTimeout(function() {
			setAlert(null)
		}, 5000)
    };

    return (
        <>
            <DashboardDevicesResearch pendingList={pendingList} onConnect={onConnect} onRefuse={onRefuse} isWSConnected={isConnected}></DashboardDevicesResearch>

            {connectedList.length > 0 &&
                <DashboardDevicesActive connectedList={connectedList} associationsList={associationsList} getPatientNameByDeviceId={getPatientNameByDeviceId}></DashboardDevicesActive>
            }
        
            {alert && <Alert type={alert.type} text={alert.text} />}
        </>
    );
}