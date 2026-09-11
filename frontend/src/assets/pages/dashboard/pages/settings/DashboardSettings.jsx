import { useState } from 'react';

import lists from '../../../../ui/lists/lists.module.css'

export default function DashboardSettings() {
    const [deleteIsOpen, setDeleteIsOpen] = useState(false);

    return (
        <>
            <div className={`${lists.list}`}>
                <div className={`${lists.item} ${lists.vertical}`} style={{padding: 20}}>
                    <div className={`${lists.details} flex flex-row`} style={{gap: 15}}>
                        <span className='flex center bg-primary' style={{width: 40, height: 40, borderRadius: 6}}>
                            <svg className='text-primary' xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z"></path><circle cx="16.5" cy="7.5" r=".5" fill="currentColor"></circle></svg>
                        </span>

                        <div className='flex flex-column' style={{width: "fit-content"}}>
                            <h2 className='font-semi-bold' style={{fontSize: 16}}>Password</h2>
                            <p className='text-sm text-little-dark'>Aggiorna la password del tuo account.</p>
                        </div>
                    </div>

                    <button className='primary-btn bg-default text-dark' style={{border: "solid 1px var(--border)", boxShadow: "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.1) 0px 1px 3px 0px, rgba(0, 0, 0, 0.1) 0px 1px 2px -1px"}}>Cambia password</button>
                </div>

                <div className={`${lists.item} ${lists.vertical} flex-column`} style={{padding: 20, gap: 20}}>
                    <div className='flex flex-row' style={{width: "100%", justifyContent: "space-between"}}>
                        <div className={`${lists.details} flex flex-row`} style={{gap: 15}}>
                            <span className='flex center bg-red' style={{width: 40, height: 40, borderRadius: 6}}>
                                <svg style={{color: "var(--red)"}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M10 11v6"></path><path d="M14 11v6"></path><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"></path><path d="M3 6h18"></path><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                            </span>

                            <div className='flex flex-column' style={{width: "fit-content"}}>
                                <h2 className='font-semi-bold' style={{fontSize: 16}}>Cancella account</h2>
                                <p className='text-sm text-little-dark'>Questa azione è irreversibile.</p>
                            </div>
                        </div>

                        <button onClick={() => setDeleteIsOpen(true)} className='primary-btn' style={{backgroundColor: "var(--red)", boxShadow: "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.1) 0px 1px 3px 0px, rgba(0, 0, 0, 0.1) 0px 1px 2px -1px"}}>Cancella account</button>
                    </div>

                    {deleteIsOpen &&
                        <div className='flex flex-column bg-red border-red' style={{borderRadius: 6, padding: 16, width: "calc(100% - 16px*2)", gap: 10}}>
                            <p className='text-sm font-medium'>Confermi la cancellazione dell’account?</p>

                            <div className='flex' style={{gap: 5}}>
                                <button onClick={() => setDeleteIsOpen(false)} className='primary-btn text-xs' style={{backgroundColor: "var(--red)", padding: "0 12px", boxShadow: "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.1) 0px 1px 3px 0px, rgba(0, 0, 0, 0.1) 0px 1px 2px -1px"}}>Conferma</button>
                                <button onClick={() => setDeleteIsOpen(false)} className='primary-btn bg-default text-dark text-xs' style={{border: "solid 1px var(--border)", padding: "0 12px", boxShadow: "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.1) 0px 1px 3px 0px, rgba(0, 0, 0, 0.1) 0px 1px 2px -1px"}}>Annulla</button>
                            </div>
                        </div>
                    }
                </div>
            </div>
        </>
    );
}