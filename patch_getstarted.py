import re

path = '/DATA/AppData/.openjarvis/src/frontend/src/pages/GetStartedPage.tsx'

with open(path, 'r') as f:
    content = f.read()

old = "function detectContext(): DeployContext {\n  if (isTauri()) return 'desktop';\n  const host = window.location.hostname;\n  if (host === 'localhost' || host === '127.0.0.1' || host === '0.0.0.0') {\n    return 'selfhosted';\n  }\n  return 'hosted';\n}"

new = "function detectContext(): DeployContext {\n  if (isTauri()) return 'desktop';\n  const host = window.location.hostname;\n  const isPrivate = host === 'localhost' || host === '127.0.0.1' || host === '0.0.0.0' || host.startsWith('192.168.') || host.startsWith('10.') || (host.startsWith('172.') && parseInt(host.split('.')[1]) >= 16 && parseInt(host.split('.')[1]) <= 31);\n  if (isPrivate) return 'selfhosted';\n  return 'hosted';\n}"

if old in content:
    content = content.replace(old, new)
    with open(path, 'w') as f:
        f.write(content)
    print('PATCH_OK')
else:
    print('NOT_FOUND - current detectContext:')
    import re
    m = re.search(r'function detectContext\(\).*?\}', content, re.DOTALL)
    if m:
        print(repr(m.group(0)[:500]))
