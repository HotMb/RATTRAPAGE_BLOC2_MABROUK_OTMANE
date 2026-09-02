import { useEffect, useState, useCallback } from 'react';
import { apiRequest, extractErrorMessage } from '../api/client';
import EntityTable from '../components/EntityTable';

const COLUMNS = [
  { key: 'nom', label: 'Nom' },
  { key: 'prenom', label: 'Prénom' },
  { key: 'email', label: 'Email' },
  { key: 'classe', label: 'Classe (id)' },
];

const EMPTY_FORM = { nom: '', prenom: '', email: '', classe: '', username: '', password: '' };

export default function EtudiantsPage() {
  const [etudiants, setEtudiants] = useState([]);
  const [classes, setClasses] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    const [etudiantsData, classesData] = await Promise.all([
      apiRequest('/etudiants/'),
      apiRequest('/classes/'),
    ]);
    setEtudiants(etudiantsData);
    setClasses(classesData);
  }, []);

  useEffect(() => { load(); }, [load]);

  function handleChange(field) {
    return (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    try {
      await apiRequest('/etudiants/', { method: 'POST', body: { ...form, classe: Number(form.classe) } });
      setForm(EMPTY_FORM);
      await load();
    } catch (err) {
      setError(extractErrorMessage(err.data));
    }
  }

  async function handleDelete(id) {
    await apiRequest(`/etudiants/${id}/`, { method: 'DELETE' });
    await load();
  }

  return (
    <main className="page">
      <h1>Étudiants</h1>
      <form onSubmit={handleSubmit} className="form-card">
        <label htmlFor="nom">Nom</label>
        <input id="nom" value={form.nom} onChange={handleChange('nom')} required />
        <label htmlFor="prenom">Prénom</label>
        <input id="prenom" value={form.prenom} onChange={handleChange('prenom')} required />
        <label htmlFor="email">Email</label>
        <input id="email" type="email" value={form.email} onChange={handleChange('email')} required />
        <label htmlFor="classe">Classe</label>
        <select id="classe" value={form.classe} onChange={handleChange('classe')} required>
          <option value="">-- Choisir --</option>
          {classes.map((c) => (
            <option key={c.id} value={c.id}>{c.nom}</option>
          ))}
        </select>
        <label htmlFor="username">Identifiant</label>
        <input id="username" value={form.username} onChange={handleChange('username')} required />
        <label htmlFor="password">Mot de passe</label>
        <input id="password" type="password" value={form.password} onChange={handleChange('password')} required />
        {error && <p role="alert">{error}</p>}
        <button type="submit">Ajouter</button>
      </form>
      <div className="table-wrapper">
        <EntityTable columns={COLUMNS} rows={etudiants} onDelete={handleDelete} />
      </div>
    </main>
  );
}
