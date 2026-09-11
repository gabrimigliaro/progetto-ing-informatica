import lists from '../../../../../ui/lists/lists.module.css'

export default function DashboardDevicesActive() {
    return (
        <div className='flex flex-column' style={{marginTop: 35}}>
            <h2 className='font-semi-bold' style={{fontSize: 16}}>Dispositivi collegati</h2>

            <div className={`${lists.list}`} style={{marginTop: 15, paddingBottom: 35}}>
                <div className={`${lists.item}`} style={{padding: 20}}>
                    <div className={`${lists.details} flex flex-row`} style={{alignItems: "center", gap: 15}}>
                        <span className='flex center text-primary'>
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M12 10v2.2l1.6 1"></path><path d="m16.13 7.66-.81-4.05a2 2 0 0 0-2-1.61h-2.68a2 2 0 0 0-2 1.61l-.78 4.05"></path><path d="m7.88 16.36.8 4a2 2 0 0 0 2 1.61h2.72a2 2 0 0 0 2-1.61l.81-4.05"></path><circle cx="12" cy="12" r="6"></circle></svg>
                        </span>

                        <div className='flex flex-column'>
                            <p className='font-medium'>MedWatch Pulse S · MW-4398</p>
                            <p className='text-sm text-little-dark'>Associato a Marco Conti · Online</p>
                        </div>
                    </div>
                </div>

                <div className={`${lists.item}`} style={{padding: 20}}>
                    <div className={`${lists.details} flex flex-row`} style={{alignItems: "center", gap: 15}}>
                        <span className='flex center text-primary'>
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M12 10v2.2l1.6 1"></path><path d="m16.13 7.66-.81-4.05a2 2 0 0 0-2-1.61h-2.68a2 2 0 0 0-2 1.61l-.78 4.05"></path><path d="m7.88 16.36.8 4a2 2 0 0 0 2 1.61h2.72a2 2 0 0 0 2-1.61l.81-4.05"></path><circle cx="12" cy="12" r="6"></circle></svg>
                        </span>

                        <div className='flex flex-column'>
                            <p className='font-medium'>MedWatch Pulse S · MW-4398</p>
                            <p className='text-sm text-little-dark'>Associato a Marco Conti · Online</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}