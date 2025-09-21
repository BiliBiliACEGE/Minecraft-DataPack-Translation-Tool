# theme.py
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFile, QTextStream

def apply_theme(app: QApplication, dark: bool):
    app.setProperty("darkTheme", dark)
    # 基础样式表（边框/圆角/悬停）
    base = DARK_QSS if dark else LIGHT_QSS
    # 太阳/月亮图标（纯 Unicode）
    icon = "🌙" if dark else "🌞"
    btn_qss = f"""
    QPushButton#ThemeButton{{
        border:none;
        border-radius:14px;               /* 一半宽/高 → 正圆 */
        background:{ "#2d2d30" if dark else "#fafafa"};
        color:{ "#e0e0e0" if dark else "#333"};
        font-size:18px;                   /* 图标大小 */
        padding:4px;                      /* 内边距 → 视觉居中 */
        qproperty-text:"{icon}";
    }}
    QPushButton#ThemeButton:hover{{
        background:{ "#0e639c" if dark else "#3399ff"};
        color:white;
        font-size:20px;                   /* 悬停微放大 */
    }}
    QPushButton#ThemeButton:pressed{{
        background:{ "#095a85" if dark else "#2277dd"};
        font-size:17px;                   /* 按下微缩小 */
    }}
    """
    app.setStyleSheet(base + btn_qss)


DARK_QSS = """
QWidget{font-family:Microsoft YaHei,Segoe UI,Helvetica Neue;}
QMainWindow{background:#1e1e1e;}
QTableWidget{
    background:#252526;
    border:none;
    border-radius:8px;
    gridline-color:#3c3c3c;
    color:#e0e0e0;
    selection-background-color:#0e639c;
}
QHeaderView::section{
    background:#2d2d30;
    border:none;
    padding:4px;
    color:#cccccc;
}
QPushButton{
    background:#0e639c;
    color:white;
    border:none;
    border-radius:6px;
    padding:6px 14px;
    font-weight:bold;
}
QLabel{color:#e0e0e0;}   /* 深色全局 */
QDialog{background:#2d2d30;}
QLabel#SettingTitle{color:#e0e0e0; font-weight:bold; font-size:14px;}
QLabel#SettingSubTitle{color:#cccccc; font-size:12px;}
QPushButton:hover{background:#1177bb;}
QPushButton:pressed{background:#095a85;}
QCheckBox{color:#e0e0e0; spacing:6px;}
QComboBox{
    background:#3c3c3c;
    color:#e0e0e0;
    border:1px solid #555;
    border-radius:4px;
    padding:4px;
}
/* 普通单元格 */
QTableWidget::item {
    background: transparent;
    color: #e0e0e0;
    padding: 4px;
}
QTableWidget::item:focus,
QTableWidget::item:edit-focus,
QTableWidget::item:selected {
    background: transparent;          /* 不覆盖原背景 */
    border: 2px solid #0e639c;        /* 一圈蓝边 */
    border-radius: 4px;
    padding: 0px;                     /* 去掉内边距，防止黄边 */
}
QComboBox::drop-down{border:none; width:20px;}
QComboBox::down-arrow{image:none; border-left:4px solid transparent; border-right:4px solid transparent; border-top:6px solid #e0e0e0;}
QMessageBox{background:#252526; color:#e0e0e0;}
QMenuBar{background:#1e1e1e; color:#e0e0e0;}
QMenu{background:#2d2d30; color:#e0e0e0; border:none;}
QMenu::item:selected{background:#0e639c;}
"""

LIGHT_QSS = """
QWidget{font-family:Microsoft YaHei,Segoe UI,Helvetica Neue;}
QMainWindow{background:#fafafa;}
QTableWidget{
    background:white;
    border:1px solid #ddd;
    border-radius:8px;
    gridline-color:#e0e0e0;
    color:#222;
    selection-background-color:#3399ff;
}
QHeaderView::section{
    background:#f0f0f0;
    border:none;
    padding:4px;
    color:#444;
}
QPushButton{
    background:#3399ff;
    color:white;
    border:none;
    border-radius:6px;
    padding:6px 14px;
    font-weight:bold;
}
QLabel{color:#333333;}   /* 浅色全局 */
QDialog{background:#fafafa;}
QLabel#SettingTitle{color:#333; font-weight:bold; font-size:14px;}
QLabel#SettingSubTitle{color:#555; font-size:12px;}
QPushButton:hover{background:#55bbff;}
QPushButton:pressed{background:#2277dd;}
QCheckBox{color:#333; spacing:6px;}
QComboBox{
    background:white;
    color:#333;
    border:1px solid #ccc;
    border-radius:4px;
    padding:4px;
}
QTableWidget::item {
    background: transparent;
    color: #333;
    padding: 4px;
}
QTableWidget::item:focus,
QTableWidget::item:edit-focus,
QTableWidget::item:selected {
    background: transparent;
    border: 2px solid #3399ff;
    border-radius: 4px;
    padding: 0px;                    
}
QComboBox::drop-down{border:none; width:20px;}
QComboBox::down-arrow{image:none; border-left:4px solid transparent; border-right:4px solid transparent; border-top:6px solid #333;}
QMessageBox{background:white; color:#333;}
QMenuBar{background:#fafafa; color:#333;}
QMenu{background:white; color:#333; border:1px solid #ccc;}
QMenu::item:selected{background:#3399ff; color:white;}
"""