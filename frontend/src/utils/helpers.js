/**
 * Utility / Helper Functions
 */

/**
 * Extract sender name from email "From" string.
 * e.g., "John Doe <john@example.com>" -> "John Doe"
 */
export function getSenderName(from) {
  if (!from) return 'Unknown';
  const match = from.match(/^([^<]+)/);
  if (match) {
    const name = match[1].trim().replace(/"/g, '');
    return name || from;
  }
  return from.split('@')[0];
}

/**
 * Extract sender email from "From" string.
 */
export function getSenderEmail(from) {
  if (!from) return '';
  const match = from.match(/<(.+?)>/);
  return match ? match[1] : from;
}

/**
 * Get initials from a name string (for avatar).
 */
export function getInitials(name) {
  if (!name) return '?';
  const parts = name.trim().split(/\s+/);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }
  return name.substring(0, 2).toUpperCase();
}

/**
 * Format a date string to a human-readable relative time.
 */
export function formatRelativeTime(dateStr) {
  if (!dateStr) return '';
  try {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateStr;
  }
}

/**
 * Format a date string to full readable format.
 */
export function formatFullDate(dateStr) {
  if (!dateStr) return '';
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return dateStr;
  }
}

/**
 * Truncate text to a max length with ellipsis.
 */
export function truncateText(text, maxLength = 100) {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
}

/**
 * Format a priority score as percentage.
 */
export function formatPriorityScore(score) {
  return `${Math.round(score * 100)}%`;
}

/**
 * Generate a consistent color based on a string (for avatars).
 */
export function stringToColor(str) {
  const colors = [
    '#7c3aed', '#06b6d4', '#10b981', '#f59e0b', '#ef4444',
    '#ec4899', '#8b5cf6', '#14b8a6', '#f97316', '#6366f1',
  ];
  let hash = 0;
  for (let i = 0; i < (str || '').length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
}
