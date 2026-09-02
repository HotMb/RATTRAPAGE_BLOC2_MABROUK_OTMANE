import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function NavBar() {
  const { user, logout } = useAuth();
  if (!user) return null;

  return (
    <nav aria-label="Navigation principale">
      <Link to="/planning">Planning</Link>
      {user.role === 'ADMIN' && (
        <>
          <Link to="/classes">Classes</Link>
          <Link to="/salles">Salles</Link>
          <Link to="/intervenants">Intervenants</Link>
          <Link to="/etudiants">Étudiants</Link>
        </>
      )}
      <span className="nav-user">{user.username} ({user.role})</span>
      <button type="button" onClick={logout}>Déconnexion</button>
    </nav>
  );
}
