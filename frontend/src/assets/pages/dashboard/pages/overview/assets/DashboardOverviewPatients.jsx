import patients from './css/dashboardOverview.module.css';
import CardAlert from '../../../../../ui/cards-alerts/card-alerts';

import { Link } from 'react-router-dom';

export default function DashboardOverviewPatients() {
    return (
        <div className={`${patients.patients}`}>
            <div className={`${patients.titles}`}>
                <h2 className='text-lg font-semi-bold'>Pazienti</h2>
                <p className='text-sm text-little-dark'>Le emergenze sono mostrate per prime.</p>
            </div>

            <div className={`${patients.cards}`}>
                <Link to={`/dashboard/patient/mario-rossi`}>
                    <div className={`${patients.patient} ${patients.yellow}`}>
                        <div className={`${patients.top}`}>
                            <div className={`${patients.left}`}>
                                <div className={`${patients.user} flex center`}>
                                    <svg className='text-little-dark' style={{width: 20}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="5"></circle><path d="M20 21a8 8 0 0 0-16 0"></path></svg>
                                </div>

                                <div className="flex flex-column" style={{gap: 2}}>
                                    <p className='font-semi-bold'>Luca Bianchi</p>
                                    <p className='text-little-dark monospace text-xs'>PZ-41 • Stanza 1, primo piano</p>
                                </div>
                            </div>

                            <div className="right">
                                <CardAlert type={"support"} />
                            </div>
                        </div>

                        <div className={`${patients.bottom}`}>
                            <div className={`${patients.heart}`}>
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"></path></svg>
                            
                                <h2 className='monospace' style={{fontSize: "1.875rem"}}>38 <span className='uppercase text-xs text-little-dark font-default' style={{fontWeight: 300}}>bpm</span></h2>
                            </div>

                            <p className='text-xs text-little-dark'>Vedi scheda paziente</p>
                        </div>
                    </div>
                </Link>

                <div className={`${patients.patient} ${patients.red}`}>
                    <div className={`${patients.top}`}>
                        <div className={`${patients.left}`}>
                            <div className={`${patients.user} flex center`}>
                                <svg className='text-little-dark' style={{width: 20}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="5"></circle><path d="M20 21a8 8 0 0 0-16 0"></path></svg>
                            </div>

                            <div className="flex flex-column" style={{gap: 2}}>
                                <p className='font-semi-bold'>Luca Bianchi</p>
                                <p className='text-little-dark monospace text-xs'>PZ-41 • Stanza 1, primo piano</p>
                            </div>
                        </div>

                        <div className="right">
                            <CardAlert type={"fall"} />
                        </div>
                    </div>

                    <div className={`${patients.bottom}`}>
                        <div className={`${patients.heart}`}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"></path></svg>
                        
                            <h2 className='monospace' style={{fontSize: "1.875rem"}}>38 <span className='uppercase text-xs text-little-dark font-default' style={{fontWeight: 300}}>bpm</span></h2>
                        </div>

                        <p className='text-xs text-little-dark'>Vedi scheda paziente</p>
                    </div>
                </div>

                <div className={`${patients.patient} ${patients.green}`}>
                    <div className={`${patients.top}`}>
                        <div className={`${patients.left}`}>
                            <div className={`${patients.user} flex center`}>
                                <svg className='text-little-dark' style={{width: 20}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="5"></circle><path d="M20 21a8 8 0 0 0-16 0"></path></svg>
                            </div>

                            <div className="flex flex-column" style={{gap: 2}}>
                                <p className='font-semi-bold'>Luca Bianchi</p>
                                <p className='text-little-dark monospace text-xs'>PZ-41 • Stanza 1, primo piano</p>
                            </div>
                        </div>

                        <div className="right">
                            <CardAlert type={"stable"} />
                        </div>
                    </div>

                    <div className={`${patients.bottom}`}>
                        <div className={`${patients.heart}`}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"></path></svg>
                        
                            <h2 className='monospace' style={{fontSize: "1.875rem"}}>38 <span className='uppercase text-xs text-little-dark font-default' style={{fontWeight: 300}}>bpm</span></h2>
                        </div>

                        <p className='text-xs text-little-dark'>Vedi scheda paziente</p>
                    </div>
                </div>

                <div className={`${patients.patient} ${patients.green}`}>
                    <div className={`${patients.top}`}>
                        <div className={`${patients.left}`}>
                            <div className={`${patients.user} flex center`}>
                                <svg className='text-little-dark' style={{width: 20}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="5"></circle><path d="M20 21a8 8 0 0 0-16 0"></path></svg>
                            </div>

                            <div className="flex flex-column" style={{gap: 2}}>
                                <p className='font-semi-bold'>Luca Bianchi</p>
                                <p className='text-little-dark monospace text-xs'>PZ-41 • Stanza 1, primo piano</p>
                            </div>
                        </div>

                        <div className="right">
                            <CardAlert type={"stable"} />
                        </div>
                    </div>

                    <div className={`${patients.bottom}`}>
                        <div className={`${patients.heart}`}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"></path></svg>
                        
                            <h2 className='monospace' style={{fontSize: "1.875rem"}}>38 <span className='uppercase text-xs text-little-dark font-default' style={{fontWeight: 300}}>bpm</span></h2>
                        </div>

                        <p className='text-xs text-little-dark'>Vedi scheda paziente</p>
                    </div>
                </div>

                <div className={`${patients.patient} ${patients.green}`}>
                    <div className={`${patients.top}`}>
                        <div className={`${patients.left}`}>
                            <div className={`${patients.user} flex center`}>
                                <svg className='text-little-dark' style={{width: 20}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="5"></circle><path d="M20 21a8 8 0 0 0-16 0"></path></svg>
                            </div>

                            <div className="flex flex-column" style={{gap: 2}}>
                                <p className='font-semi-bold'>Luca Bianchi</p>
                                <p className='text-little-dark monospace text-xs'>PZ-41 • Stanza 1, primo piano</p>
                            </div>
                        </div>

                        <div className="right">
                            <CardAlert type={"stable"} />
                        </div>
                    </div>

                    <div className={`${patients.bottom}`}>
                        <div className={`${patients.heart}`}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"></path></svg>
                        
                            <h2 className='monospace' style={{fontSize: "1.875rem"}}>38 <span className='uppercase text-xs text-little-dark font-default' style={{fontWeight: 300}}>bpm</span></h2>
                        </div>

                        <p className='text-xs text-little-dark'>Vedi scheda paziente</p>
                    </div>
                </div>

                <div className={`${patients.patient} ${patients.green}`}>
                    <div className={`${patients.top}`}>
                        <div className={`${patients.left}`}>
                            <div className={`${patients.user} flex center`}>
                                <svg className='text-little-dark' style={{width: 20}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="5"></circle><path d="M20 21a8 8 0 0 0-16 0"></path></svg>
                            </div>

                            <div className="flex flex-column" style={{gap: 2}}>
                                <p className='font-semi-bold'>Luca Bianchi</p>
                                <p className='text-little-dark monospace text-xs'>PZ-41 • Stanza 1, primo piano</p>
                            </div>
                        </div>

                        <div className="right">
                            <CardAlert type={"stable"} />
                        </div>
                    </div>

                    <div className={`${patients.bottom}`}>
                        <div className={`${patients.heart}`}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"></path></svg>
                        
                            <h2 className='monospace' style={{fontSize: "1.875rem"}}>38 <span className='uppercase text-xs text-little-dark font-default' style={{fontWeight: 300}}>bpm</span></h2>
                        </div>

                        <p className='text-xs text-little-dark'>Vedi scheda paziente</p>
                    </div>
                </div>

                <div className={`${patients.patient} ${patients.green}`}>
                    <div className={`${patients.top}`}>
                        <div className={`${patients.left}`}>
                            <div className={`${patients.user} flex center`}>
                                <svg className='text-little-dark' style={{width: 20}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="5"></circle><path d="M20 21a8 8 0 0 0-16 0"></path></svg>
                            </div>

                            <div className="flex flex-column" style={{gap: 2}}>
                                <p className='font-semi-bold'>Luca Bianchi</p>
                                <p className='text-little-dark monospace text-xs'>PZ-41 • Stanza 1, primo piano</p>
                            </div>
                        </div>

                        <div className="right">
                            <CardAlert type={"stable"} />
                        </div>
                    </div>

                    <div className={`${patients.bottom}`}>
                        <div className={`${patients.heart}`}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"></path></svg>
                        
                            <h2 className='monospace' style={{fontSize: "1.875rem"}}>38 <span className='uppercase text-xs text-little-dark font-default' style={{fontWeight: 300}}>bpm</span></h2>
                        </div>

                        <p className='text-xs text-little-dark'>Vedi scheda paziente</p>
                    </div>
                </div>

                <div className={`${patients.patient} ${patients.green}`}>
                    <div className={`${patients.top}`}>
                        <div className={`${patients.left}`}>
                            <div className={`${patients.user} flex center`}>
                                <svg className='text-little-dark' style={{width: 20}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="8" r="5"></circle><path d="M20 21a8 8 0 0 0-16 0"></path></svg>
                            </div>

                            <div className="flex flex-column" style={{gap: 2}}>
                                <p className='font-semi-bold'>Luca Bianchi</p>
                                <p className='text-little-dark monospace text-xs'>PZ-41 • Stanza 1, primo piano</p>
                            </div>
                        </div>

                        <div className="right">
                            <CardAlert type={"stable"} />
                        </div>
                    </div>

                    <div className={`${patients.bottom}`}>
                        <div className={`${patients.heart}`}>
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"></path></svg>
                        
                            <h2 className='monospace' style={{fontSize: "1.875rem"}}>38 <span className='uppercase text-xs text-little-dark font-default' style={{fontWeight: 300}}>bpm</span></h2>
                        </div>

                        <p className='text-xs text-little-dark'>Vedi scheda paziente</p>
                    </div>
                </div>
            </div>
        </div>
    );
}