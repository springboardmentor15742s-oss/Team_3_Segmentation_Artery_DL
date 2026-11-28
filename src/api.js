const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");
const TOKEN_KEY = "arteryvision_access_token";

export function getApiBaseUrl() { return API_BASE_URL; }
export function saveToken(token) { localStorage.setItem(TOKEN_KEY, token); }
export function getToken() { return localStorage.getItem(TOKEN_KEY); }
export function clearToken() { localStorage.removeItem(TOKEN_KEY); }

async function apiRequest(path, options = {}) {
  const { auth = true, ...fetchOptions } = options;
  const headers = new Headers(fetchOptions.headers || {});
  if (fetchOptions.body && !(fetchOptions.body instanceof FormData) && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  if (auth) {
    const token = getToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }
  let response;
  try { response = await fetch(`${API_BASE_URL}${path}`, { ...fetchOptions, headers }); }
  catch { throw new Error("Could not reach the backend. Check that FastAPI is running and the API URL is correct."); }
  if (response.status === 204) {
    if (!response.ok) throw new Error(`Request failed with status ${response.status}`);
    return null;
  }
  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    const message = typeof data === "object" && data?.detail ? (typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail)) : (typeof data === "string" && data ? data : `Request failed with status ${response.status}`);
    if (response.status === 401 && auth) clearToken();
    throw new Error(message);
  }
  return data;
}

export function checkBackend() { return apiRequest("/health", { auth: false }); }
export function registerUser(userData) { return apiRequest("/auth/register", { method: "POST", auth: false, body: JSON.stringify(userData) }); }
export async function loginUser(email, password) {
  const data = await apiRequest("/auth/login", { method: "POST", auth: false, body: JSON.stringify({ email, password }) });
  if (data.access_token) saveToken(data.access_token);
  return data;
}
export function logoutUser() { return apiRequest("/auth/logout", { method: "POST" }); }
export function getCurrentUser() { return apiRequest("/auth/me"); }
export function updateMyProfile(fullName) { return apiRequest("/auth/me", { method: "PATCH", body: JSON.stringify({ full_name: fullName }) }); }
export function changeMyPassword(currentPassword, newPassword) { return apiRequest("/auth/change-password", { method: "POST", body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }) }); }
export function getAdminUsers() { return apiRequest("/admin/users"); }
export function updateUserRole(userId, role) { return apiRequest(`/admin/users/${encodeURIComponent(userId)}/role`, { method: "PATCH", body: JSON.stringify({ role }) }); }

export function getCases(params = {}) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) if (value !== undefined && value !== null && value !== "") search.set(key, value);
  return apiRequest(`/cases${search.size ? `?${search.toString()}` : ""}`);
}
export function getCase(caseId) { return apiRequest(`/cases/${encodeURIComponent(caseId)}`); }
export function createCase(caseData) { return apiRequest("/cases", { method: "POST", body: JSON.stringify(caseData) }); }
export function updateCase(caseId, caseData) { return apiRequest(`/cases/${encodeURIComponent(caseId)}`, { method: "PATCH", body: JSON.stringify(caseData) }); }
export function deleteCase(caseId) { return apiRequest(`/cases/${encodeURIComponent(caseId)}`, { method: "DELETE" }); }
export function getCaseHistory(caseId) { return apiRequest(`/cases/${encodeURIComponent(caseId)}/history`); }
export function uploadImage(caseId, file) { const formData = new FormData(); formData.append("file", file); return apiRequest(`/cases/${encodeURIComponent(caseId)}/upload`, { method: "POST", body: formData }); }
export function getCaseImages(caseId) { return apiRequest(`/cases/${encodeURIComponent(caseId)}/images`); }
export async function downloadCaseImage(caseId, imageId) {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/cases/${encodeURIComponent(caseId)}/images/${encodeURIComponent(imageId)}/file`, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
  if (!response.ok) {
    let detail = `Image download failed (${response.status})`;
    try { const body = await response.json(); detail = body.detail || detail; } catch { /* ignore non-JSON error body */ }
    if (response.status === 401) clearToken();
    throw new Error(detail);
  }
  return response.blob();
}
export function preprocessCaseImage(caseId, imageId, { denoise = true, enhanceContrast = true, maxDimension = 1024 } = {}) {
  const q = new URLSearchParams({ denoise: String(denoise), enhance_contrast: String(enhanceContrast), max_dimension: String(maxDimension) });
  return apiRequest(`/cases/${encodeURIComponent(caseId)}/images/${encodeURIComponent(imageId)}/preprocess?${q.toString()}`, { method: "POST" });
}
export async function downloadPreprocessedImage(caseId, imageId) {
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/cases/${encodeURIComponent(caseId)}/images/${encodeURIComponent(imageId)}/preprocessed-file`, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
  if (!response.ok) {
    let detail = `Preprocessed image download failed (${response.status})`;
    try { const body = await response.json(); detail = body.detail || detail; } catch { /* ignore non-JSON error body */ }
    if (response.status === 401) clearToken();
    throw new Error(detail);
  }
  return response.blob();
}

