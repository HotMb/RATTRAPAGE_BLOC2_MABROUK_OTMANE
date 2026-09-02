import { useEffect, useState, useCallback } from 'react';
import { apiRequest, extractErrorMessage } from '../api/client';
import EntityTable from '../components/EntityTable';

const COLUMNS = [
  { key: 'nom', label: 'Nom' },
  { key: 'niveau', label: 'Niveau' },
];

export default function ClassesPage() {
  const [classes, setClasses] = useState([]);
  const [nom, setNom] = useState('');
  const [niveau, setNiveau] = useState('');
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    const data = await apiRequest('/classes/');
    setClasses(data);
  }, []);

  useEffect(() => { load(); }, [load]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    try {
      await apiRequest('/classes/', { method: 'POST', body: { nom, niveau } });
      setNom('');
      setNiveau('');
      await load();
    } catch (err) {
      setError(extractErrorMessage(err.data));
    }
  }

  async function handleDelete(id) {
    await apiRequest(`/classes/${id}/`, { method: 'DELETE' });
    await load();
  }

  return (
    <main className="page">
      <h1>Classes</h1>
      <form onSubmit={handleSubmit} className="form-card">
        <label htmlFor="nom">Nom</label>
        <input id="nom" value={nom} onChange={(e) => setNom(e.target.value)} required />
        <label htmlFor="niveau">Niveau</label>
        <input id="niveau" value={niveau} onChange={(e) => setNiveau(e.target.value)} required />
        {error && <p role="alert">{error}</p>}
        <button type="submit">Ajouter</button>
      </form>
      <div className="table-wrapper">
        <EntityTable columns={COLUMNS} rows={classes} onDelete={handleDelete} />
      </div>
    </main>
  );
}
