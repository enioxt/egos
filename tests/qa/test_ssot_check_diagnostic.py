import importlib.util
import sys
from pathlib import Path
from unittest import TestCase

MODULE_PATH = Path(__file__).resolve().parents[2] / 'scripts' / 'qa' / 'ssot_check_diagnostic.py'
spec = importlib.util.spec_from_file_location('ssot_check_diagnostic', MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class SsotCheckDiagnosticTests(TestCase):
    def test_classify_pass(self):
        data = module.classify_output('OK: 10 | Drift: 0 | Synced: 0', 0)
        self.assertEqual(data['classification'], 'pass')
        self.assertEqual(data['exit_code'], 0)

    def test_classify_env_drift_when_only_new(self):
        output = 'NEW guarani: PREFERENCES.md\nNEW workflow: start.md\nCI FAIL: 2 files drifted from kernel'
        data = module.classify_output(output, 1)
        self.assertEqual(data['classification'], 'env_drift')
        self.assertEqual(data['exit_code'], 0)

    def test_classify_repo_drift_when_mod_present(self):
        output = 'MOD guarani: PREFERENCES.md\nCI FAIL: drift'
        data = module.classify_output(output, 1)
        self.assertEqual(data['classification'], 'repo_drift')
        self.assertEqual(data['exit_code'], 6)

    def test_classify_mixed_drift_when_new_and_mod_present(self):
        output = 'NEW guarani: PREFERENCES.md\nMOD guarani: IDENTITY.md\nCI FAIL: drift'
        data = module.classify_output(output, 1)
        self.assertEqual(data['classification'], 'mixed_drift')
        self.assertGreaterEqual(float(data['confidence']), 0.90)


    def test_recommended_actions_by_classification(self):
        env_actions = module.recommended_actions('env_drift')
        repo_actions = module.recommended_actions('repo_drift')
        mixed_actions = module.recommended_actions('mixed_drift')

        self.assertTrue(any('governance:sync:local' in item['command'] for item in env_actions))
        self.assertTrue(any(item['priority'] == 'P0' for item in repo_actions))
        self.assertTrue(any('name-status' in item['command'] for item in mixed_actions))
