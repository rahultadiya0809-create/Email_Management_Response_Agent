import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  HiOutlineArrowPath,
  HiOutlineFunnel,
  HiOutlineMagnifyingGlass,
  HiOutlineCloudArrowDown,
} from 'react-icons/hi2';
import EmailList from '../components/EmailList';
import EmailDetail from '../components/EmailDetail';
import Loader from '../components/Loader';
import {
  fetchEmails,
  getCachedEmails,
  generateDraftReply,
  sendReply,
  archiveEmail,
} from '../api/emailApi';

export default function Inbox() {
  const [searchParams] = useSearchParams();
  const categoryFilter = searchParams.get('category');

  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [activeFilter, setActiveFilter] = useState(categoryFilter || 'all');
  const [searchQuery, setSearchQuery] = useState('');
  const [draft, setDraft] = useState(null);
  const [draftLoading, setDraftLoading] = useState(false);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    loadEmails();
  }, []);

  useEffect(() => {
    if (categoryFilter) {
      setActiveFilter(categoryFilter);
    }
  }, [categoryFilter]);

  const loadEmails = async () => {
    setLoading(true);
    try {
      // First try loading from cache
      const res = await getCachedEmails({ max_results: 50 });
      const cachedEmails = res.data.emails || [];

      if (cachedEmails.length > 0) {
        setEmails(cachedEmails);
      } else {
        // No cached emails — auto-fetch from Gmail
        setFetching(true);
        try {
          const gmailRes = await fetchEmails({ max_results: 20 });
          setEmails(gmailRes.data.emails || []);
        } catch (fetchErr) {
          console.error('Auto-fetch from Gmail failed:', fetchErr);
          setEmails([]);
        } finally {
          setFetching(false);
        }
      }
    } catch (err) {
      console.error('Error loading emails:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFetchFromGmail = async () => {
    setFetching(true);
    try {
      const res = await fetchEmails({ max_results: 20 });
      setEmails(res.data.emails || []);
      showToast('success', `Fetched ${res.data.total} emails from Gmail`);
    } catch (err) {
      showToast('error', 'Failed to fetch emails. Check Gmail connection.');
      console.error('Fetch error:', err);
    } finally {
      setFetching(false);
    }
  };

  const handleSelectEmail = (email) => {
    setSelectedEmail(email);
    setDraft(null);
  };

  const handleGenerateDraft = async (emailId) => {
    setDraftLoading(true);
    try {
      const res = await generateDraftReply(emailId);
      setDraft(res.data);
    } catch (err) {
      showToast('error', 'Failed to generate draft reply.');
      console.error('Draft error:', err);
    } finally {
      setDraftLoading(false);
    }
  };

  const handleSendReply = async (emailId, replyText) => {
    try {
      await sendReply(emailId, replyText);
      showToast('success', 'Reply sent successfully!');
      setDraft(null);
    } catch (err) {
      showToast('error', 'Failed to send reply.');
      console.error('Send error:', err);
    }
  };

  const handleArchive = async (emailId) => {
    try {
      await archiveEmail(emailId);
      setEmails(emails.filter((e) => e.id !== emailId));
      if (selectedEmail?.id === emailId) {
        setSelectedEmail(null);
      }
      showToast('success', 'Email archived.');
    } catch (err) {
      showToast('error', 'Failed to archive email.');
      console.error('Archive error:', err);
    }
  };

  const showToast = (type, message) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 4000);
  };

  // Filter emails
  const filteredEmails = emails.filter((email) => {
    const category = email.category || email.classification?.category || '';
    const matchesFilter = activeFilter === 'all' || category === activeFilter;

    const matchesSearch =
      !searchQuery ||
      (email.subject || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (email.from || email.sender || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (email.snippet || '').toLowerCase().includes(searchQuery.toLowerCase());

    return matchesFilter && matchesSearch;
  });

  const filters = [
    { key: 'all', label: 'All' },
    { key: 'urgent', label: 'Urgent' },
    { key: 'informational', label: 'Informational' },
    { key: 'promotional', label: 'Promotional' },
  ];

  return (
    <div className="fade-in">
      <div className="page-header">
        <div className="flex items-center justify-between">
          <div>
            <h1>Inbox</h1>
            <p>{filteredEmails.length} emails{activeFilter !== 'all' ? ` • ${activeFilter}` : ''}</p>
          </div>
          <div className="flex gap-sm">
            <button
              className="btn btn-primary"
              onClick={handleFetchFromGmail}
              disabled={fetching}
            >
              <HiOutlineCloudArrowDown />
              {fetching ? 'Fetching...' : 'Fetch from Gmail'}
            </button>
            <button className="btn btn-secondary" onClick={loadEmails}>
              <HiOutlineArrowPath />
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-bar">
        <HiOutlineFunnel style={{ color: 'var(--text-tertiary)' }} />
        {filters.map((filter) => (
          <button
            key={filter.key}
            className={`filter-chip ${activeFilter === filter.key ? 'active' : ''}`}
            onClick={() => setActiveFilter(filter.key)}
          >
            {filter.label}
          </button>
        ))}

        <div className="search-box">
          <HiOutlineMagnifyingGlass className="search-icon" />
          <input
            type="text"
            placeholder="Search emails..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Main Content */}
      {loading ? (
        <Loader text="Loading emails..." />
      ) : (
        <div className="inbox-layout">
          {/* Email List Panel */}
          <div className="inbox-list-panel">
            <EmailList
              emails={filteredEmails}
              selectedId={selectedEmail?.id}
              onSelectEmail={handleSelectEmail}
            />
          </div>

          {/* Email Detail Panel */}
          <div className="inbox-detail-panel">
            <EmailDetail
              email={selectedEmail}
              onArchive={handleArchive}
              onGenerateDraft={handleGenerateDraft}
              onSendReply={handleSendReply}
              draft={draft}
              draftLoading={draftLoading}
            />
          </div>
        </div>
      )}

      {/* Toast Notification */}
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
