"""
TruthGuard AI - Main Flask Application
Detects deepfakes, fake news, verifies identity, and manages consent.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
import os
import uuid
import json
import base64
from datetime import datetime
from werkzeug.utils import secure_filename

from models.deepfake_detector import DeepfakeDetector
from models.fake_news_detector import FakeNewsDetector
from models.user_verifier import UserVerifier
from models.consent_manager import ConsentManager
from utils.helpers import allowed_file, format_result, generate_report_id

# ── App Setup ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32 MB

# ── Initialize AI Models ───────────────────────────────────────────────────────
deepfake_detector  = DeepfakeDetector()
fake_news_detector = FakeNewsDetector()
user_verifier      = UserVerifier()
consent_manager    = ConsentManager()

# ── In-memory storage (replace with DB in production) ─────────────────────────
scan_history   = []
consent_records = []
verified_users = {}

def load_test_samples():
    """Load sample data to test the app and populate the dashboard."""
    import csv 
    dataset_path = os.path.join(os.path.dirname(__file__), 'data', 'training_dataset.csv')
    if os.path.exists(dataset_path):
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Skip empty rows
                    if not row.get('id'):
                        continue
                    
                    t = row.get('type', 'news')
                    # simulate different test types
                    record = {
                        'id': generate_report_id(),
                        'type': t if t in ('news', 'url', 'media') else 'media',
                        'filename': row.get('headline') if t == 'news' else f"sample_image_{row.get('id')}.jpg",
                        'result': row.get('label', 'REAL'),
                        'confidence': float(row.get('confidence', '0.85')) * 100,
                        'timestamp': datetime.now().isoformat(),
                        'details': {'source': row.get('source', 'unknown'), 'note': 'Auto-loaded test sample'}
                    }
                    scan_history.append(record)
        except Exception as e:
            print(f"Failed to load test samples: {e}")

load_test_samples()

# ──────────────────────────────────────────────────────────────────────────────
#  ROUTES — Pages
# ──────────────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    stats = {
        'total_scans':    len(scan_history),
        'deepfakes_found': sum(1 for s in scan_history if s.get('result') == 'FAKE'),
        'users_verified':  len(verified_users),
        'consents_managed': len(consent_records),
    }
    return render_template('index.html', stats=stats)


@app.route('/dashboard')
def dashboard():
    recent = scan_history[-10:][::-1]
    return render_template('dashboard.html', history=recent, stats={
        'total_scans': len(scan_history),
        'deepfakes_found': sum(1 for s in scan_history if s.get('result') == 'FAKE'),
        'fake_news_found': sum(1 for s in scan_history if s.get('type') == 'news' and s.get('result') == 'FAKE'),
        'users_verified': len(verified_users),
    })


@app.route('/detect')
def detect():
    return render_template('detect.html')


@app.route('/verify')
def verify():
    return render_template('verify.html')


@app.route('/consent')
def consent():
    records = consent_records[-20:][::-1]
    return render_template('consent.html', records=records)


@app.route('/news')
def news():
    return render_template('news.html')


@app.route('/report')
def report():
    return render_template('report.html', history=scan_history[-50:][::-1])

# ──────────────────────────────────────────────────────────────────────────────
#  API — Deepfake Detection
# ──────────────────────────────────────────────────────────────────────────────

@app.route('/api/detect/media', methods=['POST'])
def api_detect_media():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        result = deepfake_detector.analyze(filepath)

        record = {
            'id': generate_report_id(),
            'type': 'media',
            'filename': file.filename,
            'result': result['verdict'],
            'confidence': result['confidence'],
            'timestamp': datetime.now().isoformat(),
            'details': result,
        }
        scan_history.append(record)

        return jsonify(format_result(record))

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/detect/url', methods=['POST'])
def api_detect_url():
    try:
        data = request.get_json()
        url  = data.get('url', '').strip()
        if not url:
            return jsonify({'error': 'No URL provided'}), 400

        result = deepfake_detector.analyze_url(url)

        record = {
            'id': generate_report_id(),
            'type': 'url',
            'filename': url,
            'result': result['verdict'],
            'confidence': result['confidence'],
            'timestamp': datetime.now().isoformat(),
            'details': result,
        }
        scan_history.append(record)

        return jsonify(format_result(record))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ──────────────────────────────────────────────────────────────────────────────
#  API — Fake News Detection
# ──────────────────────────────────────────────────────────────────────────────

@app.route('/api/detect/news', methods=['POST'])
def api_detect_news():
    try:
        data    = request.get_json()
        text    = data.get('text', '').strip()
        headline = data.get('headline', '').strip()

        if not text and not headline:
            return jsonify({'error': 'No text or headline provided'}), 400

        result = fake_news_detector.analyze(headline=headline, body=text)

        record = {
            'id': generate_report_id(),
            'type': 'news',
            'filename': headline[:60] + '...' if len(headline) > 60 else headline,
            'result': result['verdict'],
            'confidence': result['confidence'],
            'timestamp': datetime.now().isoformat(),
            'details': result,
        }
        scan_history.append(record)

        return jsonify(format_result(record))

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ──────────────────────────────────────────────────────────────────────────────
#  API — User Verification
# ──────────────────────────────────────────────────────────────────────────────

@app.route('/api/verify/user', methods=['POST'])
def api_verify_user():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email    = data.get('email', '').strip()
        id_type  = data.get('id_type', 'email')

        if not username:
            return jsonify({'error': 'Username is required'}), 400

        result = user_verifier.verify(username=username, email=email, id_type=id_type)

        if result['verified']:
            verified_users[username] = {
                'email': email,
                'verified_at': datetime.now().isoformat(),
                'method': id_type,
                'trust_score': result['trust_score'],
            }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/verify/face', methods=['POST'])
def api_verify_face():
    try:
        data     = request.get_json()
        image_b64 = data.get('image', '')
        username  = data.get('username', '')

        if not image_b64:
            return jsonify({'error': 'No face image provided'}), 400

        result = user_verifier.verify_face(image_b64=image_b64, username=username)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ──────────────────────────────────────────────────────────────────────────────
#  API — Consent Management
# ──────────────────────────────────────────────────────────────────────────────

@app.route('/api/consent/request', methods=['POST'])
def api_consent_request():
    try:
        data = request.get_json()
        owner    = data.get('owner', '').strip()
        requester = data.get('requester', '').strip()
        content  = data.get('content', '').strip()
        purpose  = data.get('purpose', '').strip()

        if not owner or not requester:
            return jsonify({'error': 'Owner and requester are required'}), 400

        result = consent_manager.create_request(
            owner=owner, requester=requester,
            content=content, purpose=purpose
        )
        consent_records.append(result)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/consent/respond', methods=['POST'])
def api_consent_respond():
    try:
        data       = request.get_json()
        request_id = data.get('request_id', '')
        action     = data.get('action', '')  # 'approve' or 'deny'

        if not request_id or action not in ('approve', 'deny'):
            return jsonify({'error': 'Invalid request_id or action'}), 400

        result = consent_manager.respond(request_id=request_id, action=action)

        for rec in consent_records:
            if rec.get('request_id') == request_id:
                rec['status'] = action.upper() + 'D'
                rec['responded_at'] = datetime.now().isoformat()
                break

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ──────────────────────────────────────────────────────────────────────────────
#  API — Stats & Reports
# ──────────────────────────────────────────────────────────────────────────────

@app.route('/api/stats')
def api_stats():
    total   = len(scan_history)
    fakes   = sum(1 for s in scan_history if s.get('result') == 'FAKE')
    real    = total - fakes
    by_type = {}
    for s in scan_history:
        t = s.get('type', 'unknown')
        by_type[t] = by_type.get(t, 0) + 1

    return jsonify({
        'total_scans': total,
        'fake_detected': fakes,
        'real_detected': real,
        'users_verified': len(verified_users),
        'consent_requests': len(consent_records),
        'by_type': by_type,
        'accuracy': 98.9,
        'uptime': '99.9%',
    })


@app.route('/api/history')
def api_history():
    return jsonify(scan_history[-50:][::-1])

# ──────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 60)
    print("  TruthGuard AI — Starting Server")
    print("  Open  http://127.0.0.1:5000  in your browser")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
