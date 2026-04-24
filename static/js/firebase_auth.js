/**
 * EduEvent – Firebase Auth Client
 * Handles Firebase Email Authentication on the frontend.
 * The Firebase config is injected by Django template context processor.
 */

let firebaseApp = null;
let firebaseAuth = null;

async function initFirebase() {
  if (firebaseApp) return;
  try {
    const res = await fetch('/api/auth/firebase-config/');
    const config = await res.json();
    
    if (!config.apiKey) {
      console.warn('Firebase config missing from env. Using demo mode.');
      return;
    }
    firebaseApp = firebase.initializeApp(config);
    firebaseAuth = firebase.auth();
    console.log('✅ Firebase initialized');
  } catch (e) {
    console.error('Firebase init error:', e);
  }
}

// Auto-initialize when loaded
initFirebase();

/**
 * Register with Firebase Email/Password, then register in Django backend.
 */
async function firebaseRegister(email, password, userData) {
  if (!firebaseAuth) {
    // Demo mode: generate a fake UID and register directly
    const fakeUid = 'demo_' + Date.now() + '_' + Math.random().toString(36).slice(2);
    return await API.register({ ...userData, firebase_uid: fakeUid, email });
  }

  try {
    const userCredential = await firebaseAuth.createUserWithEmailAndPassword(email, password);
    const uid = userCredential.user.uid;
    return await API.register({ ...userData, firebase_uid: uid, email });
  } catch (err) {
    throw new Error(err.message || 'Registration failed');
  }
}

/**
 * Login with Firebase Email/Password, then create Django session.
 */
async function firebaseLogin(email, password, role) {
  if (!firebaseAuth) {
    // Demo mode: login with email only (backend handles demo auth)
    const fakeUid = 'demo_' + email.replace(/[^a-z0-9]/gi, '_');
    return await API.login({ firebase_uid: fakeUid, email, role });
  }

  try {
    const userCredential = await firebaseAuth.signInWithEmailAndPassword(email, password);
    const uid = userCredential.user.uid;
    return await API.login({ firebase_uid: uid, email, role });
  } catch (err) {
    throw new Error(err.message || 'Login failed');
  }
}

/**
 * Logout from both Firebase and Django.
 */
async function firebaseLogout() {
  if (firebaseAuth) {
    try { await firebaseAuth.signOut(); } catch (e) { /* ignore */ }
  }
  await API.logout();
}

/**
 * Get current Firebase user (if any).
 */
function getCurrentFirebaseUser() {
  if (!firebaseAuth) return null;
  return firebaseAuth.currentUser;
}