export function getCaseResults(caseId) { return apiRequest(`/cases/${encodeURIComponent(caseId)}/results`); }
export function compareCaseResults(caseId, baselineId, comparisonId) { const q = new URLSearchParams({ baseline_id: baselineId, comparison_id: comparisonId }); return apiRequest(`/cases/${encodeURIComponent(caseId)}/results/compare?${q.toString()}`); }

export function getDashboardSummary() { return apiRequest("/dashboard/summary"); }
export function getNotifications(unreadOnly = false, limit = 50) { return apiRequest(`/notifications?unread_only=${unreadOnly}&limit=${limit}`); }
export function markNotificationRead(notificationId) { return apiRequest(`/notifications/${encodeURIComponent(notificationId)}/read`, { method: "POST" }); }
export function markAllNotificationsRead() { return apiRequest("/notifications/read-all", { method: "POST" }); }
export function getPatients(q = "") { return apiRequest(`/patients${q ? `?q=${encodeURIComponent(q)}` : ""}`); }
export function createPatient(patientData) { return apiRequest("/patients", { method: "POST", body: JSON.stringify(patientData) }); }
export function updatePatient(patientId, patientData) { return apiRequest(`/patients/${encodeURIComponent(patientId)}`, { method: "PATCH", body: JSON.stringify(patientData) }); }
export function deletePatient(patientId) { return apiRequest(`/patients/${encodeURIComponent(patientId)}`, { method: "DELETE" }); }
export function getModels() { return apiRequest("/models"); }
export function createModel(modelData) { return apiRequest("/models", { method: "POST", body: JSON.stringify(modelData) }); }
export function updateModel(modelId, modelData) { return apiRequest(`/models/${encodeURIComponent(modelId)}`, { method: "PATCH", body: JSON.stringify(modelData) }); }
export function deleteModel(modelId) { return apiRequest(`/models/${encodeURIComponent(modelId)}`, { method: "DELETE" }); }
export function getAuditLogs(limit = 100) { return apiRequest(`/audit-logs?limit=${limit}`); }

export async function exportCaseReport(caseId, format = "pdf") {
  const record = await apiRequest(`/reports/cases/${encodeURIComponent(caseId)}/export?format=${encodeURIComponent(format)}`, { method: "POST" });
  const token = getToken();
  const response = await fetch(`${API_BASE_URL}/reports/${encodeURIComponent(record.report_id)}/download`, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
  if (!response.ok) {
    let detail = `Report download failed (${response.status})`;
    try { const body = await response.json(); detail = body.detail || detail; } catch { /* ignore */ }
    if (response.status === 401) clearToken();
    throw new Error(detail);
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `arteryvision_case_report_${caseId}.${format}`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  return record;
}
