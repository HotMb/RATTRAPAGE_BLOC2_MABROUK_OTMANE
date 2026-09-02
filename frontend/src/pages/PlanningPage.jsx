import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { apiRequest, extractErrorMessage } from '../api/client';
import { useAuth } from '../auth/AuthContext';

function buildQuery(filters) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  const query = params.toString();
  return query ? `?${query}` : '';
}

export default function PlanningPage() {
  const { user } = useAuth();
  const [cours, setCours] = useState([]);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({ date: '', classe: '', salle: '', intervenant: '' });

  const loadCours = useCallback(async () => {
    setError('');
    try {
      const data = await apiRequest(`/cours/${buildQuery(filters)}`);
      setCours(data);
    } catch (err) {
      setError(extractErrorMessage(err.data));
    }
  }, [filters]);

  useEffect(() => {
    loadCours();
  }, [loadCours]);

  function handleFilterChange(field) {
    return (event) => setFilters((prev) => ({ ...prev, [field]: event.target.value }));
  }

  return (
    <main className="page">
      <h1>Planning</h1>
      {user.role === 'ADMIN' && <Link to="/cours/nouveau" className="button-link">Nouveau cours</Link>}

      <form onSubmit={(e) => e.preventDefault()} className="filters-form">
        <div>
          <label htmlFor="filter-date">Date</label>
          <input id="filter-date" type="date" value={filters.date} onChange={handleFilterChange('date')} />
        </div>

        {user.role === 'ADMIN' && (
          <>
            <div>
              <label htmlFor="filter-classe">Classe (id)</label>
              <input id="filter-classe" value={filters.classe} onChange={handleFilterChange('classe')} />
            </div>
            <div>
              <label htmlFor="filter-salle">Salle (id)</label>
              <input id="filter-salle" value={filters.salle} onChange={handleFilterChange('salle')} />
            </div>
            <div>
              <label htmlFor="filter-intervenant">Intervenant (id)</label>
              <input id="filter-intervenant" value={filters.intervenant} onChange={handleFilterChange('intervenant')} />
            </div>
          </>
        )}
      </form>

      {error && <p role="alert">{error}</p>}

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th scope="col">Intitulé</th>
              <th scope="col">Classe</th>
              <th scope="col">Salle</th>
              <th scope="col">Intervenant</th>
              <th scope="col">Début</th>
              <th scope="col">Fin</th>
              {user.role === 'ADMIN' && <th scope="col">Actions</th>}
            </tr>
          </thead>
          <tbody>
            {cours.map((c) => (
              <tr key={c.id}>
                <td data-label="Intitulé">{c.intitule}</td>
                <td data-label="Classe">{c.classe}</td>
                <td data-label="Salle">{c.salle}</td>
                <td data-label="Intervenant">{c.intervenant}</td>
                <td data-label="Début">{new Date(c.debut).toLocaleString('fr-FR')}</td>
                <td data-label="Fin">{new Date(c.fin).toLocaleString('fr-FR')}</td>
                {user.role === 'ADMIN' && (
                  <td data-label="Actions">
                    <Link to={`/cours/${c.id}/modifier`}>Modifier</Link>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
