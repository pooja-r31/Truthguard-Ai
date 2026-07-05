"""
TruthGuard AI — Consent Management System
Handles content-sharing permission requests between users.
"""

import uuid
from datetime import datetime


class ConsentManager:
    """
    Manages content-sharing consent between platform users.
    Features:
      - Create consent requests
      - Track consent status (PENDING / APPROVED / DENIED / REVOKED)
      - Audit trail for all consent actions
      - Consent expiry management
    """

    def __init__(self):
        self._requests: dict[str, dict] = {}
        self._audit_log: list[dict]     = []
        print("[ConsentManager] Consent management engine ready.")

    # ── Public API ─────────────────────────────────────────────────────────────
    def create_request(self, owner: str, requester: str,
                       content: str, purpose: str) -> dict:
        """Create a new consent request."""
        request_id = str(uuid.uuid4())[:8].upper()
        record = {
            'request_id':  request_id,
            'owner':       owner,
            'requester':   requester,
            'content':     content[:300],
            'purpose':     purpose[:200],
            'status':      'PENDING',
            'created_at':  datetime.now().isoformat(),
            'responded_at': None,
            'expires_at':  None,
        }
        self._requests[request_id] = record
        self._log('CREATE', request_id, requester, f"Consent requested from {owner}")
        return record

    def respond(self, request_id: str, action: str) -> dict:
        """Owner responds to a consent request with 'approve' or 'deny'."""
        record = self._requests.get(request_id)
        if not record:
            return {'success': False, 'error': 'Consent request not found.'}

        if record['status'] != 'PENDING':
            return {'success': False, 'error': f"Request already {record['status']}."}

        new_status = 'APPROVED' if action == 'approve' else 'DENIED'
        record['status']       = new_status
        record['responded_at'] = datetime.now().isoformat()
        self._log(action.upper(), request_id, record['owner'],
                  f"Consent {new_status} for {record['requester']}")

        return {
            'success':     True,
            'request_id':  request_id,
            'status':      new_status,
            'responded_at': record['responded_at'],
            'message': (
                f"Consent APPROVED. {record['requester']} may now use the content."
                if new_status == 'APPROVED' else
                f"Consent DENIED. {record['requester']} is not permitted to use the content."
            ),
        }

    def revoke(self, request_id: str, owner: str) -> dict:
        """Owner revokes a previously granted consent."""
        record = self._requests.get(request_id)
        if not record:
            return {'success': False, 'error': 'Consent request not found.'}
        if record['owner'] != owner:
            return {'success': False, 'error': 'Only the content owner can revoke consent.'}

        record['status'] = 'REVOKED'
        record['responded_at'] = datetime.now().isoformat()
        self._log('REVOKE', request_id, owner, f"Consent revoked from {record['requester']}")
        return {'success': True, 'request_id': request_id, 'status': 'REVOKED'}

    def get_status(self, request_id: str) -> dict:
        record = self._requests.get(request_id)
        if not record:
            return {'found': False}
        return {'found': True, **record}

    def get_audit_log(self) -> list[dict]:
        return self._audit_log.copy()

    # ── Internal ───────────────────────────────────────────────────────────────
    def _log(self, action: str, request_id: str, actor: str, note: str):
        self._audit_log.append({
            'timestamp':  datetime.now().isoformat(),
            'action':     action,
            'request_id': request_id,
            'actor':      actor,
            'note':       note,
        })
