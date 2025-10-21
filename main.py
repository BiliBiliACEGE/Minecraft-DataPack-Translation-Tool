import json, re, zipfile, os, sys, pathlib, shutil
from typing import List, Dict, Union

# -------------------- Fluent --------------------
from qfluentwidgets import (setTheme, Theme, setThemeColor,
                            PrimaryPushButton, PushButton, TableWidget, CheckBox,
                            ComboBox, CaptionLabel, MessageBox, Dialog, SubtitleLabel,
                            FluentIcon as FI)
# -------------------- PyQt6 --------------------
from PyQt6.QtWidgets import (QApplication,QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QHeaderView, QLabel, QFileDialog, QMenuBar, QMenu,QDialog,
                            QDialogButtonBox, QSplitter,QTableWidgetItem)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings, QStandardPaths
from PyQt6.QtGui import QIcon, QKeySequence as QKS,QAction, QKeySequence

# -------------------- 多语言 --------------------
def get_lang_dir() -> "pathlib.Path":
    if getattr(sys, 'frozen', False):
        base = pathlib.Path(sys._MEIPASS)
    else:
        base = pathlib.Path(__file__).parent
    built_in = base / "langs"
    if built_in.exists() and any(built_in.glob("*.json")):
        return built_in
    config = pathlib.Path(QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppConfigLocation)) / "MCDatapackTranslator"
    config.mkdir(parents=True, exist_ok=True)
    dest = config / "langs"
    dest.mkdir(exist_ok=True)
    zh_cn = dest / "zh_CN.json"
    if not zh_cn.exists():
        zh_cn.write_text(json.dumps({
            "app_title": "MC 数据包翻译工具",
            "lang_name": "中文",
            "menu_file": "文件",
            "menu_open": "打开数据包",
            "menu_exit": "退出",
            "menu_edit": "编辑",
            "menu_settings": "设置",
            "menu_help": "帮助",
            "menu_about": "关于",
            "col_file": "文件",
            "col_path": "路径/行号",
            "col_source": "原文",
            "col_trans": "译文",
            "setting_show_vanilla": "显示原版命名空间(minecraft:)",
            "setting_lang": "界面语言",
            "btn_load": "加载数据包",
            "btn_save": "保存翻译",
            "btn_theme": "切换主题",
            "json_field": "JSON 字段",
            "mcfunction_command": "MCFunction 命令",
            "status_ready": "拖拽数据包到窗口即可开始",
            "status_parsing": "解析中…",
            "status_done": "解析完成，共 {} 条可翻译文本",
            "tip": "提示",
            "close_current": "关闭当前文件",
            "not_opened": "尚未打开任何数据包",
            "S_Closed": "已关闭数据包",
            "recent_files": "最近打开",
            "empty": "无",
            "file_no_longer_exists\n{}": "文件不存在\n{}",
            "save_ok": "已保存为\n{}",
            "about_text": "MC 数据包翻译工具\n支持全版本 Java 版数据包\n作者：Ace"
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    return dest

LANG_PATH = get_lang_dir()
DEFAULT_LANG = "zh_CN"

class Translator:
    def __init__(self, lang: str = DEFAULT_LANG):
        self.lang = lang
        self._data = {}
        self.load(lang)
    def load(self, lang: str):
        file = LANG_PATH / f"{lang}.json"
        if file.exists():
            self._data = json.loads(file.read_text(encoding="utf-8"))
    def tr(self, key: str, **kwargs) -> str:
        txt = self._data.get(key, key)
        if kwargs:
            txt = txt.format(**kwargs)
        return txt

translator = Translator(DEFAULT_LANG)
tr = translator.tr

# -------------------- 数据 --------------------
class Entry:
    def __init__(self, file: str, text: str, path: str, cmd: str = None):
        self.file = file
        self.text = text
        self.path = path
        self.cmd = cmd
        self.translated = ""
    def key(self):
        return (self.file, self.path)

JSON_FIELDS = ["text", "title", "subtitle", "description", "name", "displayName"]
COMMAND_FIELDS = {
    "tellraw": ["text"],
    "title": ["title", "subtitle", "actionbar"],
    "bossbar": ["name"],
    "team": ["displayName", "prefix", "suffix"],
    "scoreboard": ["objective.displayName"],
    "item": ["Name", "Lore[]"],
    "execute": ["run.title", "run.tellraw", "run.bossbar", "run.team", "run.scoreboard", "run.item"],
}
COMMAND_TYPES = list(COMMAND_FIELDS.keys())

# -------------------- JSON 抽取 --------------------
def extract_json_entries(z: zipfile.ZipFile, name: str, wanted: set) -> List[Entry]:
    entries = []
    def walk(node, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in wanted:
                    if isinstance(v, str):
                        entries.append(Entry(name, v, f"{path}.{k}" if path else k))
                    elif isinstance(v, list) and all(isinstance(i, str) for i in v):
                        for idx, s in enumerate(v):
                            entries.append(Entry(name, s, f"{path}.{k}[{idx}]" if path else f"{k}[{idx}]"))
                    else:
                        walk(v, f"{path}.{k}" if path else k)
                else:
                    walk(v, f"{path}.{k}" if path else k)
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                walk(item, f"{path}[{idx}]" if path else f"[{idx}]")
    try:
        data = json.loads(z.read(name).decode("utf-8"))
        walk(data)
    except Exception as e:
        print("JSON fail:", name, e)
    return entries

# -------------------- mcfunction 抽取 --------------------
RE_CMD = re.compile(r"^((execute )?)(tellraw|title|bossbar|team|scoreboard|item)\b(.*)", re.IGNORECASE)

def extract_outer_json(s: str) -> str:
    start = s.find("{")
    if start == -1: return ""
    stack = []
    for i in range(start, len(s)):
        if s[i] == "{":
            stack.append("{")
        elif s[i] == "}":
            if stack:
                stack.pop()
                if not stack:
                    return s[start:i+1]
    return ""

def parse_mcfunction(z: zipfile.ZipFile, name: str, wanted: set) -> List[Entry]:
    entries = []
    try:
        content = z.read(name).decode("utf-8")
    except: return entries
    for lineno, rawline in enumerate(content.splitlines(), 1):
        line = rawline.strip()
        if not line or line.startswith("#"): continue
        m = RE_CMD.match(line)
        if not m: continue
        base = m.group(3)
        if base not in wanted: continue
        args = m.group(4).strip()
        json_str = extract_outer_json(args)
        if not json_str: continue
        try:
            obj = json.loads(json_str)
        except: continue
        def walk(node, p=""):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == "run" and isinstance(v, dict):
                        walk(v, f"{p}.run" if p else "run")
                        continue
                    if k in ("text", "title", "subtitle", "actionbar", "Name") and isinstance(v, str):
                        entries.append(Entry(name, v, f"line{lineno}{p}.{k}", base))
                    elif k == "Lore" and isinstance(v, list):
                        for idx, lore in enumerate(v):
                            if isinstance(lore, str):
                                entries.append(Entry(name, lore, f"line{lineno}{p}.{k}[{idx}]", base))
                    elif isinstance(v, (dict, list)):
                        walk(v, f"{p}.{k}" if p else k)
            elif isinstance(node, list):
                for idx, item in enumerate(node):
                    walk(item, f"{p}[{idx}]" if p else f"[{idx}]")
        walk(obj)
    return entries

# -------------------- 回写 --------------------
def build_translated_zip(zin: zipfile.ZipFile, entries: List[Entry], out: str):
    mapping = {e.key(): e for e in entries if e.translated}
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info)
            if info.filename.endswith(".json") and any(e.file == info.filename for e in entries):
                try:
                    obj = json.loads(data.decode("utf-8"))
                    apply_json_translation(obj, mapping, info.filename)
                    data = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                except: pass
            elif info.filename.endswith(".mcfunction") and any(e.file == info.filename for e in entries):
                data = apply_mcfunction_translation(data.decode("utf-8"), mapping, info.filename).encode("utf-8")
            zout.writestr(info, data)

def apply_json_translation(obj, mapping, fname):
    def walk(node, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in JSON_FIELDS:
                    if isinstance(v, str):
                        ent = mapping.get((fname, path + f".{k}"))
                        if ent: node[k] = ent.translated
                    elif isinstance(v, list) and all(isinstance(i, str) for i in v):
                        for idx, s in enumerate(v):
                            ent = mapping.get((fname, path + f".{k}[{idx}]"))
                            if ent: v[idx] = ent.translated
                    else:
                        walk(v, path + f".{k}")
                else:
                    walk(v, path + f".{k}")
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                walk(item, f"{path}[{idx}]")
    walk(obj)

def apply_mcfunction_translation(content: str, mapping, fname):
    lines = content.splitlines()
    entries = [e for e in mapping.values() if e.file == fname and e.translated]
    for e in entries:
        m = re.search(r"line(\d+)", e.path)
        if not m: continue
        lineno = int(m.group(1)) - 1
        if not (0 <= lineno < len(lines)): continue
        line = lines[lineno]
        old_json = extract_outer_json(line)
        if not old_json: continue
        try:
            obj = json.loads(old_json)
        except: continue
        def set_nested(node, path_parts, new_val):
            cur = node
            for part in path_parts[:-1]:
                if isinstance(cur, dict) and part in cur:
                    cur = cur[part]
                elif isinstance(cur, list) and part.isdigit():
                    cur = cur[int(part)]
                else:
                    return
            last = path_parts[-1]
            if isinstance(cur, dict) and last in cur and isinstance(cur[last], str):
                cur[last] = new_val
            elif isinstance(cur, list) and last.isdigit() and isinstance(cur[int(last)], str):
                cur[int(last)] = new_val
        path_suffix = e.path.split(".", 1)[1] if "." in e.path else ""
        path_parts = path_suffix.split(".")
        m_idx = re.search(r"\[(\d+)\]\.text", e.path)
        if m_idx:
            idx = int(m_idx.group(1))
            if isinstance(obj, list) and 0 <= idx < len(obj) and obj[idx].get("text") == e.text:
                obj[idx]["text"] = e.translated
                new_json = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
                lines[lineno] = line.replace(old_json, new_json)
                continue
        if path_parts and path_parts[-1] in ("text", "title", "subtitle", "actionbar"):
            set_nested(obj, path_parts, e.translated)
            new_json = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
            lines[lineno] = line.replace(old_json, new_json)
    return "\n".join(lines)

class ParseWorker(QThread):
    parsed = pyqtSignal(list)
    def __init__(self, zpath, jf, cf):
        super().__init__()
        self.zpath = zpath
        self.jf = jf
        self.cf = cf
    def run(self):
        entries = []
        with zipfile.ZipFile(self.zpath, "r") as z:
            for name in z.namelist():
                if name.endswith(".json"):
                    entries.extend(extract_json_entries(z, name, self.jf))
                elif name.endswith(".mcfunction"):
                    entries.extend(parse_mcfunction(z, name, self.cf))
        self.parsed.emit(entries)

# -------------------- 设置 --------------------
class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("menu_settings"))
        self.setFixedSize(800, 380)
        self.lang_name_map = {"zh_CN": "中文", "en_US": "English"}
        self.cmb_lang = ComboBox()
        self.lang_map = {f.stem: f for f in LANG_PATH.glob("*.json")}
        for k in self.lang_map.keys():
            self.cmb_lang.addItem(self.lang_name_map.get(k, k), k)
        self.cmb_lang.setCurrentText(self.lang_name_map.get(parent.cur_lang, parent.cur_lang))
        self.chk_vanilla = CheckBox(tr("setting_show_vanilla"))
        self.chk_vanilla.setChecked(parent.show_vanilla)
        self.json_checks = {f: CheckBox(f) for f in JSON_FIELDS}
        for f in JSON_FIELDS:
            self.json_checks[f].setChecked(f in parent.json_fields)
        self.cmd_checks = {c: CheckBox(c) for c in COMMAND_TYPES}
        for c in COMMAND_TYPES:
            self.cmd_checks[c].setChecked(c in parent.cmd_types)
        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn.accepted.connect(self.accept)
        btn.rejected.connect(self.reject)
        v = QVBoxLayout(self)
        v.addWidget(SubtitleLabel(tr("setting_lang")))
        v.addWidget(self.cmb_lang)
        v.addWidget(self.chk_vanilla)
        v.addWidget(SubtitleLabel(tr("json_field")))
        json_grid = QHBoxLayout()
        for chk in self.json_checks.values():
            json_grid.addWidget(chk)
        v.addLayout(json_grid)
        v.addWidget(SubtitleLabel(tr("mcfunction_command")))
        cmd_grid = QHBoxLayout()
        for chk in self.cmd_checks.values():
            cmd_grid.addWidget(chk)
        v.addLayout(cmd_grid)
        v.addWidget(btn)
    def current_data(self):
        return "zh_CN" if self.cmb_lang.currentText() == "中文" else "en_US"

# -------------------- 主窗口 --------------------
class MainWindow(QMainWindow):
    restartSignal = pyqtSignal()
    RECENT_MAX = 5
    def __init__(self):
        self.json_fields = set(JSON_FIELDS)
        self.cmd_types = set(COMMAND_TYPES)
        super().__init__()
        self.setWindowIcon(QIcon("icon.ico"))
        self.restartSignal.connect(self._restart)
        self.settings = QSettings("Ace", "MCDatapackTranslator")
        self.recent_files = self.settings.value("recent", [], type=list)
        self.cur_lang = self.settings.value("language", DEFAULT_LANG, type=str)
        self.setWindowTitle(tr("app_title"))
        self.resize(1200, 800)
        self.setAcceptDrops(True)
        self.show_vanilla = True
        self.cur_lang = DEFAULT_LANG
        self.trans = Translator(self.cur_lang)
        self.table = TableWidget()
        self.table.setColumnCount(4)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels([tr("col_file"), tr("col_path"), tr("col_source"), tr("col_trans")])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(TableWidget.EditTrigger.DoubleClicked)
        self.table.itemChanged.connect(self.on_cell_change)
        self.btn_load = PrimaryPushButton(tr("btn_load"))
        self.btn_save = PrimaryPushButton(tr("btn_save"))
        self.btn_theme = PushButton(tr("btn_theme"))
        self.status = CaptionLabel(tr("status_ready"))
        top = QHBoxLayout()
        top.addWidget(self.btn_load)
        top.addWidget(self.btn_save)
        top.addWidget(self.btn_theme)
        top.addStretch()
        top.addWidget(self.status)
        right = QVBoxLayout()
        right.addLayout(top)
        right.addWidget(self.table)
        central = QWidget()
        central.setLayout(right)
        self.setCentralWidget(central)
        self.build_menu()
        self.btn_load.clicked.connect(self.load_dp)
        self.btn_save.clicked.connect(self.save_dp)
        self.btn_theme.clicked.connect(self.toggle_theme)
        self.entries: List[Entry] = []
        self.zpath = ""
        self.dark = True
        self._update_theme_icon() 
        self.dark = self.settings.value("dark_theme", True, type=bool)   
        setTheme(Theme.DARK if self.dark else Theme.LIGHT)               
        setThemeColor("#0078d4")

    def build_menu(self):
        bar = self.menuBar()
        file_menu = bar.addMenu(tr("menu_file"))
        open_act = QAction(tr("menu_open"), self)
        open_act.setShortcut(QKS("Ctrl+O"))
        open_act.triggered.connect(self.load_dp)
        file_menu.addAction(open_act)
        self.recent_menu = QMenu(tr("recent_files"), self)
        file_menu.addMenu(self.recent_menu)
        self.update_recent_menu()
        file_menu.addSeparator()
        close_act = QAction(tr("close_current"), self)
        close_act.triggered.connect(self.close_current)
        file_menu.addAction(close_act)
        exit_act = QAction(tr("menu_exit"), self)
        exit_act.setShortcut(QKS("Ctrl+Q"))
        exit_act.triggered.connect(self.close)
        file_menu.addAction(exit_act)
        edit_menu = bar.addMenu(tr("menu_edit"))
        set_act = QAction(tr("menu_settings"), self)
        set_act.setShortcut(QKS("Ctrl+,"))
        set_act.triggered.connect(self.open_settings)
        edit_menu.addAction(set_act)
        help_menu = bar.addMenu(tr("menu_help"))
        about_act = QAction(tr("menu_about"), self)
        about_act.triggered.connect(self.about)
        help_menu.addAction(about_act)

    def _restart(self):
        self.close()
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, self._spawnNew)
    def _spawnNew(self):
        w = MainWindow()
        w.show()

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.show_vanilla = dlg.chk_vanilla.isChecked()
            self.json_fields = {f for f, chk in dlg.json_checks.items() if chk.isChecked()}
            self.cmd_types   = {c for c, chk in dlg.cmd_checks.items() if chk.isChecked()}

            new_lang = dlg.current_data()
            if new_lang != self.cur_lang:
                self.cur_lang = new_lang
                translator.load(new_lang)
                global tr
                tr = translator.tr
                self.retranslate_ui()
                self.settings.setValue("language", self.cur_lang)

            if self.zpath:         
                self.run_parse()

    def retranslate_ui(self):
        self.setWindowTitle(tr("app_title"))
        self.btn_load.setText(tr("btn_load"))
        self.btn_save.setText(tr("btn_save"))
        self.status.setText(tr("status_ready"))
        self.btn_theme.setText(tr("btn_theme"))
        self.table.setHorizontalHeaderLabels([tr("col_file"), tr("col_path"), tr("col_source"), tr("col_trans")])
        self.menuBar().clear()
        self.build_menu()

    def about(self):
        MessageBox(self, tr("menu_about"), tr("about_text"), self).exec()

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
    def dropEvent(self, e):
        f = e.mimeData().urls()[0].toLocalFile()
        if f.lower().endswith(".zip"):
            self.zpath = f
            self.run_parse()
    def load_dp(self):
        f, _ = QFileDialog.getOpenFileName(self, tr("menu_open"), filter="*.zip")
        if f:
            self.zpath = f
            self.run_parse()
    def run_parse(self):
        jf = self.json_fields
        cf = self.cmd_types
        self.status.setText(tr("status_parsing"))
        self.worker = ParseWorker(self.zpath, jf, cf)
        self.worker.parsed.connect(self.on_parsed)
        self.worker.start()
    def on_parsed(self, entries: List[Entry]):
        if not self.show_vanilla:
            entries = [e for e in entries if not e.file.startswith("minecraft/")]
        self.entries = entries
        self.status.setText(tr("status_done").format(len(entries)))
        self.populate_table()
        self.add_recent(self.zpath)
    def populate_table(self):
        self.table.setRowCount(len(self.entries))
        self.table.verticalHeader().setVisible(False)
        for i, e in enumerate(self.entries):
            self.table.setItem(i, 0, QTableWidgetItem(e.file))
            self.table.setItem(i, 1, QTableWidgetItem(e.path))
            self.table.setItem(i, 2, QTableWidgetItem(e.text))
            self.table.setItem(i, 3, QTableWidgetItem(""))
            self.table.item(i, 2).setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.item(i, 0).setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.item(i, 1).setFlags(Qt.ItemFlag.ItemIsEnabled)
    def on_cell_change(self, item):
        if item.column() == 3:
            self.entries[item.row()].translated = item.text().strip()
    def save_dp(self):
        if not self.zpath or not self.entries:
            return
        out = self.zpath.replace(".zip", "_translated.zip")
        with zipfile.ZipFile(self.zpath, "r") as zin:
            build_translated_zip(zin, self.entries, out)
        MessageBox(self, "Done", tr("save_ok").format(out), self).exec()
    def toggle_theme(self):
        self.dark = not self.dark
        setTheme(Theme.DARK if self.dark else Theme.LIGHT)
        self.settings.setValue("dark_theme", self.dark)
        self._update_theme_icon()
    def _update_theme_icon(self):
        self.btn_theme.setIcon(FI.CONSTRACT)
    def update_recent_menu(self):
        self.recent_menu.clear()
        if not self.recent_files:
            self.recent_menu.addAction(tr("empty")).setEnabled(False)
            return
        for path in self.recent_files:
            act = QAction(path, self)
            act.triggered.connect(lambda _, p=path: self.load_recent(p))
            self.recent_menu.addAction(act)
    def load_recent(self, path):
        if pathlib.Path(path).exists():
            self.zpath = path
            self.run_parse()
            self.add_recent(path)
        else:
            MessageBox(self, tr("tip"), tr("file_no_longer_exists\n{}").format(path), self).exec()
            self.recent_files.remove(path)
            self.update_recent_menu()
            self.settings.setValue("recent", self.recent_files)
    def add_recent(self, path):
        if path in self.recent_files:
            self.recent_files.remove(path)
        self.recent_files.insert(0, path)
        self.recent_files = self.recent_files[:self.RECENT_MAX]
        self.settings.setValue("recent", self.recent_files)
        self.update_recent_menu()
    def close_current(self):
        if not self.zpath:
            MessageBox(self, tr("tip"), tr("not_opened"), self).exec()
            return
        self.table.setRowCount(0)
        self.entries.clear()
        self.zpath = ""
        self.status.setText(tr("S_Closed"))

# -------------------- 启动入口 --------------------
if __name__ == "__main__":
    LANG_PATH.mkdir(parents=True, exist_ok=True)
    # 生成默认语言文件
    for lang, data in [("zh_CN", {
        "app_title": "MC 数据包翻译工具",
        "lang_name": "中文",
        "menu_file": "文件",
        "menu_open": "打开数据包",
        "menu_exit": "退出",
        "menu_edit": "编辑",
        "menu_settings": "设置",
        "menu_help": "帮助",
        "menu_about": "关于",
        "col_file": "文件",
        "col_path": "路径/行号",
        "col_source": "原文",
        "col_trans": "译文",
        "setting_show_vanilla": "显示原版命名空间(minecraft:)",
        "setting_lang": "界面语言",
        "btn_load": "加载数据包",
        "btn_save": "保存翻译",
        "btn_theme": "切换主题",
        "json_field": "JSON 字段",
        "mcfunction_command": "MCFunction 命令",
        "status_ready": "拖拽数据包到窗口即可开始",
        "status_parsing": "解析中…",
        "status_done": "解析完成，共 {} 条可翻译文本",
        "tip": "提示",
        "close_current": "关闭当前文件",
        "not_opened": "尚未打开任何数据包",
        "S_Closed": "已关闭数据包",
        "recent_files": "最近打开",
        "empty": "无",
        "file_no_longer_exists\\n{}": "文件不存在\\n{}",
        "save_ok": "已保存为\n{}",
        "about_text": "MC 数据包翻译工具\n支持全版本 Java 版数据包\n作者：Ace"
    }), ("en_US", {
        "app_title": "MC Datapack Translator Tool",
        "lang_name": "English",
        "menu_file": "File",
        "menu_open": "Open Datapack",
        "menu_exit": "Exit",
        "menu_edit": "Edit",
        "menu_settings": "Settings",
        "menu_help": "Help",
        "menu_about": "About",
        "col_file": "File",
        "col_path": "Path/Line",
        "col_source": "Original text",
        "col_trans": "Translation",
        "setting_show_vanilla": "Show vanilla namespace (minecraft:)",
        "setting_lang": "Language",
        "btn_load": "Load Datapack",
        "btn_save": "Save Translation",
        "btn_theme": "Toggle Theme",
        "json_field": "JSON Fields",
        "mcfunction_command": "MCFunction Commands",
        "status_ready": "Drag datapack into window to start",
        "status_parsing": "Parsing…",
        "status_done": "Done, {} entries found",
        "tip": "Tip",
        "close_current": "Close File",
        "not_opened": "No datapack opened",
        "S_Closed": "Datapack closed",
        "recent_files": "Recent Files",
        "empty": "Empty",
        "file_no_longer_exists\n{}": "File no longer exists:\n{}",
        "save_ok": "Saved to\n{}",
        "about_text": "MC Datapack Translator Tool\nSupports all Java Edition datapacks\nAuthor: Ace"
    })]:
        f = LANG_PATH / f"{lang}.json"
        if not f.exists():
            f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    app = QApplication(sys.argv)
    setTheme(Theme.DARK)
    setThemeColor("#0078d4")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())