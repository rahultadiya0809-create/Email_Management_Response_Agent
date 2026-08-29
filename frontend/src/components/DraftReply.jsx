import { useState, useEffect } from 'react';
import {
  HiOutlinePaperAirplane,
  HiOutlineTrash,
  HiOutlinePencilSquare,
  HiOutlineSparkles,
} from 'react-icons/hi2';
import Loader from './Loader';

export default function DraftReply({ draft, loading, onSend, onDiscard }) {
  const [editedText, setEditedText] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [sending, setSending] = useState(false);

  useEffect(() => {
    if (draft?.draft_text) {
      setEditedText(draft.draft_text);
    }
  }, [draft]);

  const handleSend = async () => {
    setSending(true);
    try {
      await onSend?.(editedText);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="draft-panel fade-in-up">
      <div className="draft-panel-header">
        <div className="draft-panel-title">
          <HiOutlineSparkles />
          AI Draft Reply
          {draft?.generated_by && (
            <span className="ai-badge">
              {draft.generated_by === 'gemini' ? 'Gemini AI' : 'Template'}
            </span>
          )}
        </div>
      </div>

      {loading ? (
        <Loader text="Generating AI draft reply..." />
      ) : (
        <>
          <div className="draft-editor">
            <textarea
              value={editedText}
              onChange={(e) => {
                setEditedText(e.target.value);
                setIsEditing(true);
              }}
              placeholder="AI-generated reply will appear here..."
              className="form-input form-textarea"
            />
          </div>

          {/* Suggestions */}
          {draft?.suggestions && draft.suggestions.length > 0 && (
            <div className="draft-suggestions">
              {draft.suggestions.map((suggestion, index) => (
                <div key={index} className="suggestion-item">
                  {suggestion}
                </div>
              ))}
            </div>
          )}

          <div className="draft-actions">
            <div className="flex gap-sm">
              <button
                className="btn btn-success"
                onClick={handleSend}
                disabled={!editedText.trim() || sending}
              >
                <HiOutlinePaperAirplane />
                {sending ? 'Sending...' : 'Approve & Send'}
              </button>

              {!isEditing && (
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => setIsEditing(true)}
                >
                  <HiOutlinePencilSquare />
                  Edit
                </button>
              )}
            </div>

            <button
              className="btn btn-danger btn-sm"
              onClick={onDiscard}
            >
              <HiOutlineTrash />
              Discard
            </button>
          </div>
        </>
      )}
    </div>
  );
}
