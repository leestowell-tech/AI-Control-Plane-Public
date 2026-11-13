"""Portable receipt contract regressions; not proof of external host enforcement."""
import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]


def receipt():
    return {
        'receipt_id': 'fictional-receipt', 'job_id': 'fictional-bounded-job',
        'endpoint_id': 'fictional-test-host', 'state': 'CLOSED',
        'timestamps': {'received_at': '2026-10-21T00:00:00Z'},
        'artifacts': [{'ref': 'fictional://result', 'hash': 'fictional-content-hash'}],
        'verification': [{'test': 'actual-receiver-readback', 'result': 'PASS',
                          'evidence': 'fictional://receiver-observation'}],
        'receiver_state': 'VERIFIED',
        'reconciliation': {'scope_disposition': ['bounded scope verified complete'],
                           'mission_status': 'OPEN', 'job_status': 'CLOSED'},
    }


def artifact_free(kind='NO_CHANGE'):
    r = receipt()
    r['artifacts'] = []
    r['reconciliation']['artifact_disposition'] = {
        'kind': kind, 'contract_ref': 'fictional://owning-job-contract/v1',
        'reason': 'Owning contract permits this bounded result without an artifact.',
        'evidence': 'fictional://receiver-observation',
    }
    if kind in ('APPROVED_DEFERRAL', 'OBSERVATION_BOUND'):
        r['reconciliation']['artifact_disposition'].update(
            owner='fictional-existing-owner', return_condition='Named outside event occurs')
    if kind == 'APPROVED_DEFERRAL':
        r['reconciliation']['artifact_disposition']['approval_ref'] = 'fictional://grant/v1'
    return r


class ReceiptOutcomeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schema = json.loads((ROOT / 'schemas/execution-receipt.schema.json').read_text())
        Draft202012Validator.check_schema(schema)
        cls.validator = Draft202012Validator(schema)

    def invalid(self, r):
        self.assertTrue(list(self.validator.iter_errors(r)), 'Unsupported claim was accepted')

    def test_bounded_job_can_close_with_parent_open_blocked_or_observation_bound(self):
        for status in ('OPEN', 'BLOCKED', 'OBSERVATION'):
            with self.subTest(status=status):
                r = receipt()
                r['reconciliation']['mission_status'] = status
                self.validator.validate(r)

    def test_explicit_unfinished_job_cannot_close_even_with_closed_parent(self):
        for status in ('OPEN', 'BLOCKED', 'OBSERVATION'):
            with self.subTest(status=status):
                r = receipt()
                r['reconciliation'].update(job_status=status, mission_status='CLOSED')
                self.invalid(r)

    def test_early_state_cannot_smuggle_job_closure_without_receiving_evidence(self):
        for state in ('ACKNOWLEDGED', 'RUNNING', 'CHECKPOINTED', 'VERIFYING',
                      'BLOCKED', 'FAILED', 'CANCELLED', 'EXPIRED', 'SUPERSEDED'):
            with self.subTest(state=state):
                r = receipt()
                r.update(state=state, timestamps={}, artifacts=[], verification=[])
                r['reconciliation']['scope_disposition'] = []
                self.invalid(r)

    def test_legacy_whole_mission_closure_remains_valid(self):
        r = receipt()
        r['reconciliation'].pop('job_status')
        r['reconciliation']['mission_status'] = 'CLOSED'
        self.validator.validate(r)

    def test_legacy_open_parent_does_not_imply_job_closure(self):
        r = receipt()
        r['reconciliation'].pop('job_status')
        self.invalid(r)

    def test_r6_counterfactual_preserves_demonstrated_bad_and_valid_cases(self):
        embedded = (ROOT / 'tests/fixtures/execution-receipt-r6.schema.json').read_text()
        old = Draft202012Validator(json.loads(embedded))
        for r in (receipt(), artifact_free()):
            self.assertTrue(list(old.iter_errors(r)), 'r6 must demonstrate the valid-case regression')
            self.validator.validate(r)
        unfinished = receipt()
        unfinished['reconciliation'].update(job_status='OPEN', mission_status='CLOSED')
        undisposed = receipt()
        undisposed['state'] = 'RECONCILED'
        undisposed['reconciliation']['job_status'] = 'OPEN'
        undisposed['reconciliation']['scope_disposition'] = []
        blank = receipt()
        blank['reconciliation']['mission_status'] = 'CLOSED'
        blank['verification'][0]['evidence'] = '   '
        early_closed = receipt()
        early_closed.update(state='RUNNING', timestamps={}, artifacts=[], verification=[])
        blank_time = receipt()
        blank_time['reconciliation']['mission_status'] = 'CLOSED'
        blank_time['timestamps']['received_at'] = '   '
        for r in (unfinished, undisposed, blank, early_closed, blank_time):
            old.validate(r)
            self.invalid(r)

    def test_explicit_contract_permits_valid_artifact_free_outcomes(self):
        for state in ('RECEIVED', 'RECONCILED', 'CLOSED'):
            for kind in ('NO_CHANGE', 'ARTIFACT_FREE', 'APPROVED_DEFERRAL', 'OBSERVATION_BOUND'):
                with self.subTest(state=state, kind=kind):
                    r = artifact_free(kind)
                    r['state'] = state
                    r['reconciliation']['job_status'] = 'CLOSED' if state == 'CLOSED' else 'OPEN'
                    self.validator.validate(r)

    def test_empty_artifacts_alone_never_establish_receipt(self):
        for state in ('RECEIVED', 'RECONCILED', 'CLOSED'):
            with self.subTest(state=state):
                r = receipt()
                r['state'] = state
                r['reconciliation']['job_status'] = 'CLOSED' if state == 'CLOSED' else 'OPEN'
                r['artifacts'] = []
                self.invalid(r)

    def test_artifact_free_requires_contract_reason_and_evidence_reference(self):
        for field in ('kind', 'contract_ref', 'reason', 'evidence'):
            with self.subTest(field=field):
                r = artifact_free()
                del r['reconciliation']['artifact_disposition'][field]
                self.invalid(r)

    def test_received_timestamp_and_identity_cannot_be_blank_without_format_checker(self):
        for value in ('', '   ', '\t'):
            for field in ('receipt_id', 'job_id', 'endpoint_id', 'received_at'):
                with self.subTest(field=field, value=value):
                    r = receipt()
                    if field == 'received_at':
                        r['timestamps'][field] = value
                    else:
                        r[field] = value
                    self.invalid(r)

    def test_deferral_requires_approval_owner_and_return_condition(self):
        for field in ('approval_ref', 'owner', 'return_condition'):
            with self.subTest(field=field):
                r = artifact_free('APPROVED_DEFERRAL')
                del r['reconciliation']['artifact_disposition'][field]
                self.invalid(r)

    def test_observation_requires_owner_and_return_condition(self):
        for field in ('owner', 'return_condition'):
            with self.subTest(field=field):
                r = artifact_free('OBSERVATION_BOUND')
                del r['reconciliation']['artifact_disposition'][field]
                self.invalid(r)

    def test_artifact_free_cannot_skip_real_verification_or_receiver(self):
        for field, value in (('verification', []), ('receiver_state', 'PENDING')):
            with self.subTest(field=field):
                r = artifact_free()
                r[field] = value
                self.invalid(r)

    def test_reconciled_claim_requires_scope_disposition(self):
        r = receipt()
        r['state'] = 'RECONCILED'
        r['reconciliation']['job_status'] = 'OPEN'
        r['reconciliation']['scope_disposition'] = []
        self.invalid(r)

    def test_whitespace_is_not_evidence_or_scope_disposition(self):
        modifications = [
            ('verification', [{'test': 'readback', 'result': 'PASS', 'evidence': '   '}]),
            ('artifacts', [{'ref': '\t', 'hash': 'hash'}]),
            ('artifacts', [{'ref': 'fictional://result', 'hash': '   '}]),
            ('reconciliation', dict(receipt()['reconciliation'], scope_disposition=['   '])),
        ]
        for field, value in modifications:
            with self.subTest(field=field, value=value):
                r = copy.deepcopy(receipt())
                r['reconciliation']['mission_status'] = 'CLOSED'
                r[field] = value
                if field == 'reconciliation':
                    r[field]['mission_status'] = 'CLOSED'
                self.invalid(r)


if __name__ == '__main__':
    unittest.main()
