// ─── Trident Funnel — Entry Point ─────────────────────────────────────────────
// Import these three components and add them to your React Router.
//
// Usage:
//   import { EmailFunnel, AlertsPage, AlertDetailPage } from './trident-funnel';
//
//   <Route path="/funnel"             element={<EmailFunnel />} />
//   <Route path="/alerts/:bucket"     element={<AlertsPage />} />
//   <Route path="/alerts/:bucket/:id" element={<AlertDetailPage />} />

export { default as EmailFunnel      } from './EmailFunnel';
export { default as AlertsPage       } from './pages/AlertsPage';
export { default as AlertDetailPage  } from './pages/AlertDetailPage';
