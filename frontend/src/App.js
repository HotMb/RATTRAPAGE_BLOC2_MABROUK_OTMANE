import { BrowserRouter, Routes, Route } from 'react-router-dom';
import './App.css';
import { AuthProvider } from './auth/AuthContext';
import RequireRole from './components/RequireRole';
import NavBar from './components/NavBar';
import LoginPage from './pages/LoginPage';
import PlanningPage from './pages/PlanningPage';
import ClassesPage from './pages/ClassesPage';
import SallesPage from './pages/SallesPage';
import IntervenantsPage from './pages/IntervenantsPage';
import EtudiantsPage from './pages/EtudiantsPage';
import CoursFormPage from './pages/CoursFormPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <NavBar />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/planning" element={<RequireRole><PlanningPage /></RequireRole>} />
          <Route path="/classes" element={<RequireRole roles={['ADMIN']}><ClassesPage /></RequireRole>} />
          <Route path="/salles" element={<RequireRole roles={['ADMIN']}><SallesPage /></RequireRole>} />
          <Route path="/intervenants" element={<RequireRole roles={['ADMIN']}><IntervenantsPage /></RequireRole>} />
          <Route path="/etudiants" element={<RequireRole roles={['ADMIN']}><EtudiantsPage /></RequireRole>} />
          <Route path="/cours/nouveau" element={<RequireRole roles={['ADMIN']}><CoursFormPage /></RequireRole>} />
          <Route path="/cours/:id/modifier" element={<RequireRole roles={['ADMIN']}><CoursFormPage /></RequireRole>} />
          <Route path="*" element={<LoginPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
