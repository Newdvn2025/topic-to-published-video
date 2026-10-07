"""Validate the distributable and optional project state; no network or writes."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_state(state):
    errors = []
    if state.get('stage') == 'published' and not state.get('published_evidence'):
        errors.append('published requires publication evidence')
    if state.get('stage') in ('approved', 'delivery_ready', 'published'):
        if not state.get('confirmations', {}).get('review'):
            errors.append('approved delivery requires review confirmation')
    if state.get('stage') == 'delivery_ready' and state.get('pending'):
        errors.append('delivery_ready cannot have pending deliverables')
    return errors


def main():
    errors = []
    for path in ROOT.rglob('*.json'):
        try:
            data = json.loads(path.read_text())
            if path.name == 'production-state.json':
                errors.extend(validate_state(data))
        except (ValueError, OSError) as exc:
            errors.append(f'{path.relative_to(ROOT)}: {exc}')
    for path in ROOT.rglob('*.md'):
        text = path.read_text()
        if '/Users/' in text or '/home/' in text:
            errors.append(f'private absolute path: {path.relative_to(ROOT)}')
        for target in re.findall(r'\]\(([^)]+)\)', text):
            if '://' not in target and not target.startswith('#'):
                if not (path.parent / target.split('#')[0]).exists():
                    errors.append(f'broken link: {path.relative_to(ROOT)} -> {target}')
    config = json.loads((ROOT / 'config/creator.example.json').read_text())
    if config['creator_name'] or config['outro_template']:
        errors.append('public defaults must not invent creator identity')
    transcript = json.loads((ROOT / 'templates/transcript.json').read_text())
    if transcript['timing_status'] == 'pending_audio' and transcript['segments']:
        errors.append('pending audio must not contain invented timeline')
    if len(sys.argv) > 1:
        errors.extend(validate_state(json.loads(Path(sys.argv[1]).read_text())))
    for error in errors:
        print('ERROR:', error)
    if errors:
        return 1
    print('PASS: JSON, relative links, public defaults and state constraints')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
