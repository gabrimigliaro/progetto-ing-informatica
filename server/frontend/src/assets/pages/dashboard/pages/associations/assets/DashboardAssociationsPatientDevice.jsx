import { useState, useEffect } from 'react';

import cards from '../../../../../ui/cards/cards.module.css'
import lists from '../../../../../ui/lists/lists.module.css'

export default function DashboardAssociationsPatientDevice({ devicesList, patientsList, associationsList, createAssociation }) {
    const [associationData, setAssociationData] = useState({ p_id: '', d_id: '' });

    const handleChange = (e) => {
		setAssociationData({ ...associationData, [e.target.name]: Number(e.target.value) });
	};

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            await createAssociation(associationData)
        } catch (err) {}
    };

    useEffect(() => {
        setAssociationData((prev) => ({
            ...prev,
            p_id: prev.p_id || (patientsList.length > 0 ? patientsList[0].id : ""),
            d_id: prev.d_id || (devicesList.length > 0 ? devicesList[0].id : ""),
        }));
    }, [patientsList, devicesList]);

    return (
        <div className={`${cards.card} ${cards.associationsCard}`}>
            <h2 className='font-semi-bold' style={{fontSize: "16px"}}>Associa dispositivo a paziente</h2>
            <p className='text-sm text-little-dark'>Collega un orologio disponibile a un paziente.</p>

            <form onSubmit={handleSubmit} style={{marginTop: 10}}>
                <div className="inp">
                    <div className="label">
                        <label htmlFor="patient" className="text-sm font-medium">Paziente</label>
                    </div>

                    <select value={associationData.p_id || ""} onChange={handleChange} required name="p_id" id="patient" className="text-sm text-dark" >
                        {patientsList.map((patient) => (
                            <option key={patient.id} value={patient.id}>{patient.name} {patient.surname}</option>
                        ))}
                    </select>
                </div>

                <div className="inp" style={{marginTop: "10px"}}>
                    <div className="label">
                        <label htmlFor="device" className="text-sm font-medium">Dispositivo</label>
                    </div>

                    <select value={associationData.d_id || ""} onChange={handleChange} required name="d_id" id="device" className="text-sm text-dark" >
                        {devicesList.map((device) => (
                            <option key={device.id} value={device.id}>{device.name}-{device.id}</option>
                        ))}
                    </select>
                </div>

                <button className='primary-btn' style={{width: "100%", justifyContent: "center", height: 36, marginTop: "20px"}}>Associa dispositivo</button>
                
                {associationsList.length > 0 && (
                    <div className={`${lists.list}`} style={{marginTop: 25}}>
                        {associationsList.map((association) => (
                            <div key={association.id} className={`${lists.item}`} style={{padding: 20}}>
                                <div className={`${lists.details} flex flex-row`} style={{alignItems: "center", gap: 15}}>
                                    <div className='flex flex-column'>
                                        <p className='font-medium'>{association.patient.name} {association.patient.surname}</p>
                                        <p className='text-sm text-little-dark'>Dispositivo {association.device.name}-{association.device.id}</p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </form>
        </div>
    );
}