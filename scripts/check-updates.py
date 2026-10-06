#!/usr/bin/env python3
"""Check every specs/<pkg>/<pkg>.spec against its upstream source.

Rules
-----
* If Source0 is pinned to a commit (a %global/%define macro holding a
  40-hex hash that Source0 uses), compare it with upstream HEAD
  (or the branch given in update-check.json).
* Otherwise compare the spec Version with the newest stable upstream tag.
* Other sources pinned to a commit (e.g. basilisk's UXP) are reported as
  informational only.

Only stdlib + git are needed. Upstreams are queried with `git ls-remote`
(no API tokens, no rate limits) except PyPI, which uses its JSON API.
Per-package overrides live in scripts/update-check.json:
  {"pkg": {"skip": "reason", "repo": "https://...git", "branch": "main",
           "tag_prefix": "v"}}
"""
import argparse, json, os, re, subprocess, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

HEX40 = re.compile(r'^[0-9a-f]{40}$')
PRE = re.compile(r'(rc|alpha|beta|pre|dev|snapshot|nightly|test)', re.I)
MACRO_DEF = re.compile(r'^\s*%(?:global|define)\s+(\w+)\s+(.*?)\s*$')


def parse_spec(path):
    macros, tags = {}, {}
    for line in open(path, encoding='utf-8', errors='replace'):
        m = MACRO_DEF.match(line)
        if m and m.group(1) not in macros:
            macros[m.group(1)] = m.group(2)
            continue
        m = re.match(r'^(Name|Version|URL|Source\d*):\s*(.*?)\s*$', line)
        if m and m.group(1) not in tags:
            tags[m.group(1)] = m.group(2)
    return macros, tags


def expand(s, macros, tags):
    ctx = dict(macros)
    ctx.update(name=tags.get('Name', ''), version=tags.get('Version', ''),
               url=tags.get('URL', ''))
    ctx['nil'] = ''
    for _ in range(10):
        n = re.sub(r'%\{(\w+)\}|%(name|version)\b',
                   lambda m: ctx.get(m.group(1) or m.group(2), m.group(0)), s)
        if n == s:
            break
        s = n
    return s


def run(*cmd):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=90,
                          env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'})


def _err(r):
    return (r.stderr.strip().splitlines() or ['failed'])[0][:140]


def head_commit(repo, branch=None):
    ref = f'refs/heads/{branch}' if branch else 'HEAD'
    r = run('git', 'ls-remote', repo, ref)
    if r.returncode or not r.stdout.strip():
        raise RuntimeError(f'ls-remote {repo} {ref}: {_err(r)}')
    return r.stdout.split()[0]


def vkey(v):
    return [(0, int(p)) if p.isdigit() else (-1, p)
            for p in re.findall(r'\d+|[A-Za-z]+', v)]


def latest_tag(repo, prefixes):
    r = run('git', 'ls-remote', '--tags', '--refs', repo)
    if r.returncode:
        raise RuntimeError(f'ls-remote {repo}: {_err(r)}')
    best = None
    for line in r.stdout.splitlines():
        tag = line.split('refs/tags/', 1)[-1]
        ver = None
        for p in prefixes:
            if tag.startswith(p) and tag[len(p):][:1].isdigit():
                ver = tag[len(p):]
                break
        if ver is None or PRE.search(ver):
            continue
        if best is None or vkey(ver) > vkey(best):
            best = ver
    if best is None:
        raise RuntimeError('no stable version tags found')
    return best


def pypi_latest(module):
    for name in {module, module.replace('_', '-')}:
        try:
            with urllib.request.urlopen(
                    f'https://pypi.org/pypi/{name}/json', timeout=30) as f:
                return json.load(f)['info']['version']
        except Exception:
            continue
    raise RuntimeError(f'{module} not found on PyPI')


def repo_from_url(url):
    m = re.match(r'(https?://(?:www\.)?(?:github\.com|codeload\.github\.com)'
                 r'/[^/]+/[^/#?]+)', url)
    if m:
        return m.group(1).replace('codeload.github.com', 'github.com')
    m = re.match(r'(https?://[^#?]+?\.git)/snapshot/', url)   # git.kernel.org
    if m:
        return m.group(1)
    m = re.match(r'(https?://[^#?]+?)/-/archive/', url)       # GitLab
    if m:
        return m.group(1) + '.git'
    m = re.match(r'(https?://[^/]+/[^/]+/[^/]+)/archive/', url)  # Forgejo
    if m:
        return m.group(1)
    return None


