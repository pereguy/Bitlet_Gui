# -*- mode: python -*-
# vim: ft=python

import sys


sys.setrecursionlimit(5000)  # required on Windows


a = Analysis(
    ['main.py'],
    pathex=['bitlet'],
    binaries=[],
    datas=[
        ('Icons/*', 'Icons/')
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
)
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='Bitlet',
    debug=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    icon='Icons\icon.ico',
)
app = BUNDLE(
    exe,
    icon='Icons\icon.ico',
    bundle_identifier=None,
    info_plist={'NSHighResolutionCapable': 'True'},
)