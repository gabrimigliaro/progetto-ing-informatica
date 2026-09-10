import { Link } from 'react-router-dom';

import { usePasswordToggle } from '../../../hooks/usePasswordToggle';

export default function Login() {
	const { type, visible, toggleVisibility } = usePasswordToggle();

	return (
		<div className="flex h-full w-full center">
			<div className="flex flex-column bg-white login-card" style={{width: 448-32*2, height: "auto", borderRadius: 8, padding: 32, border: "solid 1px var(--border)", boxShadow: "rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.1) 0px 1px 3px 0px, rgba(0, 0, 0, 0.1) 0px 1px 2px -1px"}}>
				<h1 className="text-xxl text-dark">Bentornato</h1>
				<p className="text-little-dark text-sm" style={{marginTop: 4}}>Accedi per monitorare i pazienti assegnati.</p>

				<form action="#" className='flex flex-column' style={{marginTop: 28, gap: 20}}>
					<div className="inp">
						<div className="label">
							<label htmlFor="email" className="text-sm font-medium">Email</label>
						</div>

						<input type="email" id="email" placeholder="nome@struttura.it" className="text-sm" />
					</div>

					<div className="inp">
						<div className="label">
							<label htmlFor="password" className="text-sm font-medium">Password</label>

							<Link to="/">Password dimenticata?</Link>
						</div>

						<div className='flex relative' style={{alignItems: "center"}}>
							<input type={type} id="password" className="text-sm" style={{width: "100%", paddingRight: 35}} />
							<button type="button" className='absolute flex center hovered' onClick={toggleVisibility} style={{right: 0, backgroundColor: "transparent", border: "none", height: 34, padding: 10, borderTopRightRadius: 6, borderBottomRightRadius: 6}}>
								{visible ? 
								<svg style={{width: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"></path><circle cx="12" cy="12" r="3"></circle></svg>
								: 
								<svg style={{width: 16}} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M10.733 5.076a10.744 10.744 0 0 1 11.205 6.575 1 1 0 0 1 0 .696 10.747 10.747 0 0 1-1.444 2.49"></path><path d="M14.084 14.158a3 3 0 0 1-4.242-4.242"></path><path d="M17.479 17.499a10.75 10.75 0 0 1-15.417-5.151 1 1 0 0 1 0-.696 10.75 10.75 0 0 1 4.446-5.143"></path><path d="m2 2 20 20"></path></svg>}
							</button>
						</div>
					</div>

					<button className='primary-btn' style={{width: "100%", justifyContent: "center", height: 40}}>Accedi</button>

					<p className='flex center text-sm text-little-dark' style={{width: "100%", gap: 5}}>Non hai un account? <Link to="/register">Registrati</Link></p>
				</form>
			</div>
		</div>
	);
}