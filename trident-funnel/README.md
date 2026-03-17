# trident-funnel

A self-contained React module — the Trident AI email fraud detection funnel with full alert navigation. Drop it into any React + Vite project.

---

## What's inside

```
trident-funnel/
├── config.js                 ← ⚙️  Set your API URL here (only file you touch)
├── index.js                  ← Re-exports all three components
├── gmail-ball.png            ← Ball icon used in the funnel animation
├── EmailFunnel.jsx           ← Physics-based funnel animation (Matter.js)
└── pages/
    ├── AlertsPage.jsx        ← Fraud / Safe alert list (fetches from Trident API)
    └── AlertDetailPage.jsx   ← Full analysis view (gauge, modules, radar, factors)
```

---

## Integration (3 steps)

### 1. Install dependencies

```bash
npm install matter-js react-router-dom
```

### 2. Copy the asset

Copy `gmail-ball.png` into your project's `public/` folder:

```
public/
  gmail-ball.png
```

### 3. Set your API URL

Open `trident-funnel/config.js` and point it at your Trident FastAPI instance:

```js
export const TRIDENT_API_BASE = "http://your-server:8000";
```

### 4. Add the routes

In your existing router (wherever you define `<Routes>`):

```jsx
import { EmailFunnel, AlertsPage, AlertDetailPage } from './trident-funnel';

// Inside your <Routes>:
<Route path="/funnel"             element={<EmailFunnel />} />
<Route path="/alerts/:bucket"     element={<AlertsPage />} />
<Route path="/alerts/:bucket/:id" element={<AlertDetailPage />} />
```

---

## Navigation flow

```
/funnel
  ├── click FRAUD  →  /alerts/fraud   (CRITICAL / HIGH / MEDIUM alerts)
  │                        └── [▶ VIEW]  →  /alerts/fraud/:id
  │
  └── click SAFE   →  /alerts/safe    (LOW alerts)
                           └── [▶ VIEW]  →  /alerts/safe/:id
```

---

## What the detail view shows

Data is read directly from the Trident API response — nothing is hardcoded:

| Section | Source field |
|---|---|
| Risk gauge | `alert.risk_score` |
| Band badge | `alert.risk_band` |
| Recommended action | `alert.recommended_action` |
| Module score bars | `trident_result.module_scores` |
| Top risk factors | `trident_result.top_factors` |
| Explanation text | `trident_result.explanation` |
| Module radar chart | `trident_result.module_scores` (≥3 modules) |
| Confidence / processing time | `trident_result.confidence`, `.processing_time_ms` |
| Debug JSON | Full raw alert object |

---

## Requirements

| Dependency | Version |
|---|---|
| react | ≥ 18 |
| react-router-dom | ≥ 6 |
| matter-js | ≥ 0.19 |

---

## Trident API expected response

`GET /alerts?limit=50` should return:

```json
{
  "alerts": [
    {
      "received_at": "2026-03-17T10:00:00Z",
      "alert": {
        "subject": "...",
        "sender": "...",
        "email_text": "...",
        "risk_score": 91.4,
        "risk_band": "CRITICAL",
        "recommended_action": "BLOCK",
        "explanation": "...",
        "top_factors": ["..."],
        "module_scores": { "phishing": 95.0, "url_detection": 88.0 },
        "trident_result": { ... }
      }
    }
  ]
}
```
