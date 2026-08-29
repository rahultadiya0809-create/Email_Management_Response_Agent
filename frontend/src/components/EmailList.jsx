import EmailCard from './EmailCard';

export default function EmailList({ emails, selectedId, onSelectEmail }) {
  if (!emails || emails.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📭</div>
        <div className="empty-state-title">No emails found</div>
        <div className="empty-state-text">
          Fetch emails from Gmail or adjust your filters to see emails here.
        </div>
      </div>
    );
  }

  return (
    <div className="email-list">
      {emails.map((email, index) => (
        <EmailCard
          key={email.id}
          email={email}
          isSelected={email.id === selectedId}
          onClick={onSelectEmail}
        />
      ))}
    </div>
  );
}
