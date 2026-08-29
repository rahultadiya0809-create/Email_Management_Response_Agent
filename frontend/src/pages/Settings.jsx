import { useState, useEffect } from 'react';
import {
  HiOutlineCog6Tooth,
  HiOutlineKey,
  HiOutlineBell,
  HiOutlineEnvelope,
  HiOutlineCpuChip,
  HiOutlineCheckCircle,
  HiOutlineXCircle,
} from 'react-icons/hi2';
import Loader from '../components/Loader';
import {
  getSettings,
  updateSettings,
  trainClassifier,
  testNotification,
} from '../api/emailApi';

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [training, setTraining] = useState(false);
  const [toast, setToast] = useState(null);

  // Form state
  const [geminiKey, setGeminiKey] = useState('');
  const [telegramToken, setTelegramToken] = useState('');
  const [telegramChatId, setTelegramChatId] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const res = await getSettings();
      setSettings(res.data);
    } catch (err) {
      console.error('Settings load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveGemini = async () => {
    if (!geminiKey.trim()) return;
    setSaving(true);
    try {
      await updateSettings({ gemini_api_key: geminiKey });
      showToast('success', 'Gemini API key saved successfully!');
      loadSettings();
    } catch (err) {
      showToast('error', 'Failed to save Gemini API key.');
    } finally {
      setSaving(false);
    }
  };

  const handleSaveTelegram = async () => {
    if (!telegramToken.trim() || !telegramChatId.trim()) return;
    setSaving(true);
    try {
      await updateSettings({
        telegram_bot_token: telegramToken,
        telegram_chat_id: telegramChatId,
      });
      showToast('success', 'Telegram settings saved!');
      loadSettings();
    } catch (err) {
      showToast('error', 'Failed to save Telegram settings.');
    } finally {
      setSaving(false);
    }
  };

  const handleTestTelegram = async () => {
    try {
      const res = await testNotification();
      if (res.data.success) {
        showToast('success', 'Test notification sent! Check your Telegram.');
      } else {
        showToast('error', 'Telegram is not configured. Save your settings first.');
      }
    } catch (err) {
      showToast('error', 'Failed to send test notification.');
    }
  };

  const handleTrainClassifier = async () => {
    setTraining(true);
    try {
      const res = await trainClassifier();
      if (res.data.success) {
        showToast(
          'success',
          `Classifier trained! Accuracy: ${(res.data.accuracy * 100).toFixed(1)}%`
        );
        loadSettings();
      } else {
        showToast('error', res.data.error || 'Training failed.');
      }
    } catch (err) {
      showToast('error', 'Failed to train classifier.');
    } finally {
      setTraining(false);
    }
  };

  const showToast = (type, message) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 4000);
  };

  const StatusIcon = ({ connected }) =>
    connected ? (
      <span className="status-indicator connected">
        <HiOutlineCheckCircle /> Connected
      </span>
    ) : (
      <span className="status-indicator disconnected">
        <HiOutlineXCircle /> Not configured
      </span>
    );

  if (loading) {
    return <Loader text="Loading settings..." />;
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <h1>Settings</h1>
        <p>Configure your Email Management Agent</p>
      </div>

      {/* Gmail Status */}
      <div className="settings-section">
        <div className="settings-section-title">
          <HiOutlineEnvelope style={{ color: 'var(--accent-cyan)' }} />
          Gmail Connection
        </div>
        <div className="settings-card">
          <div className="flex items-center justify-between">
            <div>
              <p style={{ fontSize: '0.9rem', fontWeight: 500 }}>Gmail API</p>
              <p className="text-sm text-tertiary mt-md">
                Authenticate with Google to fetch and send emails.
                Place your <code style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-purple-light)' }}>credentials.json</code> in the backend directory.
              </p>
            </div>
            <StatusIcon connected={settings?.gmail_authenticated} />
          </div>
        </div>
      </div>

      {/* Gemini API */}
      <div className="settings-section">
        <div className="settings-section-title">
          <HiOutlineKey style={{ color: 'var(--accent-purple-light)' }} />
          Google Gemini API
        </div>
        <div className="settings-card">
          <div className="flex items-center justify-between mb-md">
            <p style={{ fontSize: '0.9rem', fontWeight: 500 }}>AI Response Generation</p>
            <StatusIcon connected={settings?.gemini_configured} />
          </div>
          <p className="text-sm text-tertiary mb-md">
            Get a free API key from{' '}
            <a href="https://aistudio.google.com/" target="_blank" rel="noopener noreferrer">
              Google AI Studio
            </a>{' '}
            — no credit card needed.
          </p>
          <div className="form-group">
            <label className="form-label">Gemini API Key</label>
            <input
              type="password"
              className="form-input"
              placeholder="Enter your Gemini API key..."
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
            />
          </div>
          <button
            className="btn btn-primary"
            onClick={handleSaveGemini}
            disabled={saving || !geminiKey.trim()}
          >
            {saving ? 'Saving...' : 'Save API Key'}
          </button>
        </div>
      </div>

      {/* Telegram */}
      <div className="settings-section">
        <div className="settings-section-title">
          <HiOutlineBell style={{ color: 'var(--accent-emerald)' }} />
          Telegram Notifications
        </div>
        <div className="settings-card">
          <div className="flex items-center justify-between mb-md">
            <p style={{ fontSize: '0.9rem', fontWeight: 500 }}>Push Notifications</p>
            <StatusIcon connected={settings?.telegram_configured} />
          </div>
          <p className="text-sm text-tertiary mb-md">
            Create a bot via{' '}
            <a href="https://t.me/botfather" target="_blank" rel="noopener noreferrer">
              @BotFather
            </a>{' '}
            on Telegram to receive high-priority email alerts.
          </p>
          <div className="form-group">
            <label className="form-label">Bot Token</label>
            <input
              type="password"
              className="form-input"
              placeholder="Enter your Telegram bot token..."
              value={telegramToken}
              onChange={(e) => setTelegramToken(e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Chat ID</label>
            <input
              type="text"
              className="form-input"
              placeholder="Enter your Telegram chat ID..."
              value={telegramChatId}
              onChange={(e) => setTelegramChatId(e.target.value)}
            />
          </div>
          <div className="flex gap-sm">
            <button
              className="btn btn-primary"
              onClick={handleSaveTelegram}
              disabled={saving || !telegramToken.trim() || !telegramChatId.trim()}
            >
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleTestTelegram}
            >
              Send Test
            </button>
          </div>
        </div>
      </div>

      {/* Classifier */}
      <div className="settings-section">
        <div className="settings-section-title">
          <HiOutlineCpuChip style={{ color: 'var(--accent-amber)' }} />
          Email Classifier
        </div>
        <div className="settings-card">
          <div className="flex items-center justify-between mb-md">
            <p style={{ fontSize: '0.9rem', fontWeight: 500 }}>ML Classification Model</p>
            <StatusIcon connected={settings?.classifier_trained} />
          </div>
          <p className="text-sm text-tertiary mb-md">
            Train the TF-IDF + Logistic Regression model on the sample dataset.
            This classifies emails as urgent, informational, or promotional.
          </p>
          <button
            className="btn btn-primary"
            onClick={handleTrainClassifier}
            disabled={training}
          >
            <HiOutlineCpuChip />
            {training ? 'Training...' : 'Train Classifier'}
          </button>
        </div>
      </div>

      {/* Priority Weights */}
      <div className="settings-section">
        <div className="settings-section-title">
          <HiOutlineCog6Tooth style={{ color: 'var(--text-tertiary)' }} />
          Priority Scoring Weights
        </div>
        <div className="settings-card">
          <p className="text-sm text-tertiary mb-md">
            The priority score is calculated using a weighted formula:
          </p>
          <code style={{
            display: 'block',
            padding: '12px 16px',
            background: 'var(--bg-tertiary)',
            borderRadius: 'var(--radius-md)',
            fontSize: '0.82rem',
            fontFamily: 'var(--font-mono)',
            color: 'var(--accent-cyan)',
            marginBottom: '16px',
          }}>
            priority = {settings?.classifier_weight || 0.6} × classifier
            + {settings?.sender_weight || 0.2} × sender
            + {settings?.keyword_weight || 0.2} × keywords
          </code>
          <p className="text-xs text-tertiary">
            Adjust weights in the backend <code style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-purple-light)' }}>.env</code> file.
          </p>
        </div>
      </div>

      {/* Toast */}
      {toast && (
        <div className="toast-container">
          <div className={`toast ${toast.type}`}>
            <span>{toast.type === 'success' ? '✅' : '❌'}</span>
            <span>{toast.message}</span>
          </div>
        </div>
      )}
    </div>
  );
}
