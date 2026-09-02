import { useEffect, useState, useCallback } from 'react';
import { apiRequest, extractErrorMessage } from '../api/client';
import EntityTable from '../components/EntityTable';

const COLUMNS = [
  { key: 'nom', label: 'Nom' },
  { key: 'prenom', label: 'Prénom' },
  { key: 'email', label: 'Email' },
];

const EMPTY_FORM = { nom: '', prenom: '', email: '', username: '', password: '' };

export default function IntervenantsPage() {
  const [intervenants, setIntervenants] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    const data = await apiRequest('/intervenants/');
    setIntervenants(data);
  }, []);

  useEffect(() => { load(); }, [load]);

  function handleChange(field) {
    return (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    try {
      await apiRequest('/intervenants/', { method: 'POST', body: form });
      setForm(EMPTY_FORM);
      await load();
    } catch (err) {
      setError(extractErrorMessage(err.data));
    }
  }

  async function handleDelete(id) {
    await apiRequest(`/intervenants/${id}/`, { method: 'DELETE' });
    await load();
  }

  return (
    <main className="page">
      <h1>Intervenants</h1>
      <form onSubmit={handleSubmit} className="form-card">
        <label htmlFor="nom">Nom</label>
        <input id="nom" value={form.nom} onChange={handleChange('nom')} required />
        <label htmlFor="prenom">Prénom</label>
        <input id="prenom" value={form.prenom} onChange={handleChange('prenom')} required />
        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={form.email} onChange={handleChange('email')} required />
        <label htmlFor="username">Identifiant</label>
        <input id="username" value={form.username} onChange={handleChange('username')} required />
        <label htmlFor="password">Mot de passe</label>
        <input id="password" type="password" value={form.password} onChange={handleChange('password')} required />
        {error && <p role="alert">{error}</p>}
        <button type="submit">Ajouter</button>
      </form>
      <div className="table-wrapper">
        <EntityTable columns={COLUMNS} rows={intervenants} onDelete={handleDelete} />
      </div>
    </main>
  );
}
