"""Interactive dependency setup. No generation, credential checks or publishing."""
from __future__ import annotations
import argparse
import getpass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DEPENDENCIES = json.loads((ROOT / 'config/dependencies.json').read_text(encoding='utf-8'))


def config_dir():
    base = os.environ.get('XDG_CONFIG_HOME')
    if not base and os.name == 'nt':
        base = os.environ.get('APPDATA')
    return (Path(base) if base else Path.home() / '.config') / 'topic-to-published-video'


def write_key(destination, token):
    token = token.strip()
    if not token or any(c in token for c in '\r\n\x00'):
        raise ValueError('Key必须为非空单行文本')
    destination = Path(destination)
    if destination.is_symlink():
        raise ValueError('密钥文件不能是符号链接')
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=destination.parent, prefix='.autodl-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write('AUTODL_ART_TOKEN=' + token + '\n')
        if os.name != 'nt':
            os.chmod(tmp, 0o600)
        os.replace(tmp, destination)
    finally:
        if Path(tmp).exists():
            Path(tmp).unlink()


def resolve_selection(profile=None, select=None):
    if select is not None:
        selected = list(dict.fromkeys(x.strip() for x in select.split(',') if x.strip()))
    else:
        selected = DEPENDENCIES['profiles'][profile or 'recommended'][:]
    if not selected or any(x not in DEPENDENCIES['tools'] for x in selected):
        raise ValueError('请选择autodl,hyperframes,remotion,chatcut中的至少一项')
    return selected


def command_for(tool, agent, global_install):
    info = DEPENDENCIES['tools'][tool]
    cmd = ['npx', '--yes', 'skills@latest', 'add', info['source'], '--skill']
    cmd += info['skills'] + ['--agent', agent, '--yes']
    if global_install:
        cmd.append('--global')
    return cmd


