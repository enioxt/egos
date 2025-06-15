---
description: Standard for Building Stand-Alone Windows GUI Applications (EGOS)
version: 1.0.0
last_updated: 2025-06-12
---

@references:
  - docs/standards/windows_gui_app_standard.md

# EGOS Standard – Windows GUI Application Blueprint ("Pochete-Style")

> This document captures the reusable patterns distilled from **Pochete 2.0** and defines a repeatable methodology for shipping stand-alone Windows desktop applications with a Python/Tkinter front-end and embedded FFmpeg back-end.  Follow this standard whenever creating a new desktop tool inside the EGOS workspace.

## 1.  Purpose & Scope  

Establish a **consistent, secure and maintainable** approach for:

* Developing GUI apps with Python 3.9+ & Tkinter.
* Embedding external binaries (e.g. `ffmpeg.exe`, `ffprobe.exe`).
* Packaging everything into a single `.exe` via PyInstaller.
* Delivering signed, user-friendly releases that run on Windows 7+ with **zero external dependencies**.

## 2.  Directory Layout

```
MyApp/
 ├─ .git/                  # VCS metadata
 ├─ build/                 # PyInstaller working dir (ignored)
 ├─ dist/                  # Final .exe output (ignored)
 ├─ ffmpeg/                # Embedded binaries or other external tools
 ├─ src/
 │   └─ gui_my_app.py      # Main Tkinter application
 ├─ assets/
 │   └─ favicon.ico        # App icon (32×32, 256-colour)
 ├─ docs/
 │   └─ ...                # Markdown docs / standards / roadmap
 ├─ MyApp.spec             # Custom PyInstaller spec
 ├─ requirements.txt       # Pin minimal deps (keep tiny!)
 ├─ CHANGELOG.md
 ├─ README.md              # End-user guide (English)
 ├─ LEIAME.md              # End-user guide (Português)
 └─ ROADMAP.md
```

## 3.  Coding Guidelines

| Area | Rule |
|------|------|
| **Imports** | Standard-library first. Use `from pathlib import Path` for paths. |
| **GUI** | Use **ttk** widgets.  Base colour `#f0f0f0`; accent `#4a6ea9`.  Default font “Segoe UI 10”. |
| **Window Sizing** | Call `_center_window(w, h)` helper; ensure pop-ups fit longest blockchain address (≈ 55 chars). |
| **Buttons** | Width `10`, padding `(5, 0)`.  Provide keyboard focus traversal. |
| **Copy Feedback** | After copying to clipboard, show `messagebox.showinfo("Copiado", ...)`. |
| **Threading** | Use `threading.Lock` when sharing the `subprocess.Popen` handle. |
| **FFmpeg Detection** | ```python
if getattr(sys,'frozen',False):

    base = Path(sys._MEIPASS)
else:
    base = Path(**file**).parent
ffmpeg_path = next(p for p in [ base/'ffmpeg/ffmpeg.exe', base/'ffmpeg.exe', Path('ffmpeg.exe') ] if p.exists())

``` |

## 4.  Packaging Workflow (PyInstaller)
1. `python -m venv venv && venv\Scripts\activate`
2. `pip install -r requirements.txt pyinstaller==6.14.0`
3. Create **spec** file (template provided below).  Key items:
   * `datas=[('ffmpeg/*', 'ffmpeg')]`
   * `hiddenimports=['tkinter','tkinter.ttk']`.
   * `icon='assets/favicon.ico'`.
4. Build: `pyinstaller --noconfirm MyApp.spec`.
5. Verify `dist/MyApp.exe` runs on host.

### `MyApp.spec` skeleton
```python
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None

a = Analysis(['src/gui_my_app.py'],
             datas=[('ffmpeg/*', 'ffmpeg')],
             hiddenimports=['tkinter','tkinter.ttk'],
             ...)
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)
exe = EXE(pyz, a.scripts,
          icon='assets/favicon.ico',
          name='MyApp',
          console=False)
```

## 5.  Post-Build Validation

* Launch `.exe` from a **clean** PowerShell where `%PATH%` lacks FFmpeg.

* Click through every mode, verify progress log, cancel button, and copy-to-clipboard dialogs.
* Run on a fresh Windows VM if possible.

## 6.  Optional Code-Signing

| Step | Command |
|------|---------|
| Purchase code-signing cert (DigiCert, GlobalSign…). | — |
| Sign | `signtool sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 /f cert.pfx /p pass dist\MyApp.exe` |

## 7.  Release Checklist

1. Bump version in `CHANGELOG.md`.
2. Tag: `git tag v1.0.0 && git push --tags`.
3. GitHub → **Releases** → Upload `.exe`.
4. Copy release notes (English + Portuguese).

## 8.  EGOS Integration Requirements

* Follow `RULE-OPS-CHECKLIST-001` at session start.

* Store standards in `docs/standards/`.
* Every new desktop project must include a link to this standard in its README.

## 9.  Template Repository

For rapid bootstrap run:

```bash
npx degit enioxt/egos-desktop-template MyNewApp
```

(The template repository contains the layout above and a starter `gui_my_app.py`.)

---
**Maintainer:** @enioxt

> _“Build once, run everywhere – flawlessly.”_  – EGOS Desktop Standards v1.0