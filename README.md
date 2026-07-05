# TruthGuard AI 🛡

An AI-powered platform that detects deepfakes, identifies fake news, verifies
user identity, and manages content-sharing consent — building a safer internet.

---

## Features
| Module | Description |
|---|---|
| 🎭 **Deepfake Detection** | Multi-signal CNN forensic pipeline for images & videos |
| 📰 **Fake News Detection** | NLP analysis of headlines and article bodies |
| 🪪 **Identity Verification** | Multi-factor trust scoring + facial recognition |
| 🔐 **Consent Management** | Permission request system with full audit trail |
| 📊 **Dashboard & Reports** | Real-time analytics with chartlets and export |

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open in Browser
```
http://127.0.0.1:5000
```

---

## Project Structure
```
mohana/
├── app.py                    ← Flask application entry point
├── requirements.txt
├── data/
│   └── training_dataset.csv  ← 110-entry labelled training dataset
├── models/
│   ├── deepfake_detector.py  ← Multi-signal forensic deepfake engine
│   ├── fake_news_detector.py ← NLP-based misinformation detector
│   ├── user_verifier.py      ← Identity verification engine
│   └── consent_manager.py   ← Consent permission system
├── utils/
│   └── helpers.py
├── static/
│   ├── css/style.css         ← Dark glassmorphism UI
│   ├── js/main.js            ← Animations & utilities
│   └── js/charts.js          ← Canvas chart library
└── templates/
    ├── index.html            ← Landing page
    ├── dashboard.html        ← Analytics dashboard
    ├── detect.html           ← Deepfake detection tool
    ├── news.html             ← Fake news detector
    ├── verify.html           ← Identity verification
    ├── consent.html          ← Consent management
    └── report.html           ← Scan reports
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/detect/media` | Upload file for deepfake analysis |
| POST | `/api/detect/url` | Analyze URL for fake media |
| POST | `/api/detect/news` | Analyze news text for misinformation |
| POST | `/api/verify/user` | Verify user identity |
| POST | `/api/verify/face` | Facial recognition verification |
| POST | `/api/consent/request` | Create consent request |
| POST | `/api/consent/respond` | Approve or deny consent |
| GET  | `/api/stats` | Platform statistics |
| GET  | `/api/history` | Recent scan history |

---

## Training Dataset
`data/training_dataset.csv` — 110 labelled entries:
- **55 FAKE** entries (news articles + AI-generated images)
- **55 REAL** entries (verified news + authentic images)
- Features: sensationalism, credibility, misinformation keywords, sentiment, source quality, pixel stats, EXIF anomalies, frequency artefacts

---

## Technology Stack
- **Backend**: Python 3.12 + Flask 3.0
- **AI / NLP**: Custom forensic signal pipeline + NLP feature extraction
- **Frontend**: Vanilla HTML/CSS/JS — dark glassmorphism design
- **Storage**: In-memory (swap for SQLite/PostgreSQL in production)

---

## Notes
> In production, replace the simulated AI analysis with real trained
> PyTorch / TensorFlow deepfake detection models. The architecture is
> designed to make this drop-in replacement straightforward.

© 2024 TruthGuard AI
