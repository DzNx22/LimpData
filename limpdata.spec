# -*- mode: python ; coding: utf-8 -*-
# Serve para gerar o .exe direto pelo github actions
# Gera o executável do Windows: pyinstaller limpdata.spec (ou .\build.ps1)

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    # Fontes, ícones e logo usados pela interface.
    datas=[("limpdata/gui/assets", "limpdata/gui/assets")],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    # Módulos não usados pelo app, excluídos para reduzir o tamanho.
    excludes=["tkinter", "unittest", "pytest", "PySide6.QtNetwork"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="LimpData",
    debug=False,
    strip=False,
    upx=False,
    console=False,  # aplicativo de janela, sem terminal
    icon="limpdata/gui/assets/limpdata.ico",
)
