import { useEffect, useMemo, useRef, useState } from 'react';



import {
  Activity,

  AlertCircle,

  ArrowRight,
  Bell,
  BrainCircuit,
  CalendarDays,

  ChartNoAxesCombined,

  CheckCircle2,

  ChevronDown, ChevronRight,

  CircleDot,
  Clock3,

  Database,
  ExternalLink,

  Eye,

  FileImage,

  FileText,

  FolderKanban,

  HeartPulse,

  History,

  LayoutDashboard,

  LockKeyhole,

  Menu,

  Moon, MoreHorizontal,
  Pencil,
  Plus,
  RefreshCw,

  ScanLine,

  Search,

  Server,

  Settings,

  ShieldCheck,

  SlidersHorizontal,

  Sun,
  Trash2,
  Upload,

  Users,
  UserCog,
  Save,

  Workflow,

  X,

  Zap
} from 'lucide-react';



import {
  createCase as apiCreateCase,
  deleteCase as apiDeleteCase,
  updateCase as apiUpdateCase,
  changeMyPassword,
  clearToken,
  compareCaseResults,
  createModel,
  createPatient,
  deletePatient,
  downloadCaseImage,
  downloadPreprocessedImage,
  exportCaseReport,
  getAuditLogs,
  getAdminUsers,
  getCaseHistory,
  getCaseImages,
  getCaseResults,
  getCases,
  getCurrentUser,
  getDashboardSummary,
  getModels,
  getNotifications,
  getPatients,
  getToken,
  loginUser,
  logoutUser,
  markAllNotificationsRead,
  markNotificationRead,
  preprocessCaseImage,
  registerUser,
  updateModel,
  updateMyProfile,
  updateUserRole,
  uploadImage,
} from './api';











function formatDate(value) {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleDateString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric'
  });
}

function mapBackendCase(record, images = []) {
  const latestImage = [...images].sort((a, b) =>
    new Date(b.uploaded_at || 0) - new Date(a.uploaded_at || 0)
  )[0];
  return {
    id: record.case_id,
    name: record.case_name,
    modality: record.imaging_modality || 'CCTA',
    region: record.anatomical_region || 'Coronary arteries',
    date: formatDate(record.created_at || record.scan_date),
    status: record.case_status || 'Pending',
    owner: record.owner_user_id || 'Current user',
    file: latestImage?.original_filename || 'No image uploaded',
    imageId: latestImage?.image_id || null,
    preprocessedAvailable: Boolean(latestImage?.preprocessed_available),
    preprocessingMetadata: latestImage?.preprocessing_metadata || null,
    scanDate: record.scan_date || '',
    notes: record.notes || '',
    patientId: record.patient_id || '',
  };
}

const navItems = [
  { id: 'Dashboard', icon: LayoutDashboard },
  { id: 'Cases', icon: FolderKanban },
  { id: 'Patients', icon: Users },
  { id: 'Image Analysis', icon: ScanLine },
  { id: 'Results & Reports', icon: FileText },
  { id: 'Model Evaluation', icon: ChartNoAxesCombined },
  { id: 'Model Registry', icon: BrainCircuit },
  { id: 'Activity Logs', icon: History, roles: ['administrator'] },
  { id: 'Settings', icon: Settings },
];



function StatusPill({ status }) {

  const cls = String(status).toLowerCase().replaceAll(' ', '-');

  const Icon = status === 'Completed' ? CheckCircle2 : status === 'Processing' ? RefreshCw : status === 'Failed' ? AlertCircle : Clock3;

  return <span className={`status-pill ${cls}`}><Icon size={12} />{status}</span>;

}



function SectionHeading({ eyebrow, title, description, action }) {

  return <div className="section-heading"><div>{eyebrow && <div className="eyebrow">{eyebrow}</div>}<h1>{title}</h1>{description && <p>{description}</p>}</div>{action && <div className="heading-action">{action}</div>}</div>;

}



function IconButton({ children, title, onClick, className = '' }) {

  return <button className={`icon-button ${className}`} title={title} aria-label={title} onClick={onClick}>{children}</button>;

}



function VesselPreview({ large = false }) {

  return <div className={`vessel-preview ${large ? 'large' : ''}`}>

    <div className="vessel-toolbar"><span><CircleDot size={13} /> Vessel visualization preview</span><span className="demo-label">Illustrative only</span></div>

    <svg viewBox="0 0 520 330" role="img" aria-label="Illustrative branching artery diagram; not an actual scan">

      <defs>

        <linearGradient id="arteryGrad" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stopColor="#51b8ec"/><stop offset="100%" stopColor="#0877bd"/></linearGradient>

        <filter id="glow"><feGaussianBlur stdDeviation="4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>

      </defs>

      <g stroke="#b9ddf1" strokeWidth="1" opacity=".35"><path d="M20 55H500M20 110H500M20 165H500M20 220H500M20 275H500M70 20V310M145 20V310M220 20V310M295 20V310M370 20V310M445 20V310" /></g>

      <g fill="none" strokeLinecap="round" strokeLinejoin="round" filter="url(#glow)">

        <path d="M253 295 C247 259 253 232 245 204 C238 178 214 157 219 125 C223 101 240 80 239 47" stroke="url(#arteryGrad)" strokeWidth="16"/>

        <path d="M247 207 C214 199 189 177 170 150 C154 127 145 99 119 84" stroke="#1397d0" strokeWidth="10"/>

        <path d="M217 158 C184 152 161 161 136 177 C117 189 96 195 76 188" stroke="#47b6e4" strokeWidth="7"/>

        <path d="M169 150 C162 124 170 104 184 83" stroke="#47b6e4" strokeWidth="6"/>

        <path d="M244 204 C280 188 309 165 327 139 C346 112 365 98 395 92" stroke="#0c87c5" strokeWidth="10"/>

        <path d="M306 167 C338 178 359 199 376 224 C390 245 411 256 436 255" stroke="#36a9df" strokeWidth="7"/>

        <path d="M327 139 C322 110 329 85 345 67" stroke="#36a9df" strokeWidth="6"/>

        <path d="M377 224 C381 244 370 263 359 276" stroke="#67c9ed" strokeWidth="5"/>

        <path d="M136 177 C119 158 98 150 79 151" stroke="#78cfee" strokeWidth="4"/>

      </g>

      <g fill="#0b7fbd" stroke="#e4f5ff" strokeWidth="3"><circle cx="219" cy="125" r="6"/><circle cx="327" cy="139" r="6"/><circle cx="170" cy="150" r="5"/></g>

      <g fill="#66839b" fontSize="11" fontFamily="Inter, Arial"><text x="28" y="29">BRANCH MAP</text><text x="344" y="306">Illustrative anatomy</text></g>

    </svg>

    <p className="preview-note">Connect the image viewer and segmentation endpoint to display real patient/de-identified dataset imagery and model output here.</p>

  </div>;

}



function CaseImagePreview({ caseRecord, loading, imageUrl, error, onImageError, onUpload }) {
  if (loading) {
    return <div className="vessel-preview large image-preview-state">
      <div className="vessel-toolbar"><span><FileImage size={13} /> Uploaded image preview</span><span className="demo-label">Loading</span></div>
      <div className="image-preview-message"><RefreshCw size={30} className="image-preview-spin" /><b>Loading image from backend…</b><p>Please wait while the stored file is retrieved.</p></div>
    </div>;
  }

  if (imageUrl && !error) {
    return <div className="vessel-preview large real-image-preview">
      <div className="vessel-toolbar"><span><FileImage size={13} /> Uploaded image preview</span><span className="demo-label">Original image · no AI overlay</span></div>
      <div className="real-image-canvas">
        <img src={imageUrl} alt={`Uploaded medical image ${caseRecord?.file || ''}`} onError={onImageError} />
      </div>
      <p className="preview-note">Original image retrieved from the backend. No segmentation mask or stenosis prediction has been applied.</p>
    </div>;
  }

  const hasImage = Boolean(caseRecord?.imageId);
  return <div className="vessel-preview large image-preview-state">
    <div className="vessel-toolbar"><span><FileImage size={13} /> Uploaded image preview</span><span className="demo-label">Original image</span></div>
    <div className="image-preview-message">
      <FileImage size={32} />
      <b>{hasImage ? 'Image preview unavailable' : 'No image uploaded to this case'}</b>
      <p>{hasImage ? (error || 'The stored file could not be displayed in this browser.') : 'Upload an image to this case. The original image will appear here after upload.'}</p>
      {!hasImage && <button className="btn secondary" type="button" onClick={onUpload}><Upload size={14} /> Upload image</button>}
    </div>
  </div>;
}


function MetricCard({ label, value, meta, icon: Icon, tone = 'blue' }) {

  return <div className="metric-card"><div className={`metric-icon ${tone}`}><Icon size={18}/></div><div className="metric-copy"><span>{label}</span><strong>{value}</strong><small>{meta}</small></div><MoreHorizontal className="metric-more" size={17}/></div>;

}



function Modal({ title, onClose, children, footer }) {

  return <div className="modal-backdrop" onMouseDown={(e) => { if (e.target === e.currentTarget) onClose(); }}><div className="modal" role="dialog" aria-modal="true"><div className="modal-head"><div><h2>{title}</h2><p>ArteryVision workspace</p></div><IconButton title="Close dialog" onClick={onClose}><X size={19}/></IconButton></div><div className="modal-body">{children}</div>{footer && <div className="modal-footer">{footer}</div>}</div></div>;

}