def check(pkg, spec_dir, cfg):
    o = cfg.get(pkg, {})
    res = {'package': pkg, 'status': 'ok', 'kind': 'tag', 'current': '',
           'latest': '', 'upstream': '', 'info': []}
    if 'skip' in o:
        return {**res, 'status': 'skipped', 'note': o['skip']}
    try:
        macros, tags = parse_spec(os.path.join(spec_dir, pkg, pkg + '.spec'))
        sources = {k: expand(v, macros, tags) for k, v in tags.items()
                   if k.startswith('Source')}
        src0 = sources.get('Source0', '')
        commits = {k: v for k, v in macros.items()
                   if HEX40.match(expand(v, macros, tags))}
        commits = {k: expand(v, macros, tags) for k, v in commits.items()}
        repo = o.get('repo') or repo_from_url(src0) or \
            repo_from_url(expand(tags.get('URL', ''), macros, tags))
        if 'pythonhosted.org' in src0 and not o.get('repo'):
            module = expand('%{module}', macros, tags)
            res.update(upstream=f'pypi:{module}', current=tags['Version'],
                       latest=pypi_latest(module))
        else:
            if not repo:
                return {**res, 'status': 'skipped',
                        'note': 'cannot derive an upstream git repo'}
            res['upstream'] = repo
            used = [c for c in commits.values() if c in src0]
            if not src0 and len(set(commits.values())) == 1:
                used = list(commits.values())      # metapackage, no Source0
            if used:                                   # commit-pinned
                res.update(kind='commit', current=used[0],
                           latest=head_commit(repo, o.get('branch')))
            else:                                      # tag/release
                rname = os.path.basename(repo)
                rname = rname[:-4] if rname.endswith('.git') else rname
                prefixes = [o['tag_prefix']] if 'tag_prefix' in o else \
                    ['v', 'V', '', f'{pkg}-', f'{rname}-']
                res.update(current=tags['Version'],
                           latest=latest_tag(repo, prefixes))
        if res['kind'] == 'commit':
            res['outdated'] = res['current'] != res['latest']
        else:
            res['outdated'] = vkey(res['latest']) > vkey(res['current'])
        # other commit-pinned sources -> informational only
        for k, src in sources.items():
            if k == 'Source0':
                continue
            for c in commits.values():
                if c in src:
                    r2 = repo_from_url(src)
                    if r2:
                        try:
                            h = head_commit(r2)
                            if h != c:
                                res['info'].append(
                                    f'{k}: pinned {c[:7]} but {r2} HEAD is {h[:7]}')
                        except Exception as e:
                            res['info'].append(f'{k}: {e}')
    except Exception as e:
        return {**res, 'status': 'error', 'note': str(e)}
    return res


def short(r, v):
    return v[:7] if r['kind'] == 'commit' else v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--specs', default='specs')
    ap.add_argument('--config', default='scripts/update-check.json')
    ap.add_argument('--only', nargs='*')
    ap.add_argument('--json'); ap.add_argument('--markdown')
    ap.add_argument('--fail-on-outdated', action='store_true')
    a = ap.parse_args()
    cfg = json.load(open(a.config)) if os.path.exists(a.config) else {}
    pkgs = sorted(d for d in os.listdir(a.specs)
                  if os.path.isfile(f'{a.specs}/{d}/{d}.spec'))
    if a.only:
        pkgs = [p for p in pkgs if p in a.only]
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(lambda p: check(p, a.specs, cfg), pkgs))

    # group commit-pinned packages that share an upstream commit (astal-*)
    outdated = [r for r in results if r.get('outdated')]
    errors = [r for r in results if r['status'] == 'error']
    groups = {}
    for r in outdated:
        groups.setdefault((r['upstream'], r['current'], r['latest']),
                          []).append(r)

    md = ['## Upstream update check', '']
    if groups:
        md += ['| Package(s) | Type | In spec | Upstream |', '|---|---|---|---|']
        for (up, cur, lat), rs in groups.items():
            r = rs[0]
            md.append(f"| {', '.join(x['package'] for x in rs)} | {r['kind']} "
                      f"| `{short(r, cur)}` | `{short(r, lat)}` |")
    else:
        md.append('All checked packages are up to date.')
    notes = [f"- `{r['package']}`: {i}" for r in results for i in r['info']]
    if notes:
        md += ['', '### Pinned dependency commits (informational)'] + notes
    if errors:
        md += ['', '### Could not check'] + \
              [f"- `{r['package']}`: {r['note']}" for r in errors]
    skipped = [r for r in results if r['status'] == 'skipped']
    if skipped:
        md += ['', '### Skipped'] + \
              [f"- `{r['package']}`: {r['note']}" for r in skipped]
    text = '\n'.join(md) + '\n'
    print(text)
    if a.markdown:
        open(a.markdown, 'w').write(text)
    if a.json:
        json.dump({'outdated': [r['package'] for r in outdated],
                   'results': results}, open(a.json, 'w'), indent=2)
    gh = os.environ.get('GITHUB_OUTPUT')
    if gh:
        with open(gh, 'a') as f:
            f.write(f"count={len(outdated)}\n")
            f.write("packages=" + ' '.join(r['package'] for r in outdated) + "\n")
    sys.exit(1 if a.fail_on_outdated and outdated else 0)


if __name__ == '__main__':
    main()
