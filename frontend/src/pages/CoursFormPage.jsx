import { useEffect, useState, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { apiRequest, extractErrorMessage } from '../api/client';

const EMPTY_FORM = { intitule: '', classe: '', salle: '', intervenant: '', debut: '', fin: '' };

export default function CoursFormPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditing = Boolean(id);

  const [classes, setClasses] = useState([]);
  const [salles, setSalles] = useState([]);
  const [intervenants, setIntervenants] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState('');

  const loadOptions = useCallback(async () => {
    const [classesData, sallesData, intervenantsData] = await Promise.all([
      apiRequest('/classes/'),
      apiRequest('/salles/'),
      apiRequest('/intervenants/'),
    ]);
    setClasses(classesData);
    setSalles(sallesData);
    setIntervenants(intervenantsData);
  }, []);

  useEffect(() => { loadOptions(); }, [loadOptions]);

  useEffect(() => {
    if (isEditing) {
      apiRequest(`/cours/${id}/`).then((data) => setForm({
        intitule: data.intitule,
        classe: data.classe,
        salle: data.salle,
        intervenant: data.intervenant,
        debut: data.debut.slice(0, 16),
        fin: data.fin.slice(0, 16),
      }));
    }
  }, [id, isEditing]);

  function handleChange(field) {
    return (event) => setForm((prev) => ({ ...prev, [field]: event.target.value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    const body = {
      intitule: form.intitule,
      classe: Number(form.classe),
      salle: Number(form.salle),
      intervenant: Number(form.intervenant),
      debut: form.debut,
      fin: form.fin,
    };
    try {
      if (isEditing) {
        await apiRequest(`/cours/${id}/`, { method: 'PATCH', body });
      } else {
        await apiRequest('/cours/', { method: 'POST', body });
      }
      navigate('/planning');
    } catch (err) {
      setError(extractErrorMessage(err.data));
    }
  }

  return (
    <main className="page">
      <h1>{isEditing ? 'Modifier le cours' : 'Nouveau cours'}</h1>
      <form onSubmit={handleSubmit} className="form-card">
        <label htmlFor="intitule">Intitulé</label>
        <input id="intitule" value={form.intitule} onChange={handleChange('intitule')} required />

        <label htmlFor="classe">Classe</label>
        <select id="classe" value={form.classe} onChange={handleChange('classe')} required>
          <option value="">-- Choisir --</option>
          {classes.map((c) => <option key={c.id} value={c.id}>{c.nom}</option>)}
        </select>

        <label htmlFor="salle">Salle</label>
        <select id="salle" value={form.salle} onChange={handleChange('salle')} required>
          <option value="">-- Choisir --</option>
          {salles.map((s) => <option key={s.id} value={s.id}>{s.nom_ou_numero}</option>)}
        </select>

        <label htmlFor="intervenant">Intervenant</label>
        <select id="intervenant" value={form.intervenant} onChange={handleChange('intervenant')} required>
          <option value="">-- Choisir --</option>
          {intervenants.map((i) => <option key={i.id} value={i.id}>{i.prenom} {i.nom}</option>)}
        </select>

        <label htmlFor="debut">Début</label>
        <input id="debut" type="datetime-local" value={form.debut} onChange={handleChange('debut')} required />

        <label htmlFor="fin">Fin</label>
        <input id="fin" type="datetime-local" value={form.fin} onChange={handleChange('fin')} required />

        {error && <p role="alert">{error}</p>}
        <button type="submit">Enregistrer</button>
      </form>
    </main>
  );
}
