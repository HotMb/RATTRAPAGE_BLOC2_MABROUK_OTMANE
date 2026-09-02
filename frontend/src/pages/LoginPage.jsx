import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    try {
      await login(username, password);
      navigate('/planning');
    } catch (err) {
      setError('Identifiant ou mot de passe incorrect.');
    }
  }

  return (
    <main className="page">
      <form onSubmit={handleSubmit} aria-label="Formulaire de connexion" className="form-card">
        <h1>Connexion</h1>
        <div>
          <label htmlFor="username">Identifiant</label>
          <input
            id="username" name="username" value={username}
            onChange={(e) => setUsername(e.target.value)} required
          />
        </div>
        <div>
          <label htmlFor="password">Mot de passe</label>
          <input
            id="password" name="password" type="password" value={password}
            onChange={(e) => setPassword(e.target.value)} required
          />
        </div>
        {error && <p role="alert">{error}</p>}
        <button type="submit">Se connecter</button>
      </form>
    </main>
  );
}
