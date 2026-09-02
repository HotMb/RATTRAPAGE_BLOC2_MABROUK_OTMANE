import { useEffect, useState, useCallback } from 'react';
import { apiRequest, extractErrorMessage } from '../api/client';
import EntityTable from '../components/EntityTable';

const COLUMNS = [
  { key: 'nom_ou_numero', label: 'Nom / numéro' },
  { key: 'capacite', label: 'Capacité' },
  { key: 'type', label: 'Type' },
];

export default function SallesPage() {
  const [salles, setSalles] = useState([]);
  const [nomOuNumero, setNomOuNumero] = useState('');
  const [capacite, setCapacite] = useState('');
  const [type, setType] = useState('');
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    const data = await apiRequest('/salles/');
    setSalles(data);
  }, []);

  useEffect(() => { load(); }, [load]);

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    try {
      await apiRequest('/salles/', {
        method: 'POST',
        body: { nom_ou_numero: nomOuNumero, capacite: Number(capacite), type },
      });
      setNomOuNumero('');
      setCapacite('');
      setType('');
      await load();
    } catch (err) {
      setError(extractErrorMessage(err.data));
    }
  }

  async function handleDelete(id) {
    await apiRequest(`/salles/${id}/`, { method: 'DELETE' });
    await load();
  }

  return (
    <main className="page">
      <h1>Salles</h1>
      <form onSubmit={handleSubmit} className="form-card">
        <label htmlFor="nom_ou_numero">Nom ou numéro</label>
        <input id="nom_ou_numero" value={nomOuNumero} onChange={(e) => setNomOuNumero(e.target.value)} required />
        <label htmlFor="capacite">Capacité</label>
        <input id="capacite" type="number" min="1" value={capacite} onChange={(e) => setCapacite(e.target.value)} required />
        <label htmlFor="type">Type</label>
        <input id="type" value={type} onChange={(e) => setType(e.target.value)} required />
        {error && <p role="alert">{error}</p>}
        <button type="submit">Ajouter</button>
      </form>
      <div className="table-wrapper">
        <EntityTable columns={COLUMNS} rows={salles} onDelete={handleDelete} />
      </div>
    </main>
  );
}