def execute(command, workspace):
    # shell=False; resolve .cmd on Windows for npx compatibility.
    program = shutil.which(command[0])
    if not program:
        raise RuntimeError(f'缺少{command[0]}，请先安装Node.js/npm后重跑')
    environment = os.environ.copy()
    environment.pop('AUTODL_ART_TOKEN', None)
    subprocess.run([program, *command[1:]], cwd=workspace, env=environment, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', nargs='?', choices=['init', 'key', 'doctor'], default='init')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--profile', choices=['recommended', 'all'])
    group.add_argument('--select', help='comma-separated tool IDs')
    parser.add_argument('--workspace', type=Path, default=Path.cwd())
    parser.add_argument('--global', dest='global_install', action='store_true')
    parser.add_argument('--agent', choices=['codex', 'claude-code', 'cursor'], default='codex')
    parser.add_argument('--yes', action='store_true', help='use only after user chose this install scope')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--replace', action='store_true', help='explicitly replace bundled AutoDL skill')
    args = parser.parse_args()
    if args.action == 'key':
        destination = config_dir() / 'autodl.env'
        if not sys.stdin.isatty():
            raise ValueError('请在本地交互终端使用隐藏输入，或自行配置环境变量；不要通过聊天传Key')
        if destination.exists() and input('已有密钥文件，替换？[y/N] ').lower() != 'y':
            return 0
        write_key(destination, getpass.getpass('AutoDL Art API Key（隐藏输入）: '))
        print('已保存至', destination, '；没有联网验证或提交任务。')
        return 0
    if args.action == 'doctor':
        print('Python:', sys.version.split()[0])
        for tool in ['node', 'npm', 'npx', 'git', 'ffmpeg', 'ffprobe']:
            print(tool + ':', 'available' if shutil.which(tool) else 'missing')
        credential = bool(os.environ.get('AUTODL_ART_TOKEN', '').strip())
        file = config_dir() / 'autodl.env'
        if not credential and file.is_file():
            credential = any(line.startswith('AUTODL_ART_TOKEN=') and line.split('=', 1)[1].strip() for line in file.read_text(encoding='utf-8').splitlines())
        print('AutoDL credential:', 'configured (not authenticated)' if credential else 'missing')
        print('ChatCut应用/连接需由代理检查；此命令不代表所有工具已可用。')
        return 0
    if not args.profile and args.select is None:
        if args.dry_run:
            args.profile = 'recommended'
        elif sys.stdin.isatty():
            print('1 推荐：AutoDL + HyperFrames\n2 全部：追加Remotion + ChatCut\n3 自选')
            choice = input('请选择[1/2/3]，默认1: ').strip() or '1'
            if choice == '3':
                args.select = input('输入工具ID，逗号分隔: ')
            elif choice in ('1', '2'):
                args.profile = 'recommended' if choice == '1' else 'all'
            else:
                raise ValueError('无效选择')
        else:
            raise ValueError('非交互执行请明确--profile或--select')
    selected = resolve_selection(args.profile, args.select)
    workspace = args.workspace.expanduser().resolve()
    if args.global_install:
        home = Path.home() / ('.codex' if args.agent == 'codex' else '.claude' if args.agent == 'claude-code' else '.cursor')
        skill_root = home / 'skills'
    else:
        skill_root = workspace / ('.claude/skills' if args.agent == 'claude-code' else '.agents/skills')
    print('选择:', ', '.join(selected))
    print('范围:', '用户级' if args.global_install else '项目级', '；工作目录:', workspace)
    print('只安装技能；不安装系统运行时、不生成付费素材。ChatCut应用需后续连接步骤。')
    commands = {tool: command_for(tool, args.agent, args.global_install) for tool in selected if tool != 'autodl'}
    for tool, cmd in commands.items():
        print(tool + ':', ' '.join(cmd))
    if args.dry_run:
        return 0
    if not args.yes:
        if not sys.stdin.isatty() or input('确认安装以上选择？[y/N] ').lower() != 'y':
            print('未安装。')
            return 0
    workspace.mkdir(parents=True, exist_ok=True)
    results = {}
    for tool in selected:
        try:
            if tool == 'autodl':
                destination = skill_root / 'autodl-broll'
                if destination.exists():
                    if not args.replace:
                        results[tool] = {'status': 'existing_unverified', 'path': str(destination)}
                        continue
                    if destination.is_symlink():
                        raise ValueError('已有技能是符号链接，请由代理确认目标后更新；不覆盖')
                    backup = destination.with_name(destination.name + '.backup')
                    if backup.exists():
                        raise ValueError('备份目录已存在，请先处理备份')
                    destination.rename(backup)
                shutil.copytree(ROOT / 'addons/autodl-broll', destination, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
                results[tool] = {'status': 'skills_installed', 'path': str(destination), 'credential': 'check_required'}
            else:
                existing = [name for name in DEPENDENCIES['tools'][tool]['skills'] if (skill_root / name / 'SKILL.md').is_file()]
                if existing:
                    results[tool] = {'status': 'existing_unverified', 'existing_skills': existing, 'next': '核对已安装版本；部分已存在时由代理只补缺失技能，避免覆盖'}
                    continue
                if tool == 'chatcut' and args.agent != 'codex':
                    raise ValueError('此ChatCut连接包仅面向Codex；其他宿主请按官方对应安装说明')
                if tool == 'hyperframes':
                    if not shutil.which('node'):
                        raise ValueError('请先安装Node.js 22+')
                    version = subprocess.check_output([shutil.which('node'), '--version'], text=True).strip()
                    if int(re.match(r'v?(\d+)', version).group(1)) < 22:
                        raise ValueError('HyperFrames需要Node.js 22+')
                execute(commands[tool], workspace)
                results[tool] = {'status': 'skills_installed', 'runtime': 'check_required'}
        except (ValueError, RuntimeError, subprocess.SubprocessError, OSError) as exc:
            results[tool] = {'status': 'failed', 'reason': str(exc)}
    report = {'selected': selected, 'agent': args.agent, 'global': args.global_install, 'tools': results, 'initialization_complete': False}
    target = workspace / '.video-workflow/setup-state.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('安装记录:', target)
    print('下一步：配置AutoDL Key、检查运行时；选择ChatCut时加载connect-chatcut-desktop完成应用连接。')
    return 1 if any(x['status'] == 'failed' for x in results.values()) else 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
