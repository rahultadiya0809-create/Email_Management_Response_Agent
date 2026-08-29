/**
 * Email API Client
 *
 * Axios-based API client for communicating with the Flask backend.
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─── Health & Auth ──────────────────────────────────────────────

export const checkHealth = () => api.get('/health');

export const getAuthStatus = () => api.get('/auth/status');

export const login = (email) => api.post('/auth/login', { email });

export const getAuthUrl = (email) => api.post('/auth/url', { email });

export const logout = () => api.post('/auth/logout');

// ─── Emails ─────────────────────────────────────────────────────

export const fetchEmails = (params = {}) =>
  api.get('/emails', { params: { source: 'gmail', max_results: 20, ...params } });

export const getCachedEmails = (params = {}) =>
  api.get('/emails', { params: { source: 'db', ...params } });

export const getEmail = (emailId) => api.get(`/emails/${emailId}`);

export const classifyEmail = (emailId) => api.post(`/emails/${emailId}/classify`);

export const archiveEmail = (emailId) => api.post(`/emails/${emailId}/archive`);

// ─── Draft Replies ──────────────────────────────────────────────

export const generateDraftReply = (emailId) =>
  api.get(`/emails/${emailId}/draft-reply`);

export const updateDraftReply = (emailId, draftText) =>
  api.put(`/emails/${emailId}/draft-reply`, { draft_text: draftText });

export const sendReply = (emailId, replyText) =>
  api.post(`/emails/${emailId}/send-reply`, { reply_text: replyText });

// ─── Stats & Activity ──────────────────────────────────────────

export const getStats = () => api.get('/stats');

export const getActivity = (limit = 20) =>
  api.get('/activity', { params: { limit } });

// ─── Settings ───────────────────────────────────────────────────

export const getSettings = () => api.get('/settings');

export const updateSettings = (data) => api.put('/settings', data);

// ─── Classifier ─────────────────────────────────────────────────

export const trainClassifier = () => api.post('/classifier/train');

export const getClassifierStatus = () => api.get('/classifier/status');

// ─── Notifications ──────────────────────────────────────────────

export const testNotification = () => api.post('/notifications/test');

export default api;
