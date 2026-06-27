import re

# Polyfill to add at the top of main.tsx
polyfill = """// Polyfill crypto.randomUUID for non-secure HTTP contexts (LAN access)
if (typeof crypto !== 'undefined' && typeof crypto.randomUUID !== 'function') {
  (crypto as any).randomUUID = function(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    }) as `${string}-${string}-${string}-${string}-${string}`;
  };
}

"""

main_path = '/DATA/AppData/.openjarvis/src/frontend/src/main.tsx'

with open(main_path, 'r') as f:
    content = f.read()

if 'randomUUID' not in content:
    # Insert polyfill at the very beginning
    content = polyfill + content
    with open(main_path, 'w') as f:
        f.write(content)
    print('POLYFILL_ADDED')
else:
    print('ALREADY_PATCHED')