export default function App() {
  // Shared authentication state used by session restore, login, and role-based UI.
  const [authUser, setAuthUser] = useState(null);
  const [activePage, setActivePage] = useState('Dashboard');
  const [cases, setCases] = useState([]);

  const userRole = String(authUser?.role || 'researcher').toLowerCase();
  const visibleNavItems = useMemo(
    () => navItems.filter((item) => !item.roles || item.roles.includes(userRole)),
    [userRole],
  );
  const allowedPages = useMemo(
    () => visibleNavItems.map((item) => item.id),
    [visibleNavItems],
  );

  useEffect(() => {
    if (authUser && !allowedPages.includes(activePage)) {
      setActivePage('Dashboard');
    }
  }, [authUser, activePage, allowedPages]);


  const [authChecked, setAuthChecked] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [authName, setAuthName] = useState('');
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState('');
  const [casesLoading, setCasesLoading] = useState(false);
  const [imagePreviewUrl, setImagePreviewUrl] = useState('');
  const [imagePreviewLoading, setImagePreviewLoading] = useState(false);
  const [imagePreviewError, setImagePreviewError] = useState('');
  const [preprocessedImageUrl, setPreprocessedImageUrl] = useState('');
  const [preprocessingMeta, setPreprocessingMeta] = useState(null);
  const [preprocessingError, setPreprocessingError] = useState('');
  const [preprocessingLoading, setPreprocessingLoading] = useState(false);
  const [preprocessingRevision, setPreprocessingRevision] = useState(0);
  const [activityHistory, setActivityHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState('');
  const [analysisResults, setAnalysisResults] = useState([]);
  const [resultsLoading, setResultsLoading] = useState(false);
  const [resultsError, setResultsError] = useState('');
  const [compareCaseId, setCompareCaseId] = useState('');
  const [baselineResultId, setBaselineResultId] = useState('');
  const [comparisonResultId, setComparisonResultId] = useState('');
  const [comparisonData, setComparisonData] = useState(null);
  const [comparisonLoading, setComparisonLoading] = useState(false);
  const [dashboardSummary, setDashboardSummary] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [patients, setPatients] = useState([]);
  const [patientSearch, setPatientSearch] = useState('');
  const [patientLoading, setPatientLoading] = useState(false);
  const [patientForm, setPatientForm] = useState({ display_code: '', age: '', sex: '', medical_history: '', risk_factors: '', clinical_notes: '' });
  const [modelsList, setModelsList] = useState([]);
  const [modelLoading, setModelLoading] = useState(false);
  const [modelForm, setModelForm] = useState({ model_name: '', version: '0.1.0', task: 'segmentation', description: '', framework: '', model_reference: '', status: 'planned' });
  const [profileName, setProfileName] = useState('');
  const [profileSaving, setProfileSaving] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [auditLogs, setAuditLogs] = useState([]);
  const [auditError, setAuditError] = useState('');
  const [adminUsers, setAdminUsers] = useState([]);
  const [adminUsersLoading, setAdminUsersLoading] = useState(false);
  const [adminUsersError, setAdminUsersError] = useState('');
  const [editingRoleUserId, setEditingRoleUserId] = useState('');
  const [editingRoleValue, setEditingRoleValue] = useState('researcher');
  const [roleSavingUserId, setRoleSavingUserId] = useState('');

  const [search, setSearch] = useState('');

  const [statusFilter, setStatusFilter] = useState('All statuses');

  const [modal, setModal] = useState('');
  const [editCaseForm, setEditCaseForm] = useState({ id: '', name: '', modality: 'CCTA', region: 'Coronary arteries', scanDate: '', notes: '', patientId: '' });
  const [caseSaveLoading, setCaseSaveLoading] = useState(false);

  const [selectedCase, setSelectedCase] = useState(null);

  const [dark, setDark] = useState(false);

  const [mobileNav, setMobileNav] = useState(false);

  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const [uploadCaseId, setUploadCaseId] = useState('');

  const [notice, setNotice] = useState('');

  const [newCase, setNewCase] = useState({ name: '', modality: 'CCTA', region: 'Coronary arteries', notes: '', patientId: '' });

  const [profileOpen, setProfileOpen] = useState(false);

  const fileInputRef = useRef(null);

  const modalFileInputRef = useRef(null);

  const apiBase = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '');

  const isDemo = !apiBase;



  const filteredCases = useMemo(() => cases.filter((item) => {

    const matchesSearch = `${item.id} ${item.name || ''} ${item.modality} ${item.region} ${item.owner} ${item.file}`.toLowerCase().includes(search.toLowerCase());

    const matchesStatus = statusFilter === 'All statuses' || item.status === statusFilter;

    return matchesSearch && matchesStatus;

  }), [cases, search, statusFilter]);



  const showNotice = (message) => {
    setNotice(message);
    window.setTimeout(() => setNotice(''), 4200);
  };

  useEffect(() => { setProfileName(authUser?.full_name || ''); }, [authUser?.full_name]);

  async function loadDashboard() {
    try { setDashboardSummary(await getDashboardSummary()); }
    catch (error) { showNotice(`Dashboard stats unavailable: ${error.message}`); }
  }

  async function loadNotifications() {
    try { setNotifications(await getNotifications(false, 30)); }
    catch (error) { showNotice(`Notifications unavailable: ${error.message}`); }
  }

  async function loadPatients() {
    setPatientLoading(true);
    try { setPatients(await getPatients(patientSearch)); }
    catch (error) { showNotice(`Could not load patient records: ${error.message}`); }
    finally { setPatientLoading(false); }
  }

  async function loadModelRegistry() {
    setModelLoading(true);
    try { setModelsList(await getModels()); }
    catch (error) { showNotice(`Could not load model registry: ${error.message}`); }
    finally { setModelLoading(false); }
  }

  async function saveProfile() {
    setProfileSaving(true);
    try {
      const updated = await updateMyProfile(profileName.trim());
      setAuthUser(updated);
      showNotice('Profile updated successfully.');
    } catch (error) { showNotice(`Could not update profile: ${error.message}`); }
    finally { setProfileSaving(false); }
  }

  async function savePassword() {
    setPasswordSaving(true);
    try {
      await changeMyPassword(currentPassword, newPassword);
      clearToken();
      setAuthUser(null);
      setCurrentPassword(''); setNewPassword('');
      showNotice('Password changed. Sign in again with your new password.');
    } catch (error) { showNotice(`Could not change password: ${error.message}`); }
    finally { setPasswordSaving(false); }
  }

  async function submitPatient(e) {
    e.preventDefault();
    if (!patientForm.display_code.trim()) { showNotice('Enter a de-identified patient code.'); return; }
    try {
      await createPatient({
        display_code: patientForm.display_code.trim(),
        age: patientForm.age === '' ? null : Number(patientForm.age),
        sex: patientForm.sex || null,
        medical_history: patientForm.medical_history.trim() || null,
        risk_factors: patientForm.risk_factors.trim() || null,
        clinical_notes: patientForm.clinical_notes.trim() || null,
      });
      setPatientForm({ display_code: '', age: '', sex: '', medical_history: '', risk_factors: '', clinical_notes: '' });
      await loadPatients();
      showNotice('Patient metadata saved. Use de-identified records only.');
    } catch (error) { showNotice(`Could not save patient record: ${error.message}`); }
  }

  async function submitModel(e) {
    e.preventDefault();
    if (!modelForm.model_name.trim() || !modelForm.version.trim()) { showNotice('Model name and version are required.'); return; }
    try {
      await createModel({ ...modelForm, model_name: modelForm.model_name.trim(), version: modelForm.version.trim(), description: modelForm.description.trim() || null, framework: modelForm.framework.trim() || null, model_reference: modelForm.model_reference.trim() || null });
      setModelForm({ model_name: '', version: '0.1.0', task: 'segmentation', description: '', framework: '', model_reference: '', status: 'planned' });
      await loadModelRegistry();
      showNotice('Model metadata registered. This does not load or run a model.');
    } catch (error) { showNotice(`Could not register model: ${error.message}`); }
  }

  async function retireModel(modelId) {
    try { await updateModel(modelId, { status: 'retired' }); await loadModelRegistry(); showNotice('Model metadata updated to retired.'); }
    catch (error) { showNotice(`Could not update model: ${error.message}`); }
  }

  async function exportReport(caseItem, format) {
    try { await exportCaseReport(caseItem.id, format); showNotice(`${format.toUpperCase()} case export downloaded.`); }
    catch (error) { showNotice(`Report export failed: ${error.message}`); }
  }

  async function openNotifications() {
    setNotificationsOpen((prev) => !prev);
    await loadNotifications();
  }

  async function readNotification(item) {
    try {
      await markNotificationRead(item.notification_id);
      setNotifications((previous) => previous.map((n) => n.notification_id === item.notification_id ? { ...n, is_read: true } : n));
    } catch (error) { showNotice(`Could not update notification: ${error.message}`); }
  }

  async function readAllNotifications() {
    try { await markAllNotificationsRead(); await loadNotifications(); showNotice('All notifications marked as read.'); }
    catch (error) { showNotice(`Could not update notifications: ${error.message}`); }
  }

  async function loadAdminAudit() {
    if (authUser?.role !== 'administrator') return;
    setAuditError('');
    try { setAuditLogs(await getAuditLogs(100)); }
    catch (error) { setAuditError(error.message || 'Could not load audit logs.'); }
  }

  async function loadAdminUsers() {
    if (authUser?.role !== 'administrator') return;
    setAdminUsersLoading(true);
    setAdminUsersError('');
    try {
      const rows = await getAdminUsers();
      setAdminUsers(Array.isArray(rows) ? rows : []);
    } catch (error) {
      setAdminUsersError(error.message || 'Could not load registered users.');
    } finally {
      setAdminUsersLoading(false);
    }
  }

  async function saveUserRole(user) {
    if (!user || user.user_id === authUser?.user_id) return;
    setRoleSavingUserId(user.user_id);
    setAdminUsersError('');
    try {
      const updated = await updateUserRole(user.user_id, editingRoleValue);
      setAdminUsers((previous) => previous.map((item) => item.user_id === updated.user_id ? updated : item));
      setEditingRoleUserId('');
      showNotice(`Role updated for ${updated.email}. They must sign in again to refresh permissions.`);
    } catch (error) {
      setAdminUsersError(error.message || 'Could not update the user role.');
    } finally {
      setRoleSavingUserId('');
    }
  }

  async function loadCases() {
    setCasesLoading(true);
    try {
      const records = await getCases();
      const mapped = await Promise.all(records.map(async (record) => {
        let images = [];
        try {
          images = await getCaseImages(record.case_id);
        } catch {
          // Case metadata can still be displayed if image listing fails.
        }
        return mapBackendCase(record, images);
      }));
      setCases(mapped);
      setSelectedCase((previous) => {
        if (previous) {
          return mapped.find((item) => item.id === previous.id) || mapped[0] || null;
        }
        return mapped[0] || null;
      });
      setUploadCaseId((previous) => mapped.some((item) => item.id === previous)
        ? previous
        : (mapped[0]?.id || ''));
      return mapped;
    } catch (error) {
      showNotice(`Could not load cases: ${error.message}`);
      throw error;
    } finally {
      setCasesLoading(false);
    }
  }

  useEffect(() => {
    let active = true;

    async function restoreSession() {
      if (!getToken()) {
        if (active) setAuthChecked(true);
        return;
      }

      try {
        const user = await getCurrentUser();
        if (!active) return;
        setAuthUser(user);

        try { await loadCases(); } catch { /* case data may load on a manual refresh */ }
        try { setDashboardSummary(await getDashboardSummary()); } catch { /* dashboard fallback uses case list */ }
        try { setNotifications(await getNotifications(false, 30)); } catch { /* notification panel can retry */ }
        try { setPatients(await getPatients()); } catch { /* patient page can retry */ }
      } catch {
        clearToken();
        if (active) setAuthUser(null);
      } finally {
        if (active) setAuthChecked(true);
      }
    }

    restoreSession();
    return () => { active = false; };
  }, []);

  // Retrieve an authorized image preview whenever the selected case/image changes.
  useEffect(() => {
    let cancelled = false;
    let objectUrl = null;

    async function loadImagePreview() {
      setImagePreviewUrl('');
      setImagePreviewError('');

      const caseId = selectedCase?.id;
      const imageId = selectedCase?.imageId;
      const fileName = selectedCase?.file || '';

      if (!authUser || !caseId || !imageId || !fileName || fileName === 'No image uploaded') {
        setImagePreviewLoading(false);
        return;
      }

      const extension = fileName.toLowerCase().split('.').pop();
      const mimeTypes = {
        png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg',
        gif: 'image/gif', webp: 'image/webp', bmp: 'image/bmp'
      };

      if (!mimeTypes[extension]) {
        setImagePreviewLoading(false);
        setImagePreviewError('This file is stored, but a browser preview is available only for PNG, JPG/JPEG, GIF, WebP, and BMP. DICOM, NIfTI, and TIFF need a suitable medical-image viewer.');
        return;
      }

      setImagePreviewLoading(true);
      try {
        const blob = await downloadCaseImage(caseId, imageId);
        if (cancelled) return;
        const mimeType = blob.type && blob.type.startsWith('image/') ? blob.type : mimeTypes[extension];
        objectUrl = URL.createObjectURL(new Blob([blob], { type: mimeType }));
        setImagePreviewUrl(objectUrl);
      } catch (error) {
        if (!cancelled) setImagePreviewError(error.message || 'Could not retrieve the uploaded image.');
      } finally {
        if (!cancelled) setImagePreviewLoading(false);
      }
    }

    loadImagePreview();
    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [authUser, selectedCase?.id, selectedCase?.imageId, selectedCase?.file]);

  // Load a previously saved non-AI preprocessing preview when the case changes.
  useEffect(() => {
    let cancelled = false;
    let objectUrl = null;
    async function loadSavedPreprocessedPreview() {
      if (preprocessedImageUrl) URL.revokeObjectURL(preprocessedImageUrl);
      setPreprocessedImageUrl('');
      setPreprocessingMeta(selectedCase?.preprocessingMetadata || null);
      setPreprocessingError('');
      if (!authUser || !selectedCase?.id || !selectedCase?.imageId || !selectedCase?.preprocessedAvailable) return;
      try {
        const blob = await downloadPreprocessedImage(selectedCase.id, selectedCase.imageId);
        if (cancelled) return;
        objectUrl = URL.createObjectURL(new Blob([blob], { type: 'image/png' }));
        setPreprocessedImageUrl(objectUrl);
      } catch (error) { if (!cancelled) setPreprocessingError(error.message || 'Could not retrieve the preprocessed preview.'); }
    }
    loadSavedPreprocessedPreview();
    return () => { cancelled = true; if (objectUrl) URL.revokeObjectURL(objectUrl); };
    // The selection's ID and persisted preprocessing metadata control reloads.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authUser, selectedCase?.id, selectedCase?.imageId, selectedCase?.preprocessedAvailable, preprocessingRevision]);

  async function runBasicPreprocessing() {
    if (!selectedCase?.id || !selectedCase?.imageId) { showNotice('Select a case with an uploaded image first.'); return; }
    setPreprocessingLoading(true);
    setPreprocessingError('');
    try {
      const result = await preprocessCaseImage(selectedCase.id, selectedCase.imageId, { denoise: true, enhanceContrast: true, maxDimension: 1024 });
      setPreprocessingMeta(result.metadata || null);
      setCases((previous) => previous.map((item) => item.id === selectedCase.id ? { ...item, preprocessedAvailable: true, preprocessingMetadata: result.metadata || null } : item));
      setSelectedCase((previous) => previous?.id === selectedCase.id ? { ...previous, preprocessedAvailable: true, preprocessingMetadata: result.metadata || null } : previous);
      setPreprocessingRevision((previous) => previous + 1);
      showNotice('Basic non-AI preprocessing completed. The original file is unchanged.');
    } catch (error) { setPreprocessingError(error.message || 'Preprocessing failed.'); }
    finally { setPreprocessingLoading(false); }
  }

  async function handleAuthSubmit(event) {
    event.preventDefault();
    setAuthError('');
    setAuthLoading(true);
    try {
      if (authMode === 'register') {
        await registerUser({
          full_name: authName.trim(),
          email: authEmail.trim(),
          password: authPassword,
        });
      }
      await loginUser(authEmail.trim(), authPassword);
      const user = await getCurrentUser();
      setAuthUser(user);
      setAuthPassword('');
      try { await loadCases(); } catch { /* the notice from loadCases explains the data problem */ }
      try { setDashboardSummary(await getDashboardSummary()); } catch { /* dashboard fallback uses case list */ }
      try { setNotifications(await getNotifications(false, 30)); } catch { /* notification panel can retry */ }
      try { setPatients(await getPatients()); } catch { /* patient page can retry */ }
      setActivePage('Dashboard');
      showNotice(`Welcome, ${user.full_name || 'user'}.`);
    } catch (error) {
      setAuthError(error.message || 'Authentication failed. Please try again.');
    } finally {
      setAuthLoading(false);
      setAuthChecked(true);
    }
  }

  async function handleLogout() {
    try { await logoutUser(); } catch { /* local sign-out still happens if the API is unreachable */ }
    clearToken();
    setAuthUser(null);
    setCases([]);
    setSelectedCase(null);
    setUploadCaseId('');
    setProfileOpen(false);
    setActivePage('Dashboard');
    setAuthPassword('');
    setAuthError('');
    showNotice('You have been signed out.');
  }

  async function createCase(e) {
    e.preventDefault();
    if (!newCase.name.trim()) {
      showNotice('Enter a case name.');
      return;
    }
    try {
      const data = await apiCreateCase({
        case_name: newCase.name.trim(),
        imaging_modality: newCase.modality,
        anatomical_region: newCase.region,
        notes: newCase.notes.trim() || null,
        patient_id: newCase.patientId || null,
      });
      const item = mapBackendCase(data);
      setCases((previous) => [item, ...previous]);
      setSelectedCase(item);
      setUploadCaseId(item.id);
      setNewCase({ name: '', modality: 'CCTA', region: 'Coronary arteries', notes: '', patientId: '' });
      setModal('');
      setActivePage('Cases');
      showNotice('Case created and saved to PostgreSQL.');
    } catch (error) {
      showNotice(`Could not create case: ${error.message}`);
    }
  }

  function openEditCase(item) {
    setEditCaseForm({ id: item.id, name: item.name || '', modality: item.modality || 'CCTA', region: item.region || 'Coronary arteries', scanDate: item.scanDate || '', notes: item.notes || '', patientId: item.patientId || '' });
    setModal('edit-case');
  }

  async function saveCaseEdits(e) {
    e.preventDefault();
    if (!editCaseForm.name.trim()) { showNotice('Enter a case name.'); return; }
    setCaseSaveLoading(true);
    try {
      const saved = await apiUpdateCase(editCaseForm.id, {
        case_name: editCaseForm.name.trim(),
        imaging_modality: editCaseForm.modality,
        anatomical_region: editCaseForm.region,
        scan_date: editCaseForm.scanDate || null,
        notes: editCaseForm.notes.trim() || null,
        patient_id: editCaseForm.patientId || null,
      });
      const current = cases.find((c) => c.id === saved.case_id);
      const mapped = mapBackendCase(saved, current?.imageId ? [{ image_id: current.imageId, original_filename: current.file }] : []);
      setCases((previous) => previous.map((c) => c.id === saved.case_id ? { ...mapped, file: current?.file || mapped.file, imageId: current?.imageId || null } : c));
      setSelectedCase((previous) => previous?.id === saved.case_id ? { ...mapped, file: current?.file || mapped.file, imageId: current?.imageId || null } : previous);
      setModal('');
      showNotice('Case details updated.');
    } catch (error) { showNotice(`Could not update case: ${error.message}`); }
    finally { setCaseSaveLoading(false); }
  }

  async function deleteCaseRecord(item) {
    if (!window.confirm(`Delete case "${item.name}" and its linked image/report files? This action cannot be undone.`)) return;
    try {
      await apiDeleteCase(item.id);
      setCases((previous) => previous.filter((c) => c.id !== item.id));
      setSelectedCase((previous) => previous?.id === item.id ? null : previous);
      setUploadCaseId((previous) => previous === item.id ? '' : previous);
      showNotice('Case and its stored files were deleted.');
    } catch (error) { showNotice(`Could not delete case: ${error.message}`); }
  }

  async function submitUpload(e) {
    e?.preventDefault?.();
    if (!uploadedFile) {
      showNotice('Choose an image file first.');
      return;
    }
    const chosenCase = cases.find((item) => item.id === uploadCaseId);
    if (!chosenCase) {
      showNotice('Select a case to attach this file to.');
      return;
    }
    setUploading(true);
    try {
      await uploadImage(uploadCaseId, uploadedFile);
      const images = await getCaseImages(uploadCaseId);
      const updated = mapBackendCase({
        case_id: chosenCase.id,
        case_name: chosenCase.name,
        imaging_modality: chosenCase.modality,
        anatomical_region: chosenCase.region,
        case_status: chosenCase.status,
        created_at: chosenCase.date,
        owner_user_id: chosenCase.owner,
      }, images);
      setCases((previous) => previous.map((item) => item.id === uploadCaseId ? updated : item));
      setSelectedCase(updated);
      setUploadedFile(null);
      setModal('');
      setActivePage('Image Analysis');
      showNotice('Image uploaded successfully and linked to the case.');
    } catch (error) {
      showNotice(`Image upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  }

  async function loadActivityHistory() {
    setHistoryLoading(true);
    setHistoryError('');
    try {
      const grouped = await Promise.all(cases.map(async (caseItem) => {
        try {
          const entries = await getCaseHistory(caseItem.id);
          return (Array.isArray(entries) ? entries : []).map((entry) => ({
            ...entry,
            caseName: caseItem.name || caseItem.id,
            caseId: caseItem.id,
          }));
        } catch (error) {
          throw new Error(`Could not load history for ${caseItem.name || caseItem.id}: ${error.message}`);
        }
      }));
      const rows = grouped.flat().sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
      setActivityHistory(rows);
    } catch (error) {
      setHistoryError(error.message || 'Could not load activity history.');
    } finally {
      setHistoryLoading(false);
    }
  }

  async function loadAnalysisResults() {
    setResultsLoading(true);
    setResultsError('');
    try {
      const grouped = await Promise.all(cases.map(async (caseItem) => {
        const records = await getCaseResults(caseItem.id);
        return (Array.isArray(records) ? records : []).map((record) => ({
          ...record,
          caseName: caseItem.name || caseItem.id,
          caseDisplayId: caseItem.id,
        }));
      }));
      setAnalysisResults(grouped.flat().sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0)));
    } catch (error) {
      setResultsError(error.message || 'Could not load analysis results.');
    } finally {
      setResultsLoading(false);
    }
  }

  useEffect(() => {
    if (!authUser) return;
    if (activePage === 'Dashboard') loadDashboard();
    if (activePage === 'Patients') loadPatients();
    if (activePage === 'Model Registry') loadModelRegistry();
    if (activePage === 'Activity Logs') { loadActivityHistory(); loadAdminAudit(); }
    if (activePage === 'Results & Reports') loadAnalysisResults();
    // Data is fetched when the user opens the corresponding page.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activePage, authUser, cases]);

  useEffect(() => {
    if (authUser?.role === 'administrator' && activePage === 'Settings') {
      loadAdminUsers();
    }
    // User list is fetched on entry to Settings or when the signed-in role changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activePage, authUser?.role]);

  async function requestAnalysis(item) {
    setSelectedCase(item);
    showNotice('Case and image APIs are connected. AI analysis is not implemented in this project phase.');
  }

  const compareCandidates = useMemo(() => analysisResults.filter((r) => r.caseDisplayId === compareCaseId), [analysisResults, compareCaseId]);

  useEffect(() => {
    if (!compareCaseId && cases.length) setCompareCaseId(cases[0].id);
    if (compareCaseId && !cases.some((c) => c.id === compareCaseId)) setCompareCaseId(cases[0]?.id || '');
  }, [cases, compareCaseId]);

  useEffect(() => {
    if (compareCandidates.length && !compareCandidates.some((r) => r.result_id === baselineResultId)) setBaselineResultId(compareCandidates[0].result_id);
    if (compareCandidates.length > 1 && (!compareCandidates.some((r) => r.result_id === comparisonResultId) || comparisonResultId === baselineResultId)) setComparisonResultId(compareCandidates.find((r) => r.result_id !== baselineResultId)?.result_id || '');
    if (compareCandidates.length < 2) { setComparisonResultId(''); setComparisonData(null); }
  }, [compareCandidates, baselineResultId, comparisonResultId]);

  async function runResultsComparison() {
    if (!compareCaseId || !baselineResultId || !comparisonResultId || baselineResultId === comparisonResultId) { showNotice('Choose two different saved results for the same case.'); return; }
    setComparisonLoading(true);
    try { setComparisonData(await compareCaseResults(compareCaseId, baselineResultId, comparisonResultId)); }
    catch (error) { showNotice(`Could not compare results: ${error.message}`); }
    finally { setComparisonLoading(false); }
  }

  async function refreshHealth() {
    try {
      const response = await fetch(`${apiBase}/health`);
      if (!response.ok) throw new Error(`API returned ${response.status}`);
      const data = await response.json();
      showNotice(`Backend connected: ${data.service || 'FastAPI'} (${data.status || 'ok'}).`);
    } catch (error) {
      showNotice(`Backend health check failed: ${error.message}`);
    }
  }

  function openCase(item) { setSelectedCase(item); setActivePage('Image Analysis'); }

  function headerAction() { setProfileOpen((prev) => !prev); }



  if (!authChecked) {
    return <div className={`app-shell ${dark ? 'dark-mode' : ''}`} style={{ minHeight: '100vh', display: 'grid', placeItems: 'center' }}>
      <div className="panel" style={{ padding: 24 }}>Checking your ArteryVision session...</div>
    </div>;
  }

  if (!authUser) {
    return <AuthScreen
      dark={dark}
      setDark={setDark}
      mode={authMode}
      setMode={setAuthMode}
      fullName={authName}
      setFullName={setAuthName}
      email={authEmail}
      setEmail={setAuthEmail}
      password={authPassword}
      setPassword={setAuthPassword}
      loading={authLoading}
      error={authError}
      onSubmit={handleAuthSubmit}
    />;
  }

  return <div className={`app-shell ${dark ? 'dark-mode' : ''}`}>

    <header className="topbar">

      <button className="brand" onClick={() => setActivePage('Dashboard')} aria-label="ArteryVision dashboard">

        <span className="brand-mark"><HeartPulse size={22}/></span><span className="brand-text"><b>ArteryVision</b><small>Coronary Imaging Workspace</small></span>

      </button>

      <div className="topbar-right">

        <div className="environment-pill"><Zap size={15}/><span>{isDemo ? 'Demo workspace' : 'API connected'}</span><i className={isDemo ? 'dot amber' : 'dot green'}/><small>{isDemo ? 'Sample data' : 'API'}</small></div>

        <div className="profile-wrap notification-wrap"><button className="theme-button" onClick={openNotifications} aria-label="Notifications"><Bell size={16}/><span>Alerts</span><b className="notification-count">{notifications.filter((n) => !n.is_read).length}</b></button>
          {notificationsOpen && <div className="profile-menu notification-menu"><div className="notification-menu-head"><b>Notifications</b><button className="text-action" onClick={readAllNotifications}>Mark all read</button></div>{notifications.length === 0 ? <p className="muted">No notifications yet.</p> : notifications.slice(0, 8).map((item) => <button key={item.notification_id} className={`notification-item ${item.is_read ? 'read' : 'unread'}`} onClick={() => readNotification(item)}><b>{item.alert_type.replaceAll('_', ' ')}</b><span>{item.message}</span><small>{new Date(item.created_at).toLocaleString()}</small></button>)}</div>}
        </div>
        <button className="theme-button" onClick={() => setDark(!dark)}>{dark ? <Sun size={16}/> : <Moon size={16}/>}<span>{dark ? 'Dark' : 'Light'}</span></button>

        <div className="profile-wrap"><button className="profile-chip" onClick={headerAction}><span className="avatar">{(authUser?.full_name || 'User').split(/\s+/).map(part => part[0]).join('').slice(0,2).toUpperCase()}</span><span className="profile-name">{authUser?.full_name || 'User'}</span><span className="role-chip">{(authUser?.role || 'RESEARCHER').toUpperCase()}</span><ChevronDown size={14}/></button>
          {profileOpen && <div className="profile-menu"><b>{authUser?.full_name || 'Signed-in user'}</b><span>{authUser?.email || ''}</span><button onClick={() => { setProfileOpen(false); setActivePage('Settings'); }}>Profile & Settings</button><button onClick={handleLogout}>Sign out</button></div>}
        </div>
      </div>

    </header>



    <nav className={`main-nav ${mobileNav ? 'nav-open' : ''}`} aria-label="Main navigation">

      <button className="mobile-nav-toggle" onClick={() => setMobileNav(!mobileNav)}><Menu size={16}/> Navigation <ChevronDown size={14}/></button>

      <div className="nav-scroller">
  {visibleNavItems.map(({ id, icon: Icon }) => (
    <button
      key={id}
      className={`nav-item ${activePage === id ? 'active' : ''}`}
      onClick={() => {
        setActivePage(id);
        setMobileNav(false);
      }}
    >
      <Icon size={16} />
      <span>{id}</span>
    </button>
  ))}
</div>

    </nav>



    <main className="page-container">

      {activePage === 'Dashboard' && <>

        <section className="hero-card">

          <div className="hero-content"><span className="hero-kicker"><Activity size={13}/> MEDICAL IMAGE INTELLIGENCE</span><h1>Understand arteries.<br/>Visualize findings with clarity.</h1><p>Manage coronary imaging cases, prepare scans for analysis, and review AI-assisted segmentation and stenosis results in one workspace.</p><div className="hero-actions"><button className="btn primary" onClick={() => setModal('new-case')}><Plus size={16}/> New case</button><button className="btn secondary" onClick={() => { setUploadedFile(null); setModal('upload'); }}><Upload size={16}/> Upload scan</button></div><div className="hero-foot"><span><i className="dot green"/> Case workflow</span><span><i className="dot blue"/> Protected access enabled</span><span className="demo-label">AI inference not connected</span></div></div>

          <div className="hero-art"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><div className="hero-heart"><HeartPulse size={72} strokeWidth={1.3}/></div><span className="orbit-caption cap-one">SEGMENT</span><span className="orbit-caption cap-two">ANALYZE</span><span className="orbit-caption cap-three">REVIEW</span></div>

        </section>

        <div className="demo-banner"><AlertCircle size={16}/><span><b>Backend connected:</b> cases and image uploads use FastAPI. AI analysis results will appear after an analysis endpoint and model are implemented.</span><button onClick={refreshHealth}><RefreshCw size={14}/> Check connection</button></div>

        <div className="dashboard-data-strip"><span><b>{dashboardSummary?.images_uploaded ?? cases.filter(c => c.file && c.file !== 'No image uploaded').length}</b><small>Uploaded image records</small></span><span><b>{dashboardSummary?.stored_result_records ?? analysisResults.length}</b><small>Stored result records</small></span><span><b>{dashboardSummary?.unread_notifications ?? notifications.filter(n => !n.is_read).length}</b><small>Unread notifications</small></span><button className="text-action" onClick={loadDashboard}><RefreshCw size={13}/> Refresh metrics</button></div>

        <section className="metrics-grid">

          <MetricCard label="Total cases" value={String(dashboardSummary?.total_cases ?? cases.length).padStart(2, '0')} meta="Cases saved in your account" icon={FolderKanban} tone="blue"/>

          <MetricCard label="Completed" value={String(dashboardSummary?.completed_cases ?? cases.filter(c => c.status === 'Completed').length).padStart(2,'0')} meta="Current case status" icon={CheckCircle2} tone="green"/>

          <MetricCard label="In progress" value={String(dashboardSummary?.processing_cases ?? cases.filter(c => c.status === 'Processing').length).padStart(2,'0')} meta="Current case status" icon={Clock3} tone="violet"/>

          <MetricCard label="Pending / failed" value={String((dashboardSummary?.pending_cases ?? cases.filter(c => c.status === 'Pending').length) + (dashboardSummary?.failed_cases ?? cases.filter(c => c.status === 'Failed').length)).padStart(2,'0')} meta="Needs review or processing" icon={AlertCircle} tone="amber"/>

        </section>

        <div className="dashboard-grid">

          <section className="panel system-panel"><div className="panel-heading"><div><h2>Workspace status</h2><p>Backend and analysis service readiness</p></div><button className="text-action" onClick={refreshHealth}>Refresh <RefreshCw size={13}/></button></div>

            <div className="service-row"><span className="service-symbol green-bg"><Server size={16}/></span><div className="service-copy"><b>FastAPI backend</b><small>API base URL: {apiBase}</small></div><span className="service-status ok">Configured</span></div>

            <div className="service-row"><span className="service-symbol blue-bg"><Database size={16}/></span><div className="service-copy"><b>PostgreSQL database</b><small>Database is configured on the backend; API-level DB test passed</small></div><span className="service-status ok">Backend tested</span></div>

            <div className="service-row"><span className="service-symbol violet-bg"><BrainCircuit size={16}/></span><div className="service-copy"><b>Deep learning model</b><small>Segmentation and stenosis inference</small></div><span className="service-status neutral">Not connected</span></div>

            <div className="service-row"><span className="service-symbol teal-bg"><ShieldCheck size={16}/></span><div className="service-copy"><b>Access control</b><small>JWT login is handled by the backend</small></div><span className="service-status ok">Enabled</span></div>

          </section>

          <section className="panel quick-panel"><div className="panel-heading"><div><h2>Quick actions</h2><p>Start a task without leaving the overview</p></div></div><div className="quick-grid">

            <button className="quick-action" onClick={() => setModal('new-case')}><span className="quick-icon blue-bg"><Plus size={17}/></span><span><b>Create a case</b><small>Set up an imaging case</small></span><ChevronRight size={16}/></button>

            <button className="quick-action" onClick={() => { setUploadedFile(null); setModal('upload'); }}><span className="quick-icon teal-bg"><Upload size={17}/></span><span><b>Upload a scan</b><small>Add an image to a case</small></span><ChevronRight size={16}/></button>

            <button className="quick-action" onClick={() => setActivePage('Cases')}><span className="quick-icon violet-bg"><Search size={17}/></span><span><b>Find a case</b><small>Search case records</small></span><ChevronRight size={16}/></button>

            <button className="quick-action" onClick={() => setActivePage('Model Evaluation')}><span className="quick-icon amber-bg"><ChartNoAxesCombined size={17}/></span><span><b>Model evaluation</b><small>Review metric availability</small></span><ChevronRight size={16}/></button>

          </div></section>

        </div>

        <section className="panel recent-panel"><div className="panel-heading"><div><h2>Recent cases</h2><p>Latest case activity from your account</p></div><button className="text-action" onClick={() => setActivePage('Cases')}>View all cases <ArrowRight size={14}/></button></div>{casesLoading ? <div className="empty-state">Loading your cases...</div> : <CaseTable cases={cases.slice(0,4)} onOpen={openCase} onAnalyze={requestAnalysis} onEditCase={openEditCase} onDeleteCase={deleteCaseRecord} emptyText="No cases yet. Create your first case."/>}</section>

      </>}



      {activePage === 'Cases' && <>

        <SectionHeading eyebrow="CASE WORKSPACE" title="Case management" description="Create, organize, and track coronary imaging cases." action={<button className="btn primary" onClick={() => setModal('new-case')}><Plus size={16}/> New case</button>}/>

        <div className="metrics-grid compact"><MetricCard label="All cases" value={String(cases.length).padStart(2,'0')} meta="Visible in workspace" icon={FolderKanban}/><MetricCard label="Completed" value={String(cases.filter(c=>c.status==='Completed').length).padStart(2,'0')} meta="From your account" icon={CheckCircle2} tone="green"/><MetricCard label="Processing" value={String(cases.filter(c=>c.status==='Processing').length).padStart(2,'0')} meta="From your account" icon={Clock3} tone="violet"/><MetricCard label="Needs attention" value={String(cases.filter(c=>['Pending','Failed'].includes(c.status)).length).padStart(2,'0')} meta="Pending or failed" icon={AlertCircle} tone="amber"/></div>

        <section className="panel table-panel"><div className="filter-bar"><div className="search-field"><Search size={16}/><input value={search} onChange={e=>setSearch(e.target.value)} placeholder="Search by case ID, modality, file..."/></div><div className="filter-controls"><select value={statusFilter} onChange={e=>setStatusFilter(e.target.value)} aria-label="Filter by status"><option>All statuses</option><option>Pending</option><option>Processing</option><option>Completed</option><option>Failed</option></select><button className="btn secondary" onClick={()=>{setSearch('');setStatusFilter('All statuses');}}><SlidersHorizontal size={15}/> Reset</button></div></div>{casesLoading ? <div className="empty-state">Loading your cases...</div> : <CaseTable cases={filteredCases} onOpen={openCase} onAnalyze={requestAnalysis} onEditCase={openEditCase} onDeleteCase={deleteCaseRecord} emptyText="No cases match your search."/>}</section>

      </>}




      {activePage === 'Patients' && <>
        <SectionHeading eyebrow="CASE METADATA" title="Patient records" description="Manage minimal, de-identified metadata that can be linked to imaging cases." action={<button className="btn secondary" onClick={loadPatients} disabled={patientLoading}><RefreshCw size={15}/> Refresh</button>}/>
        <div className="info-callout"><ShieldCheck size={17}/><span>Use public or de-identified datasets. Do not enter patient names, addresses, medical record numbers, or other direct identifiers in this student project.</span></div>
        <div className="two-col patient-page-grid">
          <form className="panel form-stack" onSubmit={submitPatient}><h2>Add patient metadata</h2><div className="settings-field"><label>De-identified code *</label><input maxLength={80} required value={patientForm.display_code} onChange={e=>setPatientForm({...patientForm,display_code:e.target.value})} placeholder="e.g. CCTA-DEMO-001"/></div><div className="field-grid"><div className="settings-field"><label>Age (optional)</label><input type="number" min="0" max="120" value={patientForm.age} onChange={e=>setPatientForm({...patientForm,age:e.target.value})} placeholder="Age"/></div><div className="settings-field"><label>Sex (optional)</label><select value={patientForm.sex} onChange={e=>setPatientForm({...patientForm,sex:e.target.value})}><option value="">Not provided</option><option>Female</option><option>Male</option><option>Other</option><option>Unknown</option></select></div></div><div className="settings-field"><label>Medical history (optional)</label><textarea rows="2" maxLength={5000} value={patientForm.medical_history} onChange={e=>setPatientForm({...patientForm,medical_history:e.target.value})}/></div><div className="settings-field"><label>Risk factors (optional)</label><textarea rows="2" maxLength={5000} value={patientForm.risk_factors} onChange={e=>setPatientForm({...patientForm,risk_factors:e.target.value})}/></div><div className="settings-field"><label>Clinical notes (optional)</label><textarea rows="2" maxLength={5000} value={patientForm.clinical_notes} onChange={e=>setPatientForm({...patientForm,clinical_notes:e.target.value})}/></div><button className="btn primary" type="submit"><Plus size={15}/> Save patient record</button></form>
          <section className="panel table-panel"><div className="panel-heading"><div><h2>Patient metadata</h2><p>{patients.length} record(s) loaded</p></div></div><div className="settings-field"><label>Search by de-identified code</label><div className="search-box"><Search size={15}/><input value={patientSearch} onChange={e=>setPatientSearch(e.target.value)} placeholder="Search patient code"/><button className="text-action" onClick={loadPatients}>Search</button></div></div>{patientLoading ? <div className="empty-state"><RefreshCw size={24}/><b>Loading records…</b></div> : patients.length === 0 ? <div className="empty-state"><Users size={28}/><b>No patient metadata yet</b><p>Create a de-identified record to link it to a case.</p></div> : <div className="table-wrap"><table className="data-table"><thead><tr><th>Code</th><th>Age</th><th>Sex</th><th>Created</th><th></th></tr></thead><tbody>{patients.map(p=><tr key={p.patient_id}><td><b>{p.display_code}</b><small className="table-subtext">{p.patient_id}</small></td><td>{p.age ?? '—'}</td><td>{p.sex || '—'}</td><td>{p.created_at ? formatDate(p.created_at) : '—'}</td><td><button className="text-action danger-text" onClick={async()=>{if(!window.confirm(`Delete patient metadata ${p.display_code}? Cases will keep their data but lose this link.`))return;try{await deletePatient(p.patient_id);await loadPatients();showNotice('Patient record deleted.');}catch(error){showNotice(`Delete failed: ${error.message}`)}}}>Delete</button></td></tr>)}</tbody></table></div>}</section>
        </div>
      </>}

      {activePage === 'Image Analysis' && <>

        <SectionHeading eyebrow="IMAGE WORKSPACE" title="Image analysis" description="Select a case, upload a supported image, and prepare it for model inference." action={<button className="btn secondary" onClick={()=>setModal('upload')}><Upload size={15}/> Upload image</button>}/>

        <div className="analysis-layout"><div className="analysis-main"><div className="panel analysis-viewer-panel"><div className="panel-heading"><div><h2>Image viewer</h2><p>{selectedCase?.id || 'Select a case'} · {selectedCase?.modality || 'CCTA'}</p></div><span className="demo-label">{selectedCase?.imageId ? 'Backend image' : 'No uploaded image'}</span></div><CaseImagePreview caseRecord={selectedCase} loading={imagePreviewLoading} imageUrl={imagePreviewUrl} error={imagePreviewError} onImageError={() => setImagePreviewError('The server returned a file that this browser could not preview.')} onUpload={() => setModal('upload')} /><div className="viewer-controls"><button className="btn secondary small" onClick={()=>showNotice('Image zoom controls will be enabled when the medical image viewer is connected.')}><Eye size={14}/> Viewer tools</button><button className="btn secondary small" onClick={()=>showNotice('No real segmentation mask is connected yet.')}><LayersIcon/> Toggle overlay</button><button className="btn secondary small" disabled={!selectedCase?.imageId || preprocessingLoading} onClick={runBasicPreprocessing}><RefreshCw size={14}/>{preprocessingLoading ? 'Preprocessing…' : 'Preprocess image'}</button><button className="btn primary small" onClick={()=>requestAnalysis(selectedCase || cases[0])}><Zap size={14}/> Request analysis</button></div></div>

          <div className="panel upload-panel"><div className="panel-heading"><div><h2>Input image</h2><p>Attach a medical image to the selected case</p></div></div><div className="upload-drop" onClick={()=>fileInputRef.current?.click()} onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault(); const f=e.dataTransfer.files?.[0]; if(f)setUploadedFile(f);}} role="button" tabIndex={0} onKeyDown={e=>e.key==='Enter'&&fileInputRef.current?.click()}><span className="upload-icon"><Upload size={22}/></span><b>{uploadedFile ? uploadedFile.name : 'Drop a medical image here'}</b><p>Choose a supported file to inspect its name and size.</p><button className="btn secondary" type="button">Browse files</button><input ref={fileInputRef} type="file" accept=".dcm,.nii,.nii.gz,.png,.jpg,.jpeg,.tif,.tiff" hidden onChange={e=>setUploadedFile(e.target.files?.[0]||null)}/>{uploadedFile&&<span className="file-detail"><FileImage size={14}/>{(uploadedFile.size/1024/1024).toFixed(2)} MB · selected locally</span>}</div><div className="upload-footer"><span><ShieldCheck size={14}/> De-identified/public data recommended</span><button className="text-action" onClick={()=>setModal('upload')}>Attach to case <ArrowRight size={13}/></button></div></div></div>

          <aside className="analysis-side"><div className="panel"><div className="panel-heading"><div><h2>Selected case</h2><p>Case information</p></div><IconButton title="Open cases" onClick={()=>setActivePage('Cases')}><ExternalLink size={15}/></IconButton></div>{selectedCase ? <><div className="detail-id">{selectedCase.id}</div><StatusPill status={selectedCase.status}/><div className="detail-list"><Detail label="Modality" value={selectedCase.modality}/><Detail label="Region" value={selectedCase.region}/><Detail label="Created" value={selectedCase.date}/><Detail label="Image" value={selectedCase.file}/></div></>:<p className="muted">Select a case first.</p>}<button className="btn secondary full" onClick={()=>setModal('upload')}><Upload size={15}/> Upload to case</button></div>

            <div className="panel status-note"><span className="notice-icon"><AlertCircle size={17}/></span><h3>Model not connected</h3><p>Actual segmentation, stenosis measurements, and severity outputs will appear after the inference API and trained model are connected.</p></div>

            <div className="panel"><h2 className="mini-title">Analysis pipeline</h2>{['Image validation','Preprocessing','Artery segmentation','Stenosis detection','Results storage'].map((s,i)=><div className="pipeline-row" key={s}><span className="pipeline-number">{i+1}</span><span>{s}</span><span className={`pipeline-state ${i < 2 ? 'pipeline-ready' : ''}`}>{i === 0 ? 'Available' : i === 1 ? 'Basic preview' : 'AI pending'}</span></div>)}</div>

          </aside></div>
        {preprocessingError && <div className="auth-error" role="alert"><AlertCircle size={16}/><span>{preprocessingError}</span></div>}
        {preprocessedImageUrl && <section className="panel preprocessed-preview-panel"><div className="panel-heading"><div><h2>Preprocessed image preview</h2><p>Basic non-AI normalization for inspection only. The uploaded original is unchanged.</p></div><span className="demo-label">Not a diagnosis</span></div><div className="real-image-canvas"><img src={preprocessedImageUrl} alt="Basic preprocessed medical image preview"/></div>{preprocessingMeta?.operations && <div className="preprocessing-operations"><b>Operations applied</b><div>{preprocessingMeta.operations.map((op, index)=><span key={index}>{op}</span>)}</div></div>}<p className="preview-note">For 3D DICOM/NIfTI data this shows a selected 2D slice only. No artery segmentation, stenosis detection, or clinical interpretation is performed.</p></section>}

      </>}



      {activePage === 'Results & Reports' && <>

        <SectionHeading eyebrow="OUTPUTS" title="Results & reports" description="Review analysis-result records stored by the backend." action={<button className="btn secondary" onClick={loadAnalysisResults} disabled={resultsLoading}><RefreshCw size={15}/> {resultsLoading ? 'Refreshing…' : 'Refresh results'}</button>}/>

        <div className="demo-banner"><AlertCircle size={16}/><span>This page reads saved records from the backend. AI inference is not implemented, so an empty results list is expected until a trusted workflow saves analysis outputs.</span></div>
        {resultsError && <div className="auth-error" role="alert"><AlertCircle size={16}/><span>{resultsError}</span></div>}
        <section className="panel table-panel">
          <div className="panel-heading"><div><h2>Saved analysis results</h2><p>{analysisResults.length} result record(s) returned by the backend</p></div></div>
          {resultsLoading ? <div className="empty-state"><RefreshCw size={24}/><b>Loading saved results…</b></div> : analysisResults.length === 0 ? <div className="empty-state"><FileText size={28}/><b>No analysis results saved yet</b><p>This is expected while AI analysis is outside the current implementation.</p></div> : <div className="table-wrap"><table className="data-table"><thead><tr><th>Case</th><th>Model version</th><th>Estimated narrowing</th><th>Confidence</th><th>Created</th></tr></thead><tbody>{analysisResults.map((result) => <tr key={result.result_id}><td><button className="case-link" onClick={() => { const found = cases.find((item) => item.id === result.caseDisplayId); if (found) openCase(found); }}><span><b>{result.caseName}</b><small>{result.caseDisplayId}</small></span></button></td><td>{result.model_version || '—'}</td><td>{result.estimated_narrowing == null ? '—' : `${result.estimated_narrowing}%`}</td><td>{result.confidence_score == null ? '—' : result.confidence_score}</td><td>{result.created_at ? new Date(result.created_at).toLocaleString() : '—'}</td></tr>)}</tbody></table></div>}
        </section>

        <section className="panel results-compare-panel"><div className="panel-heading"><div><h2>Compare saved result records</h2><p>Compares metadata already saved in the database. It does not run AI inference.</p></div></div>{analysisResults.length < 2 ? <div className="empty-state"><ChartNoAxesCombined size={26}/><b>Two stored results are required</b><p>Comparison will be available once two result records exist for the same case.</p></div> : <><div className="field-grid"><div className="settings-field"><label>Case</label><select value={compareCaseId} onChange={e=>{setCompareCaseId(e.target.value);setComparisonData(null);}}>{cases.filter(c=>analysisResults.some(r=>r.caseDisplayId===c.id)).map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select></div><div className="settings-field"><label>Baseline result</label><select value={baselineResultId} onChange={e=>{setBaselineResultId(e.target.value);setComparisonData(null);}}>{compareCandidates.map(r=><option key={r.result_id} value={r.result_id}>{r.model_version || 'Version unknown'} · {new Date(r.created_at).toLocaleString()}</option>)}</select></div><div className="settings-field"><label>Comparison result</label><select value={comparisonResultId} onChange={e=>{setComparisonResultId(e.target.value);setComparisonData(null);}}>{compareCandidates.filter(r=>r.result_id!==baselineResultId).map(r=><option key={r.result_id} value={r.result_id}>{r.model_version || 'Version unknown'} · {new Date(r.created_at).toLocaleString()}</option>)}</select></div></div><button className="btn primary" onClick={runResultsComparison} disabled={comparisonLoading || compareCandidates.length<2 || !baselineResultId || !comparisonResultId}>{comparisonLoading ? 'Comparing…' : 'Compare selected results'}</button>{comparisonData && <div className="comparison-results"><h3>Stored metadata differences</h3><div className="metrics-grid compact"><MetricCard label="Narrowing difference" value={comparisonData.changes.estimated_narrowing_delta == null ? '—' : `${comparisonData.changes.estimated_narrowing_delta}%`} meta="Comparison minus baseline" icon={Activity}/><MetricCard label="Confidence difference" value={comparisonData.changes.confidence_score_delta == null ? '—' : comparisonData.changes.confidence_score_delta} meta="Comparison minus baseline" icon={ChartNoAxesCombined} tone="violet"/><MetricCard label="Model version changed" value={comparisonData.changes.model_version_changed ? 'Yes' : 'No'} meta="Metadata field only" icon={BrainCircuit} tone="blue"/></div></div>}</>}</section>

        <section className="panel"><div className="panel-heading"><div><h2>Cases</h2><p>Select a case to view its uploaded image and export stored records.</p></div></div><CaseTable cases={cases} onOpen={openCase} onAnalyze={requestAnalysis} onEditCase={openEditCase} onDeleteCase={deleteCaseRecord} emptyText="No cases available. Create a case first."/><div className="report-export-list">{cases.map(item=><div className="report-export-row" key={item.id}><div><b>{item.name}</b><small>{item.id}</small></div><div className="report-export-actions"><button className="btn secondary small" onClick={()=>exportReport(item,'pdf')}>PDF</button><button className="btn secondary small" onClick={()=>exportReport(item,'json')}>JSON</button><button className="btn secondary small" onClick={()=>exportReport(item,'csv')}>CSV</button></div></div>)}</div></section>

      </>}



      {activePage === 'Model Evaluation' && <>

        <SectionHeading eyebrow="MODEL QUALITY" title="Model evaluation" description="Track segmentation and detection metrics from actual evaluation runs." action={<button className="btn secondary" onClick={()=>showNotice('Evaluation records will appear after model evaluation is implemented.')}><RefreshCw size={15}/> Refresh metrics</button>}/>

        <div className="demo-banner"><AlertCircle size={16}/><span>Evaluation metrics are not connected yet. Do not interpret placeholder cards as model performance.</span></div>

        <div className="metrics-grid"><MetricCard label="Dice score" value="—" meta="Segmentation metric" icon={ChartNoAxesCombined}/><MetricCard label="IoU" value="—" meta="Segmentation metric" icon={Activity} tone="green"/><MetricCard label="Precision / Recall" value="— / —" meta="Stenosis detection" icon={Workflow} tone="violet"/><MetricCard label="Inference time" value="—" meta="Per image" icon={Zap} tone="amber"/></div>

        <div className="two-col"><div className="panel"><h2>Segmentation evaluation</h2><p className="muted">Metrics will be calculated by comparing model masks with ground-truth annotations.</p><div className="metric-placeholder"><ChartNoAxesCombined size={30}/><b>No evaluation run yet</b><span>Dice, IoU, sensitivity and boundary distance</span></div></div><div className="panel"><h2>Stenosis detection evaluation</h2><p className="muted">Detection results will be compared with dataset annotations and reference labels.</p><div className="metric-placeholder"><Activity size={30}/><b>No evaluation run yet</b><span>Precision, recall, F1-score and AUC-ROC</span></div></div></div>

      </>}



      {activePage === 'Model Registry' && <>
        <SectionHeading eyebrow="MODEL METADATA" title="Model registry" description="Store model names, versions, intended tasks, status, and reported metrics. Registering metadata does not load or run a model." action={<button className="btn secondary" onClick={loadModelRegistry} disabled={modelLoading}><RefreshCw size={15}/> Refresh registry</button>}/>
        <div className="demo-banner"><AlertCircle size={16}/><span>This registry tracks metadata only. It does not train, deploy, evaluate, or run AI models.</span></div>
        {['administrator', 'ml_engineer'].includes(userRole) ? <form className="panel form-stack model-registration-form" onSubmit={submitModel}><h2>Register model metadata</h2><div className="field-grid"><div className="settings-field"><label>Model name *</label><input value={modelForm.model_name} onChange={e=>setModelForm({...modelForm,model_name:e.target.value})} maxLength={150} required placeholder="e.g. Artery segmentation baseline"/></div><div className="settings-field"><label>Version *</label><input value={modelForm.version} onChange={e=>setModelForm({...modelForm,version:e.target.value})} maxLength={50} required placeholder="0.1.0"/></div></div><div className="field-grid"><div className="settings-field"><label>Task</label><select value={modelForm.task} onChange={e=>setModelForm({...modelForm,task:e.target.value})}><option value="segmentation">Segmentation</option><option value="stenosis_detection">Stenosis detection</option><option value="centerline">Centerline</option><option value="other">Other</option></select></div><div className="settings-field"><label>Status</label><select value={modelForm.status} onChange={e=>setModelForm({...modelForm,status:e.target.value})}><option value="planned">Planned</option><option value="available">Available</option><option value="deployed">Deployed</option><option value="retired">Retired</option></select></div></div><div className="field-grid"><div className="settings-field"><label>Framework (optional)</label><input value={modelForm.framework} onChange={e=>setModelForm({...modelForm,framework:e.target.value})} placeholder="e.g. PyTorch"/></div><div className="settings-field"><label>Model reference (optional)</label><input value={modelForm.model_reference} onChange={e=>setModelForm({...modelForm,model_reference:e.target.value})} placeholder="Internal path or controlled URI"/></div></div><div className="settings-field"><label>Description (optional)</label><textarea rows="2" value={modelForm.description} onChange={e=>setModelForm({...modelForm,description:e.target.value})}/></div><button className="btn primary" type="submit"><Plus size={15}/> Register metadata</button></form> : <div className="info-callout"><LockKeyhole size={17}/><span>Your current role is {authUser?.role || 'researcher'}. Only administrators or ML engineers can add or update model metadata.</span></div>}
        <section className="panel table-panel"><div className="panel-heading"><div><h2>Registered models</h2><p>{modelsList.length} model record(s)</p></div></div>{modelLoading ? <div className="empty-state"><RefreshCw size={24}/><b>Loading model metadata…</b></div> : modelsList.length === 0 ? <div className="empty-state"><BrainCircuit size={28}/><b>No model metadata registered</b><p>Records can be added when the model versions and owners are known.</p></div> : <div className="table-wrap"><table className="data-table"><thead><tr><th>Name / version</th><th>Task</th><th>Framework</th><th>Status</th><th>Created / updated</th><th></th></tr></thead><tbody>{modelsList.map(model=><tr key={model.model_id}><td><b>{model.model_name}</b><small className="table-subtext">v{model.version}</small>{model.description&&<small>{model.description}</small>}</td><td>{model.task.replaceAll('_',' ')}</td><td>{model.framework || '—'}</td><td><span className={`status-pill ${model.status}`}>{model.status}</span></td><td>{model.updated_at ? new Date(model.updated_at).toLocaleDateString() : '—'}</td><td>{['administrator','ml_engineer'].includes(authUser?.role) && model.status !== 'retired' ? <button className="text-action" onClick={()=>retireModel(model.model_id)}>Retire</button> : '—'}</td></tr>)}</tbody></table></div>}</section>
      </>}

      {activePage === 'Activity Logs' && <>

        <SectionHeading eyebrow="TRACEABILITY" title="Activity logs" description="Review case events returned by the backend." action={<button className="btn secondary" onClick={loadActivityHistory} disabled={historyLoading}><RefreshCw size={15}/> {historyLoading ? 'Refreshing…' : 'Refresh history'}</button>}/>

        {historyError && <div className="auth-error" role="alert"><AlertCircle size={16}/><span>{historyError}</span></div>}
        <section className="panel">
          <div className="panel-heading"><div><h2>Case activity</h2><p>{activityHistory.length} event(s) returned from case history APIs</p></div></div>
          {historyLoading ? <div className="empty-state"><RefreshCw size={24}/><b>Loading activity history…</b></div> : activityHistory.length === 0 ? <div className="empty-state"><History size={28}/><b>No activity history found</b><p>Events appear here when the backend records case creation, updates, and other supported actions.</p></div> : activityHistory.map((entry) => <div className="log-row" key={entry.history_id}><span className="log-mark violet-bg"><History size={16}/></span><div><b>{entry.action || 'Case activity'}</b><small>{entry.caseName || entry.caseId} · {entry.status || 'Status unavailable'}{entry.message ? ` · ${entry.message}` : ''}</small></div><span className="log-time">{entry.created_at ? new Date(entry.created_at).toLocaleString() : '—'}</span></div>)}
        </section>
        {authUser?.role === 'administrator' && <section className="panel table-panel audit-panel"><div className="panel-heading"><div><h2>Security audit log</h2><p>Administrative view of recorded sensitive actions.</p></div><button className="btn secondary" onClick={loadAdminAudit}><RefreshCw size={14}/> Refresh</button></div>{auditError && <div className="auth-error" role="alert"><AlertCircle size={16}/><span>{auditError}</span></div>}{auditLogs.length === 0 ? <div className="empty-state"><History size={24}/><b>No audit entries loaded</b></div> : <div className="table-wrap"><table className="data-table"><thead><tr><th>Action</th><th>Resource</th><th>Outcome</th><th>Timestamp</th><th>User ID</th></tr></thead><tbody>{auditLogs.map(row=><tr key={row.audit_id}><td>{row.action}</td><td>{row.resource_type} · {row.resource_id || '—'}</td><td>{row.outcome}</td><td>{row.created_at ? new Date(row.created_at).toLocaleString() : '—'}</td><td>{row.user_id || '—'}</td></tr>)}</tbody></table></div>}</section>}

      </>}



      {activePage === 'Settings' && <>
        <SectionHeading eyebrow="ACCOUNT & WORKSPACE" title="Settings" description="Manage your profile, password, and backend connection."/>
        <div className="settings-grid">
          <div className="panel"><h2>Profile</h2><div className="settings-profile"><span className="avatar big">{(authUser?.full_name || 'User').split(/\s+/).map(part => part[0]).join('').slice(0,2).toUpperCase()}</span><div><b>{authUser?.full_name || 'User'}</b><p className="muted">{authUser?.email || ''} · {authUser?.role || 'researcher'}</p></div></div><form className="form-stack" onSubmit={e=>{e.preventDefault();saveProfile();}}><div className="settings-field"><label>Display name</label><input value={profileName} onChange={e=>setProfileName(e.target.value)} minLength={2} maxLength={100} required/></div><div className="settings-field"><label>Email (not editable here)</label><input value={authUser?.email || ''} readOnly/></div><div className="settings-field"><label>Role (assigned by an administrator)</label><input value={authUser?.role || 'researcher'} readOnly/></div><button className="btn primary" type="submit" disabled={profileSaving}>{profileSaving ? 'Saving…' : 'Save profile'}</button></form></div>
          <div className="panel"><h2>Change password</h2><p className="muted">Changing your password revokes active sessions. You must sign in again afterward.</p><form className="form-stack" onSubmit={e=>{e.preventDefault();savePassword();}}><div className="settings-field"><label>Current password</label><input type="password" value={currentPassword} onChange={e=>setCurrentPassword(e.target.value)} required autoComplete="current-password"/></div><div className="settings-field"><label>New password (at least 8 characters)</label><input type="password" value={newPassword} onChange={e=>setNewPassword(e.target.value)} minLength={8} maxLength={128} required autoComplete="new-password"/></div><button className="btn secondary" type="submit" disabled={passwordSaving}>{passwordSaving ? 'Updating…' : 'Change password'}</button></form></div>
          <div className="panel"><h2>Backend connection</h2><p className="muted">Configure the FastAPI base URL using your frontend environment file.</p><div className="settings-field"><label>API base URL</label><input value={apiBase || 'Not configured — demo mode'} readOnly/></div><div className="connection-state"><span className={`dot ${apiBase?'green':'amber'}`}/><div><b>{apiBase ? 'API URL configured' : 'Demo mode active'}</b><small>{apiBase ? 'Use the health test to verify reachability.' : 'Set VITE_API_BASE_URL in .env.local and restart Vite.'}</small></div></div><button className="btn secondary" onClick={refreshHealth}><RefreshCw size={15}/> Test health endpoint</button></div>
          <div className="panel"><h2>Security</h2><div className="service-row"><LockKeyhole size={17}/><div className="service-copy"><b>JWT session tracking</b><small>Backend stores and revokes login sessions</small></div><span className="service-status ok">Enabled</span></div><div className="service-row"><ShieldCheck size={17}/><div className="service-copy"><b>Case ownership checks</b><small>Access is enforced by the API for each case</small></div><span className="service-status ok">Enabled</span></div><div className="form-note"><AlertCircle size={15}/> Keep .env private and rotate the secret key if a token or secret was shared.</div></div>
        </div>
        {authUser?.role === 'administrator' && <section className="panel table-panel role-management-panel">
          <div className="panel-heading role-management-heading"><div><h2><UserCog size={17}/> Role Management</h2><p>Review registered accounts and assign application roles. Role changes revoke the affected user's current sessions.</p></div><button type="button" className="btn secondary" onClick={loadAdminUsers} disabled={adminUsersLoading}><RefreshCw size={14}/> {adminUsersLoading ? 'Refreshing…' : 'Refresh users'}</button></div>
          {adminUsersError && <div className="auth-error" role="alert"><AlertCircle size={16}/><span>{adminUsersError}</span></div>}
          {adminUsersLoading && adminUsers.length === 0 ? <div className="empty-state"><RefreshCw size={24}/><b>Loading registered users…</b></div> : adminUsers.length === 0 ? <div className="empty-state"><Users size={26}/><b>No registered users found</b><p>Users who register will appear here.</p></div> : <div className="table-wrap"><table className="data-table role-management-table"><thead><tr><th>User</th><th>Email</th><th>Current role</th><th>Account</th><th>Assign role</th><th>Action</th></tr></thead><tbody>{adminUsers.map((user) => { const isSelf = user.user_id === authUser?.user_id; const isEditing = editingRoleUserId === user.user_id; return <tr key={user.user_id}><td><b>{user.full_name}</b><small className="table-subtext">Joined {user.created_at ? formatDate(user.created_at) : 'date unavailable'}</small></td><td>{user.email}</td><td><span className={`role-badge role-${String(user.role || 'researcher').toLowerCase()}`}>{String(user.role || 'researcher').replaceAll('_', ' ')}</span>{isSelf && <small className="table-subtext">Signed-in administrator</small>}</td><td><span className={`status-pill ${user.is_active ? 'completed' : 'failed'}`}>{user.is_active ? 'Active' : 'Inactive'}</span></td><td>{isSelf ? <span className="muted">Your role cannot be changed here</span> : <select className="role-select" aria-label={`Role for ${user.email}`} value={isEditing ? editingRoleValue : user.role} disabled={Boolean(roleSavingUserId)} onChange={(event) => { setEditingRoleUserId(user.user_id); setEditingRoleValue(event.target.value); }}><option value="clinician">Clinician</option><option value="researcher">Researcher</option><option value="ml_engineer">ML Engineer</option><option value="administrator">Administrator</option></select>}</td><td>{isSelf ? '—' : isEditing ? <div className="role-action-group"><button type="button" className="btn primary small-btn" onClick={() => saveUserRole(user)} disabled={roleSavingUserId === user.user_id || editingRoleValue === user.role}>{roleSavingUserId === user.user_id ? 'Saving…' : <><Save size={13}/> Save</>}</button><button type="button" className="btn secondary small-btn" onClick={() => { setEditingRoleUserId(''); setEditingRoleValue('researcher'); }} disabled={roleSavingUserId === user.user_id}>Cancel</button></div> : <button type="button" className="text-action" onClick={() => { setEditingRoleUserId(user.user_id); setEditingRoleValue(user.role); }}>Edit role</button>}</td></tr>; })}</tbody></table></div>}
          <div className="form-note role-management-note"><ShieldCheck size={15}/> Public sign-up always receives the Researcher role. Only the backend-authorized administrator can assign a different role; you cannot change your own role.</div>
        </section>}
      </>}


      <footer className="app-footer"><span>ArteryVision <span className="footer-sep">•</span> Medical image analysis workspace</span><span><i className="dot green"/> Backend-connected frontend <span className="footer-sep">•</span> Not for clinical diagnosis</span></footer>

    </main>



    {modal === 'new-case' && <Modal title="Create a new case" onClose={()=>setModal('')} footer={<><button className="btn secondary" onClick={()=>setModal('')}>Cancel</button><button className="btn primary" form="new-case-form" type="submit"><Plus size={15}/> Create case</button></>}><form id="new-case-form" className="form-stack" onSubmit={createCase}><div className="settings-field"><label>Case name *</label><input value={newCase.name} onChange={e=>setNewCase({...newCase,name:e.target.value})} placeholder="e.g. CCTA research case 001" maxLength={150} required /></div><div className="field-grid"><div className="settings-field"><label>Imaging modality *</label><select value={newCase.modality} onChange={e=>setNewCase({...newCase,modality:e.target.value})}><option value="CCTA">CCTA — Coronary CT Angiography</option><option value="XCA">X-ray Coronary Angiography</option></select></div><div className="settings-field"><label>Anatomical region *</label><select value={newCase.region} onChange={e=>setNewCase({...newCase,region:e.target.value})}><option>Coronary arteries</option><option>Left coronary artery</option><option>Right coronary artery</option><option>Other vascular region</option></select></div></div><div className="settings-field"><label>Linked patient record (optional)</label><select value={newCase.patientId} onChange={e=>setNewCase({...newCase,patientId:e.target.value})}><option value="">No patient link</option>{patients.map(patient=><option key={patient.patient_id} value={patient.patient_id}>{patient.display_code}</option>)}</select></div><div className="settings-field"><label>Notes (optional)</label><textarea value={newCase.notes} onChange={e=>setNewCase({...newCase,notes:e.target.value})} rows="3" placeholder="Add non-identifying case notes..."/></div><div className="form-note"><ShieldCheck size={15}/> Use public or de-identified data. Avoid entering patient-identifying information in this demo.</div></form></Modal>}

    {modal === 'edit-case' && <Modal title="Edit case details" onClose={()=>setModal('')} footer={<><button className="btn secondary" onClick={()=>setModal('')}>Cancel</button><button className="btn primary" type="submit" form="edit-case-form" disabled={caseSaveLoading}><Pencil size={15}/>{caseSaveLoading ? 'Saving…' : 'Save changes'}</button></>}><form id="edit-case-form" className="form-stack" onSubmit={saveCaseEdits}><div className="settings-field"><label>Case name *</label><input maxLength={150} required value={editCaseForm.name} onChange={e=>setEditCaseForm({...editCaseForm,name:e.target.value})}/></div><div className="field-grid"><div className="settings-field"><label>Modality</label><select value={editCaseForm.modality} onChange={e=>setEditCaseForm({...editCaseForm,modality:e.target.value})}><option value="CCTA">CCTA — Coronary CT Angiography</option><option value="XCA">XCA — X-ray Coronary Angiography</option></select></div><div className="settings-field"><label>Anatomical region</label><select value={editCaseForm.region} onChange={e=>setEditCaseForm({...editCaseForm,region:e.target.value})}><option>Coronary arteries</option><option>Left coronary artery</option><option>Right coronary artery</option><option>Other vascular region</option></select></div></div><div className="settings-field"><label>Scan date (optional)</label><input type="date" value={editCaseForm.scanDate} onChange={e=>setEditCaseForm({...editCaseForm,scanDate:e.target.value})}/></div><div className="settings-field"><label>Linked patient (optional)</label><select value={editCaseForm.patientId} onChange={e=>setEditCaseForm({...editCaseForm,patientId:e.target.value})}><option value="">No patient link</option>{patients.map(patient=><option key={patient.patient_id} value={patient.patient_id}>{patient.display_code}</option>)}</select></div><div className="settings-field"><label>Notes</label><textarea rows="3" maxLength={5000} value={editCaseForm.notes} onChange={e=>setEditCaseForm({...editCaseForm,notes:e.target.value})}/></div></form></Modal>}

    {modal === 'upload' && <Modal title="Upload a medical image" onClose={()=>setModal('')} footer={<><button className="btn secondary" onClick={()=>setModal('')}>Cancel</button><button className="btn primary" onClick={submitUpload} disabled={uploading}>{uploading ? <><RefreshCw size={15}/> Uploading…</> : <><Upload size={15}/> Attach image</>}</button></>}><form className="form-stack" onSubmit={submitUpload}><div className="settings-field"><label>Attach to case *</label><select value={uploadCaseId} onChange={e=>setUploadCaseId(e.target.value)} required disabled={!cases.length}>{cases.map(c=><option key={c.id} value={c.id}>{c.name || c.id} — {c.region}</option>)}</select></div><div className="modal-drop" onClick={()=>modalFileInputRef.current?.click()} onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();if(e.dataTransfer.files?.[0])setUploadedFile(e.dataTransfer.files[0]);}}><Upload size={26}/><b>{uploadedFile ? uploadedFile.name : 'Choose or drop a scan file'}</b><span>Supported selection: DICOM, NIfTI, PNG, JPEG, TIFF</span><button type="button" className="btn secondary" onClick={e=>{e.stopPropagation();modalFileInputRef.current?.click();}}>Browse files</button><input ref={modalFileInputRef} hidden type="file" accept=".dcm,.nii,.gz,.png,.jpg,.jpeg,.tif,.tiff" onChange={e=>setUploadedFile(e.target.files?.[0]||null)}/>{uploadedFile && <small>{(uploadedFile.size/1024/1024).toFixed(2)} MB · selected in browser</small>}</div><div className="form-note"><AlertCircle size={15}/> The selected file will be uploaded to the backend when you click Attach image.</div></form></Modal>}



    {notice && <div className="toast" role="status"><CheckCircle2 size={17}/><span>{notice}</span><button onClick={()=>setNotice('')} aria-label="Dismiss notification"><X size={15}/></button></div>}

  </div>;

}



function AuthScreen({ dark, setDark, mode, setMode, fullName, setFullName, email, setEmail, password, setPassword, loading, error, onSubmit }) {
  const isRegister = mode === 'register';
  return (
    <div className={`app-shell ${dark ? 'dark-mode' : ''}`} style={{ minHeight: '100vh' }}>
      <header className="topbar">
        <div className="brand" aria-label="ArteryVision">
          <span className="brand-mark"><HeartPulse size={22} /></span>
          <span className="brand-text"><b>ArteryVision</b><small>Coronary Imaging Workspace</small></span>
        </div>
        <div className="topbar-right">
          <button className="theme-button" type="button" onClick={() => setDark(!dark)}>
            {dark ? <Sun size={16} /> : <Moon size={16} />}<span>{dark ? 'Dark' : 'Light'}</span>
          </button>
        </div>
      </header>
      <main className="auth-main" style={{ width: 'min(1080px, calc(100% - 40px))', margin: '56px auto', display: 'grid', gridTemplateColumns: 'minmax(0, 1.1fr) minmax(320px, .9fr)', gap: 48, alignItems: 'center' }}>
        <section>
          <div className="hero-kicker"><Activity size={13} /> MEDICAL IMAGE INTELLIGENCE</div>
          <h1 style={{ fontSize: 'clamp(34px, 4vw, 54px)', lineHeight: 1.08, margin: '20px 0' }}>Understand arteries.<br />Visualize findings with clarity.</h1>
          <p style={{ lineHeight: 1.8, maxWidth: 550, color: 'var(--muted, #718096)' }}>Manage coronary imaging cases, upload medical scans, and review available artery segmentation and stenosis analysis results in one workspace.</p>
          <div style={{ display: 'grid', gap: 16, marginTop: 28 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}><ShieldCheck size={18} /> Secure user access</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}><Database size={18} /> Organized case management</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}><ScanLine size={18} /> Medical image workflows</div>
          </div>
          <p style={{ fontSize: 12, opacity: .75, marginTop: 30 }}>For research and decision support; not a standalone diagnostic system.</p>
        </section>
        <section className="panel" style={{ padding: 28, borderRadius: 18, maxWidth: 460, width: '100%', justifySelf: 'end' }}>
          <div className="eyebrow">{isRegister ? 'CREATE ACCOUNT' : 'WELCOME BACK'}</div>
          <h2 style={{ margin: '10px 0 8px' }}>{isRegister ? 'Create your account' : 'Sign in'}</h2>
          <p style={{ marginTop: 0, marginBottom: 22, color: 'var(--muted, #718096)' }}>{isRegister ? 'Register to access your imaging workspace.' : 'Sign in to manage your medical cases.'}</p>
          <form className="form-stack" onSubmit={onSubmit}>
            {isRegister && <div className="settings-field"><label htmlFor="auth-full-name">Full name</label><input id="auth-full-name" value={fullName} onChange={e => setFullName(e.target.value)} placeholder="Enter your full name" minLength={2} maxLength={100} required /></div>}
            <div className="settings-field"><label htmlFor="auth-email">Email address</label><input id="auth-email" type="email" autoComplete="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" required /></div>
            <div className="settings-field"><label htmlFor="auth-password">Password</label><input id="auth-password" type="password" autoComplete={isRegister ? 'new-password' : 'current-password'} minLength={isRegister ? 8 : undefined} value={password} onChange={e => setPassword(e.target.value)} placeholder="Enter your password" required /></div>
            {error && <div role="alert" className="info-callout" style={{ color: '#dc2626' }}><AlertCircle size={16} /><span>{error}</span></div>}
            <button className="btn primary" type="submit" disabled={loading} style={{ width: '100%', justifyContent: 'center', marginTop: 4 }}>{loading ? 'Please wait...' : isRegister ? 'Create account' : 'Sign in'}</button>
          </form>
          <div style={{ marginTop: 20, display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: 6, fontSize: 13 }}>
            <span>{isRegister ? 'Already have an account?' : "Don't have an account?"}</span>
            <button type="button" className="text-action" onClick={() => setMode(isRegister ? 'login' : 'register')}>{isRegister ? 'Sign in' : 'Register'}</button>
          </div>
        </section>
      </main>
      <style>{`@media (max-width: 760px) { .auth-main { grid-template-columns: 1fr !important; } }`}</style>
    </div>
  );
}

function LayersIcon() { return <Workflow size={14}/>; }

function Detail({ label, value }) { return <div className="detail-row"><span>{label}</span><b>{value || '—'}</b></div>; }

function CaseTable({ cases, onOpen, onAnalyze, onEditCase, onDeleteCase, emptyText = 'No cases available.' }) {

  if (!cases.length) return <div className="empty-state"><FolderKanban size={28}/><b>{emptyText}</b><p>Try changing the search or filter.</p></div>;

  return <div className="table-wrap"><table className="data-table"><thead><tr><th>Case ID</th><th>Modality</th><th>Anatomical region</th><th>Created</th><th>Status</th><th className="align-right">Actions</th></tr></thead><tbody>{cases.map(item=><tr key={item.id}><td><button className="case-link" onClick={()=>onOpen(item)}><span className="case-mini-icon"><FileImage size={15}/></span><span><b>{item.name || item.id}</b><small>{item.id} · {item.file}</small></span></button></td><td><span className="modality-tag">{item.modality}</span></td><td>{item.region}</td><td><span className="date-cell"><CalendarDays size={13}/>{item.date}</span></td><td><StatusPill status={item.status}/></td><td><div className="row-actions"><IconButton title="Open image workspace" onClick={()=>onOpen(item)}><Eye size={15}/></IconButton><IconButton title="Analysis status (AI not connected)" onClick={()=>onAnalyze(item)}><Zap size={15}/></IconButton>{onEditCase && <IconButton title="Edit case" onClick={()=>onEditCase(item)}><Pencil size={15}/></IconButton>}{onDeleteCase && <IconButton title="Delete case" onClick={()=>onDeleteCase(item)}><Trash2 size={15}/></IconButton>}</div></td></tr>)}</tbody></table></div>;

}
