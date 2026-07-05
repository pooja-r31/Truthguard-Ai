# TruthGuard AI 🛡

An AI-powered platform that detects deepfakes, identifies fake news, verifies
user identity, and manages content-sharing consent — building a safer internet.

## Features
| Module | Description |
|---|---|
| 🎭 **Deepfake Detection** | Multi-signal CNN forensic pipeline for images & videos |
| 📰 **Fake News Detection** | NLP analysis of headlines and article bodies |
| 🪪 **Identity Verification** | Multi-factor trust scoring + facial recognition |
| 🔐 **Consent Management** | Permission request system with full audit trail |
| 📊 **Dashboard & Reports** | Real-time analytics with chartlets and export |

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

## Training Dataset
`data/training_dataset.csv` — 110 labelled entries:
- **55 FAKE** entries (news articles + AI-generated images)
- **55 REAL** entries (verified news + authentic images)
- Features: sensationalism, credibility, misinformation keywords, sentiment, source quality, pixel stats, EXIF anomalies, frequency artefacts

## Technology Stack
- **Backend**: Python 3.12 + Flask 3.0
- **AI / NLP**: Custom forensic signal pipeline + NLP feature extraction
- **Frontend**: Vanilla HTML/CSS/JS — dark glassmorphism design
- **Storage**: In-memory (swap for SQLite/PostgreSQL in production)

## Notes
> In production, replace the simulated AI analysis with real trained
> PyTorch / TensorFlow deepfake detection models. The architecture is
> designed to make this drop-in replacement straightforward.

© 2025 TruthGuard AI
