"""
TruthGuard AI — Alpha Testing App
Same detection interface but with manual correction/labeling capability.
Testers can override the AI verdict to train the system through trial & error.

Usage:
    python app_alpha.py
    Open http://127.0.0.1:5001 in your browser
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

# Feedback data storage
FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), 'data', 'feedback_labels.json')

# ── Initialize AI Models ───────────────────────────────────────────────────────
deepfake_detector  = DeepfakeDetector()
fake_news_detector = FakeNewsDetector()
user_verifier      = UserVerifier()
consent_manager    = ConsentManager()

# ── In-memory storage ─────────────────────────────────────────────────────────
scan_history   = []
consent_records = []
verified_users = {}
feedback_data  = []  # Stores manual corrections

def load_feedback():
    """Load previously saved feedback/corrections from disk."""
    global feedback_data
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
                feedback_data = json.load(f)
            print(f"[Alpha] Loaded {len(feedback_data)} feedback entries")
        except Exception as e:
            print(f"[Alpha] Could not load feedback: {e}")
            feedback_data = []

def save_feedback():
    """Persist feedback/corrections to disk."""
    try:
        os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
        with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
            json.dump(feedback_data, f, indent=2, default=str)
    except Exception as e:
        print(f"[Alpha] Could not save feedback: {e}")

def get_feedback_stats():
    """Calculate accuracy stats from feedback data."""
    total = len(feedback_data)
    if total == 0:
        return {'total': 0, 'correct': 0, 'incorrect': 0, 'accuracy': 0.0}
    correct = sum(1 for f in feedback_data if f.get('ai_verdict') == f.get('human_label'))
    incorrect = total - correct
    return {
        'total': total,
        'correct': correct,
        'incorrect': incorrect,
        'accuracy': round((correct / total) * 100, 1),
        'by_type': _feedback_by_type(),
    }

def _feedback_by_type():
    """Break down feedback stats by content type."""
    types = {}
    for f in feedback_data:
        t = f.get('content_type', 'unknown')
        if t not in types:
            types[t] = {'total': 0, 'correct': 0, 'incorrect': 0}
        types[t]['total'] += 1
        if f.get('ai_verdict') == f.get('human_label'):
            types[t]['correct'] += 1
        else:
            types[t]['incorrect'] += 1
    for t in types:
        types[t]['accuracy'] = round(
            (types[t]['correct'] / max(types[t]['total'], 1)) * 100, 1
        )
    return types

load_feedback()

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
        'feedback': get_feedback_stats(),
    }
    return render_template('alpha_index.html', stats=stats)

@app.route('/detect')
def detect():
    return render_template('alpha_detect.html')

@app.route('/news')
def news():
    return render_template('alpha_news.html')

@app.route('/feedback')
def feedback_page():
    stats = get_feedback_stats()
    recent = feedback_data[-50:][::-1]
    return render_template('alpha_feedback.html', stats=stats, feedback=recent)


# ──────────────────────────────────────────────────────────────────────────────
#  API — Deepfake Detection (same as main app)
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
#  API — Manual Labeling / Feedback (ALPHA ONLY)
# ──────────────────────────────────────────────────────────────────────────────

@app.route('/api/feedback/label', methods=['POST'])
def api_feedback_label():
    """
    Tester manually labels a scan result as correct or incorrect.
    This feedback is stored and used to track model accuracy + improve thresholds.
    """
    try:
        data = request.get_json()
        scan_id = data.get('scan_id', '').strip()
        human_label = data.get('human_label', '').strip().upper()  # 'FAKE' or 'REAL'
        notes = data.get('notes', '').strip()
        tester_name = data.get('tester_name', 'anonymous').strip()

        if not scan_id:
            return jsonify({'error': 'scan_id is required'}), 400
        if human_label not in ('FAKE', 'REAL'):
            return jsonify({'error': 'human_label must be FAKE or REAL'}), 400

        # Find the scan record
        record = None
        for s in scan_history:
            if s.get('id') == scan_id:
                record = s
                break

        if not record:
            return jsonify({'error': f'Scan {scan_id} not found'}), 404

        ai_verdict = record.get('result', 'UNKNOWN')
        is_correct = (ai_verdict == human_label)

        feedback_entry = {
            'feedback_id': 'FB-' + str(uuid.uuid4())[:8].upper(),
            'scan_id': scan_id,
            'content_type': record.get('type', 'unknown'),
            'filename': record.get('filename', ''),
            'ai_verdict': ai_verdict,
            'ai_confidence': record.get('confidence', 0),
            'human_label': human_label,
            'is_correct': is_correct,
            'notes': notes,
            'tester_name': tester_name,
            'timestamp': datetime.now().isoformat(),
            'signals': record.get('details', {}).get('signals', {}),
        }

        feedback_data.append(feedback_entry)
        save_feedback()

        return jsonify({
            'success': True,
            'feedback_id': feedback_entry['feedback_id'],
            'ai_verdict': ai_verdict,
            'human_label': human_label,
            'is_correct': is_correct,
            'message': f"AI was {'CORRECT ✅' if is_correct else 'WRONG ❌'}. Feedback saved.",
            'total_feedback': len(feedback_data),
            'current_accuracy': get_feedback_stats()['accuracy'],
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback/stats')
def api_feedback_stats():
    """Get aggregate feedback statistics."""
    return jsonify(get_feedback_stats())


@app.route('/api/feedback/history')
def api_feedback_history():
    """Get recent feedback entries."""
    limit = request.args.get('limit', 50, type=int)
    return jsonify(feedback_data[-limit:][::-1])


@app.route('/api/feedback/export')
def api_feedback_export():
    """Export all feedback data for model retraining."""
    return jsonify({
        'export_date': datetime.now().isoformat(),
        'total_entries': len(feedback_data),
        'stats': get_feedback_stats(),
        'entries': feedback_data,
    })


@app.route('/api/feedback/clear', methods=['POST'])
def api_feedback_clear():
    """Clear all feedback data (admin only in production)."""
    global feedback_data
    feedback_data = []
    save_feedback()
    return jsonify({'success': True, 'message': 'All feedback cleared.'})


@app.route('/api/stats')
def api_stats():
    total   = len(scan_history)
    fakes   = sum(1 for s in scan_history if s.get('result') == 'FAKE')
    real    = total - fakes
    fb = get_feedback_stats()

    return jsonify({
        'total_scans': total,
        'fake_detected': fakes,
        'real_detected': real,
        'feedback': fb,
        'model_accuracy': fb.get('accuracy', 'N/A'),
    })


@app.route('/api/history')
def api_history():
    return jsonify(scan_history[-50:][::-1])


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 60)
    print("  TruthGuard AI — ALPHA Testing Server")
    print("  Open  http://127.0.0.1:5001  in your browser")
    print("  This is the ALPHA build with manual labeling support")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5001)
