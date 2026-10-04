const rawApiUrl = import.meta.env.VITE_API_URL;
export const API_BASE = rawApiUrl
  ? `${rawApiUrl.replace(/\/+$/, '')}/api/v1`
  : '/api/v1';

/**
 * Generates headers for HTTP requests including JWT authorization token if available.
 * @param {Object} extra - Optional additional headers
 * @returns {Object} Combined headers object
 */
export const getAuthHeaders = (extra = {}) => {
  const token = localStorage.getItem('knowledge_ai_token');
  const headers = { ...extra };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};
