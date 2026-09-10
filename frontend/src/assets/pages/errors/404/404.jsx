import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="flex flex-column center h-full">
      <h1 className="monospace text-primary font-bold text-xxxl">404</h1>
      <h2 className="text-secondary font-semi-bold text-xl" style={{marginTop: 16}}>Pagina non trovata</h2>
      <p className="text-third text-sm" style={{marginTop: 8}}>La pagina richiesta non esiste oppure è stata spostata.</p>
      <Link to="/dashboard"><button className="primary-btn" style={{marginTop: 24}}>Torna alla dashboard</button></Link>
    </div>
  );
}