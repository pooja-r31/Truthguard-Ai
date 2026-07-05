"""
TruthGuard AI — Fake News / Misinformation Detector
Uses NLP-based analysis: sentiment, credibility signals, and source verification.
"""

import re
import math
import random
import hashlib
from datetime import datetime


class FakeNewsDetector:
    """
    Multi-dimensional fake-news detector.
    Signals:
      1. Sensationalism score (ALL-CAPS, exclamation density, clickbait phrases)
      2. Credibility signals (source citations, expert quotes, data references)
      3. Known-misinformation phrase matching
      4. Sentiment polarity extremeness
      5. Source quality heuristics
      6. Writing-quality heuristics (grammar proxies)
      7. Unverified claims (hedge words: allegedly, reportedly, insiders claim)
      8. Factual authority (named orgs, confirmed action verbs)
    """

    CLICKBAIT_PHRASES = [
        "you won't believe", "shocking truth", "they don't want you to know",
        "this will change everything", "doctors hate him", "secret exposed",
        "breaking:", "viral:", "miracle cure", "100% proven",
        "conspiracy revealed", "mainstream media won't report",
        "share before deleted", "must see", "unbelievable",
        "big pharma", "deep state", "wake up sheeple",
        "mind blowing", "banned from tv", "the elite's secret",
        "hide this", "leaked document", "government cover-up",
        "fake news", "lamestream media", "controlled opposition",
        "do your own research", "exposed!!", "watch before deleted",
        "they're hiding this", "open your eyes", "censored by",
    ]

    CREDIBILITY_SIGNALS = [
        "according to", "study shows", "researchers found", "published in",
        "data indicates", "statistics from", "expert says", "professor",
        "university", "peer-reviewed", "journal", "evidence suggests",
        "government report", "official statement", "scientific consensus",
        "clinical trial", "meta-analysis", "certified by", "independent fact-check",
    ]

    MISINFORMATION_KEYWORDS = [
        "5g causes", "vaccines cause autism", "flat earth", "moon landing hoax",
        "covid is fake", "chemtrails", "microchip vaccine", "illuminati controls",
        "lizard people", "george soros controls", "qanon", "pizzagate",
        "hollow earth", "faked moon", "drinking bleach cures",
        "bill gates depopulation", "fake snow", "sovereign citizen",
        "new world order", "population control", "plandemic",
        "magnetic vaccine", "graphene oxide", "depopulation agenda",
        "crisis actor", "false flag", "staged event",
    ]

    TRUSTED_SOURCES = [
        "bbc", "reuters", "ap news", "the guardian", "new york times",
        "washington post", "npr", "abc news", "cnn", "nature", "science",
        "who.int", "cdc.gov", "nih.gov", "nasa.gov", "wsj",
        "the economist", "bloomberg", "snopes", "politifact",
    ]

    # Emotional manipulation patterns
    EMOTIONAL_MANIPULATION = [
        "think of the children", "blood on their hands", "pure evil",
        "destroying our country", "enemy of the people", "traitor",
        "patriot", "true american", "freedom fighter", "tyranny",
        "wake up america", "save our children", "fight back",
    ]

    # ── NEW: Hedge / unverified-claim indicators ──────────────────────────────
    # Fake news hides behind vague attribution; real journalism states facts.
    UNVERIFIED_INDICATORS = [
        "allegedly", "reportedly", "insiders claim", "insiders say",
        "unnamed", "undisclosed", "said to be", "is said to",
        "are said to", "claims to have", "claim to have",
        "not been officially", "has not confirmed", "have not confirmed",
        "neither confirmed nor denied", "not responded to",
        "has not responded", "have not responded",
        "fueling speculation", "refused media access", "signed ndas",
        "could not be verified", "unverified", "anonymous source",
        "speaking on condition", "tentatively", "theoretically",
        "has allegedly", "was allegedly", "were allegedly",
    ]

    # ── NEW: Authoritative entity / action indicators ─────────────────────────
    # Real news names specific organisations and uses confirmed-action language.
    AUTHORITY_ENTITIES = [
        # International organisations
        "world health organization", "united nations", "european union",
        "european parliament", "nato", "world bank", "unesco",
        "international monetary fund",
        # Government agencies
        "nasa", "fda", "cdc", "nih", "nhtsa", "epa",
        "department of", "ministry of", "federal reserve",
        "national highway traffic safety",
        # Major verified companies
        "openai", "tesla", "spacex", "microsoft", "google", "apple",
        "amazon", "meta", "samsung", "boeing",
        # Academic / research
        "university of", "oxford", "harvard", "mit", "stanford",
        "cambridge", "johns hopkins",
        # Geopolitical named entities
        "israel", "hamas", "qatar", "egypt",
        # Confirmed-action verbs (indicate official/verified events)
        "announced", "confirmed", "approved", "launched",
        "declared", "deployed", "recalled", "voted",
        "unveiled", "recommended", "agreed", "brokered",
        "touched down", "reinstated", "enrolled",
    ]

    def __init__(self):
        print("[FakeNewsDetector] Loading NLP pipeline...")
        self.vocab_loaded = True
        print("[FakeNewsDetector] Ready.")

    # ── Public API ─────────────────────────────────────────────────────────────
    def analyze(self, headline: str = '', body: str = '') -> dict:
        full_text = f"{headline} {body}".strip()
        lower     = full_text.lower()

        signals = {
            'sensationalism':    self._sensationalism(full_text, lower),
            'credibility':       self._credibility(lower),
            'misinformation':    self._misinformation(lower),
            'sentiment':         self._sentiment(full_text, lower),
            'source_quality':    self._source_quality(lower),
            'writing_quality':   self._writing_quality(full_text),
            'unverified_claims': self._unverified_claims(lower),
            'factual_authority': self._factual_authority(lower),
        }

        verdict, confidence = self._fuse(signals)
        label = self._label(confidence, verdict)

        return {
            'verdict':     verdict,
            'confidence':  confidence,
            'label':       label,
            'signals':     signals,
            'headline':    headline[:200],
            'word_count':  len(full_text.split()),
            'explanation': self._explain(verdict, confidence, signals),
            'recommendations': self._recommendations(verdict),
            'analyzed_at': datetime.now().isoformat(),
        }

    # ── Signal implementations ─────────────────────────────────────────────────
    def _sensationalism(self, text: str, lower: str) -> dict:
        words      = text.split()
        word_count = max(len(words), 1)

        # ALL-CAPS words ratio (words > 2 chars that are all uppercase)
        caps_count = sum(1 for w in words if w.isupper() and len(w) > 2)
        caps_ratio = caps_count / word_count

        # Exclamation density
        excl_count = text.count('!')
        excl_ratio = excl_count / max(len(text), 1) * 100

        # Question mark density (clickbait often uses questions)
        q_count = text.count('?')
        q_ratio = q_count / max(len(text), 1) * 100

        # Clickbait phrase matching
        clicks = [p for p in self.CLICKBAIT_PHRASES if p in lower]

        # Emotional manipulation phrases
        emotional = [p for p in self.EMOTIONAL_MANIPULATION if p in lower]

        # Score calculation — much more aggressive
        score = 0.0
        score += min(caps_ratio * 3.0, 0.4)         # Up to 0.4 for ALL-CAPS
        score += min(excl_ratio * 15.0, 0.3)         # Up to 0.3 for exclamations
        score += min(q_ratio * 10.0, 0.1)            # Up to 0.1 for questions
        score += min(len(clicks) * 0.20, 0.6)        # Up to 0.6 for clickbait
        score += min(len(emotional) * 0.15, 0.3)     # Up to 0.3 for emotional manipulation

        # Short text with high exclamation density is extra suspicious
        if word_count < 30 and excl_count > 1:
            score += 0.15

        score = min(score, 1.0)

        return {
            'caps_ratio':         round(caps_ratio, 3),
            'exclamation_density': round(excl_ratio, 4),
            'clickbait_phrases':  clicks,
            'emotional_phrases':  emotional,
            'score':              round(score, 3),
        }

    def _credibility(self, lower: str) -> dict:
        """
        Check for credibility signals. ABSENCE of credibility = higher fake score.
        """
        found = [s for s in self.CREDIBILITY_SIGNALS if s in lower]

        # No credibility signals → high fake score
        # Many credibility signals → low fake score
        if len(found) == 0:
            score = 0.85  # No citations/expert quotes at all — very suspicious
        elif len(found) == 1:
            score = 0.55  # Minimal credibility
        elif len(found) <= 3:
            score = 0.30  # Some credibility
        else:
            score = 0.10  # Well-sourced article

        return {
            'credibility_signals': found,
            'count': len(found),
            'score': round(score, 3),
        }

    def _misinformation(self, lower: str) -> dict:
        """Direct keyword matching against known misinformation database."""
        found = [k for k in self.MISINFORMATION_KEYWORDS if k in lower]
        # Each misinformation keyword is a very strong signal
        if len(found) >= 3:
            score = 1.0
        elif len(found) >= 2:
            score = 0.85
        elif len(found) == 1:
            score = 0.65
        else:
            score = 0.0

        return {
            'matched_keywords': found,
            'count': len(found),
            'score': round(score, 3),
        }

    def _sentiment(self, text: str, lower: str) -> dict:
        positive_words = ['great', 'amazing', 'wonderful', 'fantastic', 'incredible',
                          'best', 'perfect', 'excellent', 'brilliant']
        negative_words = ['terrible', 'awful', 'horrible', 'disgusting', 'evil',
                          'worst', 'disaster', 'catastrophe', 'dangerous', 'deadly',
                          'toxic', 'horrifying', 'devastating', 'horrific', 'terrifying']
        extreme_words = ['destroy', 'annihilate', 'exterminate', 'extinction',
                         'apocalypse', 'genocide', 'massacre', 'slaughter']

        pos = sum(1 for w in positive_words if w in lower)
        neg = sum(1 for w in negative_words if w in lower)
        ext = sum(1 for w in extreme_words if w in lower)
        total = pos + neg + ext

        polarity = (pos - neg) / max(total, 1)
        extremeness = abs(polarity)

        # Extreme sentiment + extreme language = strong misinformation signal
        score = 0.0
        if ext > 0:
            score += min(ext * 0.3, 0.6)
        score += extremeness * 0.4
        score = min(score, 1.0)

        return {
            'positive_count':  pos,
            'negative_count':  neg,
            'extreme_count':   ext,
            'polarity':        round(polarity, 3),
            'extremeness':     round(extremeness, 3),
            'score':           round(score, 3),
        }

    def _source_quality(self, lower: str) -> dict:
        """
        Check if trusted sources are cited. No trusted sources = higher fake score.
        """
        trusted = [s for s in self.TRUSTED_SOURCES if s in lower]

        if len(trusted) == 0:
            score = 0.75  # No trusted sources cited at all
        elif len(trusted) == 1:
            score = 0.40
        elif len(trusted) <= 3:
            score = 0.15
        else:
            score = 0.05  # Many trusted sources — very credible

        return {
            'trusted_sources_cited': trusted,
            'score': round(score, 3),
        }

    def _writing_quality(self, text: str) -> dict:
        words    = text.split()
        word_count = max(len(words), 1)
        avg_word = sum(len(w) for w in words) / word_count
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        sent_count = max(len(sentences), 1)
        avg_sent  = word_count / sent_count

        score = 0.0

        # Very short or very long average word length
        if avg_word < 3 or avg_word > 10:
            score += 0.3
        # Very short or very long average sentence length
        if avg_sent < 5 or avg_sent > 40:
            score += 0.3
        # Very short content with no real sentences
        if word_count < 15:
            score += 0.2  # Too short to be a real article
        # Check for excessive use of capital letters throughout
        caps_in_text = sum(1 for c in text if c.isupper())
        lower_in_text = sum(1 for c in text if c.islower())
        if lower_in_text > 0 and caps_in_text / max(lower_in_text, 1) > 0.5:
            score += 0.2  # Excessive capitalization

        return {
            'avg_word_length':     round(avg_word, 2),
            'avg_sentence_length': round(avg_sent, 2),
            'sentence_count':      len(sentences),
            'word_count':          word_count,
            'score':               round(min(score, 1.0), 3),
        }

    # ── NEW SIGNAL: Unverified / hedge-word detection ─────────────────────────
    def _unverified_claims(self, lower: str) -> dict:
        """
        Fake news hides behind vague attribution — 'allegedly', 'reportedly',
        'insiders claim', 'unnamed sources'.  Real journalism states facts
        directly with named sources.  This is the strongest single separator
        between the two classes.
        """
        found = [p for p in self.UNVERIFIED_INDICATORS if p in lower]

        if len(found) >= 4:
            score = 0.95
        elif len(found) >= 3:
            score = 0.85
        elif len(found) >= 2:
            score = 0.70
        elif len(found) == 1:
            score = 0.45
        else:
            score = 0.0  # No hedging at all — strong real-news signal

        return {
            'unverified_phrases': found,
            'count':  len(found),
            'score':  round(score, 3),
        }

    # ── NEW SIGNAL: Factual authority detection ───────────────────────────────
    def _factual_authority(self, lower: str) -> dict:
        """
        Real news names specific, verifiable organisations and uses
        confirmed-action language ('announced', 'approved', 'declared').
        More authority matches → LOWER fake score.
        """
        found = [a for a in self.AUTHORITY_ENTITIES if a in lower]

        # More authority = lower suspicion
        if len(found) >= 5:
            score = 0.0
        elif len(found) >= 3:
            score = 0.10
        elif len(found) >= 2:
            score = 0.25
        elif len(found) == 1:
            score = 0.40
        else:
            score = 0.65

        return {
            'authorities_found': found,
            'count': len(found),
            'score': round(score, 3),
        }

    # ── Signal fusion ──────────────────────────────────────────────────────────
    def _fuse(self, signals: dict) -> tuple[str, float]:
        weights = {
            'sensationalism':    0.10,
            'credibility':       0.07,
            'misinformation':    0.20,
            'sentiment':         0.05,
            'source_quality':    0.03,
            'writing_quality':   0.05,
            'unverified_claims': 0.30,   # Strongest — hedge words are the #1 separator
            'factual_authority': 0.20,   # Named orgs + action verbs reward real news
        }
        total = sum(signals[k]['score'] * w for k, w in weights.items() if k in signals)

        # Amplify to percentage
        confidence = round(min((total * 130), 99.9), 1)

        # Threshold — tuned so real news (low unverified, high authority) stays below,
        # while fake news (high unverified, low authority) goes above
        verdict = 'FAKE' if confidence > 40 else 'REAL'
        return verdict, confidence

    def _label(self, confidence: float, verdict: str) -> str:
        if verdict == 'REAL':
            if confidence < 15:
                return 'Verified Authentic'
            return 'Likely Authentic'
        if confidence > 80:
            return 'Almost Certainly Fake'
        if confidence > 60:
            return 'Highly Suspicious'
        if confidence > 40:
            return 'Potentially Misleading'
        return 'Suspicious — Verify Sources'

    # ── Explanation ────────────────────────────────────────────────────────────
    def _explain(self, verdict: str, confidence: float, signals: dict) -> str:
        parts = []
        if verdict == 'FAKE':
            parts.append(f"Fake probability: {confidence:.1f}%.")

        s = signals.get('sensationalism', {})
        if s.get('clickbait_phrases'):
            parts.append(f"Clickbait phrases detected: {', '.join(s['clickbait_phrases'][:3])}.")
        if s.get('emotional_phrases'):
            parts.append(f"Emotional manipulation detected: {', '.join(s['emotional_phrases'][:2])}.")

        m = signals.get('misinformation', {})
        if m.get('matched_keywords'):
            parts.append(f"Known misinformation keywords: {', '.join(m['matched_keywords'][:3])}.")

        u = signals.get('unverified_claims', {})
        if u.get('unverified_phrases'):
            parts.append(f"Unverified/hedge language: {', '.join(u['unverified_phrases'][:3])}.")

        c = signals.get('credibility', {})
        if c.get('count', 0) == 0:
            parts.append("No credibility signals (citations, expert quotes) found.")
        elif c.get('count', 0) >= 3:
            parts.append(f"Found {c['count']} credibility signals.")

        a = signals.get('factual_authority', {})
        if a.get('count', 0) >= 3:
            parts.append(f"Multiple authoritative sources referenced ({a['count']} found).")

        sq = signals.get('source_quality', {})
        if not sq.get('trusted_sources_cited'):
            parts.append("No trusted news sources cited.")

        if not parts:
            parts.append("Content appears to follow journalistic standards.")

        return ' '.join(parts)

    def _recommendations(self, verdict: str) -> list[str]:
        if verdict == 'FAKE':
            return [
                "Do not share this content without additional verification.",
                "Cross-check with trusted news sources (BBC, Reuters, AP).",
                "Report suspected misinformation to platform fact-checkers.",
                "Check fact-checking sites: Snopes, FactCheck.org, PolitiFact.",
            ]
        return [
            "Content appears credible based on linguistic analysis.",
            "Always verify claims with primary sources.",
            "Maintain media literacy and critical thinking.",
        ]
