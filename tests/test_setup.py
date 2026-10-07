import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SETUP = load('setup_module', ROOT / 'scripts/setup.py')
AUTODL = load('autodl_module', ROOT / 'addons/autodl-broll/scripts/autodl_broll.py')


class SetupTests(unittest.TestCase):
    def test_dry_run_does_not_create_workspace_or_execute(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / 'not-created'
            with patch('sys.argv', ['setup', '--profile', 'all', '--dry-run', '--workspace', str(workspace)]), patch.object(SETUP, 'execute') as execute, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(SETUP.main(), 0)
                execute.assert_not_called()
            self.assertFalse(workspace.exists())

    def test_local_install_preserves_existing_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = ['setup', '--select', 'autodl', '--yes', '--workspace', tmp]
            with patch('sys.argv', args), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(SETUP.main(), 0)
            skill = Path(tmp) / '.agents/skills/autodl-broll/SKILL.md'
            skill.write_text('user changes', encoding='utf-8')
            with patch('sys.argv', args), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(SETUP.main(), 0)
            self.assertEqual(skill.read_text(), 'user changes')
            state = json.loads((Path(tmp) / '.video-workflow/setup-state.json').read_text())
            self.assertEqual(state['tools']['autodl']['status'], 'existing_unverified')
            self.assertFalse(state['initialization_complete'])

    def test_paid_generation_is_never_part_of_install_commands(self):
        for tool in ('hyperframes', 'remotion', 'chatcut'):
            command = SETUP.command_for(tool, 'codex', False)
            self.assertIn('add', command)
            self.assertNotIn('render', command)
        with self.assertRaises(ValueError):
            SETUP.resolve_selection(select='arbitrary-command')

    def test_key_file_permissions_and_environment_precedence(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / 'autodl.env'
            SETUP.write_key(file, 'dummy-file-token')
            if os.name != 'nt':
                self.assertEqual(file.stat().st_mode & 0o777, 0o600)
            with patch.dict(os.environ, {'AUTODL_ART_TOKEN': 'dummy-env-token'}):
                AUTODL.load_env(file)
                self.assertEqual(os.environ['AUTODL_ART_TOKEN'], 'dummy-env-token')
            with patch.dict(os.environ, {'AUTODL_ART_TOKEN': ''}):
                AUTODL.load_env(file)
                self.assertEqual(os.environ['AUTODL_ART_TOKEN'], 'dummy-file-token')
            with self.assertRaises(ValueError):
                SETUP.write_key(file, 'bad\nnew-key')

    def test_api_request_uses_raw_token_and_no_network_for_test(self):
        response = io.BytesIO(b'{"code":"Success","data":{"task_id":"demo"}}')
        with patch.object(AUTODL.urllib.request, 'urlopen', return_value=response) as network:
            result = AUTODL.Client('dummy-token').submit('demo-workflow', {'prompt': 'demo'})
            request = network.call_args.args[0]
            self.assertEqual(request.get_header('Authorization'), 'dummy-token')
            self.assertEqual(result['task_id'], 'demo')


if __name__ == '__main__':
    unittest.main()
