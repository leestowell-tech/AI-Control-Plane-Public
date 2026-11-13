"""Offline packaging regressions; not an AI behavior or target-account test."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

# Test dependency only; portable runtime/schema consumers choose their validator.
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prepare_bundle', ROOT / 'deployment/prepare_bundle.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'source'
        shutil.copytree(ROOT, self.root)
        explicit_manifest = os.environ.get('BUNDLE_SOURCE_MANIFEST')
        if explicit_manifest:
            self.manifest = json.loads(Path(explicit_manifest).read_text())
        else:
            release = json.loads((ROOT / 'deployment/CAPABILITY_PROFILE.json').read_text())['release']
            matches = [json.loads(p.read_text()) for p in (ROOT / 'deployment/releases').glob('*-source.json')]
            matches = [m for m in matches if m.get('release') == release]
            self.assertEqual(len(matches), 1, 'Exactly one current release manifest is required; use BUNDLE_SOURCE_MANIFEST for a development candidate')
            self.manifest = matches[0]

    def tearDown(self):
        self.temp.cleanup()

    def refresh_pin(self, name):
        sha = package.blob_sha((self.root / name).read_bytes())
        for entry in self.manifest['files']:
            if entry['path'] == name:
                entry['sha'] = sha
                return
        self.manifest['files'].append({'path': name, 'sha': sha})

    def add_recipe_source(self, name):
        recipe = self.root / 'deployment/PROJECT_BUNDLE.md'
        original = recipe.read_text()
        altered = original.replace('## Project instruction', '- `' + name + '`\n\n## Project instruction')
        self.assertNotEqual(original, altered, 'Fault injection must change the recipe')
        recipe.write_text(altered)
        self.refresh_pin('deployment/PROJECT_BUNDLE.md')
        self.refresh_pin(name)

    def test_complete_and_roundtrip(self):
        result, count = package.build(self.root, self.manifest)
        self.assertEqual(count, 51)
        self.assertIn(b'Target surface and consenting account holder: not yet verified', result)
        self.assertIn(b'<!-- SOURCE kernel/EXECUTION_ROUTING.md', result)

    def test_missing_scope(self):
        (self.root / 'kernel/SCOPE_SELECTION.md').unlink()
        with self.assertRaises(FileNotFoundError):
            package.build(self.root, self.manifest)

    def test_missing_routing(self):
        (self.root / 'kernel/EXECUTION_ROUTING.md').unlink()
        with self.assertRaises(FileNotFoundError):
            package.build(self.root, self.manifest)

    def test_altered_source(self):
        (self.root / 'BOOT.md').write_text('Not the reviewed source')
        with self.assertRaisesRegex(ValueError, 'Source hash mismatch'):
            package.build(self.root, self.manifest)

    def test_missing_manifest_entry(self):
        self.manifest['files'] = [x for x in self.manifest['files'] if x['path'] != 'BOOT.md']
        with self.assertRaisesRegex(ValueError, 'Missing pinned source'):
            package.build(self.root, self.manifest)

    def test_mutable_revision_rejected(self):
        self.manifest['source_commit'] = 'main'
        with self.assertRaisesRegex(ValueError, 'Immutable source commit'):
            package.build(self.root, self.manifest)

    def test_path_traversal_rejected(self):
        self.manifest['files'].append({'path': '../private.md', 'sha': '0' * 40})
        with self.assertRaisesRegex(ValueError, 'Unsafe source path'):
            package.build(self.root, self.manifest)

    def test_unlisted_private_file_not_exported(self):
        (self.root / 'state').mkdir(exist_ok=True)
        (self.root / 'state/CURRENT_STATE.md').write_text('PRIVATE SENTINEL NOT FOR EXPORT')
        result, _ = package.build(self.root, self.manifest)
        self.assertNotIn(b'PRIVATE SENTINEL NOT FOR EXPORT', result)

    def test_quickmarket_optional(self):
        result, count = package.build(self.root, self.manifest, False)
        self.assertEqual(count, 50)
        self.assertNotIn(b'<!-- SOURCE domains/QUICKMARKET.md', result)

    def test_legacy_manifest_rejected_even_with_new_hash(self):
        p = self.root / 'deployment/PROJECT_BUNDLE.md'
        p.write_text(p.read_text().replace('- `kernel/SCOPE_SELECTION.md`\n', ''))
        for entry in self.manifest['files']:
            if entry['path'] == 'deployment/PROJECT_BUNDLE.md':
                entry['sha'] = package.blob_sha(p.read_bytes())
        with self.assertRaisesRegex(ValueError, 'Incomplete or duplicate'):
            package.build(self.root, self.manifest)

    def test_dependency_outside_package_rejected(self):
        p = self.root / 'BOOT.md'
        p.write_text(p.read_text() + '\nRead `kernel/MISSING.md`.\n')
        for entry in self.manifest['files']:
            if entry['path'] == 'BOOT.md':
                entry['sha'] = package.blob_sha(p.read_bytes())
        with self.assertRaisesRegex(ValueError, 'Unpackaged source reference'):
            package.build(self.root, self.manifest)

    def test_private_marker_rejected_even_with_new_hash(self):
        p = self.root / 'BOOT.md'
        p.write_text(p.read_text() + '\nPrivate checkout /Users/example/project\n')
        for entry in self.manifest['files']:
            if entry['path'] == 'BOOT.md':
                entry['sha'] = package.blob_sha(p.read_bytes())
        with self.assertRaisesRegex(ValueError, 'Possible private-state'):
            package.build(self.root, self.manifest)

    def test_memory_workflow_is_required(self):
        (self.root / 'deployment/MEMORY_WORKFLOW.md').unlink()
        with self.assertRaises(FileNotFoundError):
            package.build(self.root, self.manifest)

    def test_memory_entry_is_required_even_if_recipe_hash_is_refreshed(self):
        p = self.root / 'deployment/PROJECT_BUNDLE.md'
        p.write_text(p.read_text().replace('- `templates/PROJECT_INSTRUCTIONS.md`\n', ''))
        for entry in self.manifest['files']:
            if entry['path'] == 'deployment/PROJECT_BUNDLE.md':
                entry['sha'] = package.blob_sha(p.read_bytes())
        with self.assertRaisesRegex(ValueError, 'Incomplete or duplicate'):
            package.build(self.root, self.manifest)

    def test_full_protocol_dependencies_cannot_be_omitted(self):
        for name in ('kernel/BUILD.md', 'kernel/RESET.md', 'kernel/MIRROR.md',
                     'OPERATOR.md', 'kernel/ROUTING.md', 'kernel/UPGRADE.md',
                     'kernel/WORKING_MODES.md', 'kernel/LOOSE_ENDS.md',
                     'kernel/RECALL.md', 'kernel/WEBBING.md', 'kernel/NORTH_STAR.md',
                     'deployment/CAPABILITY_PROFILE.json', 'deployment/UPDATES.md'):
            with self.subTest(path=name):
                p = self.root / 'deployment/PROJECT_BUNDLE.md'
                original = p.read_text()
                removed = original.replace('- `' + name + '`\n', '')
                self.assertNotEqual(removed, original, 'Fault injection must remove the dependency')
                p.write_text(removed)
                for entry in self.manifest['files']:
                    if entry['path'] == 'deployment/PROJECT_BUNDLE.md':
                        entry['sha'] = package.blob_sha(p.read_bytes())
                with self.assertRaisesRegex(ValueError, 'Incomplete or duplicate'):
                    package.build(self.root, self.manifest)
                p.write_text(original)
                for entry in self.manifest['files']:
                    if entry['path'] == 'deployment/PROJECT_BUNDLE.md':
                        entry['sha'] = package.blob_sha(p.read_bytes())

    def test_plain_text_dependency_is_checked(self):
        p = self.root / 'kernel/RESET.md'
        p.write_text(p.read_text() + '\nUse kernel/UNAVAILABLE.md.\n')
        for entry in self.manifest['files']:
            if entry['path'] == 'kernel/RESET.md':
                entry['sha'] = package.blob_sha(p.read_bytes())
        with self.assertRaisesRegex(ValueError, 'Unpackaged source reference'):
            package.build(self.root, self.manifest)

    def test_user_instance_not_exported(self):
        result, _ = package.build(self.root, self.manifest)
        self.assertNotIn(b'<!-- SOURCE state/users/', result)
        self.assertNotIn(b'<!-- SOURCE state/', result)

    def test_incomplete_capability_profile_rejected(self):
        p = self.root / 'deployment/CAPABILITY_PROFILE.json'
        value = json.loads(p.read_text())
        value['capabilities'] = [x for x in value['capabilities'] if x['id'] != 'reset']
        p.write_text(json.dumps(value))
        for entry in self.manifest['files']:
            if entry['path'] == 'deployment/CAPABILITY_PROFILE.json':
                entry['sha'] = package.blob_sha(p.read_bytes())
        with self.assertRaisesRegex(ValueError, 'capability profile'):
            package.build(self.root, self.manifest)

    def test_extended_commands_cannot_be_dropped_from_profile(self):
        p = self.root / 'deployment/CAPABILITY_PROFILE.json'
        original = p.read_text()
        for capability in ('working_modes', 'loose_ends', 'recall', 'webbing', 'north_star'):
            with self.subTest(capability=capability):
                value = json.loads(original)
                value['capabilities'] = [x for x in value['capabilities'] if x['id'] != capability]
                p.write_text(json.dumps(value))
                self.refresh_pin('deployment/CAPABILITY_PROFILE.json')
                with self.assertRaisesRegex(ValueError, 'capability profile'):
                    package.build(self.root, self.manifest)
        p.write_text(original)
        self.refresh_pin('deployment/CAPABILITY_PROFILE.json')
        # Valid unchanged control still passes the actual package producer.
        package.build(self.root, self.manifest)

    def test_default_help_stays_small_with_full_reference_available(self):
        result, _ = package.build(self.root, self.manifest)
        menu = (self.root / 'OPERATOR.md').read_text()
        short = menu.split('## Short start menu', 1)[1].split('## Full reference', 1)[0]
        rows = [line for line in short.splitlines() if line.startswith('|')]
        self.assertEqual(len(rows) - 2, 6)
        self.assertLess(len(short), 900)
        for name in ('WORKING_MODES', 'LOOSE_ENDS', 'RECALL', 'WEBBING', 'NORTH_STAR'):
            self.assertIn(('<!-- SOURCE kernel/' + name + '.md').encode(), result)

    def test_profile_cannot_reference_private_runtime_source(self):
        p = self.root / 'deployment/CAPABILITY_PROFILE.json'
        value = json.loads(p.read_text())
        value['capabilities'][0]['path'] = 'https://example.invalid/private/reset.md'
        p.write_text(json.dumps(value))
        for entry in self.manifest['files']:
            if entry['path'] == 'deployment/CAPABILITY_PROFILE.json':
                entry['sha'] = package.blob_sha(p.read_bytes())
        with self.assertRaisesRegex(ValueError, 'Unpackaged profile dependency'):
            package.build(self.root, self.manifest)

    def test_inconsistent_release_rejected(self):
        p = self.root / 'deployment/RELEASE.md'
        release = json.loads((self.root / 'deployment/CAPABILITY_PROFILE.json').read_text())['release']
        original = p.read_text()
        altered = original.replace('Release: ' + release, 'Release: old-release')
        self.assertNotEqual(altered, original, 'Fault injection must change the release')
        p.write_text(altered)
        for entry in self.manifest['files']:
            if entry['path'] == 'deployment/RELEASE.md':
                entry['sha'] = package.blob_sha(p.read_bytes())
        with self.assertRaisesRegex(ValueError, 'Profile/release mismatch'):
            package.build(self.root, self.manifest)

    def test_manifest_release_mismatch_rejected(self):
        self.manifest['release'] = 'wrong-release'
        with self.assertRaisesRegex(ValueError, 'Manifest/profile release mismatch'):
            package.build(self.root, self.manifest)

    def test_missing_manifest_release_rejected(self):
        self.manifest.pop('release')
        with self.assertRaisesRegex(ValueError, 'Manifest/profile release mismatch'):
            package.build(self.root, self.manifest)

    def test_recipe_cannot_export_instance_even_with_refreshed_pins(self):
        name = 'state/users/synthetic/CURRENT_STATE.md'
        target = self.root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('A private appointment is on Tuesday.\n')
        self.add_recipe_source(name)
        with self.assertRaisesRegex(ValueError, 'User-instance state cannot be packaged'):
            package.build(self.root, self.manifest)

    def test_recipe_alias_cannot_export_instance(self):
        private = self.root / 'state/synthetic.md'
        private.parent.mkdir(exist_ok=True)
        private.write_text('A private appointment is on Tuesday.\n')
        name = 'templates/synthetic-alias.md'
        (self.root / name).symlink_to(private)
        self.add_recipe_source(name)
        with self.assertRaisesRegex(ValueError, 'User-instance state cannot be packaged'):
            package.build(self.root, self.manifest)

    def test_valid_extra_template_and_empty_memory_seed_remain_exportable(self):
        name = 'templates/synthetic-example.md'
        (self.root / name).write_text('Blank reusable example, no instance data.\n')
        self.add_recipe_source(name)
        result, count = package.build(self.root, self.manifest)
        self.assertEqual(count, 52)
        self.assertIn(b'<!-- SOURCE templates/synthetic-example.md', result)
        self.assertIn(b'<!-- SOURCE templates/MEMORY_STORE.json', result)

    def test_noncanonical_manifest_path_rejected(self):
        self.manifest['files'].append({'path': './BOOT.md', 'sha': '0' * 40})
        with self.assertRaisesRegex(ValueError, 'Unsafe source path'):
            package.build(self.root, self.manifest)


class ExecutionReceiptSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((ROOT / 'schemas/execution-receipt.schema.json').read_text())
        Draft202012Validator.check_schema(cls.schema)
        cls.validator = Draft202012Validator(cls.schema)

    def pending(self, state='RUNNING'):
        return {
            'receipt_id': 'synthetic-receipt', 'job_id': 'synthetic-job',
            'endpoint_id': 'synthetic-endpoint', 'state': state,
            'timestamps': {}, 'artifacts': [], 'verification': [],
            'reconciliation': {'scope_disposition': [], 'mission_status': 'OPEN'},
        }

    def received(self, state='CLOSED'):
        receipt = self.pending(state)
        receipt.update({
            'timestamps': {'received_at': '2026-10-20T18:30:00Z'},
            'artifacts': [{'ref': 'synthetic://artifact', 'hash': 'synthetic-sha256'}],
            'verification': [{'test': 'receiver-readback', 'result': 'PASS',
                              'evidence': 'synthetic://readback'}],
            'receiver_state': 'VERIFIED',
        })
        if state in ('RECONCILED', 'CLOSED'):
            receipt['reconciliation'] = {
                'scope_disposition': ['synthetic task received; no remaining executable scope'],
                'mission_status': 'CLOSED' if state == 'CLOSED' else 'OPEN',
            }
        return receipt

    def assert_invalid(self, receipt):
        self.assertTrue(list(self.validator.iter_errors(receipt)), 'Invalid receipt was accepted')

    def test_r5_counterfactual_accepts_premature_close_current_rejects(self):
        # Exercise the actual immutable shipped schema, rather than reconstructing
        # an imagined old implementation by removing the new guard.
        embedded = (ROOT / 'tests/fixtures/execution-receipt-r5.schema.json').read_text()
        old = json.loads(embedded)
        premature = self.pending('CLOSED')
        self.assertEqual(list(Draft202012Validator(old).iter_errors(premature)), [])
        self.assert_invalid(premature)

    def test_verified_reconciled_closed_receipt_is_valid(self):
        self.validator.validate(self.received())

    def test_intermediate_and_exception_receipts_keep_existing_shape(self):
        for state in ('ACKNOWLEDGED', 'RUNNING', 'CHECKPOINTED', 'VERIFYING',
                      'BLOCKED', 'FAILED', 'CANCELLED', 'EXPIRED', 'SUPERSEDED'):
            with self.subTest(state=state):
                self.validator.validate(self.pending(state))

    def test_receiving_does_not_force_whole_mission_closed(self):
        for state in ('RECEIVED', 'RECONCILED'):
            with self.subTest(state=state):
                self.validator.validate(self.received(state))

    def test_all_receiving_states_require_actual_evidence(self):
        for state in ('RECEIVED', 'RECONCILED', 'CLOSED'):
            with self.subTest(state=state):
                self.assert_invalid(self.pending(state))

    def test_receiving_rejects_empty_or_unidentified_artifacts(self):
        for artifacts in ([], [{'ref': 'synthetic://artifact'}],
                          [{'ref': '', 'hash': 'synthetic-hash'}],
                          [{'ref': 'synthetic://artifact', 'hash': ''}],
                          [{'ref': 'synthetic://artifact', 'hash': None}]):
            with self.subTest(artifacts=artifacts):
                r = self.received()
                r['artifacts'] = artifacts
                self.assert_invalid(r)

    def test_receiving_rejects_empty_failed_unknown_or_unproven_verification(self):
        for verification in ([], [{'test': 'check', 'result': 'FAIL', 'evidence': 'synthetic'}],
                             [{'test': 'check', 'result': 'UNKNOWN', 'evidence': 'synthetic'}],
                             [{'test': 'check', 'result': 'PASS'}],
                             [{'test': 'check', 'result': 'PASS', 'evidence': None}],
                             [{'test': 'check', 'result': 'PASS', 'evidence': ''}]):
            with self.subTest(verification=verification):
                r = self.received()
                r['verification'] = verification
                self.assert_invalid(r)

    def test_receiving_requires_verified_receiver(self):
        for receiver in (None, '', 'PENDING', 'FAILED'):
            with self.subTest(receiver=receiver):
                r = self.received()
                r['receiver_state'] = receiver
                self.assert_invalid(r)
        r = self.received()
        del r['receiver_state']
        self.assert_invalid(r)

    def test_receiving_requires_timestamp(self):
        for timestamps in ({}, {'received_at': None}):
            with self.subTest(timestamps=timestamps):
                r = self.received()
                r['timestamps'] = timestamps
                self.assert_invalid(r)

    def test_closed_requires_reconciliation_and_scope_dispositions(self):
        for status in ('OPEN', 'BLOCKED', 'OBSERVATION'):
            with self.subTest(status=status):
                r = self.received()
                r['reconciliation']['mission_status'] = status
                self.assert_invalid(r)
        r = self.received()
        r['reconciliation']['scope_disposition'] = []
        self.assert_invalid(r)


if __name__ == '__main__':
    unittest.main()
