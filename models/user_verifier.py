"""
TruthGuard AI — User Identity Verifier
Verifies user identity with multi-factor checks and trust scoring.
"""

import re
import uuid
import random
import hashlib
from datetime import datetime


class UserVerifier:
    """
    Multi-factor user identity verification.
    Methods:
      1. Email format & domain validation
      2. Username pattern analysis
      3. Behavioral fingerprint scoring
      4. Simulated face-match verification
      5. OTP / code simulation (stub for real SMS/email OTP)
    """

    DISPOSABLE_DOMAINS = [
        'mailinator.com', 'guerrillamail.com', 'throwam.com', 'yopmail.com',
        'temp-mail.org', 'fakeinbox.com', 'sharklasers.com', 'trashmail.com',
        '10minutemail.com', 'getairmail.com',
    ]

    BOT_PATTERNS = [
        r'^user\d{4,}$', r'^test\d+$', r'^bot\w+', r'^\w{1,3}\d{5,}$',
        r'^[a-z]{1,2}[0-9]{6,}$',
    ]

    def __init__(self):
        self._otp_store: dict[str, str] = {}
        print("[UserVerifier] Identity verification engine ready.")

    # ── Public API ─────────────────────────────────────────────────────────────
    def verify(self, username: str, email: str = '', id_type: str = 'email') -> dict:
        checks = {
            'username_valid':   self._check_username(username),
            'email_valid':      self._check_email(email) if email else {'valid': False, 'score': 0.3},
            'bot_likelihood':   self._check_bot_pattern(username),
            'account_age_sim':  self._simulate_account_age(username),
            'behavior_score':   self._simulate_behavior(username),
        }

        trust_score = self._calculate_trust(checks)
        verified    = trust_score >= 60

        return {
            'verified':    verified,
            'trust_score': trust_score,
            'level':       self._trust_level(trust_score),
            'checks':      checks,
            'username':    username,
            'email':       email,
            'method':      id_type,
            'verified_at': datetime.now().isoformat(),
            'session_token': str(uuid.uuid4()) if verified else None,
            'recommendations': self._verification_recs(trust_score),
        }

    def verify_face(self, image_b64: str, username: str = '') -> dict:
        """Simulated facial recognition verification."""
        rng = random.Random(image_b64[:50] + username)

        # Simulate liveness & face-match scores
        liveness_score = rng.uniform(70, 99)
        match_score    = rng.uniform(65, 99)
        spoof_detected = liveness_score < 75

        verified = liveness_score >= 75 and match_score >= 70 and not spoof_detected

        return {
            'verified':       verified,
            'liveness_score': round(liveness_score, 1),
            'match_score':    round(match_score, 1),
            'spoof_detected': spoof_detected,
            'face_quality':   'high' if liveness_score > 85 else 'medium',
            'username':       username,
            'verified_at':    datetime.now().isoformat(),
            'message': (
                "Face verification successful — identity confirmed."
                if verified else
                "Face verification failed — possible spoof attempt detected."
            ),
        }

    def generate_otp(self, contact: str) -> str:
        """Generate a 6-digit OTP (stub — integrate SMS/email service in production)."""
        otp = str(random.randint(100000, 999999))
        self._otp_store[contact] = otp
        return otp   # In production: send via SMS/email, never return directly

    def verify_otp(self, contact: str, otp: str) -> bool:
        stored = self._otp_store.get(contact)
        if stored and stored == otp:
            del self._otp_store[contact]
            return True
        return False

    # ── Checks ─────────────────────────────────────────────────────────────────
    def _check_username(self, username: str) -> dict:
        valid = bool(re.match(r'^[a-zA-Z][a-zA-Z0-9_.-]{2,29}$', username))
        score = 80 if valid else 20
        return {'valid': valid, 'length': len(username), 'score': score}

    def _check_email(self, email: str) -> dict:
        pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
        valid   = bool(re.match(pattern, email))
        domain  = email.split('@')[-1].lower() if '@' in email else ''
        disposable = domain in self.DISPOSABLE_DOMAINS
        score = 80 if (valid and not disposable) else (30 if not valid else 20)
        return {
            'valid':      valid,
            'disposable': disposable,
            'domain':     domain,
            'score':      score,
        }

    def _check_bot_pattern(self, username: str) -> dict:
        is_bot = any(re.match(p, username.lower()) for p in self.BOT_PATTERNS)
        score  = 80 if is_bot else 10
        return {'is_bot': is_bot, 'score': score}

    def _simulate_account_age(self, username: str) -> dict:
        rng  = random.Random(username + 'age')
        days = rng.randint(0, 2000)
        score = max(0, 60 - (30 if days < 30 else 0))
        return {'account_age_days': days, 'new_account': days < 30, 'score': score}

    def _simulate_behavior(self, username: str) -> dict:
        rng = random.Random(username + 'beh')
        posting_rate = rng.uniform(0, 100)
        report_count = rng.randint(0, 15)
        score = max(0, 80 - report_count * 5 - (20 if posting_rate > 80 else 0))
        return {
            'posting_rate': round(posting_rate, 1),
            'report_count': report_count,
            'score': max(score, 0),
        }

    # ── Trust calculation ──────────────────────────────────────────────────────
    def _calculate_trust(self, checks: dict) -> float:
        weights = {
            'username_valid':  0.15,
            'email_valid':     0.25,
            'bot_likelihood':  0.20,   # higher bot score → lower trust
            'account_age_sim': 0.20,
            'behavior_score':  0.20,
        }
        trust = 0.0
        for key, w in weights.items():
            check = checks.get(key, {})
            raw_score = check.get('score', 50)
            if key == 'bot_likelihood':
                raw_score = 100 - raw_score   # invert: high bot score → low trust
            trust += raw_score * w
        return round(trust, 1)

    def _trust_level(self, score: float) -> str:
        if score >= 85:
            return 'HIGH'
        if score >= 60:
            return 'MEDIUM'
        if score >= 40:
            return 'LOW'
        return 'UNTRUSTED'

    def _verification_recs(self, score: float) -> list[str]:
        if score >= 85:
            return ["Identity fully verified.", "Access all platform features."]
        if score >= 60:
            return [
                "Basic verification passed.",
                "Enable 2FA for enhanced trust level.",
                "Complete profile to unlock advanced features.",
            ]
        return [
            "Identity verification failed or incomplete.",
            "Provide a valid email address.",
            "Complete face verification for account approval.",
            "Contact support if you believe this is an error.",
        ]
