import { Navigate, Route, Routes } from 'react-router-dom';

import DashboardLayout from './layouts/DashboardLayout';
import { useAuth } from './hooks/useAuth';

import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import GenerateCodes from './pages/GenerateCodes';
import Batches from './pages/Batches';
import BatchDetail from './pages/BatchDetail';
import Products from './pages/Products';
import Quantities from './pages/Quantities';
import WhatsappPresets from './pages/WhatsappPresets';
import ZohoSettings from './pages/ZohoSettings';
import ShortDomainSettings from './pages/ShortDomainSettings';

function Protected({ children }) {
  const { isAuthed } = useAuth();
  if (!isAuthed) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route
        path="/"
        element={
          <Protected>
            <DashboardLayout />
          </Protected>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="generate" element={<GenerateCodes />} />
        <Route path="batches" element={<Batches />} />
        <Route path="batches/:id" element={<BatchDetail />} />
        <Route path="products" element={<Products />} />
        <Route path="quantities" element={<Quantities />} />
        <Route path="presets" element={<WhatsappPresets />} />
        <Route path="settings/zoho" element={<ZohoSettings />} />
        <Route path="settings/short-domain" element={<ShortDomainSettings />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
