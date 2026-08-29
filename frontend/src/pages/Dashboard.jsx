import { useState, useEffect } from 'react';
import {
  HiOutlineArrowPath,
  HiOutlineInbox,
  HiOutlineClock,
  HiOutlineChartBar,
} from 'react-icons/hi2';
import StatsPanel from '../components/StatsPanel';
import EmailCard from '../components/EmailCard';
import Loader from '../components/Loader';
import { getStats, getCachedEmails, getActivity } from '../api/emailApi';

export default function Dashboard({ onNavigateToEmail }) {
  const [stats, setStats] = useState(null);
  const [recentEmails, setRecentEmails] = useState([]);
  const [activity, setActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const [statsRes, emailsRes, activityRes] = await Promise.allSettled([
        getStats(),
        getCachedEmails({ max_results: 5, source: 'db' }),
        getActivity(10),
      ]);

      if (statsRes.status === 'fulfilled') setStats(statsRes.value.data);
      if (emailsRes.status === 'fulfilled') setRecentEmails(emailsRes.value.data.emails || []);
      if (activityRes.status === 'fulfilled') setActivity(activityRes.value.data.activity || []);
    } catch (err) {
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loader text="Loading dashboard..." />;
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1>Dashboard</h1>
            <p>Overview of your email management agent</p>
          </div>
          <button className="btn btn-secondary" onClick={loadDashboard}>
            <HiOutlineArrowPath />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <StatsPanel stats={stats} />

      {/* Content Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
        {/* Recent High-Priority Emails */}
        <div className="glass-card" style={{ gridColumn: window.innerWidth <= 768 ? '1 / -1' : undefined }}>
          <div className="flex items-center justify-between mb-md">
            <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <HiOutlineInbox style={{ color: 'var(--accent-purple-light)' }} />
              Recent Emails
            </h3>
          </div>

          {recentEmails.length > 0 ? (
            <div className="email-list">
              {recentEmails.slice(0, 5).map((email) => (
                <EmailCard
                  key={email.id}
                  email={email}
                  onClick={() => onNavigateToEmail?.(email)}
                />
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">📭</div>
              <div className="empty-state-title">No emails yet</div>
              <div className="empty-state-text">
                Go to Inbox and fetch emails from Gmail to get started.
              </div>
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <div className="glass-card" style={{ gridColumn: window.innerWidth <= 768 ? '1 / -1' : undefined }}>
          <div className="flex items-center justify-between mb-md">
            <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <HiOutlineClock style={{ color: 'var(--accent-cyan)' }} />
              Recent Activity
            </h3>
          </div>

          {activity.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {activity.map((item, index) => (
                <div
                  key={item.id || index}
                  className="fade-in-up"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '8px 12px',
                    background: 'var(--bg-tertiary)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.82rem',
                  }}
                >
                  <span style={{ fontSize: '1rem' }}>
                    {item.action === 'classified' && '🏷️'}
                    {item.action === 'draft_generated' && '✨'}
                    {item.action === 'reply_sent' && '📤'}
                    {item.action === 'archived' && '📦'}
                    {item.action === 'reclassified' && '🔄'}
                    {item.action === 'draft_edited' && '✏️'}
                    {!['classified', 'draft_generated', 'reply_sent', 'archived', 'reclassified', 'draft_edited'].includes(item.action) && '📋'}
                  </span>
                  <span className="text-secondary" style={{ flex: 1 }}>
                    {item.action.replace(/_/g, ' ')}
                  </span>
                  {item.details && (
                    <span className="category-tag" style={{ fontSize: '0.65rem' }}>
                      {item.details}
                    </span>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">📊</div>
              <div className="empty-state-title">No activity yet</div>
              <div className="empty-state-text">
                Start processing emails to see activity here.
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Priority Distribution */}
      {stats?.by_priority && Object.keys(stats.by_priority).length > 0 && (
        <div className="glass-card mt-lg">
          <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <HiOutlineChartBar style={{ color: 'var(--accent-emerald)' }} />
            Priority Distribution
          </h3>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            {Object.entries(stats.by_priority).map(([level, count]) => (
              <div
                key={level}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 16px',
                  background: 'var(--bg-tertiary)',
                  borderRadius: 'var(--radius-md)',
                }}
              >
                <span className={`priority-badge ${level.toLowerCase()}`}>
                  {level}
                </span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, fontSize: '1.1rem' }}>
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
