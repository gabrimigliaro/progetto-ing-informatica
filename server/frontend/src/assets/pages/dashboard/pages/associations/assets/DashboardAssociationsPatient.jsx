import { useEffect, useState } from 'react';

import cards from '../../../../../ui/cards/cards.module.css'

export default function DashboardAssociationsPatient( {addPatient} ) {
    const [formData, setFormData] = useState({ name: '', surname: ''});
    const [maxDate, setMaxDate] = useState(null)

    const handleChange = (e) => {
		setFormData({ ...formData, [e.target.name]: e.target.value });
	};

    useEffect(() => {
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        setMaxDate(yesterday.toLocaleDateString('en-CA'))
    }, [])

    const handleSubmit = async (e) => {
        e.preventDefault();

        await addPatient(formData);
    };

    return (
        <div className={`${cards.card} ${cards.associationsCard}`}>
            <h2 className='font-semi-bold' style={{fontSize: "16px"}}>Nuovo Paziente</h2>
            <p className='text-sm text-little-dark'>Inserisci i dati anagrafici dell'operatore.</p>

            <form onSubmit={handleSubmit} style={{marginTop: 10}}>
                <div className="inp flex flex-row" style={{justifyContent: "space-between"}}>
                    <div style={{width: "45%"}}>
                        <div className="label">
                            <label htmlFor="nome" className="text-sm font-medium">Nome</label>
                        </div>

                        <input onChange={handleChange} required type="text" id="nome" name='name' className="text-sm" style={{width: "calc(100% - 12px*2)"}} />
                    </div>

                    <div style={{width: "45%"}}>
                        <div className="label">
                            <label htmlFor="cognome" className="text-sm font-medium">Cognome</label>
                        </div>

                        <input onChange={handleChange} required type="text" id="cognome" name='surname' className="text-sm" style={{width: "calc(100% - 12px*2)"}} />
                    </div>
                </div>

                <div className="inp" style={{marginTop: "10px"}}>
                    <div className="label">
                        <label htmlFor="date" className="text-sm font-medium">Data di nascita</label>
                    </div>

                    <input required type="date" id="date" name='date' max={maxDate} className="text-sm text-dark" />
                </div>

                <button className='primary-btn' style={{width: "100%", justifyContent: "center", height: 36, marginTop: "20px"}}>Aggiungi paziente</button>
            </form>
        </div>
    );
}