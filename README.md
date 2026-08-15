# SurakshaNet — Privacy-Preserving Community Health Anomaly Detection Platform

SurakshaNet is a complete, hackathon-ready decision-support prototype built for Smart India Hackathon (SIH) Problem Statement S10. It demonstrates how community disease clusters and symptom anomalies can be detected in real time by combining multiple decentralized, privacy-protected data sources without centralizing individual patient records.

---

## 1. Problem Statement
Public health systems require timely alerts of disease outbreaks. However, collecting and centralizing raw health records (such as clinic logs, pharmacy prescriptions, and diagnostic results) from various private and public institutions poses extreme privacy, data leak, and regulatory compliance risks. SurakshaNet addresses this challenge by maintaining a core principle: **"Detect the signal, not the person."**

---

## 2. Architecture & Data Flow
SurakshaNet separates raw clinical processing from central statistical aggregation using local nodes.

```text
  [ LOCAL CLINIC INTRANET ]
              │
              ▼ (Raw patient records: symptom, age, hostel location)
   Identifier Scrubbing & Filtering
              │
              ▼ (De-identified symptom counts)
    Small-Group Protection Threshold Check
              │ (If count < 10, data is suppressed)
              ▼
   Differential Privacy Noise Addition (Laplace)
              │
              ▼ (Protected aggregate JSON payload: e.g. {"gastrointestinal": 52.1})
      Encrypted API Transmission (HTTPS POST)
              │
              ▼
  [ CENTRAL ANALYTICS SERVER ]
              │
              ▼
  Univariate Baseline & Z-Score Analysis 
  (Compares observed value vs. historical normal range)
              │
              ▼
  Multivariate Anomaly Ingress (Isolation Forest Classifier)
              │
              ▼
  Triangulated Signal Fusion & Risk Scoring
  (Clinic: 40% | Water: 30% | Pharmacy: 20% | Environment: 10%)
              │
              ▼
  Explainable AI (XAI) Contribution Engine
  (Identifies relative signal impacts and generates alerts)
```

---

## 3. Privacy Model & Differential Privacy (DP)
SurakshaNet guarantees local differential privacy using two robust protection mechanisms:

### 1. Laplace Mechanism
At the local node boundary, aggregate counts of symptoms are transformed by adding noise sampled from a Laplace distribution:
$$f(x) = \text{Count} + Y$$
Where $Y \sim \text{Laplace}(0, \frac{\Delta f}{\epsilon})$.
- **Epsilon ($\epsilon$)**: The privacy budget. Smaller epsilon increases noise, offering stronger privacy but reducing data accuracy.
- **Sensitivity ($\Delta f$)**: The maximum influence a single individual can have on the query outcome (for counting queries, sensitivity = 1).

### 2. Small-Group Suppression
To prevent the re-identification of individuals in small populations (e.g. rural sectors or small hostels), a minimum threshold ($k = 10$) is enforced. If the raw aggregate count is less than 10, the count is suppressed entirely and reported as `"SUPPRESSED"`.

---

## 4. Anomaly Detection & Triangulation Methodology

### Univariate Z-Score
For each signal, the current value is compared against its historical baseline:
$$Z = \frac{x_{\text{observed}} - \mu_{\text{baseline}}}{\sigma_{\text{baseline}}}$$
- For symptoms and environmental variables, only positive deviation (risk) is evaluated.
- For water pH, absolute deviation in both directions is computed.

### Multivariate Isolation Forest
An Isolation Forest model trains dynamically on $N = 200$ synthetic normal baseline inputs for the target area, scoring the current vector of combined signals. The resulting anomaly index is normalized to a $[0, 100]$ scale.

### Triangulation (Signal Fusion) & Data Quality Controls
Risk scores are calculated by fusing univariate deviations using weights:
- **Clinic Symptoms**: $40\%$
- **Water Quality Indicators**: $30\%$
- **Pharmacy OTC Demand**: $20\%$
- **Environmental Factors**: $10\%$

#### Data Quality False Alarm Protection:
- **Single Source Spike**: If only clinic cases spike but water/pharmacy metrics are normal, the system flags the state as `VERIFY` (Under Verification), notifying officials of a potential reporting anomaly.
- **Rural Under-Reporting**: If water quality is contaminated but clinic metrics are low, the status triggers `WATCH / DATA GAP`, alerting officers to a possible clinical reporting lag.

---

## 5. Technology Stack
- **Backend**: Python 3.13, FastAPI (with CORS, static mounts), Uvicorn server, Pydantic (data models), Pandas, NumPy, Scikit-learn (Isolation Forest), SQLite (relational storage).
- **Frontend**: React.js, Tailwind CSS (modern curated color scheme, typography), Chart.js (interactive line/bar and XAI doughnut charts), Lucide Icons.

---

## 6. Project Structure
```text
surakshanet/
├── backend/
│   ├── main.py              # Application entry point, server launch
│   ├── models/
│   │   └── schemas.py       # Pydantic validation schemas
│   ├── data/
│   │   ├── database.py      # SQLite connection, baseline & scenario seeding
│   │   └── surakshanet.db   # SQLite relational database
│   ├── privacy/
│   │   └── processor.py     # Laplace noise & small-group suppression
│   ├── analytics/
│   │   └── engine.py        # Z-scores, Isolation Forest, and Risk Scoring
│   ├── api/
│   │   └── endpoints.py     # FastAPI routers (scenarios, audits, aggregation)
│   ├── static/
│   │   └── index.html       # Single-Page App (Landing, Citizen, Officer, Node)
│   └── tests/
│       └── test_surakshanet.py # Unit tests for privacy, analytics, APIs
├── README.md
└── requirements.txt
```

---

## 7. Setup & Run Instructions

### 1. Prerequisites
Make sure Python 3.11+ is installed on your computer.

### 2. Install Dependencies
Navigate to the `backend/` directory and install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run Server
Execute `main.py` to start the backend API and serve the React interface:
```bash
python main.py
```
Open your browser and navigate to:
**`http://127.0.0.1:8000`**

### 4. Run Unit Tests
To execute the automated test suite, run:
```bash
python -m pytest tests/test_surakshanet.py
```

---

## 8. API Documentation
- **`GET /api/scenarios`**: Returns the active scenario and available scenario triggers.
- **`POST /api/scenarios/activate`**: Activates a demo scenario.
- **`GET /api/areas`**: Lists all monitored regions with general risk levels.
- **`GET /api/areas/{area_id}`**: Retrieves complete analytical details, Z-scores, and XAI contributions for a specific region.
- **`GET /api/areas/{area_id}/privacy`**: Returns the local Laplace noise audit log for the selected region.
- **`POST /api/local-data/aggregate`**: Simulates the local clinic processing boundary. Accepts raw patient logs, performs suppression/noising, and returns the protected payload.
- **`POST /api/privacy/protect`**: Sandboxed math engine returning original vs. Laplace-noised counts.
