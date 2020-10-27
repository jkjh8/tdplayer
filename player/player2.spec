# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['player.py'],
             pathex=["C:/Program Files/VideoLAN/VLC/"],
             binaries=[("C:/Program Files/VideoLAN/VLC/plugins/*", "plugins")],
             datas=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries + [("libVLC.dll", "C:/Program Files/VideoLAN/VLC/libvlc.dll", "BINARY")],
          a.zipfiles,
          a.datas,
          [],
          name='player',
          debug=False,
          bootloader_ignore_signals=True,
          strip=False,
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False, icon="favicon_player.ico" )
