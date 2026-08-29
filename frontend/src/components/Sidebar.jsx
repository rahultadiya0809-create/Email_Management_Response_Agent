import { NavLink, useLocation } from 'react-router-dom';
import { useState } from 'react';
import {
  HiOutlineInbox,
  HiOutlineChartBar,
  HiOutlineCog6Tooth,
  HiOutlineSparkles,
  HiOutlineBell,
  HiOutlineShieldCheck,
  HiOutlineBars3,
  HiOutlineXMark,
  HiOutlineArrowRightOnRectangle,
} from 'react-icons/hi2';

export default function Sidebar({ stats, onLogout }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    {
      section: 'Main',
      items: [
        { path: '/', label: 'Dashboard', icon: <HiOutlineChartBar />, badge: null },
        { path: '/inbox', label: 'Inbox', icon: <HiOutlineInbox />, badge: stats?.unread || null },
      ],
    },
    {
      section: 'Categories',
      items: [
        { path: '/inbox?category=urgent', label: 'Urgent', icon: <HiOutlineBell />, badge: stats?.by_category?.urgent || null },
        { path: '/inbox?category=informational', label: 'Informational', icon: <HiOutlineSparkles />, badge: stats?.by_category?.informational || null },
        { path: '/inbox?category=promotional', label: 'Promotional', icon: <HiOutlineShieldCheck />, badge: stats?.by_category?.promotional || null },
      ],
    },
    {
      section: 'System',
      items: [
        { path: '/settings', label: 'Settings', icon: <HiOutlineCog6Tooth />, badge: null },
      ],
    },
  ];

  const toggleMobile = () => setMobileOpen(!mobileOpen);

  return (
    <>
      {/* Mobile hamburger button */}
      <button
        className="btn-icon"
        onClick={toggleMobile}
        style={{
          position: 'fixed',
          top: 16,
          left: 16,
          zIndex: 101,
          display: 'none',
        }}
        id="mobile-menu-btn"
      >
        {mobileOpen ? <HiOutlineXMark /> : <HiOutlineBars3 />}
      </button>

      {/* Mobile overlay */}
      <div
        className={`sidebar-overlay ${mobileOpen ? 'visible' : ''}`}
        onClick={() => setMobileOpen(false)}
      />

      {/* Sidebar */}
      <aside className={`sidebar ${mobileOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">📧</div>
          <div>
            <div className="sidebar-title">Email Agent</div>
            <div className="sidebar-subtitle">AI-Powered Inbox</div>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((section) => (
            <div key={section.section}>
              <div className="sidebar-section-label">{section.section}</div>
              {section.items.map((item) => (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `nav-item ${isActive && location.search === '' ? 'active' : ''}`
                  }
                  onClick={() => setMobileOpen(false)}
                >
                  <span className="nav-item-icon">{item.icon}</span>
                  <span>{item.label}</span>
                  {item.badge > 0 && (
                    <span className="nav-item-badge">{item.badge}</span>
                  )}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-status" style={{ marginBottom: '12px' }}>
            <span className={`status-dot ${stats ? 'online' : 'offline'}`} />
            <span>{stats ? 'Agent Active' : 'Connecting...'}</span>
          </div>

          {/* Logout Button */}
          <button
            onClick={onLogout}
            className="btn-logout"
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '10px 14px',
              borderRadius: 'var(--radius-md)',
              background: 'var(--bg-tertiary)',
              color: 'var(--text-secondary)',
              fontSize: '0.85rem',
              fontWeight: 500,
              border: '1px solid var(--border-subtle)',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(225, 29, 72, 0.06)';
              e.currentTarget.style.color = 'var(--accent-rose)';
              e.currentTarget.style.borderColor = 'rgba(225, 29, 72, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'var(--bg-tertiary)';
              e.currentTarget.style.color = 'var(--text-secondary)';
              e.currentTarget.style.borderColor = 'var(--border-subtle)';
            }}
          >
            <HiOutlineArrowRightOnRectangle style={{ fontSize: '1.15rem' }} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Mobile bottom nav */}
      <nav className="mobile-nav">
        <div className="mobile-nav-items">
          <NavLink to="/" className={({ isActive }) => `mobile-nav-item ${isActive ? 'active' : ''}`}>
            <HiOutlineChartBar className="icon" />
            <span>Dashboard</span>
          </NavLink>
          <NavLink to="/inbox" className={({ isActive }) => `mobile-nav-item ${isActive ? 'active' : ''}`}>
            <HiOutlineInbox className="icon" />
            <span>Inbox</span>
          </NavLink>
          <NavLink to="/settings" className={({ isActive }) => `mobile-nav-item ${isActive ? 'active' : ''}`}>
            <HiOutlineCog6Tooth className="icon" />
            <span>Settings</span>
          </NavLink>
          <button
            onClick={onLogout}
            className="mobile-nav-item"
            style={{ background: 'none', border: 'none' }}
          >
            <HiOutlineArrowRightOnRectangle className="icon" />
            <span>Logout</span>
          </button>
        </div>
      </nav>

      <style>{`
        @media (max-width: 768px) {
          #mobile-menu-btn { display: flex !important; }
        }
      `}</style>
    </>
  );
}
