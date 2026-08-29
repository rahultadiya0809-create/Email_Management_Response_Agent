import { useState } from 'react';
import {
  HiOutlineArrowUturnLeft,
  HiOutlineArchiveBox,
  HiOutlineSparkles,
  HiOutlineTag,
} from 'react-icons/hi2';
import PriorityBadge from './PriorityBadge';
import CategoryTag from './CategoryTag';
import DraftReply from './DraftReply';
import {
  getSenderName,
  getSenderEmail,
  getInitials,
  formatFullDate,
  formatPriorityScore,
  stringToColor,
} from '../utils/helpers';

export default function EmailDetail({
  email,
  onArchive,
  onGenerateDraft,
  onSendReply,
  draft,
  draftLoading,
}) {
  const [showDraft, setShowDraft] = useState(false);

  if (!email) {
    return (
      <div className="empty-state" style={{ minHeight: '50vh' }}>
        <div className="empty-state-icon">📬</div>
        <div className="empty-state-title">Select an email</div>
        <div className="empty-state-text">
          Choose an email from the list to view its details, classification, and generate AI-powered replies.
        </div>
      </div>
    );
  }

  const senderName = getSenderName(email.from || email.sender);
  const senderEmail = getSenderEmail(email.from || email.sender);
  const initials = getInitials(senderName);
  const avatarColor = stringToColor(senderName);

  const category = email.category || email.classification?.category;
  const priorityLevel = email.priority_level || email.priority?.level;
  const priorityScore = email.priority_score || email.priority?.score;
  const confidence = email.category_confidence || email.classification?.confidence;

  const handleGenerateDraft = () => {
    setShowDraft(true);
    onGenerateDraft?.(email.id);
  };

  return (
    <div className="fade-in">
      <div className="email-detail">
        {/* Header */}
        <div className="email-detail-header">
          <div className="email-detail-subject">
            {email.subject || '(No Subject)'}
          </div>

          <div className="email-detail-meta">
            <div className="email-detail-sender-info">
              <div
                className="email-card-avatar"
                style={{ background: avatarColor }}
              >
                {initials}
              </div>
              <div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>
                  {senderName}
                </div>
                <div className="text-xs text-tertiary">{senderEmail}</div>
              </div>
            </div>

            <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
              {priorityLevel && <PriorityBadge level={priorityLevel} />}
              {category && <CategoryTag category={category} />}
            </div>
          </div>

          {/* Priority & Classification Info */}
          <div style={{ marginTop: '16px', display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
            {priorityScore != null && (
              <div className="text-sm">
                <span className="text-tertiary">Priority Score: </span>
                <span style={{ fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
                  {formatPriorityScore(priorityScore)}
                </span>
                {/* Priority Bar */}
                <div className="priority-bar" style={{ marginTop: '6px', width: '140px' }}>
                  <div
                    className={`priority-bar-fill ${(priorityLevel || 'low').toLowerCase()}`}
                    style={{ width: `${priorityScore * 100}%` }}
                  />
                </div>
              </div>
            )}

            {confidence != null && (
              <div className="text-sm">
                <span className="text-tertiary">Classification Confidence: </span>
                <span style={{ fontWeight: 600, fontFamily: 'var(--font-mono)' }}>
                  {Math.round(confidence * 100)}%
                </span>
              </div>
            )}

            <div className="text-sm text-tertiary">
              {formatFullDate(email.date)}
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="email-detail-body">
          {email.body || email.snippet || 'No content available.'}
        </div>

        {/* Actions */}
        <div className="email-detail-actions">
          <button
            className="btn btn-primary"
            onClick={handleGenerateDraft}
          >
            <HiOutlineSparkles />
            AI Draft Reply
          </button>

          <button
            className="btn btn-secondary"
            onClick={() => onArchive?.(email.id)}
          >
            <HiOutlineArchiveBox />
            Archive
          </button>
        </div>
      </div>

      {/* Draft Reply Panel */}
      {showDraft && (
        <DraftReply
          draft={draft}
          loading={draftLoading}
          onSend={(text) => onSendReply?.(email.id, text)}
          onDiscard={() => setShowDraft(false)}
        />
      )}
    </div>
  );
}
