import { useState, useEffect, useRef } from 'react';
import { getAuthUrl, getAuthStatus } from '../api/emailApi';

export default function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [fetchingEmails, setFetchingEmails] = useState(false);
  const [error, setError] = useState('');
  const pollTimerRef = useRef(null);

  useEffect(() => {
    const handleAuthMessage = async (event) => {
      if (event.data?.type === 'GOOGLE_AUTH_SUCCESS') {
        clearInterval(pollTimerRef.current);
        setLoading(false);
        setFetchingEmails(true);
        await onLoginSuccess?.();
      }
    };

    window.addEventListener('message', handleAuthMessage);
    return () => {
      window.removeEventListener('message', handleAuthMessage);
      clearInterval(pollTimerRef.current);
    };
  }, [onLoginSuccess]);

  const handleLogin = async (e) => {
    e?.preventDefault();

    if (email.trim() && (!email.includes('@') || !email.toLowerCase().includes('gmail'))) {
      setError('Please enter a valid Gmail address (e.g. yourname@gmail.com).');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const res = await getAuthUrl(email.trim());
      if (res.data.success && res.data.auth_url) {
        const width = 520;
        const height = 650;
        const left = window.screen.width / 2 - width / 2;
        const top = window.screen.height / 2 - height / 2;

        const popup = window.open(
          res.data.auth_url,
          'GoogleAccountSignIn',
          `width=${width},height=${height},top=${top},left=${left},scrollbars=yes,status=yes`
        );

        if (!popup || popup.closed || typeof popup.closed === 'undefined') {
          setError('Popup blocked by browser. Please allow popups for localhost and try again.');
          setLoading(false);
          return;
        }

        // Poll in case postMessage does not trigger or window is closed after login
        clearInterval(pollTimerRef.current);
        pollTimerRef.current = setInterval(async () => {
          try {
            const statusRes = await getAuthStatus();
            if (statusRes.data.authenticated) {
              clearInterval(pollTimerRef.current);
              try {
                popup.close();
              } catch (_) {}
              setLoading(false);
              setFetchingEmails(true);
              await onLoginSuccess?.();
            } else if (popup.closed) {
              clearInterval(pollTimerRef.current);
              setLoading(false);
            }
          } catch (_) {}
        }, 1200);
      } else {
        setError(res.data.error || 'Failed to initiate Google sign in.');
        setLoading(false);
      }
    } catch (err) {
      const message =
        err.response?.data?.error ||
        err.response?.data?.help ||
        'Failed to connect to the backend server. Make sure Flask is running.';
      setError(message);
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card fade-in-up">
        <div className="login-logo">📧</div>

        <h1 className="login-title">Email Agent</h1>
        <p className="login-subtitle">
          AI-powered email management &amp; response assistant
        </p>

        <form onSubmit={handleLogin} style={{ width: '100%' }}>
          {/* Email Input Field */}
          <div style={{ marginBottom: '16px' }}>
            <label
              htmlFor="email-input"
              style={{
                display: 'block',
                fontSize: '0.78rem',
                fontWeight: 600,
                color: 'var(--text-secondary)',
                marginBottom: '8px',
                textAlign: 'left',
              }}
            >
              Gmail Address
            </label>
            <input
              id="email-input"
              type="email"
              placeholder="yourname@gmail.com"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                if (error) setError('');
              }}
              disabled={loading || fetchingEmails}
              autoFocus
              autoComplete="email"
              style={{
                width: '100%',
                padding: '12px 16px',
                fontSize: '0.9rem',
                fontFamily: 'var(--font-body)',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--border-primary)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                outline: 'none',
                transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
                boxSizing: 'border-box',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = 'var(--accent-purple)';
                e.target.style.boxShadow = '0 0 0 3px rgba(99, 102, 241, 0.1)';
                e.target.style.background = 'var(--bg-secondary)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = 'var(--border-primary)';
                e.target.style.boxShadow = 'none';
                e.target.style.background = 'var(--bg-tertiary)';
              }}
            />
          </div>

          {/* Sign In Button */}
          <button
            type="submit"
            className="google-btn"
            disabled={loading || fetchingEmails}
            style={{ marginBottom: '16px', width: '100%' }}
          >
            <svg width="20" height="20" viewBox="0 0 48 48">
              <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
              <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
              <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
              <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
            </svg>
            {fetchingEmails ? 'Fetching Emails...' : loading ? 'Connecting...' : 'Sign in with Google'}
          </button>
        </form>

        {error && (
          <div style={{
            marginTop: '16px',
            padding: '12px 16px',
            background: 'rgba(225, 29, 72, 0.05)',
            border: '1px solid rgba(225, 29, 72, 0.15)',
            borderRadius: 'var(--radius-md)',
            color: 'var(--accent-rose)',
            fontSize: '0.82rem',
            textAlign: 'left',
          }}>
            {error}
          </div>
        )}

        <div style={{ marginTop: '24px' }}>
          <p className="text-xs text-tertiary" style={{ lineHeight: 1.6 }}>
            Enter your Gmail address and sign in via Google OAuth 2.0.
            <br />
            Your credentials are stored locally — never on any server.
          </p>
        </div>
      </div>
    </div>
  );
}
