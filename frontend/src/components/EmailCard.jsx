import PriorityBadge from './PriorityBadge';
import CategoryTag from './CategoryTag';
import { getSenderName, getInitials, formatRelativeTime, stringToColor } from '../utils/helpers';

export default function EmailCard({ email, isSelected, onClick }) {
  const senderName = getSenderName(email.from || email.sender);
  const initials = getInitials(senderName);
  const avatarColor = stringToColor(senderName);
  const isUnread = !email.is_read;

  const category = email.category || email.classification?.category;
  const priorityLevel = email.priority_level || email.priority?.level;

  return (
    <div
      className={`email-card ${isUnread ? 'unread' : ''} ${isSelected ? 'selected' : ''} fade-in-up`}
      onClick={() => onClick?.(email)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick?.(email)}
    >
      <div
        className="email-card-avatar"
        style={{ background: avatarColor }}
      >
        {initials}
      </div>

      <div className="email-card-content">
        <div className="email-card-header">
          <span className="email-card-sender">{senderName}</span>
          <span className="email-card-time">
            {formatRelativeTime(email.date)}
          </span>
        </div>

        <div className="email-card-subject">
          {email.subject || '(No Subject)'}
        </div>

        <div className="email-card-snippet">
          {email.snippet || ''}
        </div>

        <div className="email-card-meta">
          {priorityLevel && <PriorityBadge level={priorityLevel} />}
          {category && <CategoryTag category={category} />}
        </div>
      </div>
    </div>
  );
}
