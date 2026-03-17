/**
 * auth/index.js — barrel export
 *
 * Usage in App.jsx (or any parent):
 *
 *   // Full page (100vh transparent section + scroll-exit animation)
 *   import AuthSection from './components/auth';
 *
 *   // Panel only (drop it yourself inside any container)
 *   import { AuthPanel } from './components/auth';
 */
export { default }       from './AuthSection'; // default → AuthSection
export { default as AuthPanel } from './AuthPanel';
