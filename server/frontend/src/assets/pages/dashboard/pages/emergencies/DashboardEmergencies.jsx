import { useState } from 'react';
import { useEmergencies } from '../../../../../context/EmergencyContext';

import Alert from '../../../../ui/alerts/alerts';

import DashboardEmergenciesToRisolve from "./assets/DashboardEmergenciesToRisolve";
import DashboardEmergenciesResolved from "./assets/DashboardEmergenciesResolved";

export default function DashboardEmergencies() {
    const [alert, setAlert] = useState(null);
    const { activeEmergencies, resolvedEmergencies, handleResolveEmergency, getEmergencyTypeInfo } = useEmergencies()

    const resolveEmergency = async (emergencyId) => {
		try {
			await handleResolveEmergency(emergencyId);
			setAlert({ type: 'success', text: `Emergenza ID-${emergencyId} risolta` });
		} catch (err) {
			const errorMsg = err.response?.data?.detail || err.message;
            setAlert({ type: 'error', text: `Non è stato possibile risolvere l'emergenza: ${errorMsg}` });
		}

		setTimeout(function() {
			setAlert(null)
		}, 5000)
	};

    return (
        <>  
            {activeEmergencies.length > 0 &&
                <DashboardEmergenciesToRisolve activeEmergenciesList={activeEmergencies} getEmergencyTypeInfo={getEmergencyTypeInfo} resolveEmergency={resolveEmergency}></DashboardEmergenciesToRisolve>
            }  
            
            {resolvedEmergencies.length > 0 &&
                <DashboardEmergenciesResolved resolvedEmergenciesList={resolvedEmergencies} getEmergencyTypeInfo={getEmergencyTypeInfo}></DashboardEmergenciesResolved>
            }

            {alert && <Alert type={alert.type} text={alert.text} />}
        </>
    );
}