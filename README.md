<img width="2404" height="1660" alt="image" src="https://github.com/user-attachments/assets/11f27ee8-7756-4720-a41d-e0037f0b97d3" />## MC Datapack Translator Tool

A cross-platform desktop tool for **batch-translating all localisable text inside Minecraft Java Edition datapacks** (`.zip`).

- Extracts every translatable string from  
  – JSON files (`text`, `title`, `subtitle`, `description`, `name`, `displayName` …)  
  – `.mcfunction` files (`tellraw`, `title`, `bossbar`, `team`, `scoreboard`, `item`, `execute` …)  
- Shows everything in a table – edit translations directly or paste from CAT tools  
- Writes the translations back into a **new datapack** (`*_translated.zip`) without touching the original  
- Drag-&-drop, recent-files, bilingual UI (zh-CN / en-US), dark / light theme, remembers your settings

---

## Quick Start

1. Install Python ≥ 3.9 (or grab the ready-made Windows exe in [Releases](https://github.com/yourname/yourrepo/releases)).  
2. Run  
   ```bash
   python MCDatapackTranslator.py
   ```
3. Drag a datapack into the window → all translatable lines appear.  
4. Fill the “译文 / Translation” column.  
5. Click “保存翻译 / Save Translation” → a new `*_translated.zip` is created next to the original.  
6. Put the new zip into your `saves/<world>/datapacks` folder, done.

---

## Screenshots

| Dark theme | Light theme |
|------------|-------------|
| <img width="2404" height="1660" alt="image" src="https://github.com/user-attachments/assets/9e3076cb-faad-4710-90ca-b8195de5a31b" />|<img width="2404" height="1660" alt="image" src="https://github.com/user-attachments/assets/5f842375-a352-40bb-bed8-239dbc415c59" />   
|            | 

---

## Features

| | |
|-|-|
| **Full coverage** | JSON text components & every major text-bearing command |
| **Namespace filter** | Hide vanilla (`minecraft:`) entries with one click |
| **Field picker** | Choose which JSON keys / command types you want to see |
| **Conflict-safe** | Original file stays intact; new zip is written atomically |
| **Portable** | Single folder, no external dependencies (PyQt6 bundled in exe) |
| **Extensible** | Add new languages by dropping `<lang>.json` into `langs/` |

---

## File Layout

```
MCDatapackTranslator/
├─ main.py   # main script
├─ Style.py                   # QSS themes
├─ langs/                     # UI translations
│  ├─ zh_CN.json
│  └─ en_US.json
├─ icon.ico
└─ README.md                  # this file
```

---

## Building from Source

```bash
# 1. Clone
git clone https://github.com/BiliBiliACEGE/Minecraft-DataPack-Translation-Tool.git
cd Minecraft-DataPack-Translation-Tool

# 2. Create venv (optional but recommended)
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS / Linux

# 3. Install deps
pip install -r requirements.txt
# requirements.txt:
#   PyQt6>=6.4
#   pywinstyles>=1.8   # Windows only, optional

# 4. Run
python MCDatapackTranslator.py

# 5. Build standalone exe (Windows)
pyinstaller -F -w -i icon.ico --add-data "langs;langs" MCDatapackTranslator.py
```

---

## Language Files

UI language is detected in this order:  
1. User choice (saved in `QSettings`)  
2. System locale  
3. Fallback `zh_CN`

To add a new language:  
1. Copy `langs/en_US.json` → `langs/<code>.json`  
2. Translate the values (keep the keys untouched)  
3. Restart the program – the new language appears in Settings.

---

## Datapack Compatibility

| Minecraft version | JSON format | Commands | Status |
|-------------------|-------------|----------|--------|
| 1.13 – 1.20.4     | ✅          | ✅       | Fully tested |
| 1.20.5+           | expected to work (report issues) |

---

## Contributing

Pull-requests welcome – especially:  
- More command parsers (`/data`, `/dialogue`, …)  
- Extra UI languages  
- macOS / Linux cosmetic fixes

---

## License

MIT – do whatever you want, just keep the copyright line.

---

## Author

Ace · [GitHub](https://github.com/BiliBiliACEGE) · [Email](mailto:BiliBiliACEGE-Github@outlook.com)
