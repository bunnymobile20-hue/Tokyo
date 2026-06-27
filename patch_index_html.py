path = '/DATA/AppData/.openjarvis/src/frontend/index.html'

with open(path, 'r') as f:
    content = f.read()

polyfill_script = """  <script>
    // Polyfill crypto.randomUUID for HTTP (non-secure) contexts like LAN access
    if (typeof crypto === 'undefined' || typeof crypto.randomUUID !== 'function') {
      var _crypto = typeof crypto !== 'undefined' ? crypto : {};
      _crypto.randomUUID = function() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
          var r = Math.random() * 16 | 0;
          var v = c === 'x' ? r : (r & 0x3 | 0x8);
          return v.toString(16);
        });
      };
      if (typeof crypto === 'undefined') { window.crypto = _crypto; }
    }
  </script>
"""

if 'randomUUID polyfill' in content or 'crypto.randomUUID = function' in content:
    print('ALREADY_PATCHED')
elif '<head>' in content:
    content = content.replace('<head>', '<head>\n' + polyfill_script, 1)
    with open(path, 'w') as f:
        f.write(content)
    print('PATCH_OK')
else:
    print('HEAD_NOT_FOUND')
    print(repr(content[:200]))
