import {
  HiOutlineInbox,
  HiOutlineEnvelope,
  HiOutlineBell,
  HiOutlineSparkles,
  HiOutlineShieldCheck,
} from 'react-icons/hi2';

export default function StatsPanel({ stats }) {
  const cards = [
    {
      label: 'Total Emails',
      value: stats?.total_emails ?? 0,
      icon: <HiOutlineInbox />,
      colorClass: 'purple',
    },
    {
      label: 'Unread',
      value: stats?.unread ?? 0,
      icon: <HiOutlineEnvelope />,
      colorClass: 'cyan',
    },
    {
      label: 'Urgent',
      value: stats?.by_category?.urgent ?? 0,
      icon: <HiOutlineBell />,
      colorClass: 'rose',
    },
    {
      label: 'Informational',
      value: stats?.by_category?.informational ?? 0,
      icon: <HiOutlineSparkles />,
      colorClass: 'emerald',
    },
    {
      label: 'Promotional',
      value: stats?.by_category?.promotional ?? 0,
      icon: <HiOutlineShieldCheck />,
      colorClass: 'amber',
    },
  ];

  return (
    <div className="stats-grid">
      {cards.map((card, index) => (
        <div
          key={card.label}
          className={`stat-card fade-in-up stagger-${index + 1}`}
        >
          <div className={`stat-card-icon ${card.colorClass}`}>
            {card.icon}
          </div>
          <div>
            <div className="stat-card-value">{card.value}</div>
            <div className="stat-card-label">{card.label}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
