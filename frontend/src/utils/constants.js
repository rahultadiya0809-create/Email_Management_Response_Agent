/**
 * Application Constants
 */

export const PRIORITY_LEVELS = {
  CRITICAL: { label: 'Critical', color: '#ef4444', bgColor: 'rgba(239, 68, 68, 0.12)', icon: '🔴' },
  HIGH:     { label: 'High',     color: '#f97316', bgColor: 'rgba(249, 115, 22, 0.12)', icon: '🟠' },
  MEDIUM:   { label: 'Medium',   color: '#eab308', bgColor: 'rgba(234, 179, 8, 0.12)',  icon: '🟡' },
  LOW:      { label: 'Low',      color: '#22c55e', bgColor: 'rgba(34, 197, 94, 0.12)',   icon: '🟢' },
};

export const CATEGORIES = {
  urgent:        { label: 'Urgent',        color: '#ef4444', bgColor: 'rgba(239, 68, 68, 0.12)' },
  informational: { label: 'Informational', color: '#3b82f6', bgColor: 'rgba(59, 130, 246, 0.12)' },
  promotional:   { label: 'Promotional',   color: '#a855f7', bgColor: 'rgba(168, 85, 247, 0.12)' },
  spam:          { label: 'Spam',          color: '#6b7280', bgColor: 'rgba(107, 114, 128, 0.12)' },
};

export const DRAFT_STATUS = {
  DRAFT:     'draft',
  APPROVED:  'approved',
  SENT:      'sent',
  DISCARDED: 'discarded',
};
