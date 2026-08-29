import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Inbox from './pages/Inbox';
import Settings from './pages/Settings';
import Login from './pages/Login';
import { checkHealth, getStats, fetchEmails, logout as logoutApi } from './api/emailApi';

function AppContent() {
  const [authenticated, setAuthenticated] = useState(false);
  const [backendOnline, setBackendOnline] = useState(false);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    setLoading(true);
    try {
      const healthRes = await checkHealth();
      setBackendOnline(true);

      const services = healthRes.data.services || {};
      setAuthenticated(services.gmail || false);

      // Load stats
      try {
        const statsRes = await getStats();
        setStats(statsRes.data);
      } catch {
        // Stats may fail if no emails processed yet
      }
    } catch (err) {
      setBackendOnline(false);
      console.error('Backend not available:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSuccess = async () => {
    setAuthenticated(true);

    // Auto-fetch emails from Gmail right after login
    try {
      await fetchEmails({ max_results: 20 });
    } catch (err) {
      console.error('Auto-fetch after login failed:', err);
    }

    // Refresh stats then navigate to inbox
    await initializeApp();
    navigate('/');
  };

  const handleLogout = async () => {
    try {
      await logoutApi();
    } catch (err) {
      console.error('Logout error:', err);
    }
    setAuthenticated(false);
    setStats(null);
    navigate('/');
  };

  const handleNavigateToEmail = (email) => {
    navigate('/inbox');
  };

  // Loading screen
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        flexDirection: 'column',
        gap: '16px',
      }}>
        <div className="sidebar-logo" style={{ width: 64, height: 64, fontSize: '2rem' }}>
          📧
        </div>
        <div className="spinner" />
        <div className="text-secondary text-sm">Connecting to Email Agent...</div>
      </div>
    );
  }

  // Backend offline
  if (!backendOnline) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        flexDirection: 'column',
        gap: '16px',
        padding: '24px',
        textAlign: 'center',
      }}>
        <div style={{ fontSize: '3rem' }}>🔌</div>
        <h2 style={{
          fontFamily: 'var(--font-display)',
          fontSize: '1.5rem',
          fontWeight: 700,
          color: 'var(--text-primary)',
        }}>
          Backend Not Connected
        </h2>
        <p className="text-secondary" style={{ maxWidth: '400px' }}>
          Start the Flask backend server to connect:
        </p>
        <code style={{
          display: 'block',
          padding: '16px 24px',
          background: 'var(--bg-tertiary)',
          borderRadius: 'var(--radius-md)',
          fontFamily: 'var(--font-mono)',
          fontSize: '0.85rem',
          color: 'var(--accent-cyan)',
        }}>
          cd backend && python app.py
        </code>
        <button
          className="btn btn-primary"
          onClick={initializeApp}
          style={{ marginTop: '8px' }}
        >
          Retry Connection
        </button>
      </div>
    );
  }

  // Not authenticated — show Login page (blocks all other routes)
  if (!authenticated) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  // Authenticated — show full app
  return (
    <div className="app-layout">
      <Sidebar stats={stats} onLogout={handleLogout} />
      <main className="main-content">
        <Routes>
          <Route
            path="/"
            element={<Dashboard onNavigateToEmail={handleNavigateToEmail} />}
          />
          <Route path="/inbox" element={<Inbox />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Dashboard onNavigateToEmail={handleNavigateToEmail} />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}
