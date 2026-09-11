import lists from '../../../../../ui/lists/lists.module.css'

export default function DashboardDevicesResearch() {
    return (
        <div className={`${lists.list}`}>
            <div className={`${lists.item}`} style={{padding: 20}}>
                <div className={`${lists.details} flex flex-column`} style={{gap: 5}}>
                    <h2 className='font-semi-bold' style={{fontSize: 16}}>Richieste in attesa</h2>
                    <p className='text-sm text-little-dark'>Gli orologi rilevati compaiono qui automaticamente.</p>
                </div>

                <span className='flex flex-row text-xs text-primary' style={{gap: 10, alignItems: "center"}}>
                    <svg style={{width: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M16.247 7.761a6 6 0 0 1 0 8.478"></path><path d="M19.075 4.933a10 10 0 0 1 0 14.134"></path><path d="M4.925 19.067a10 10 0 0 1 0-14.134"></path><path d="M7.753 16.239a6 6 0 0 1 0-8.478"></path><circle cx="12" cy="12" r="2"></circle></svg>
                
                    Ricerca attiva
                </span>
            </div>

            <div className={`${lists.item} ${lists.vertical}`} style={{padding: 20}}>
                <div className={`${lists.details} flex flex-row`} style={{alignItems: "center", gap: 15}}>
                    <span className='flex center bg-primary text-primary' style={{borderRadius: 6, width: 44, height: 44}}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M12 10v2.2l1.6 1"></path><path d="m16.13 7.66-.81-4.05a2 2 0 0 0-2-1.61h-2.68a2 2 0 0 0-2 1.61l-.78 4.05"></path><path d="m7.88 16.36.8 4a2 2 0 0 0 2 1.61h2.72a2 2 0 0 0 2-1.61l.81-4.05"></path><circle cx="12" cy="12" r="6"></circle></svg>
                    </span>

                    <div className='flex flex-column'>
                        <p className='font-medium'>MedWatch Pulse S</p>
                        <p className='monospace text-xs text-little-dark'>ID MW-4471 · Rilevato Ora</p>
                    </div>
                </div>

                <div className='flex flex-row' style={{gap: 5}}>
                    <button className='primary-btn' style={{gap: 10}}>
                        <svg style={{width: 16, height: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"></path></svg>
                        Accetta
                    </button>

                    <button className='primary-btn bg-default text-dark' style={{gap: 10, border: "solid 1px var(--border)", boxShadow: "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.1) 0px 1px 3px 0px, rgba(0, 0, 0, 0.1) 0px 1px 2px -1px"}}>
                        <svg style={{width: 16, height: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M18 6 6 18"></path><path d="m6 6 12 12"></path></svg>
                        Rifiuta
                    </button>
                </div>
            </div>

            <div className={`${lists.item} ${lists.vertical}`} style={{padding: 20}}>
                <div className={`${lists.details} flex flex-row`} style={{alignItems: "center", gap: 15}}>
                    <span className='flex center bg-primary text-primary' style={{borderRadius: 6, width: 44, height: 44}}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M12 10v2.2l1.6 1"></path><path d="m16.13 7.66-.81-4.05a2 2 0 0 0-2-1.61h-2.68a2 2 0 0 0-2 1.61l-.78 4.05"></path><path d="m7.88 16.36.8 4a2 2 0 0 0 2 1.61h2.72a2 2 0 0 0 2-1.61l.81-4.05"></path><circle cx="12" cy="12" r="6"></circle></svg>
                    </span>

                    <div className='flex flex-column'>
                        <p className='font-medium'>MedWatch Pulse S</p>
                        <p className='monospace text-xs text-little-dark'>ID MW-4471 · Rilevato Ora</p>
                    </div>
                </div>

                <div className='flex flex-row' style={{gap: 5}}>
                    <button className='primary-btn' style={{gap: 10}}>
                        <svg style={{width: 16, height: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"></path></svg>
                        Accetta
                    </button>

                    <button className='primary-btn bg-default text-dark' style={{gap: 10, border: "solid 1px var(--border)", boxShadow: "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.1) 0px 1px 3px 0px, rgba(0, 0, 0, 0.1) 0px 1px 2px -1px"}}>
                        <svg style={{width: 16, height: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M18 6 6 18"></path><path d="m6 6 12 12"></path></svg>
                        Rifiuta
                    </button>
                </div>
            </div>
        </div>
    );
}