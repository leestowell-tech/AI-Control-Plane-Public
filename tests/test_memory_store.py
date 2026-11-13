"""Mechanical integrity only: these tests do not run an AI or prove user recall."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('memory_store', Path(__file__).resolve().parents[1] / 'deployment/memory_store.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def request(key='studio-saturday', base=0):
    return dict(id=key, base_revision=base, value=dict(
        recorded_at='2026-09-30T17:00:00-04:00', topic='studio/schedule',
        title='Saturday lesson timing', aliases=['weekend class', 'Saturday workshop'],
        **{'class': 'DECISION'}, statement_kind='user_decision', status='active',
        summary='Start the workshop at 11 am, subject to instructor confirmation.',
        details='Move from 10 am to 11 am; instructor availability is unconfirmed.',
        source=dict(origin='synthetic_user', reference='synthetic fixture A',
                    excerpt='Make it 11, if the instructor confirms.'),
        valid_until=None, uncertainty='Instructor confirmation remains open.',
        decision_maker='synthetic_user', authorization_source='synthetic fixture A'))


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.store = m.empty('synthetic-instance')

    def save(self, r, store=None):
        source = self.store if store is None else store
        return m.prepare(source, r, m.digest(source))[0]

    def test_new_record_and_index_are_one_change(self):
        got = self.save(request())
        self.assertEqual(got['index'][0]['aliases'], request()['value']['aliases'])
        self.assertEqual(got['generation'], 1)
        self.assertEqual(self.store['records'], {})

    def test_revision_preserves_qualification_and_history(self):
        original = self.save(request())
        change = request(base=1)
        change['value'].update(summary='Workshop is at noon, subject to instructor confirmation.',
                               details='User revised 11 am to noon; availability still unconfirmed.')
        got = self.save(change, original)
        versions = got['records']['studio-saturday']['revisions']
        self.assertEqual(len(versions), 2)
        self.assertEqual(versions[0], original['records']['studio-saturday']['revisions'][0])
        self.assertEqual(versions[1]['uncertainty'], 'Instructor confirmation remains open.')
        self.assertEqual(got['index'][0]['revision'], 2)

    def test_unrelated_subject_survives(self):
        first = self.save(request())
        got = self.save(request('equipment-order'), first)
        self.assertEqual(got['records']['studio-saturday'], first['records']['studio-saturday'])

    def test_stale_store_rejected(self):
        received = self.save(request())
        with self.assertRaisesRegex(ValueError, 'Store conflict'):
            m.prepare(received, request('equipment-order'), m.digest(self.store))

    def test_stale_record_rejected(self):
        received = self.save(request())
        change = request()
        change['value']['summary'] = 'Different interpretation, not an identical retry.'
        with self.assertRaisesRegex(ValueError, 'Record conflict'):
            self.save(change, received)

    def test_exact_timeout_retry_does_not_duplicate(self):
        received = self.save(request())
        got, status = m.prepare(received, request(), m.digest(self.store))
        self.assertEqual(status, 'ALREADY_PRESENT')
        self.assertEqual(got, received)

    def test_proposal_cannot_pass_as_decision(self):
        r = request()
        r['value']['statement_kind'] = 'assistant_proposal'
        with self.assertRaisesRegex(ValueError, 'Proposal'):
            self.save(r)

    def test_missing_authorization_rejected(self):
        r = request()
        del r['value']['authorization_source']
        with self.assertRaisesRegex(ValueError, 'authority'):
            self.save(r)

    def test_missing_provenance_rejected(self):
        r = request()
        r['value']['source']['excerpt'] = ''
        with self.assertRaisesRegex(ValueError, 'provenance'):
            self.save(r)

    def test_stale_index_rejected(self):
        got = self.save(request())
        got['index'] = []
        with self.assertRaisesRegex(ValueError, 'Index'):
            m.validate(got)

    def test_withdrawal_preserves_history(self):
        first = self.save(request())
        r = request(base=1)
        r['value'].update(status='withdrawn', summary='Workshop plan withdrawn.',
                          details='Synthetic user cancelled this plan.')
        got = self.save(r, first)
        self.assertEqual(got['index'][0]['status'], 'withdrawn')
        self.assertEqual(got['records']['studio-saturday']['revisions'][0]['status'], 'active')

    def test_template_is_not_a_bound_user_store(self):
        with self.assertRaisesRegex(ValueError, 'bound'):
            m.empty('UNBOUND')

    def test_duplicate_json_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'bad.json'
            p.write_text('{"records": {}, "records": {}}')
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                m.load_json(p)

    def test_invalid_change_does_not_mutate_original(self):
        original = self.save(request())
        before = copy.deepcopy(original)
        r = request(base=1)
        r['value']['source'] = {}
        with self.assertRaises(ValueError):
            self.save(r, original)
        self.assertEqual(original, before)

    def test_unknown_fields_not_silently_dropped(self):
        r = request()
        r['value']['secret_context'] = 'unexpected'
        with self.assertRaisesRegex(ValueError, 'fields'):
            self.save(r)


if __name__ == '__main__':
    unittest.main()
