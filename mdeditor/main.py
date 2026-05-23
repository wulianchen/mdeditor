"""
Markdown编辑器 - PyQt6版本
支持真正的HTML渲染，包括表格、代码高亮等
"""
import sys
import os
import html
import logging
from logging.handlers import RotatingFileHandler

# 【优化11】配置日志系统 - 使用RotatingFileHandler实现日志轮转
logger = logging.getLogger('MarkdownEditor')
logger.setLevel(logging.INFO)

# 【关键】防止重复添加handler
if not logger.handlers:
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 【优化11】确定日志目录位置（确保在exe同级目录）
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后：log目录在exe所在目录
        log_base_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境：log目录在项目根目录（main.py所在目录）
        log_base_dir = os.path.dirname(os.path.abspath(__file__))

    log_dir = os.path.join(log_base_dir, 'log')
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception as e:
            print(f"警告: 无法创建日志目录 {log_dir}: {e}")
            log_dir = log_base_dir  # 如果创建失败，使用exe同级目录

    # 文件处理器 - 使用RotatingFileHandler，保存到log目录
    # maxBytes=5MB: 单个日志文件最大5MB
    # backupCount=3: 保留3个备份文件（error.log.1, error.log.2, error.log.3）
    # 总容量最多 20MB（1个主文件 + 3个备份文件）
    log_file_path = os.path.join(log_dir, 'error.log')
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

# 设置Qt插件路径
# noinspection PyInterpreter
if hasattr(sys, '_MEIPASS'):
    # PyInstaller打包后的路径
    base_path = sys._MEIPASS
    
    # 设置Qt插件路径 (Qt6)
    qt_plugins_path = os.path.join(base_path, 'PyQt6', 'Qt6', 'plugins')
    if os.path.exists(qt_plugins_path):
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(qt_plugins_path, 'platforms')
    
    # 设置QtWebEngine相关路径 (Qt6)
    qt_base = os.path.join(base_path, 'PyQt6', 'Qt6')
    webengine_path = os.path.join(qt_base, 'bin')
    webengine_process = os.path.join(webengine_path, 'QtWebEngineProcess.exe')

    if os.path.exists(webengine_process):
        os.environ['QTWEBENGINEPROCESS_PATH'] = webengine_process
    
    # 设置资源文件路径
    resources_path = os.path.join(qt_base, 'resources')
    if os.path.exists(resources_path):
        os.environ['QTWEBENGINE_RESOURCES_PATH'] = resources_path
    
    # 设置翻译文件路径
    translations_path = os.path.join(qt_base, 'translations')
    if os.path.exists(translations_path):
        os.environ['QTWEBENGINE_LOCALES_PATH'] = os.path.join(translations_path, 'qtwebengine_locales')
    
    # 添加到PATH
    if os.path.exists(webengine_path):
        os.environ['PATH'] = webengine_path + os.pathsep + os.environ.get('PATH', '')
else:
    # 开发环境
    import site
    for path in site.getsitepackages():
        plugin_path = os.path.join(path, 'PyQt6', 'Qt6', 'plugins', 'platforms')
        if os.path.exists(plugin_path):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
            
        # 设置QtWebEngine路径 (Qt6)
        webengine_path = os.path.join(path, 'PyQt6', 'Qt6', 'bin')
        webengine_process = os.path.join(webengine_path, 'QtWebEngineProcess.exe')
        if os.path.exists(webengine_process):
            os.environ['QTWEBENGINEPROCESS_PATH'] = webengine_process
            os.environ['PATH'] = webengine_path + os.pathsep + os.environ.get('PATH', '')
            break

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QSplitter, QMenuBar, 
                             QMenu, QFileDialog, QMessageBox, QLabel,
                             QStatusBar, QToolBar, QDialog, QLineEdit, QPushButton,
                             QCheckBox, QComboBox, QSpinBox, QToolButton)
from PyQt6.QtCore import Qt, QMimeData, QTimer
from PyQt6.QtGui import QFont, QIcon, QDragEnterEvent, QDropEvent, QTextCharFormat, QColor, QTextCursor, QAction
from PyQt6.QtWebEngineWidgets import QWebEngineView
import markdown
import style_templates
import re

# ==================== Markdown 转义清理工具（集成版）====================
class MarkdownEscapeCleaner:
    """Markdown 转义清理器 - 用于清理 AI 生成的过度转义字符"""
    
    def __init__(self):
        # 定义需要清理的过度转义模式
        self.escape_patterns = [
            (r'\\\\([*_`~#])', r'\1'),
            (r'&lt;', '<'),
            (r'&gt;', '>'),
            (r'&amp;', '&'),
            (r'&quot;', '"'),
            (r'&#39;', "'"),
            (r'\\"', '"'),
        ]
        
        self.protected_patterns = [
            r'```[\s\S]*?```',
            r'`[^`]+`',
            r'https?://[^\s]+',
        ]
    
    def detect_excessive_escapes(self, text: str) -> dict:
        """检测文本中是否存在过度转义"""
        issues = []
        checks = [
            {'name': '双反斜杠转义', 'pattern': r'\\\\[*_`~#\[\](){}]', 'description': '发现 \\*、\\_ 等过度转义'},
            {'name': 'HTML 实体转义', 'pattern': r'&(lt|gt|amp|quot|#39);', 'description': '发现 &lt;、&gt; 等 HTML 实体'},
            {'name': 'JSON 风格转义', 'pattern': r'\\"', 'description': '发现 \\" 等 JSON 风格转义'},
            {'name': '过度转义的链接', 'pattern': r'\\\[.*?\\\]\\\(.*?\\\)', 'description': '发现 \\[text\\](url) 格式的链接'},
            {'name': '过度转义的标题', 'pattern': r'^\\#+\s', 'description': '发现 \\# 标题格式', 'flags': re.MULTILINE},
        ]
        
        for check in checks:
            flags = check.get('flags', 0)
            matches = re.findall(check['pattern'], text, flags)
            if matches:
                issues.append({'type': check['name'], 'count': len(matches), 'description': check['description'], 'examples': matches[:3]})
        
        return {'has_issues': len(issues) > 0, 'issues': issues, 'issue_count': sum(issue['count'] for issue in issues)}
    
    def clean_escapes(self, text: str) -> str:
        """清理文本中的过度转义 - 激进模式"""
        protected_blocks = []
        
        def protect_code(match):
            placeholder = f"__PROTECTED_BLOCK_{len(protected_blocks)}__"
            protected_blocks.append(match.group(0))
            return placeholder
        
        text = re.sub(r'```[\s\S]*?```', protect_code, text)
        text = re.sub(r'`[^`]+`', protect_code, text)
        
        cleaned_text = text
        for iteration in range(10):
            prev_text = cleaned_text
            cleaned_text = re.sub(r'\\\\([*_`~#\[\](){}>+|=-])', r'\1', cleaned_text)
            
            html_entities = {'&lt;': '<', '&gt;': '>', '&amp;': '&', '&quot;': '"', '&#39;': "'", '&nbsp;': ' '}
            for entity, replacement in html_entities.items():
                cleaned_text = cleaned_text.replace(entity, replacement)
            
            cleaned_text = re.sub(r'\\"', '"', cleaned_text)
            cleaned_text = re.sub(r"\\'", "'", cleaned_text)
            cleaned_text = re.sub(r'\\\[(.+?)\\\]\\\((.+?)\\\)', r'[\1](\2)', cleaned_text)
            cleaned_text = re.sub(r'!\\\[(.+?)\\\]\\\((.+?)\\\)', r'![\1](\2)', cleaned_text)
            cleaned_text = re.sub(r'^\\+(#+)\s', r'\1 ', cleaned_text, flags=re.MULTILINE)
            cleaned_text = re.sub(r'^\\+([-*+])\s', r'\1 ', cleaned_text, flags=re.MULTILINE)
            cleaned_text = re.sub(r'\\+\*\*(.+?)\\+\*\*', r'**\1**', cleaned_text)
            cleaned_text = re.sub(r'\\+\*(.+?)\\+\*', r'*\1*', cleaned_text)
            cleaned_text = re.sub(r'\\+_(.+?)\\+_', r'_\1_', cleaned_text)
            cleaned_text = re.sub(r'\\+__(.+?)\\+__', r'__\1__', cleaned_text)
            cleaned_text = re.sub(r'^\\+>\s', r'> ', cleaned_text, flags=re.MULTILINE)
            cleaned_text = re.sub(r'^\\+[-*_]{3,}\s*$', r'---', cleaned_text, flags=re.MULTILINE)
            cleaned_text = re.sub(r'\\+\|', '|', cleaned_text)
            
            if cleaned_text == prev_text:
                break
        
        markdown_special_chars = r'\*\_\#\[\]\(\)\>\+\|\=\-'
        cleaned_text = re.sub(r'\\([' + markdown_special_chars + r'])', r'\1', cleaned_text)
        
        for i, block in enumerate(protected_blocks):
            placeholder = f"__PROTECTED_BLOCK_{i}__"
            cleaned_text = cleaned_text.replace(placeholder, block)
        
        return cleaned_text
    
    def clean_and_report(self, text: str) -> dict:
        """清理转义并生成报告"""
        detection = self.detect_excessive_escapes(text)
        
        if detection['has_issues']:
            cleaned_text = self.clean_escapes(text)
            after_detection = self.detect_excessive_escapes(cleaned_text)
            
            return {
                'success': True,
                'original_issues': detection,
                'remaining_issues': after_detection,
                'cleaned_text': cleaned_text,
                'improvement': {
                    'before_count': detection['issue_count'],
                    'after_count': after_detection['issue_count'],
                    'fixed_count': detection['issue_count'] - after_detection['issue_count']
                }
            }
        else:
            return {'success': True, 'message': '未发现过度转义问题', 'original_issues': detection, 'cleaned_text': text}


# 创建全局清理器实例（已集成到 main.py，始终可用）
ESCAPE_CLEANER = MarkdownEscapeCleaner()
ESCAPE_CLEANER_AVAILABLE = True


class DropWebView(QWebEngineView):
    """支持文件拖放的Web视图"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)  # 启用拖放
        self.parent_window = parent
        
        # 启用页面设置，确保可以选择和复制文本
        try:
            from PyQt6.QtWebEngineCore import QWebEngineSettings
            settings = self.page().settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            # 允许加载本地文件（图片等）
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        except Exception as e:
            logger.error(f"WebEngine设置失败: {e}")
        
        # 连接信号，拦截链接点击
        self.page().linkHovered.connect(self._on_link_hovered)
        # 重写 acceptNavigationRequest 来拦截导航
        
    def contextMenuEvent(self, event):
        """自定义右键菜单，确保可以复制选中的文本"""
        from PyQt6.QtWidgets import QMenu
        menu = QMenu(self)
        
        # 添加复制动作
        copy_action = menu.addAction('复制')
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self._copy_selected_text)
        
        # 添加全选动作
        select_all_action = menu.addAction('全选')
        select_all_action.setShortcut('Ctrl+A')
        select_all_action.triggered.connect(self._select_all_text)
        
        menu.addSeparator()
        
        # 添加刷新动作
        refresh_action = menu.addAction('刷新预览')
        refresh_action.triggered.connect(self._refresh_preview)
        
        menu.addSeparator()
        
        # 添加导出长图动作
        export_action = menu.addAction('🖼️ 导出长图')
        export_action.triggered.connect(self._export_long_image)
        
        menu.exec(event.globalPos())
    
    def _copy_selected_text(self):
        """复制选中的文本"""
        try:
            self.page().triggerAction(self.page().WebAction.Copy)
        except Exception as e:
            logger.error(f"复制失败: {e}")
    
    def _select_all_text(self):
        """全选文本"""
        try:
            self.page().triggerAction(self.page().WebAction.SelectAll)
        except Exception as e:
            logger.error(f"全选失败: {e}")
    
    def _refresh_preview(self):
        """刷新预览"""
        try:
            if self.parent_window:
                self.parent_window.update_preview()
        except Exception as e:
            logger.error(f"刷新失败: {e}")
    
    def _export_long_image(self):
        """导出长图"""
        try:
            if self.parent_window:
                self.parent_window.export_long_image()
        except Exception as e:
            logger.error(f"导出失败: {e}")
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件 - 接受所有文件"""
        if event.mimeData().hasUrls():
            # 接受所有文件，验证在dropEvent中进行
            event.acceptProposedAction()
        else:
            event.ignore()
        
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件 - 调用统一的打开方法"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                # 调用父窗口的打开文件方法（会进行统一验证）
                if self.parent_window and hasattr(self.parent_window, 'open_file_by_path'):
                    self.parent_window.open_file_by_path(file_path)
                    break
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        """拦截导航请求，在系统默认浏览器中打开链接"""
        from PyQt6.QtWebEngineCore import QWebEnginePage
        
        # 如果是链接点击（不是页面加载、后退、前进等）
        if navigation_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            # 在系统默认浏览器中打开链接
            import webbrowser
            webbrowser.open(url.toString())
            return False  # 阻止在 WebEngine 中导航
        
        # 其他情况允许导航
        return super().acceptNavigationRequest(url, navigation_type, is_main_frame)
    
    def _on_link_hovered(self, url):
        """链接悬停事件"""
        # 可以在这里显示链接预览或状态栏信息
        pass


class MarkdownEditor(QMainWindow):
    def __init__(self, file_path=None):
        super().__init__()
        logger.info("初始化 Markdown 编辑器")
        
        self.current_file = None
        self.page_loaded = False  # 标记页面是否加载完成
        self.preview_scroll_position = 0  # 保存预览区滚动位置
        self.need_restore_scroll = False  # 标记是否需要恢复滚动位置
        self.highlight_format = QTextCharFormat()  # 高亮格式
        self.highlight_format.setBackground(QColor('#FFFF00'))  # 黄色背景
        self.search_dialog = None  # 搜索对话框
        self.replace_dialog = None  # 替换对话框
        self.search_results = []  # 搜索结果列表
        self.current_search_index = -1  # 当前搜索结果索引
        self.current_search_text = ''  # 当前搜索文本
        self.current_style = 'default'  # 当前预览风格
        self.base_font_size = 16  # 基准字体大小（px）
        self.base_font_weight = 400  # 基础字重 (400=normal, 500=medium, 600=semibold, 700=bold)
        self.base_font_family = '微软雅黑'  # 基础字体
        self.preview_zoom = 100  # 预览区缩放比例（百分比）
        self.drag_overlay = None  # 拖拽提示层
        self.saved_md5 = None  # 保存时的文档MD5值
        self.is_fullscreen = False  # 【新增】全屏状态标志
        self.pdf_export_ratio = 'A4'  # 【新增】PDF导出比例，默认A4
        self.pdf_export_orientation = 'portrait'  # 【新增】PDF导出方向，默认竖屏
        
        # 【新增】渲染超时提示相关
        self.render_timeout_timer = None  # 渲染超时定时器
        self.render_progress_dialog = None  # 渲染进度提示对话框
        
        # 【关键】预览更新防抖定时器 - 避免字体/样式频繁改变时重复渲染
        self.preview_update_timer = QTimer(self)
        self.preview_update_timer.setSingleShot(True)  # 只触发一次
        self.preview_update_timer.timeout.connect(self._do_update_preview)
        
        # 【新增】待处理的样式切换标志
        self._pending_style_change = None
        
        # 加载上一次的设置
        self.load_settings()
        
        self.init_ui()
        
        # 如果提供了文件路径，则自动打开该文件
        if file_path and os.path.exists(file_path):
            logger.info(f"从命令行打开文件: {file_path}")
            QTimer.singleShot(100, lambda: self.open_file_by_path(file_path))
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('快乐马MarkDown编辑器')
        # 设置窗口尺寸，确保所有工具栏控件完整显示
        self.setGeometry(100, 100, 1350, 900)
        
        # 启用拖拽支持
        self.setAcceptDrops(True)
        
        # 设置窗口图标
        try:
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller打包后的路径（onedir模式下，_MEIPASS指向_internal目录）
                icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
            else:
                # 开发环境
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
            
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                logger.info(f"已加载窗口图标: {icon_path}")
            else:
                logger.warning(f"图标文件不存在: {icon_path}")
                # 尝试其他可能的位置
                if hasattr(sys, '_MEIPASS'):
                    # 尝试从exe所在目录查找
                    icon_path = os.path.join(os.path.dirname(sys.executable), 'icon.ico')
                    if os.path.exists(icon_path):
                        self.setWindowIcon(QIcon(icon_path))
                        logger.info(f"已从备用位置加载图标: {icon_path}")
        except Exception as e:
            logger.error(f"设置窗口图标失败: {e}")
        
        # 设置菜单栏样式 - 修复悬浮高亮不易识别的问题
        self.setStyleSheet("""
            QMenuBar {
                background-color: #f0f0f0;
                border-bottom: 1px solid #d0d0d0;
                padding: 2px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
                margin: 2px;
                border-radius: 3px;
            }
            QMenuBar::item:selected {
                background-color: #4a90e2;
                color: white;
            }
            QMenuBar::item:pressed {
                background-color: #357abd;
                color: white;
            }
            QMenu {
                background-color: white;
                border: 1px solid #d0d0d0;
                padding: 5px;
            }
            QMenu::item {
                padding: 6px 25px 6px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #4a90e2;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e0e0e0;
                margin: 5px 0px;
            }
            QToolBar {
                background-color: #fafafa;
                border-bottom: 1px solid #d0d0d0;
                spacing: 5px;
                padding: 3px;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 4px;
            }
            QToolButton:hover {
                background-color: #e8e8e8;
                border: 1px solid #c0c0c0;
            }
            QToolButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建主界面
        self.create_main_area()
        
        # 创建状态栏
        self.statusBar().showMessage('就绪')
        
        # 初始化导出按钮状态（文档为空时禁用）
        self._update_export_buttons_state(False)
        
        # 【优化2】预览区滚动同步定时器 - 按需启动/停止，节省CPU
        self.preview_scroll_timer = QTimer(self)
        self.preview_scroll_timer.timeout.connect(self._sync_preview_to_editor)
        # 初始不启动，只在鼠标进入预览区时才启动
        self.preview_scroll_active = False  # 标记定时器是否激活
        
        # 跟踪鼠标位置，决定哪个区域控制滚动
        self.mouse_in_editor = False
        self.mouse_in_preview = False
        
        # 监听编辑区和预览区的鼠标进入/离开事件
        self.editor.installEventFilter(self)
        self.preview.installEventFilter(self)
        
    def create_menu(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        new_action = QAction('新建', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('打开', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('保存', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction('另存为', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Alt+F4')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu('编辑')
        
        undo_action = QAction('撤销', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(lambda: self.editor.undo())
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('重做', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(lambda: self.editor.redo())
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction('剪切', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(lambda: self.editor.cut())
        edit_menu.addAction(cut_action)
        
        copy_action = QAction('复制', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(lambda: self.editor.copy())
        edit_menu.addAction(copy_action)
        
        paste_action = QAction('粘贴', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(lambda: self.editor.paste())
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        # 搜索功能
        search_action = QAction('查找', self)
        search_action.setShortcut('Ctrl+F')
        search_action.triggered.connect(self.show_search_dialog)
        edit_menu.addAction(search_action)
        
        replace_action = QAction('替换', self)
        replace_action.setShortcut('Ctrl+H')
        replace_action.triggered.connect(self.show_replace_dialog)
        edit_menu.addAction(replace_action)
        
        find_next_action = QAction('查找下一个', self)
        find_next_action.setShortcut('F3')
        find_next_action.triggered.connect(self.find_next)
        edit_menu.addAction(find_next_action)
        
        find_previous_action = QAction('查找上一个', self)
        find_previous_action.setShortcut('Shift+F3')
        find_previous_action.triggered.connect(self.find_previous)
        edit_menu.addAction(find_previous_action)
        
        # 视图菜单
        view_menu = menubar.addMenu('视图')
        
        fullscreen_action = QAction('全屏', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        refresh_action = QAction('刷新预览', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.update_preview)
        view_menu.addAction(refresh_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        
        product_intro_action = QAction('产品简介', self)
        product_intro_action.triggered.connect(lambda: self.show_pdf_document('产品简介.pdf'))
        help_menu.addAction(product_intro_action)
        
        whitepaper_action = QAction('技术白皮书', self)
        whitepaper_action.triggered.connect(lambda: self.show_pdf_document('技术白皮书.pdf'))
        help_menu.addAction(whitepaper_action)
        
        copyright_action = QAction('版权声明', self)
        copyright_action.triggered.connect(lambda: self.show_pdf_document('版权声明.pdf'))
        help_menu.addAction(copyright_action)
        
        help_menu.addSeparator()
        
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 文件操作组 - 仅显示图标
        new_action = toolbar.addAction('📄', self.new_file)
        new_action.setToolTip('新建')
        
        open_action = toolbar.addAction('📂', self.open_file)
        open_action.setToolTip('打开')
        
        save_action = toolbar.addAction('💾', self.save_file)
        save_action.setToolTip('保存')
        
        toolbar.addSeparator()
        
        # 搜索功能 - 仅显示图标
        search_action = toolbar.addAction('🔍', self.show_search_dialog)
        search_action.setToolTip('查找')
        toolbar.addSeparator()
        
        # 刷新功能
        toolbar.addAction('🔄 刷新', self.update_preview)
        toolbar.addSeparator()
        
        # 插入功能组 - 带标签和图标
        insert_label = QLabel('插入:')
        toolbar.addWidget(insert_label)
        
        insert_url_action = toolbar.addAction('🔗', self.insert_url)
        insert_url_action.setToolTip('插入网址')
        
        insert_link_action = toolbar.addAction('📝', self.insert_text_link)
        insert_link_action.setToolTip('插入文本链接')
        
        insert_image_action = toolbar.addAction('🖼️', self.insert_image)
        insert_image_action.setToolTip('插入图片')
        
        toolbar.addSeparator()
        
        # 导出功能组 - 先添加比例选择，再添加导出按钮
        export_ratio_label = QLabel('导出比例:')
        toolbar.addWidget(export_ratio_label)
        
        self.pdf_ratio_combo = QComboBox()
        self.pdf_ratio_combo.setFixedWidth(60)
        pdf_ratios = [
            ('A3', 'A3'),
            ('A4', 'A4'),
            ('A5', 'A5'),
            ('B5', 'B5'),
            ('Letter', 'Letter'),
            ('Legal', 'Legal'),
        ]
        for ratio_key, ratio_name in pdf_ratios:
            self.pdf_ratio_combo.addItem(ratio_name, ratio_key)
        # 【关键】使用加载的配置值，如果没有则默认A4
        self.pdf_ratio_combo.setCurrentText(self.pdf_export_ratio)
        # 【新增】连接信号，当用户改变比例时更新配置
        self.pdf_ratio_combo.currentIndexChanged.connect(self.on_pdf_ratio_changed)
        toolbar.addWidget(self.pdf_ratio_combo)
        
        # 【新增】添加方向选择下拉框
        orientation_label = QLabel('方向:')
        toolbar.addWidget(orientation_label)
        
        self.pdf_orientation_combo = QComboBox()
        self.pdf_orientation_combo.setFixedWidth(60)
        orientations = [
            ('portrait', '竖屏'),
            ('landscape', '横屏'),
        ]
        for orient_key, orient_name in orientations:
            self.pdf_orientation_combo.addItem(orient_name, orient_key)
        # 使用加载的配置值
        index = self.pdf_orientation_combo.findData(self.pdf_export_orientation)
        if index != -1:
            self.pdf_orientation_combo.setCurrentIndex(index)
        # 连接信号
        self.pdf_orientation_combo.currentIndexChanged.connect(self.on_pdf_orientation_changed)
        toolbar.addWidget(self.pdf_orientation_combo)
        
        # 保存需要禁用的按钮引用
        self.export_pdf_action = toolbar.addAction('📄 导出PDF', self.export_pdf)
        self.export_long_image_action = toolbar.addAction('🖼️ 导出长图', self.export_long_image)
        self.export_image_collection_action = toolbar.addAction('📚 导出图集', self.export_image_collection)
        
        toolbar.addSeparator()
        
        # 样式风格组
        self.style_combo = QComboBox()
        self.style_combo.setFixedWidth(110)
        
        styles = [
            # 默认风格
            ('default', '默认风格'),
            
            # 程序员/科技风格
            ('geek', '极客复古终端'),
            ('dark_coder', '暗黑程序员'),
            ('cyber_neon', '赛博朋克霓虹'),
            
            # 特效风格
            ('glass', '玻璃拟态'),
            ('neumorphism', '新拟态'),
            
            # 商务专业风格
            ('business_blue', '蓝白商务专业'),
            
            # 现代简约风格
            ('flat', '极简扁平风'),
            ('apple', '苹果风格'),
            
            # 文艺清新风格
            ('nordic_cold', '北欧冷淡风'),
            ('school_fresh', '校园青春清新'),
            
            # 阅读友好风格
            ('paper_eye', '纸质护眼宣纸'),
            ('magazine_bw', '极简黑白杂志'),
            ('old_newspaper', '复古报纸老式'),
            
            # UI设计系统风格
            ('ant', 'Ant Design'),
            ('material', 'Material Design'),
            ('element', 'Element Plus'),
            ('arco', 'Arco Design'),
            ('fluent', 'Fluent Design'),
            ('shadcn', 'shadcn/ui'),
        ]
        
        for style_key, style_name in styles:
            self.style_combo.addItem(style_name, style_key)
            if style_key == self.current_style:
                self.style_combo.setCurrentIndex(len(self.style_combo) - 1)
        
        # 添加分组分隔线（使用不可选的分割项）
        # 需要从后往前插入，避免索引偏移
        # 原始列表索引（0-19），需要在以下位置插入分隔线（每个位置减1）：
        separator_indices = [14, 11, 9, 7, 6, 4, 1]
        for idx in sorted(separator_indices, reverse=True):  # 从大到小排序，从后往前插入
            self.style_combo.insertSeparator(idx)
        
        self.style_combo.currentIndexChanged.connect(self.on_style_changed)
        toolbar.addWidget(self.style_combo)
        
        toolbar.addSeparator()
        
        # 添加字体选择
        self.font_family_combo = QComboBox()
        self.font_family_combo.setFixedWidth(110)
        
        # 获取系统中所有可用的字体 (Qt6)
        from PyQt6.QtGui import QFontDatabase
        all_fonts = QFontDatabase.families()  # Qt6 中使用静态方法
        
        # 过滤掉明显无用的字体和重复的变体
        def is_valid_font(font_name):
            # 跳过包含版本号的字体（如 pt_font.8.8）
            if any(c.isdigit() for c in font_name) and '.' in font_name:
                return False
            # 跳过包含下划线的字体
            if '_' in font_name:
                return False
            # 跳过空名称
            if not font_name.strip():
                return False
            return True
        
        valid_fonts = [f for f in all_fonts if is_valid_font(f)]
        
        # 进一步去重：对于相似字体族，只保留最简洁的名称
        # 例如：Kozuka Gothic Pro, Kozuka Gothic Pro B, Kozuka Gothic Pro L -> 只保留 Kozuka Gothic Pro
        def get_base_font_name(font_name):
            """提取字体的基础名称，去除样式后缀"""
            # 常见样式后缀列表
            style_suffixes = [
                ' Bold', ' Italic', ' Light', ' Medium', ' Regular',
                ' Thin', ' Black', ' Heavy', ' DemiBold', ' ExtraBold',
                ' Condensed', ' Extended', ' Narrow', ' Wide',
                ' Pro', ' Plus', ' UI', ' Display', ' Text',
                ' B', ' I', ' BI', ' L', ' M', ' R', ' T',
            ]
            
            base_name = font_name
            for suffix in style_suffixes:
                if base_name.endswith(suffix):
                    base_name = base_name[:-len(suffix)]
                    break
            
            return base_name.strip()
        
        # 按基础名称分组，每组只保留一个代表
        font_groups = {}
        for font in valid_fonts:
            base_name = get_base_font_name(font)
            
            # 特殊处理：将同一系列字体归为一组（如所有 Kozuka 字体）
            # 可以根据需要添加更多系列
            special_groups = {
                'Kozuka': 'Kozuka',  # 所有 Kozuka 开头的字体归为一组
            }
            
            group_key = base_name
            for prefix, group_name in special_groups.items():
                if base_name.startswith(prefix):
                    group_key = group_name
                    break
            
            if group_key not in font_groups:
                font_groups[group_key] = font  # 保留第一个出现的完整名称
        
        deduplicated_fonts = list(font_groups.values())
        
        # 将常用中文字体排在前面
        preferred_fonts = ['微软雅黑', '宋体', '黑体', '楷体', '仿宋', '思源黑体', '思源宋体']
        other_fonts = sorted([f for f in deduplicated_fonts if f not in preferred_fonts])
        sorted_fonts = preferred_fonts + other_fonts
        
        for font_name in sorted_fonts:
            self.font_family_combo.addItem(font_name)
            if font_name == self.base_font_family:
                self.font_family_combo.setCurrentIndex(len(self.font_family_combo) - 1)
        self.font_family_combo.currentTextChanged.connect(self.on_font_family_changed)
        toolbar.addWidget(self.font_family_combo)
        
        toolbar.addSeparator()
        
        # 添加字体大小调节
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 32)
        self.font_size_spinbox.setValue(self.base_font_size)
        self.font_size_spinbox.setFixedWidth(60)
        self.font_size_spinbox.valueChanged.connect(self.on_font_size_changed)
        toolbar.addWidget(self.font_size_spinbox)
        
        toolbar.addSeparator()
        
        # 添加字重调节
        self.font_weight_combo = QComboBox()
        self.font_weight_combo.setFixedWidth(60)
        font_weights = [
            (300, '细体'),
            (400, '常规'),
            (500, '中等'),
            (600, '半粗'),
            (700, '粗体'),
        ]
        for weight_value, weight_name in font_weights:
            self.font_weight_combo.addItem(weight_name, weight_value)
            if weight_value == self.base_font_weight:
                self.font_weight_combo.setCurrentIndex(len(self.font_weight_combo) - 1)
        self.font_weight_combo.currentIndexChanged.connect(self.on_font_weight_changed)
        toolbar.addWidget(self.font_weight_combo)
        
        toolbar.addSeparator()
        
        # 添加预览区缩放控制
        self.preview_zoom_spinbox = QSpinBox()
        self.preview_zoom_spinbox.setRange(20, 100)  # 限制最大值为100%
        self.preview_zoom_spinbox.setValue(self.preview_zoom)  # 使用加载的配置值
        self.preview_zoom_spinbox.setFixedWidth(60)
        self.preview_zoom_spinbox.setSuffix('%')
        self.preview_zoom_spinbox.valueChanged.connect(self.on_preview_zoom_changed)
        toolbar.addWidget(self.preview_zoom_spinbox)
    
    def on_style_changed(self, index):
        """当风格下拉框改变时触发 - 使用防抖"""
        style_key = self.style_combo.itemData(index)
        if style_key and style_key != self.current_style:
            # 【关键】保存待切换的样式，并使用防抖定时器
            self._pending_style_change = style_key
            self.preview_update_timer.stop()
            self.preview_update_timer.start(300)
            self.statusBar().showMessage(f'准备切换到: {self.get_style_name(style_key)}')
    
    def on_font_size_changed(self, size):
        """当字体大小改变时触发 - 使用防抖"""
        self.base_font_size = size
        # 【关键】使用防抖定时器，300ms后才真正更新预览
        self.preview_update_timer.stop()  # 停止之前的定时器
        self.preview_update_timer.start(300)  # 300ms后执行
        self.statusBar().showMessage(f'字体大小: {size}px')
    
    def on_font_family_changed(self, font_name):
        """当字体改变时触发 - 使用防抖"""
        if font_name:
            self.base_font_family = font_name
            # 【关键】使用防抖定时器
            self.preview_update_timer.stop()
            self.preview_update_timer.start(300)
            self.statusBar().showMessage(f'字体: {font_name}')
    
    def on_font_weight_changed(self, index):
        """当字重改变时触发 - 使用防抖"""
        weight = self.font_weight_combo.itemData(index)
        if weight:
            self.base_font_weight = weight
            # 【关键】使用防抖定时器
            self.preview_update_timer.stop()
            self.preview_update_timer.start(300)
            weight_names = {300: '细体', 400: '常规', 500: '中等', 600: '半粗', 700: '粗体'}
            self.statusBar().showMessage(f'字重: {weight_names.get(weight, "未知")}')
    
    def on_pdf_ratio_changed(self, index):
        """当PDF导出比例改变时触发"""
        ratio_key = self.pdf_ratio_combo.itemData(index)
        if ratio_key:
            self.pdf_export_ratio = ratio_key
            self.statusBar().showMessage(f'PDF导出比例: {ratio_key}')
    
    def on_pdf_orientation_changed(self, index):
        """当PDF导出方向改变时触发"""
        orientation_key = self.pdf_orientation_combo.itemData(index)
        if orientation_key:
            self.pdf_export_orientation = orientation_key
            orient_name = '竖屏' if orientation_key == 'portrait' else '横屏'
            self.statusBar().showMessage(f'PDF导出方向: {orient_name}')
    
    def _do_update_preview(self):
        """实际执行预览更新（由防抖定时器调用）"""
        try:
            # 检查是否有待处理的样式切换
            if hasattr(self, '_pending_style_change') and self._pending_style_change:
                style_key = self._pending_style_change
                self._pending_style_change = None
                # 先执行样式切换
                self.current_style = style_key
                # 更新工具栏下拉框
                if hasattr(self, 'style_combo'):
                    index = self.style_combo.findData(style_key)
                    if index != -1:
                        self.style_combo.blockSignals(True)
                        self.style_combo.setCurrentIndex(index)
                        self.style_combo.blockSignals(False)
            
            # 执行预览更新
            self.update_preview()
        except Exception as e:
            logger.error(f"预览更新失败: {e}")
    
    def insert_url(self):
        """插入网址 - 使用 Markdown 自动链接语法 <URL>"""
        from PyQt6.QtWidgets import QInputDialog
        url, ok = QInputDialog.getText(self, '插入网址', '请输入网址:')
        if ok and url:
            cursor = self.editor.textCursor()
            # 使用 Markdown 自动链接语法
            auto_link = f'<{url}>'
            cursor.insertText(auto_link)
            self.editor.setTextCursor(cursor)
            self.editor.document().setModified(True)
            self.statusBar().showMessage('已插入网址')
    
    def insert_text_link(self):
        """插入文本链接 - 使用对话框"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
        
        # 创建对话框
        dialog = QDialog(self)
        dialog.setWindowTitle('插入文本链接')
        dialog.setFixedWidth(400)
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 显示文字输入框
        text_layout = QHBoxLayout()
        text_label = QLabel('显示文字:')
        text_label.setFixedWidth(80)
        text_input = QLineEdit()
        text_input.setPlaceholderText('请输入链接显示的文字')
        text_layout.addWidget(text_label)
        text_layout.addWidget(text_input)
        layout.addLayout(text_layout)
        
        # 网址输入框
        url_layout = QHBoxLayout()
        url_label = QLabel('网址:')
        url_label.setFixedWidth(80)
        url_input = QLineEdit()
        url_input.setPlaceholderText('请输入链接地址（例如：https://example.com）')
        url_layout.addWidget(url_label)
        url_layout.addWidget(url_input)
        layout.addLayout(url_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QPushButton('确定')
        ok_btn.setFixedWidth(80)
        ok_btn.setDefault(True)
        
        def on_confirm():
            """确定按钮点击事件"""
            text = text_input.text().strip()
            url = url_input.text().strip()
            
            # 检查显示文字是否为空
            if not text:
                QMessageBox.warning(dialog, '警告', '显示文字不能为空')
                text_input.setFocus()  # 焦点回到文字输入框
                return  # 不关闭对话框，等待用户输入
            
            # 检查网址是否为空
            if not url:
                QMessageBox.warning(dialog, '警告', '网址不能为空')
                url_input.setFocus()  # 焦点回到网址输入框
                return  # 不关闭对话框，等待用户输入
            
            # 验证通过，插入链接并关闭对话框
            cursor = self.editor.textCursor()
            link_text = f'[{text}]({url})'
            cursor.insertText(link_text)
            self.editor.setTextCursor(cursor)
            self.editor.document().setModified(True)
            self.statusBar().showMessage('已插入文本链接')
            dialog.accept()
        
        ok_btn.clicked.connect(on_confirm)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.setFixedWidth(80)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        # 设置焦点到第一个输入框
        text_input.setFocus()
        
        # 显示对话框
        dialog.exec()
    
    def insert_image(self):
        """插入图片 - 自动获取宽高"""
        from PyQt6.QtWidgets import QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
        from PyQt6.QtGui import QImage
        from PyQt6.QtCore import Qt
        import shutil
        
        # 先检查文档是否已保存（针对本地图片）
        if not self.current_file:
            # 创建自定义对话框
            save_dialog = QDialog(self)
            save_dialog.setWindowTitle('提示')
            save_dialog.setFixedWidth(350)
            
            dialog_layout = QVBoxLayout()
            
            # 提示信息
            hint_label = QLabel('要先保存文档才能引入图片')
            hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hint_label.setStyleSheet("font-size: 14px; padding: 10px;")
            dialog_layout.addWidget(hint_label)
            
            # 按钮区域
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            
            save_btn = QPushButton('立即保存')
            save_btn.setFixedWidth(80)
            save_btn.setDefault(True)
            save_btn.clicked.connect(lambda: self._save_for_insert(save_dialog))
            btn_layout.addWidget(save_btn)
            
            cancel_btn = QPushButton('取消')
            cancel_btn.setFixedWidth(80)
            cancel_btn.clicked.connect(save_dialog.reject)
            btn_layout.addWidget(cancel_btn)
            
            dialog_layout.addLayout(btn_layout)
            save_dialog.setLayout(dialog_layout)
            
            # 显示对话框
            if save_dialog.exec() != QDialog.DialogCode.Accepted:
                return  # 用户点击取消
            
            # 如果保存后还是没有文件路径（用户取消了保存），则退出
            if not self.current_file:
                return
        
        # 创建选择对话框
        choice_dialog = QDialog(self)
        choice_dialog.setWindowTitle('插入图片')
        choice_dialog.setFixedWidth(350)
        
        layout = QVBoxLayout()
        
        # 按钮区域 - 两个并排按钮
        button_row = QHBoxLayout()
        
        # 左边按钮：输入图片网址
        url_btn = QPushButton('🌐 输入图片网址')
        url_btn.setFixedHeight(40)
        url_btn.clicked.connect(lambda: self._insert_image_from_url())
        url_btn.clicked.connect(choice_dialog.accept)
        button_row.addWidget(url_btn)
        
        # 右边按钮：选择本机图片
        local_btn = QPushButton('💻 选择本机图片')
        local_btn.setFixedHeight(40)
        local_btn.clicked.connect(lambda: self._insert_image_from_local())
        local_btn.clicked.connect(choice_dialog.accept)
        button_row.addWidget(local_btn)
        
        layout.addLayout(button_row)
        
        # 取消按钮
        cancel_layout = QHBoxLayout()
        cancel_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.setFixedWidth(80)
        cancel_btn.clicked.connect(choice_dialog.reject)
        cancel_layout.addWidget(cancel_btn)
        
        layout.addLayout(cancel_layout)
        choice_dialog.setLayout(layout)
        
        # 显示选择对话框
        if choice_dialog.exec() != QDialog.DialogCode.Accepted:
            return  # 用户点击取消
    
    def _insert_image_from_url(self):
        """从URL插入图片"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
        from PyQt6.QtGui import QImage
        
        cursor = self.editor.textCursor()
        
        # 使用自定义对话框输入图片信息
        dialog = QDialog(self)
        dialog.setWindowTitle('插入网络图片')
        dialog.setFixedWidth(450)
        
        layout = QVBoxLayout()
        
        # 网址输入框（必填）
        url_layout = QHBoxLayout()
        url_label = QLabel('网址:')
        url_label.setFixedWidth(80)
        url_input = QLineEdit()
        url_input.setPlaceholderText('请输入图片URL（必填）')
        url_layout.addWidget(url_label)
        url_layout.addWidget(url_input)
        layout.addLayout(url_layout)
        
        # 标题输入框（可选）
        title_layout = QHBoxLayout()
        title_label = QLabel('标题:')
        title_label.setFixedWidth(80)
        title_input = QLineEdit()
        title_input.setPlaceholderText('请输入图片标题（可选）')
        title_layout.addWidget(title_label)
        title_layout.addWidget(title_input)
        layout.addLayout(title_layout)
        
        # 替代文字输入框（可选）
        alt_layout = QHBoxLayout()
        alt_label = QLabel('替代文字:')
        alt_label.setFixedWidth(80)
        alt_input = QLineEdit()
        alt_input.setPlaceholderText('图片无法显示时的替代文字（可选）')
        alt_layout.addWidget(alt_label)
        alt_layout.addWidget(alt_input)
        layout.addLayout(alt_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QPushButton('确定')
        ok_btn.setFixedWidth(80)
        ok_btn.setDefault(True)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.setFixedWidth(80)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        # 设置焦点到第一个输入框
        url_input.setFocus()
        
        # 【关键】定义验证和插入函数
        def validate_and_insert():
            """验证URL并插入图片"""
            url = url_input.text().strip()
            title = title_input.text().strip()
            alt_text = alt_input.text().strip()
            
            if not url:
                QMessageBox.warning(dialog, '警告', '图片网址不能为空')
                url_input.setFocus()
                return  # 不关闭对话框，让用户修改
            
            # 如果标题为空，使用默认占位符
            if not title:
                title = '标题'
            
            # 【关键】尝试获取网络图片尺寸（会下载到临时文件）
            result = self._get_image_dimensions(url)
            
            # 如果获取失败，显示错误信息并保持对话框打开
            if result is None or len(result) != 4:
                logger.info(f"网络图片获取失败，请用户修改URL: {url}")
                url_input.setFocus()  # 聚焦到URL输入框，方便修改
                url_input.selectAll()  # 全选文本，方便替换
                return  # 不关闭对话框
            
            width, height, temp_file_path, error_message = result
            
            # 如果有错误信息，显示并让用户修改
            if error_message:
                logger.info(f"网络图片获取失败: {error_message}")
                QMessageBox.warning(dialog, '提示', error_message)
                url_input.setFocus()
                url_input.selectAll()
                return  # 不关闭对话框
            
            # 【关键】按本地图片逻辑处理：复制到文档图片目录
            from PyQt6.QtGui import QImage
            import shutil
            
            # 获取当前文档路径
            current_file = self.current_file
            if not current_file:
                QMessageBox.warning(self, '警告', '请先保存文档，再插入网络图片')
                # 删除临时文件
                try:
                    os.remove(temp_file_path)
                except:
                    pass
                return
            
            # 创建图片目录
            doc_dir = os.path.dirname(current_file)
            doc_name = os.path.splitext(os.path.basename(current_file))[0]
            image_dir = os.path.join(doc_dir, f'{doc_name}_图片')
            
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)
            
            # 复制图片到目录
            image_filename = os.path.basename(temp_file_path)
            dest_path = os.path.join(image_dir, image_filename)
            
            # 如果文件已存在，添加序号
            if os.path.exists(dest_path):
                base_name, ext = os.path.splitext(image_filename)
                counter = 1
                while os.path.exists(dest_path):
                    new_filename = f"{base_name}_{counter}{ext}"
                    dest_path = os.path.join(image_dir, new_filename)
                    counter += 1
            
            try:
                shutil.copy2(temp_file_path, dest_path)
                logger.info(f"网络图片已保存到: {dest_path}")
                
                # 删除临时文件
                try:
                    os.remove(temp_file_path)
                    logger.debug(f"已删除临时文件: {temp_file_path}")
                except:
                    pass
                
                # 生成相对路径
                relative_path = os.path.relpath(dest_path, doc_dir)
                # Windows下将反斜杠转换为正斜杠
                relative_path = relative_path.replace('\\', '/')
                
                # 生成Markdown语法（height设为空，只使用width进行同比例调节）
                image_text = f'![{alt_text}]({relative_path} "{title}" width="{width}" height="")'
                
                cursor.insertText(image_text)
                self.editor.setTextCursor(cursor)
                self.editor.document().setModified(True)
                self.statusBar().showMessage('已插入网络图片')
                
                # 成功后关闭对话框
                dialog.accept()
                
            except Exception as e:
                logger.error(f"复制网络图片失败: {e}")
                QMessageBox.critical(self, '错误', f'保存图片失败: {str(e)}')
                # 删除临时文件
                try:
                    os.remove(temp_file_path)
                except:
                    pass
                return
        
        # 绑定按钮事件
        ok_btn.clicked.connect(validate_and_insert)
        cancel_btn.clicked.connect(dialog.reject)
        
        # 支持回车键提交
        url_input.returnPressed.connect(validate_and_insert)
        
        # 显示对话框
        dialog.exec()
    
    def _insert_image_from_local(self):
        """从本地插入图片"""
        # 直接继续执行图片插入流程（保存检查已在 insert_image 中完成）
        self._continue_insert_image()
    
    def _save_for_insert(self, dialog):
        """为插入图片保存文档"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        
        # 调用保存功能
        if self.current_file:
            # 已有文件，直接保存
            self.save_file()
        else:
            # 新文件，弹出保存对话框
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                '保存文件',
                '',
                'Markdown 文件 (*.md);;所有文件 (*)'
            )
            if file_path:
                # 确保文件扩展名为 .md
                if not file_path.endswith('.md'):
                    file_path += '.md'
                
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(self.editor.toPlainText())
                    self.current_file = file_path
                    # 更新窗口标题
                    filename = os.path.basename(file_path)
                    self.setWindowTitle(f'快乐马MarkDown编辑器 - {filename}')
                    self.editor.document().setModified(False)
                    self.statusBar().showMessage(f'已保存: {file_path}')
                except Exception as e:
                    QMessageBox.critical(self, '错误', f'保存失败: {str(e)}')
                    return
        
        # 关闭提示对话框并接受
        dialog.accept()
    
    def _continue_insert_image(self):
        """继续执行图片插入流程"""
        from PyQt6.QtWidgets import QFileDialog, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
        from PyQt6.QtGui import QImage
        import shutil
        
        cursor = self.editor.textCursor()
        
        # 先选择图片文件（只记录位置，不复制）
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '选择图片',
            '',
            '图片文件 (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;所有文件 (*)'
        )
        
        if not file_path:
            return  # 用户取消选择
        
        # 获取当前文档路径
        current_file = self.current_file
        
        # 创建图片目录路径（暂不创建）
        doc_dir = os.path.dirname(current_file)
        doc_name = os.path.splitext(os.path.basename(current_file))[0]
        image_dir = os.path.join(doc_dir, f'{doc_name}_图片')
        
        # 获取图片尺寸
        image = QImage(file_path)
        width = image.width()
        height = image.height()
        
        # 弹出确认对话框
        confirm_dialog = QDialog(self)
        confirm_dialog.setWindowTitle('插入本地图片')
        confirm_dialog.setFixedWidth(500)
        
        dialog_layout = QVBoxLayout()
        
        # 第一行：图片位置框（不可修改） + 选择文件按钮
        path_layout = QHBoxLayout()
        path_label = QLabel('图片位置:')
        path_label.setFixedWidth(80)
        path_input = QLineEdit(file_path)  # 显示原始文件路径
        path_input.setReadOnly(True)  # 不可修改
        path_input.setStyleSheet("background-color: #f0f0f0;")
        select_btn = QPushButton('选择文件')
        select_btn.setFixedWidth(80)
        
        # 存储选中的文件路径
        selected_file = [file_path]
        selected_width = [width]
        selected_height = [height]
        
        def reselect_file():
            """重新选择文件"""
            new_path, _ = QFileDialog.getOpenFileName(
                confirm_dialog,
                '选择图片',
                '',
                '图片文件 (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;所有文件 (*)'
            )
            if new_path:
                selected_file[0] = new_path
                path_input.setText(new_path)
                
                # 更新图片尺寸
                new_image = QImage(new_path)
                selected_width[0] = new_image.width()
                selected_height[0] = new_image.height()
        
        select_btn.clicked.connect(reselect_file)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(path_input)
        path_layout.addWidget(select_btn)
        dialog_layout.addLayout(path_layout)
        
        # 第二行：标题输入框（可选）
        title_layout = QHBoxLayout()
        title_label = QLabel('标题:')
        title_label.setFixedWidth(80)
        title_input = QLineEdit()
        title_input.setPlaceholderText('请输入图片标题（可选）')
        title_layout.addWidget(title_label)
        title_layout.addWidget(title_input)
        dialog_layout.addLayout(title_layout)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton('确定')
        ok_btn.setFixedWidth(80)
        ok_btn.setDefault(True)
        
        def on_confirm():
            """确认按钮点击事件"""
            # 创建图片目录
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)
            
            # 复制图片到目录
            image_filename = os.path.basename(selected_file[0])
            dest_path = os.path.join(image_dir, image_filename)
            
            # 如果文件已存在，添加序号
            if os.path.exists(dest_path):
                base_name, ext = os.path.splitext(image_filename)
                counter = 1
                while os.path.exists(dest_path):
                    new_filename = f'{base_name}_{counter}{ext}'
                    dest_path = os.path.join(image_dir, new_filename)
                    counter += 1
            
            try:
                shutil.copy2(selected_file[0], dest_path)
                
                # 生成相对路径
                rel_path = os.path.relpath(dest_path, doc_dir)
                # Windows下将反斜杠转换为正斜杠
                rel_path = rel_path.replace('\\', '/')
                
                # 获取标题
                title = title_input.text().strip()
                if not title:
                    title = '标题'
                
                # 生成带宽高的Markdown图片语法（height设为空，只使用width进行同比例调节）
                image_text = f'![{title}]({rel_path} "{title}" width="{selected_width[0]}" height="")'
                cursor.insertText(image_text)
                self.editor.setTextCursor(cursor)
                self.editor.document().setModified(True)
                self.statusBar().showMessage(f'已插入图片: {rel_path} ({selected_width[0]}x{selected_height[0]})')
                
                confirm_dialog.accept()
            except Exception as e:
                QMessageBox.critical(self, '错误', f'复制图片失败: {str(e)}')
                # 【关键】如果复制失败，删除已创建的目标文件（如果存在）
                try:
                    if os.path.exists(dest_path):
                        os.remove(dest_path)
                        logger.debug(f"已删除未完成的图片文件: {dest_path}")
                except:
                    pass
        
        ok_btn.clicked.connect(on_confirm)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.setFixedWidth(80)
        cancel_btn.clicked.connect(confirm_dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        dialog_layout.addLayout(btn_layout)
        confirm_dialog.setLayout(dialog_layout)
        
        # 设置焦点到标题输入框
        title_input.setFocus()
        
        # 显示对话框
        confirm_dialog.exec()
    
    def _get_image_dimensions(self, url):
        """获取网络图片尺寸 - 使用requests下载到临时文件后读取
        返回: (width, height, temp_file_path) 或 (None, None, None, error_message)
        """
        import tempfile
        import os
        import requests
        
        temp_file_path = None
        try:
            from PyQt6.QtGui import QImage
            
            logger.info(f"开始下载网络图片: {url}")
            
            # 【关键】验证URL格式
            from urllib.parse import urlparse
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                logger.warning(f"无效的URL格式: {url}")
                return None, None, None, '请输入有效的网址（以http://或https://开头）'
            
            # 【关键】完全模拟浏览器的请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site',
            }
            
            # 设置Referer为域名根路径（使用前面已解析的parsed）
            referer = f"{parsed.scheme}://{parsed.netloc}"
            headers['Referer'] = referer
            
            logger.debug(f"请求头 - Referer: {referer}")
            
            # 【关键】使用requests下载，超时保护（连接5秒，读取30秒）
            # connect timeout: 5秒（建立连接的时间）
            # read timeout: 30秒（下载数据的时间，大图片需要更多时间）
            response = requests.get(url, headers=headers, timeout=(5, 30), allow_redirects=True)
            
            # 检查HTTP状态码
            if response.status_code != 200:
                logger.warning(f"HTTP错误: {response.status_code}")
                return None, None, None, f'该网络图片不存在 (HTTP {response.status_code})'
            
            # 检查Content-Type
            content_type = response.headers.get('Content-Type', '')
            logger.info(f"Content-Type: {content_type}")
            
            if 'image' not in content_type.lower():
                logger.warning(f"服务器返回的不是图片: {content_type}")
                return None, None, None, f'服务器返回的不是图片 (Content-Type: {content_type})'
            
            data = response.content
            logger.info(f"下载数据大小: {len(data)} bytes")
            
            if len(data) == 0:
                logger.warning("下载的数据为空")
                return None, None, None, '该网络图片不存在或者网络不通'
            
            # 【关键】创建临时文件
            suffix = '.jpg'  # 默认扩展名
            if 'png' in content_type.lower():
                suffix = '.png'
            elif 'gif' in content_type.lower():
                suffix = '.gif'
            elif 'webp' in content_type.lower():
                suffix = '.webp'
            elif 'bmp' in content_type.lower():
                suffix = '.bmp'
            
            temp_file = tempfile.NamedTemporaryFile(
                mode='wb',
                suffix=suffix,
                prefix='mdeditor_img_',
                delete=False
            )
            temp_file_path = temp_file.name
            temp_file.write(data)
            temp_file.close()
            
            logger.debug(f"已保存到临时文件: {temp_file_path}")
            
            # 【关键】像本地图片一样读取尺寸
            image = QImage(temp_file_path)
            
            if image.isNull():
                logger.warning(f"无法解析图片文件: {temp_file_path}")
                # 删除临时文件
                try:
                    os.remove(temp_file_path)
                    logger.debug(f"已删除临时文件: {temp_file_path}")
                except:
                    pass
                
                return None, None, None, '该文件不是有效的图片格式'
            
            width, height = image.width(), image.height()
            logger.info(f"成功获取网络图片尺寸: {width}x{height}")
            
            # 【关键】不删除临时文件，留给后续插入逻辑使用
            return width, height, temp_file_path, None
                
        except requests.exceptions.Timeout:
            logger.warning(f"下载网络图片超时: {url}")
            # 清理临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass
            return None, None, None, '该网络图片不存在或者网络不通'
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"下载网络图片失败: {e}")
            # 清理临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass
            return None, None, None, '该网络图片不存在或者网络不通'
                
        except Exception as e:
            import traceback
            logger.warning(f"获取图片尺寸异常: {e}")
            logger.debug(traceback.format_exc())
            
            # 清理临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.debug(f"已删除临时文件: {temp_file_path}")
                except:
                    pass
            
            return None, None, None, f'获取图片失败: {str(e)}'
    
    def on_preview_zoom_changed(self, zoom):
        """当预览区缩放改变时触发 - 仅缩放宽度，文字大小不变"""
        self.preview_zoom = zoom
        # 不再使用 setZoomFactor，改为通过 CSS transform 和容器宽度控制
        self.update_preview_width()
        self.statusBar().showMessage(f'文档宽度: {zoom}%')
    
    def on_splitter_moved(self, pos, index):
        """当splitter移动时触发 - 限制预览区宽度"""
        try:
            # 【关键】防止递归调用
            if hasattr(self, '_adjusting_splitter') and self._adjusting_splitter:
                return
            
            # 【关键】检查预览区是否过宽，如果是则强制调整
            main_window_width = self.width()
            max_preview_width = int(main_window_width * 0.9)
            min_editor_width = int(main_window_width * 0.1)  # 编辑区至少10%
            
            # 获取当前splitter的尺寸
            if hasattr(self, 'centralWidget'):
                splitter = self.centralWidget()
                sizes = splitter.sizes()
                if len(sizes) == 2:
                    editor_width = sizes[0]
                    preview_width = sizes[1]
                    
                    # 如果预览区超过最大宽度，强制调整
                    if preview_width > max_preview_width:
                        self._adjusting_splitter = True  # 设置标志
                        # 设置新的尺寸：编辑区最小宽度，预览区最大宽度
                        new_sizes = [min_editor_width, max_preview_width]
                        splitter.setSizes(new_sizes)
                        self._adjusting_splitter = False  # 清除标志
                        logger.debug(f"Splitter调整: 编辑区={min_editor_width}px, 预览区={max_preview_width}px")
        except Exception as e:
            logger.error(f"Splitter移动处理失败: {e}")
    
    def update_preview_width(self):
        """更新预览区宽度 - 仅缩放宽席，文字大小不变"""
        try:
            # 获取容器的总宽度
            container_width = self.preview_container.width()
            
            # 【关键】计算目标宽度（基于缩放比例）
            target_width = int(container_width * self.preview_zoom / 100.0)
            
            # 【关键】限制预览区最大宽度，防止无限膨胀
            # 最小宽度：300px（保证基本可读性）
            # 最大宽度：窗口宽度的90%（保证编辑区至少有10%空间）
            main_window_width = self.width()
            min_preview_width = 300
            max_preview_width = int(main_window_width * 0.9)
            
            # 应用宽度限制
            target_width = max(min_preview_width, min(target_width, max_preview_width))
            
            # 设置preview的固定宽度
            self.preview.setFixedWidth(target_width)
            
            # 应用宽度约束
            self.apply_width_constraint()
            
            # 强制更新布局
            self.preview_container.updateGeometry()
            self.preview_container.update()
        except Exception as e:
            logger.error(f"更新预览宽度失败: {e}")
    
    def apply_width_constraint(self):
        """应用宽度约束到预览区 - 仅缩放宽席，文字大小不变"""
        try:
            # 获取当前目标宽度
            container_width = self.preview_container.width()
            target_width = int(container_width * self.preview_zoom / 100.0)
            
            # 通过 JavaScript 设置 body 的最大宽度
            js_code = f"""
                (function() {{
                    var body = document.body;
                    if (body) {{
                        // 设置最大宽度为容器宽度
                        body.style.maxWidth = '{target_width}px';
                        body.style.marginLeft = 'auto';
                        body.style.marginRight = 'auto';
                        
                        // 确保内容不会溢出
                        body.style.overflowX = 'hidden';
                    }}
                }})();
            """
            self.preview.page().runJavaScript(js_code)
        except Exception as e:
            logger.error(f"应用宽度约束失败: {e}")
        
    def create_main_area(self):
        """创建主编辑区域"""
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧编辑器
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(5, 5, 5, 5)  # 设置边距
        editor_layout.setSpacing(0)  # 移除间距
        
        editor_label = QLabel('编辑区')
        editor_label.setFont(QFont('微软雅黑', 10, QFont.Weight.Bold))
        editor_label.setStyleSheet("padding: 5px;")
        editor_layout.addWidget(editor_label)
        
        self.editor = QTextEdit()
        # 设置编辑器字体和行间距（符合源码编辑器规范）
        editor_font = QFont('Consolas', 14)
        editor_font.setFixedPitch(True)  # 等宽字体
        self.editor.setFont(editor_font)
        
        # 设置行间距为1.5倍（更舒适的阅读体验）
        from PyQt6.QtGui import QTextBlockFormat
        block_format = QTextBlockFormat()
        # PyQt6 中使用整数值：ProportionalHeight = 1
        block_format.setLineHeight(150, 1)  # 1 = ProportionalHeight
        cursor = self.editor.textCursor()
        cursor.select(cursor.SelectionType.Document)
        cursor.mergeBlockFormat(block_format)
        cursor.clearSelection()
        self.editor.setTextCursor(cursor)
        
        # 设置字符格式（优化阅读体验）
        char_format = QTextCharFormat()
        char_format.setFontLetterSpacing(100)  # 正常字符间距
        self.editor.setCurrentCharFormat(char_format)
        
        # 设置占位符文本
        self.editor.setPlaceholderText('请在这里编辑或粘贴MarkDown文本')
        # 添加与预览区相同的1像素边框样式
        editor_bg_color = self.editor.palette().color(self.editor.backgroundRole()).name()
        self.editor.setStyleSheet(f"""
            QTextEdit {{
                border: 1px solid #d0d0d0;
                line-height: 1.5;
                padding: 8px;
            }}
        """)
        self.editor.textChanged.connect(self.update_preview)
        editor_layout.addWidget(self.editor, 1)  #  stretch=1 让编辑器占据所有剩余空间
        
        splitter.addWidget(editor_widget)
        
        # 右侧预览区（使用WebEngineView渲染HTML）
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        # 设置与编辑区相同的上边距，确保上下边框对齐
        preview_layout.setContentsMargins(5, 5, 5, 5)
        preview_layout.setSpacing(0)  # 移除间距
        
        preview_label = QLabel('预览区 - 拖曳文件到这里')
        preview_label.setFont(QFont('微软雅黑', 10, QFont.Weight.Bold))
        preview_label.setStyleSheet("padding: 5px;")
        preview_layout.addWidget(preview_label)
        
        # 创建一个容器widget来控制WebEngineView的宽度
        self.preview_container = QWidget()
        # 使用与编辑器相同的背景色，并添加1像素细线边框（无圆角）
        editor_bg_color = self.editor.palette().color(self.editor.backgroundRole()).name()
        self.preview_container.setStyleSheet(f"""
            background-color: {editor_bg_color};
            border: 1px solid #d0d0d0;
        """)
        container_layout = QHBoxLayout(self.preview_container)
        # 设置内边距，确保HTML内容不会遮挡边框
        container_layout.setContentsMargins(3, 3, 3, 3)
        container_layout.setSpacing(0)
        
        # 添加弹性空间（左侧）
        container_layout.addStretch()
        
        # 使用支持拖放的WebView
        self.preview = DropWebView(parent=self)
        self.preview.setMinimumHeight(400)  # 设置最小高度
        self.preview.setMinimumWidth(300)  # 设置最小宽度
        container_layout.addWidget(self.preview)
        
        # 添加弹性空间（右侧）
        container_layout.addStretch()
        
        preview_layout.addWidget(self.preview_container, 1)  # stretch=1 让预览器占据所有剩余空间
        
        splitter.addWidget(preview_widget)
        
        # 设置初始比例：编辑区40%，预览区60%（2:3）
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        
        # 设置初始大小（窗口宽度的2:3比例）
        total_width = 1350
        splitter.setSizes([int(total_width * 0.4), int(total_width * 0.6)])
        
        # 确保splitter均匀分配高度
        splitter.setHandleWidth(3)  # 分隔条宽度
        
        # 【关键】连接splitter的移动信号，限制预览区宽度
        splitter.splitterMoved.connect(self.on_splitter_moved)
        
        # 连接编辑区滚动信号到槽函数
        self.editor.verticalScrollBar().valueChanged.connect(self.on_editor_scroll)
        
        # 连接页面加载完成信号
        self.preview.page().loadFinished.connect(self.on_page_loaded)
        
        # 初始化预览区宽度
        self.update_preview_width()
        
        self.setCentralWidget(splitter)
    
    def on_page_loaded(self, ok):
        """页面加载完成"""
        if ok:
            self.page_loaded = True
            # 【新增】取消渲染超时定时器并关闭提示框
            self._cancel_render_timeout()
            
            # 如果需要恢复滚动位置，立即执行
            if self.need_restore_scroll:
                self.need_restore_scroll = False
                self._restore_preview_scroll()
            
            # 应用当前的宽度限制（确保缩放生效）
            self.apply_width_constraint()
    
    def on_editor_scroll(self, value):
        """当编辑区滚动时，同步滚动预览区"""
        try:
            # 只有当鼠标在编辑区时才同步到预览区
            if not self.mouse_in_editor:
                return
            
            # 设置标志，防止循环触发
            if hasattr(self, '_syncing') and self._syncing:
                return
            
            editor_scroll = self.editor.verticalScrollBar()
            editor_max = editor_scroll.maximum()
            
            if editor_max <= 0:
                return
            
            scroll_ratio = value / editor_max
            self._syncing = True
            QTimer.singleShot(10, lambda: self._sync_scroll(scroll_ratio))
            QTimer.singleShot(50, lambda: setattr(self, '_syncing', False))
        except Exception as e:
            pass
    
    def _sync_scroll(self, scroll_ratio):
        """实际执行滚动同步"""
        try:
            js_code = f"""
                (function() {{
                    var targetScroll = {scroll_ratio} * (document.documentElement.scrollHeight - window.innerHeight);
                    window.scroll({{ top: targetScroll, left: 0, behavior: 'auto' }});
                    document.scrollingElement.scrollTop = targetScroll;
                }})();
            """
            self.preview.page().runJavaScript(js_code)
        except Exception as e:
            pass
    
    def _sync_preview_to_editor(self):
        """从预览区同步滚动到编辑区（增加防抖机制）"""
        try:
            # 【优化6】只有当鼠标在预览区时才同步到编辑区
            if not self.mouse_in_preview:
                return
            
            # 设置标志，防止循环触发
            if hasattr(self, '_syncing') and self._syncing:
                return
            
            # 【优化6】增加防抖：如果上次同步在50ms内，则跳过
            import time
            current_time = time.time()
            if hasattr(self, '_last_sync_time'):
                if current_time - self._last_sync_time < 0.05:  # 50ms防抖
                    return
            self._last_sync_time = current_time
            
            # 获取预览区的滚动比例
            js_code = """
                (function() {
                    if (typeof window._previewScrollRatio !== 'undefined') {
                        return window._previewScrollRatio;
                    }
                    return -1;
                })();
            """
            
            def callback(scroll_ratio):
                if scroll_ratio is not None and scroll_ratio >= 0:
                    # 设置同步标志
                    self._syncing = True
                    
                    # 同步到编辑区
                    editor_scroll = self.editor.verticalScrollBar()
                    editor_max = editor_scroll.maximum()
                    if editor_max > 0:
                        target_value = int(scroll_ratio * editor_max)
                        editor_scroll.setValue(target_value)
                    
                    # 50ms 后解除同步标志
                    QTimer.singleShot(50, lambda: setattr(self, '_syncing', False))
            
            self.preview.page().runJavaScript(js_code, callback)
        except Exception as e:
            pass
        
    def update_preview(self):
        """更新预览"""
        try:
            markdown_text = self.editor.toPlainText()
            
            if not markdown_text.strip():
                self.preview.setHtml('<html><body style="font-family: 微软雅黑; padding: 20px;"></body></html>')
                # 文档为空，禁用导出按钮
                self._update_export_buttons_state(False)
                # 【新增】取消渲染超时定时器
                self._cancel_render_timeout()
                return
            
            # 文档不为空，启用导出按钮
            self._update_export_buttons_state(True)
            
            # 【新增】启动渲染超时定时器（1秒后如果未完成则显示提示）
            self._start_render_timeout()
            
            # 预处理：将转义的HTML实体（如 \&amp;）转换为普通文本
            # 这样markdown解析器会保留它们，然后我们再统一解码
            import re
            # 匹配 \&amp;, \&lt;, \&gt;, \&quot;, \&#数字; 等转义的HTML实体
            # 先处理 \&\#数字; 这种双重转义的情况
            markdown_text = re.sub(r'\\&\\(#\d+;)', r'&\1', markdown_text)
            # 再处理其他单层转义的情况
            markdown_text = re.sub(r'\\(&amp;|&lt;|&gt;|&quot;)', r'\1', markdown_text)
            
            # 处理脚注：先处理脚注定义，再处理脚注标记
            # 处理脚注定义：\[^1\]: 内容 -> [^1]: 内容
            markdown_text = re.sub(r'\\\[\^(\d+)\\\]:', r'[^\1]:', markdown_text)
            # 处理脚注标记：\[^1\] -> [^1]
            markdown_text = re.sub(r'\\\[\^(\d+)\\\]', r'[^\1]', markdown_text)
            
            # 移除脚注定义后的多余空行，避免 nl2br 产生多余的 <br>
            markdown_text = re.sub(r'(\[^\d+\]:.+?)\n\s*\n', r'\1\n', markdown_text)
            
            # 处理删除线语法：~~文本~~ -> <del>文本</del>
            # 注意：需要在 Markdown 解析之前处理
            markdown_text = re.sub(r'~~(.+?)~~', r'<del>\1</del>', markdown_text)
            
            # === 预处理：提取并保护数学公式和 Mermaid 图表 ===
            # 1. 先提取 Mermaid 代码块（避免公式提取干扰）
            mermaid_blocks = []
            def save_mermaid_block(match):
                mermaid_code = match.group(1)  # 获取代码内容（第一个捕获组）
                mermaid_blocks.append(mermaid_code)
                return f'<!-- MERMAID_BLOCK_{len(mermaid_blocks)-1} -->'
            
            markdown_text = re.sub(r'```mermaid\s*\n(.*?)```', save_mermaid_block, markdown_text, flags=re.DOTALL)
            
            # 2. 提取块级公式 $$...$$ 或 \[...\]
            block_formulas = []
            def save_block_formula(match):
                block_formulas.append(match.group(0))
                return f'<!-- BLOCK_FORMULA_{len(block_formulas)-1} -->'
            
            # 支持 $$...$$ 和 \[...\] 两种语法
            markdown_text = re.sub(r'\$\$(.+?)\$\$', save_block_formula, markdown_text, flags=re.DOTALL)
            markdown_text = re.sub(r'\\\[(.+?)\\\]', save_block_formula, markdown_text, flags=re.DOTALL)
            
            # 3. 提取行内公式 $...$ 或 \(...\)
            inline_formulas = []
            def save_inline_formula(match):
                inline_formulas.append(match.group(0))
                return f'<!-- INLINE_FORMULA_{len(inline_formulas)-1} -->'
            
            # 支持 $...$ 和 \(...\) 两种语法
            # 更严格的正则：要求公式内容至少包含一个非中文字符，避免误匹配图片alt等
            markdown_text = re.sub(r'(?<!\$)\$(?!\$)([^$\n]{1,200}?)(?<!\$)\$(?!\$)', save_inline_formula, markdown_text)
            markdown_text = re.sub(r'\\\(([^)]{1,200}?)\\\)', save_inline_formula, markdown_text)
            
            # 转换为HTML
            # 注意：footnotes 扩展需要在 nl2br 之前处理，避免脚注定义被错误转换
            # extra 已包含: abbr, def_list, attr_list
            html_content = markdown.markdown(
                markdown_text, 
                extensions=['footnotes', 'extra', 'codehilite', 'tables', 'fenced_code', 'nl2br', 'attr_list', 'def_list', 'abbr']
            )
            
            # 为所有链接添加 target="_blank" 属性
            import re as link_re
            # 匹配 <a href="..."> 标签，如果已经有 target 属性则跳过
            def add_target_blank(match):
                full_tag = match.group(0)
                # 如果已经有 target 属性，不修改
                if 'target=' in full_tag:
                    return full_tag
                # 在 <a 后面添加 target="_blank"
                return full_tag.replace('<a ', '<a target="_blank" ', 1)
            
            html_content = link_re.sub(r'<a\s+href=[^>]+>', add_target_blank, html_content)
            
            # 清理脚注区域中多余的 <br> 标签
            import re as html_re
            # 移除脚注列表项末尾的 <br> 标签
            html_content = html_re.sub(r'(<li[^>]*>.*?)(?:<br\s*/?>\s*)+</li>', r'\1</li>', html_content, flags=html_re.DOTALL)
            # 移除脚注容器末尾的多余 <br>
            html_content = html_re.sub(r'(<div class="footnotes"[^>]*>.*?)(?:<br\s*/?>\s*)+</div>', r'\1</div>', html_content, flags=html_re.DOTALL)
            
            # 解码HTML实体（将 &amp; 转换为 &，&lt; 转换为 <，&gt; 转换为 > 等）
            html_content = html.unescape(html_content)
            
            # 处理 Emoji 短代码：将 :emoji: 转换为 Unicode emoji
            emoji_map = {
                ':smile:': '😊', ':heart:': '❤️', ':star:': '⭐', ':thumbsup:': '👍',
                ':rocket:': '🚀', ':fire:': '🔥', ':sparkles:': '✨', ':check:': '✅',
                ':x:': '❌', ':warning:': '⚠️', ':bulb:': '💡', ':book:': '📚',
                ':pencil:': '✏️', ':computer:': '💻', ':phone:': '📱', ':camera:': '📷',
                ':muscle:': '💪', ':pray:': '🙏', ':clap:': '👏', ':tada:': '🎉',
                ':gift:': '🎁', ':trophy:': '🏆', ':medal:': '🏅', ':flag:': '🚩',
                ':home:': '🏠', ':office:': '🏢', ':school:': '🏫', ':hospital:': '🏥',
                ':sun:': '☀️', ':moon:': '🌙', ':cloud:': '☁️', ':rainbow:': '🌈',
                ':coffee:': '☕', ':beer:': '🍺', ':pizza:': '🍕', ':apple:': '🍎',
                ':dog:': '🐶', ':cat:': '🐱', ':bird:': '🐦', ':fish:': '🐟',
                ':car:': '🚗', ':bike:': '🚲', ':airplane:': '✈️', ':train:': '🚂',
                ':love:': '😍', ':laughing:': '😆', ':cry:': '😢', ':angry:': '😠',
                ':thinking:': '🤔', ':sleeping:': '😴', ':cool:': '😎', ':wink:': '😉',
            }
            
            for short_code, emoji_char in emoji_map.items():
                html_content = html_content.replace(short_code, emoji_char)
            
            # 清理代码元素中多余的反斜杠
            import re as html_re2
            # 移除 <code> 标签中的 \.\(\) 等转义反斜杠
            def clean_code_backslashes(match):
                code_content = match.group(1)
                # 移除常见的转义反斜杠
                code_content = code_content.replace('\\.', '.').replace('\\(', '(').replace('\\)', ')')
                code_content = code_content.replace('\\!', '!').replace('\\-', '-').replace('\\#', '#')
                return f'<code>{code_content}</code>'
            html_content = html_re2.sub(r'<code>(.*?)</code>', clean_code_backslashes, html_content)
            
            # 处理任务列表：将 [ ] 和 [x] 转换为 checkbox
            # 匹配 <li><p>[ ] 或 <li><p>[x] 或 <li>[ ] 或 <li>[x]
            def convert_task_list(match):
                li_and_p = match.group(1)  # <li><p> 或 <li>
                checkbox_mark = match.group(2)  # 空格 或 x/X
                text = match.group(3)  # 剩余文本
                
                if checkbox_mark.strip() == '':
                    # 未完成任务
                    return f'{li_and_p}<input type="checkbox" disabled> {text}'
                elif checkbox_mark.strip().lower() == 'x':
                    # 已完成任务
                    return f'{li_and_p}<input type="checkbox" checked disabled> {text}'
                else:
                    # 不是任务列表，保持原样
                    return match.group(0)
            
            # 先尝试匹配 <li><p>[x] 或 <li><p>[ ]
            html_content = html_re2.sub(r'(<li[^>]*>\s*<p[^>]*>)\[([ xX])\]\s*(.+?)', convert_task_list, html_content)
            # 再尝试匹配 <li>[x] 或 <li>[ ]（没有<p>标签的情况）
            html_content = html_re2.sub(r'(<li[^>]*>)\[([ xX])\]\s*(.+?)', convert_task_list, html_content)
            
            # === 后处理：恢复数学公式和 Mermaid 图表 ===
            # 调试：打印提取的公式数量
            if block_formulas or inline_formulas:
                logger.info(f"提取到 {len(block_formulas)} 个块级公式, {len(inline_formulas)} 个行内公式")
            
            # 1. 恢复块级公式 - 直接传递纯 LaTeX 内容，不添加 \[\] 标记
            for i, formula in enumerate(block_formulas):
                # 去除 $$ 或 \[\]
                if formula.startswith('$$'):
                    formula_content = formula[2:-2]
                else:  # \[...\]
                    formula_content = formula[2:-2]
                placeholder = f'<!-- BLOCK_FORMULA_{i} -->'
                html_content = html_content.replace(
                    placeholder,
                    f'<div class="math-block">{formula_content}</div>'
                )
            
            # 2. 恢复行内公式 - 直接传递纯 LaTeX 内容，不添加 \(\) 标记
            for i, formula in enumerate(inline_formulas):
                # 去除 $ 或 \(\)
                if formula.startswith('$'):
                    formula_content = formula[1:-1]
                else:  # \(...\)
                    formula_content = formula[2:-2]
                placeholder = f'<!-- INLINE_FORMULA_{i} -->'
                html_content = html_content.replace(
                    placeholder,
                    f'<span class="math-inline">{formula_content}</span>'
                )
            
            # 3. 恢复 Mermaid 图表
            for i, mermaid_code in enumerate(mermaid_blocks):
                placeholder = f'<!-- MERMAID_BLOCK_{i} -->'
                # 对 Mermaid 代码进行 HTML 转义
                escaped_code = html.escape(mermaid_code.strip())
                html_content = html_content.replace(
                    placeholder,
                    f'<div class="mermaid">{escaped_code}</div>'
                )
            
            # 获取当前风格的CSS
            style_css = self.get_style_css()
            
            # 完整的HTML文档
            full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <!-- KaTeX CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css"
          onerror="this.onerror=null; addDebug('ERROR: Failed to load KaTeX CSS from CDN')">
    <!-- KaTeX JS -->
    <script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"
            onerror="this.onerror=null; addDebug('ERROR: Failed to load KaTeX JS from CDN')"></script>
    <!-- Mermaid JS -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js"
            onerror="this.onerror=null; addDebug('ERROR: Failed to load Mermaid JS from CDN')"></script>
    <style>
{style_css}
    </style>
</head>
<body>
<div class="markdown-body">
{html_content}
</div>

<script>
// 创建调试信息面板（默认隐藏）
var debugPanel = document.createElement('div');
debugPanel.style.cssText = 'position: fixed; top: 10px; right: 10px; background: rgba(0,0,0,0.8); color: #0f0; padding: 10px; font-size: 12px; z-index: 9999; max-height: 300px; overflow-y: auto; display: none;';
debugPanel.innerHTML = '<b>调试信息:</b><br>';
document.body.appendChild(debugPanel);

// 按 Ctrl+Shift+D 切换调试面板显示/隐藏
document.addEventListener('keydown', function(e) {{
    if (e.ctrlKey && e.shiftKey && e.key === 'D') {{
        e.preventDefault();
        if (debugPanel.style.display === 'none') {{
            debugPanel.style.display = 'block';
        }} else {{
            debugPanel.style.display = 'none';
        }}
    }}
}});

function addDebug(msg) {{
    debugPanel.innerHTML += msg + '<br>';
    console.log(msg);
}}

addDebug('Script started');

// 检查库是否加载
function checkLibraries() {{
    var katexLoaded = typeof katex !== 'undefined';
    var mermaidLoaded = typeof mermaid !== 'undefined';
    addDebug('KaTeX loaded: ' + katexLoaded);
    addDebug('Mermaid loaded: ' + mermaidLoaded);
    return katexLoaded && mermaidLoaded;
}}

// 初始化 Mermaid
if (typeof mermaid !== 'undefined') {{
    addDebug('Initializing Mermaid');
    mermaid.initialize({{ 
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'loose'
    }});
}} else {{
    addDebug('WARNING: Mermaid not loaded yet');
}}

// 渲染 Mermaid 图表
async function renderMermaid() {{
    if (typeof mermaid === 'undefined') {{
        addDebug('ERROR: Mermaid not available');
        return;
    }}
    addDebug('Rendering Mermaid diagrams...');
    const mermaidElements = document.querySelectorAll('.mermaid');
    addDebug('Found ' + mermaidElements.length + ' mermaid elements');
    for (const element of mermaidElements) {{
        try {{
            const graphDefinition = element.textContent;
            const {{ svg }} = await mermaid.render('mermaid-' + Math.random().toString(36).substr(2, 9), graphDefinition);
            element.innerHTML = svg;
        }} catch (error) {{
            addDebug('Mermaid error: ' + error.message);
            element.innerHTML = '<pre style="color: red;">图表渲染失败: ' + error.message + '</pre>';
        }}
    }}
}}

// 渲染 KaTeX 公式
function renderMath() {{
    if (typeof katex === 'undefined') {{
        addDebug('ERROR: KaTeX not available - formulas will NOT be rendered');
        // 显示友好提示
        var mathBlocks = document.querySelectorAll('.math-block');
        var mathInline = document.querySelectorAll('.math-inline');
        mathBlocks.forEach(function(el) {{
            el.innerHTML = '<div style="color: #ff6b6b; padding: 10px; background: #fff5f5; border-left: 3px solid #ff6b6b;">⚠️ 公式渲染失败：KaTeX 库未加载<br><small>请检查网络连接，或按 Ctrl+Shift+D 查看详细信息</small></div>';
        }});
        mathInline.forEach(function(el) {{
            el.innerHTML = '<span style="color: #ff6b6b; background: #fff5f5; padding: 2px 4px;">⚠️公式</span>';
        }});
        return;
    }}
    addDebug('✓ KaTeX is available, version: ' + (katex.version || 'unknown'));
    addDebug('Rendering math formulas...');
    
    // 渲染块级公式
    const blockFormulas = document.querySelectorAll('.math-block');
    addDebug('Found ' + blockFormulas.length + ' block formulas');
    let blockSuccess = 0;
    let blockFailed = 0;
    blockFormulas.forEach((element, index) => {{
        try {{
            let tex = element.textContent.trim();
            addDebug('Block formula ' + (index+1) + ': ' + tex.substring(0, 50));
            katex.render(tex, element, {{
                displayMode: true,
                throwOnError: false,
                errorColor: '#ff6b6b'
            }});
            blockSuccess++;
            addDebug('✓ Block formula ' + (index+1) + ' rendered');
        }} catch (error) {{
            blockFailed++;
            addDebug('✗ KaTeX block error: ' + error.message);
            element.innerHTML = '<span style="color: red;">公式渲染失败: ' + error.message + '</span>';
        }}
    }});
    addDebug('Block formulas result: ' + blockSuccess + ' success, ' + blockFailed + ' failed');
    
    // 渲染行内公式
    const inlineFormulas = document.querySelectorAll('.math-inline');
    addDebug('Found ' + inlineFormulas.length + ' inline formulas');
    let inlineSuccess = 0;
    let inlineFailed = 0;
    inlineFormulas.forEach((element, index) => {{
        try {{
            let tex = element.textContent.trim();
            if (index < 5) {{
                addDebug('Inline formula ' + (index+1) + ': ' + tex.substring(0, 50));
            }}
            katex.render(tex, element, {{
                displayMode: false,
                throwOnError: false,
                errorColor: '#ff6b6b'
            }});
            inlineSuccess++;
        }} catch (error) {{
            inlineFailed++;
            if (index < 5) {{
                addDebug('✗ KaTeX inline error: ' + error.message);
            }}
            element.innerHTML = '<span style="color: red;">公式</span>';
        }}
    }});
    addDebug('Inline formulas result: ' + inlineSuccess + ' success, ' + inlineFailed + ' failed');
    addDebug('Total: ' + (blockSuccess + inlineSuccess) + ' rendered, ' + (blockFailed + inlineFailed) + ' failed');
}}

// 立即执行渲染（延迟确保DOM和库都准备好）
setTimeout(function() {{
    addDebug('Timeout triggered, checking libraries...');
    if (checkLibraries()) {{
        addDebug('All libraries loaded, starting render');
        renderMath();
        renderMermaid();
        addDebug('Render functions called');
        
        // 处理任务列表样式
        styleTaskLists();
        
        // 延迟检查渲染结果
        setTimeout(function() {{
            var mathBlocks = document.querySelectorAll('.math-block');
            var mathInline = document.querySelectorAll('.math-inline');
            addDebug('--- After rendering ---');
            addDebug('Block formulas rendered: ' + mathBlocks.length);
            addDebug('Inline formulas rendered: ' + mathInline.length);
            
            // 检查第一个块级公式的HTML内容
            if (mathBlocks.length > 0) {{
                var firstBlock = mathBlocks[0];
                var hasKatexClass = firstBlock.querySelector('.katex') !== null;
                var hasSVG = firstBlock.querySelector('svg') !== null;
                var katexElement = firstBlock.querySelector('.katex');
                addDebug('First block has .katex class: ' + hasKatexClass);
                addDebug('First block has SVG: ' + hasSVG);
                addDebug('First block innerHTML length: ' + firstBlock.innerHTML.length);
                
                if (katexElement) {{
                    var computedStyle = window.getComputedStyle(katexElement);
                    addDebug('Katex color: ' + computedStyle.color);
                    addDebug('Katex fontSize: ' + computedStyle.fontSize);
                    addDebug('Katex display: ' + computedStyle.display);
                }}
                
                // 高亮显示公式区域
                firstBlock.style.border = '1px solid red';
                firstBlock.style.padding = '10px';
                firstBlock.style.backgroundColor = 'rgba(255, 255, 0, 0.1)';
            }}
        }}, 500);
    }} else {{
        addDebug('ERROR: Libraries not loaded, retrying in 1s...');
        setTimeout(function() {{
            if (checkLibraries()) {{
                renderMath();
                renderMermaid();
            }} else {{
                addDebug('ERROR: Still not loaded after retry');
            }}
        }}, 1000);
    }}
}}, 500);

// 处理任务列表样式
function styleTaskLists() {{
    console.log('Styling task lists...');
    var checkboxes = document.querySelectorAll('li input[type="checkbox"]');
    console.log('Found', checkboxes.length, 'checkboxes');
    
    checkboxes.forEach(function(checkbox) {{
        var li = checkbox.closest('li');
        var p = checkbox.parentElement;
        
        if (checkbox.checked) {{
            // 已完成任务：添加删除线和灰色
            if (p && p.tagName === 'P') {{
                p.style.textDecoration = 'line-through';
                p.style.color = '#6c757d';
                p.style.opacity = '0.7';
            }}
            if (li) {{
                li.style.color = '#6c757d';
            }}
            console.log('Styled completed task');
        }} else {{
            // 未完成任务：正常显示
            console.log('Styled incomplete task');
        }}
    }});
}}

// 监听预览区滚动，同步到编辑区
var lastScrollRatio = -1;
var scrollCheckInterval = setInterval(function() {{
    var scrollTop = window.scrollY || document.documentElement.scrollTop;
    var scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (scrollHeight > 0) {{
        var scrollRatio = scrollTop / scrollHeight;
        // 只有当滚动比例变化超过阈值时才同步
        if (Math.abs(scrollRatio - lastScrollRatio) > 0.01) {{
            lastScrollRatio = scrollRatio;
            // 将滚动比例存储到全局变量，供 Python 读取
            window._previewScrollRatio = scrollRatio;
        }}
    }}
}}, 50);  // 每 50ms 检查一次

addDebug('Script ended');
</script>
</body>
</html>
"""
            
            # 先保存滚动位置，然后在callback中设置HTML和恢复
            self._save_and_update_preview(full_html)
            
        except Exception as e:
            logger.error(f"预览更新错误: {e}")

    def _save_and_update_preview(self, full_html):
        """保存滚动位置并更新预览"""
        try:
            js_code = """
                (function() {
                    return document.scrollingElement.scrollTop;
                })();
            """
            def callback(position):
                if position is not None:
                    self.preview_scroll_position = position
                    
                    # 设置HTML
                    # 如果有当前文件，设置 Base URL 以便加载相对路径的图片
                    if self.current_file:
                        from PyQt6.QtCore import QUrl
                        current_dir = os.path.dirname(os.path.abspath(self.current_file))
                        base_url = QUrl.fromLocalFile(current_dir + '/')
                        self.preview.setHtml(full_html, base_url)
                    else:
                        self.preview.setHtml(full_html)
                    
                    # 标记需要在页面加载完成后恢复滚动位置
                    if self.preview_scroll_position > 0:
                        self.need_restore_scroll = True
            
            self.preview.page().runJavaScript(js_code, callback)
        except Exception as e:
            logger.error(f"保存并更新预览失败: {e}")
    
    def _save_preview_scroll(self):
        """保存预览区滚动位置"""
        try:
            js_code = """
                (function() {
                    return document.scrollingElement.scrollTop;
                })();
            """
            def callback(position):
                if position is not None:
                    self.preview_scroll_position = position
            
            self.preview.page().runJavaScript(js_code, callback)
        except:
            pass
    
    def _restore_preview_scroll(self):
        """恢复预览区滚动位置"""
        try:
            if self.preview_scroll_position > 0:
                js_code = f"""
                    (function() {{
                        document.scrollingElement.scrollTop = {self.preview_scroll_position};
                        window.scrollTo(0, {self.preview_scroll_position});
                    }})();
                """
                self.preview.page().runJavaScript(js_code)
        except:
            pass
    
    def _update_export_buttons_state(self, enabled):
        """更新导出按钮和工具栏控件的启用状态
        
        Args:
            enabled: True-启用，False-禁用
        """
        # 更新导出按钮
        if hasattr(self, 'export_pdf_action'):
            self.export_pdf_action.setEnabled(enabled)
        if hasattr(self, 'export_long_image_action'):
            self.export_long_image_action.setEnabled(enabled)
        if hasattr(self, 'export_image_collection_action'):
            self.export_image_collection_action.setEnabled(enabled)
        
        # 更新工具栏控件
        if hasattr(self, 'style_combo'):
            self.style_combo.setEnabled(enabled)
        if hasattr(self, 'font_family_combo'):
            self.font_family_combo.setEnabled(enabled)
        if hasattr(self, 'font_size_spinbox'):
            self.font_size_spinbox.setEnabled(enabled)
        if hasattr(self, 'font_weight_combo'):
            self.font_weight_combo.setEnabled(enabled)
        if hasattr(self, 'preview_zoom_spinbox'):
            self.preview_zoom_spinbox.setEnabled(enabled)
        if hasattr(self, 'pdf_ratio_combo'):
            self.pdf_ratio_combo.setEnabled(enabled)
        # 【新增】更新方向下拉框
        if hasattr(self, 'pdf_orientation_combo'):
            self.pdf_orientation_combo.setEnabled(enabled)
    
    def _start_render_timeout(self):
        """【新增】启动渲染超时定时器（1秒后如果未完成则显示提示）"""
        try:
            # 先取消之前的定时器（如果有）
            self._cancel_render_timeout()
            
            # 创建新的定时器
            self.render_timeout_timer = QTimer(self)
            self.render_timeout_timer.setSingleShot(True)  # 只触发一次
            self.render_timeout_timer.timeout.connect(self._on_render_timeout)
            self.render_timeout_timer.start(1000)  # 1秒超时
            
            logger.debug("已启动渲染超时定时器")
        except Exception as e:
            logger.error(f"启动渲染超时定时器失败: {e}")
    
    def _cancel_render_timeout(self):
        """【新增】取消渲染超时定时器并关闭提示框"""
        try:
            # 停止定时器
            if self.render_timeout_timer is not None:
                self.render_timeout_timer.stop()
                self.render_timeout_timer.deleteLater()
                self.render_timeout_timer = None
                logger.debug("已取消渲染超时定时器")
            
            # 关闭提示框
            if self.render_progress_dialog is not None:
                self.render_progress_dialog.close()
                self.render_progress_dialog.deleteLater()
                self.render_progress_dialog = None
                logger.debug("已关闭渲染进度提示框")
        except Exception as e:
            logger.error(f"取消渲染超时定时器失败: {e}")
    
    def _on_render_timeout(self):
        """【新增】渲染超时回调 - 显示带进度条动画的提示框"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
            from PyQt6.QtCore import Qt, QTimer
            
            logger.info("文档渲染超时，显示带进度条的提示框")
            
            # 创建提示对话框
            self.render_progress_dialog = QDialog(self)
            self.render_progress_dialog.setWindowTitle('请稍候')
            self.render_progress_dialog.setModal(False)  # 非模态，不阻塞UI
            self.render_progress_dialog.setFixedSize(400, 150)
            
            layout = QVBoxLayout()
            
            # 提示信息
            hint_label = QLabel('正在渲染文档，请稍候...')
            hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hint_label.setStyleSheet("""
                font-size: 14px;
                padding: 10px;
                color: #333;
            """)
            layout.addWidget(hint_label)
            
            # 【新增】进度条（不确定模式，显示动画）
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 0)  # 设置为不确定模式（循环动画）
            progress_bar.setTextVisible(False)  # 不显示百分比文字
            progress_bar.setFixedHeight(8)
            progress_bar.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 4px;
                    background-color: #e0e0e0;
                }
                QProgressBar::chunk {
                    background-color: #4a90e2;
                    border-radius: 4px;
                }
            """)
            layout.addWidget(progress_bar)
            
            # 添加小提示文字
            tip_label = QLabel('大文档或首次渲染可能需要更多时间')
            tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tip_label.setStyleSheet("""
                font-size: 11px;
                color: #999;
                padding: 5px;
            """)
            layout.addWidget(tip_label)
            
            self.render_progress_dialog.setLayout(layout)
            
            # 显示对话框（居中）
            self.render_progress_dialog.show()
            
            # 将对话框移动到屏幕中央
            screen_geometry = self.screen().geometry()
            dialog_geometry = self.render_progress_dialog.geometry()
            x = (screen_geometry.width() - dialog_geometry.width()) // 2
            y = (screen_geometry.height() - dialog_geometry.height()) // 2
            self.render_progress_dialog.move(x, y)
            
        except Exception as e:
            logger.error(f"显示渲染超时提示框失败: {e}")
    
    def clear_highlight(self):
        """清除编辑区的高亮"""
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(QTextCharFormat())  # 清除所有格式
    
    def highlight_in_editor(self, selected_text):
        """在编辑区高亮选中的文本"""
        if not selected_text or not selected_text.strip():
            return
        
        try:
            # 先清除之前的高亮
            self.clear_highlight()
            
            # 获取编辑区的全文
            full_text = self.editor.toPlainText()
            
            # 查找选中的文本
            pos = full_text.find(selected_text)
            
            if pos != -1:
                # 创建光标并选择文本
                cursor = self.editor.textCursor()
                cursor.setPosition(pos)
                cursor.setPosition(pos + len(selected_text), QTextCursor.MoveMode.KeepAnchor)
                
                # 应用高亮格式
                cursor.mergeCharFormat(self.highlight_format)
                
                # 设置光标位置，确保可见
                self.editor.setTextCursor(cursor)
                self.editor.ensureCursorVisible()
                
                # 滚动到该行
                line_num = full_text[:pos].count('\n')
                block = self.editor.document().findBlockByNumber(line_num)
                if block.isValid():
                    cursor.setPosition(block.position())
                    self.editor.setTextCursor(cursor)
                    self.editor.centerCursor() if hasattr(self.editor, 'centerCursor') else self.editor.ensureCursorVisible()
        except Exception as e:
            logger.error(f"高亮失败: {e}")
            
    def new_file(self):
        """新建文件"""
        if self.maybe_save():
            self.editor.clear()
            self.current_file = None
            self.saved_md5 = None  # 重置 MD5
            self.setWindowTitle('快乐马MarkDown编辑器 - 无标题')
            self.statusBar().showMessage('新建文件')
            
    def is_text_file(self, file_path):
        """检测文件是否为文本文件 - 读取完整文件进行解码判断"""
        try:
            # 【修复】读取完整文件内容，避免部分读取导致的误判
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # 【调试】记录文件信息
            logger.debug(f"检测文件: {file_path}")
            logger.debug(f"文件大小: {len(content)} bytes")
            has_null_byte = b'\x00' in content
            logger.debug(f"包含空字节: {has_null_byte}")
            
            # 检查是否包含空字节（二进制文件的特征）
            if b'\x00' in content:
                logger.warning(f"文件包含空字节，判定为二进制文件: {file_path}")
                return False
            
            # 如果文件为空，认为是文本文件
            if len(content) == 0:
                return True
            
            # 【修复】尝试完整解码为UTF-8
            try:
                content.decode('utf-8')
                logger.debug(f"UTF-8解码成功: {file_path}")
                return True
            except UnicodeDecodeError as e:
                logger.debug(f"UTF-8解码失败: {e}")
            
            # 尝试完整解码为GBK（中文Windows常用编码）
            try:
                content.decode('gbk')
                logger.debug(f"GBK解码成功: {file_path}")
                return True
            except UnicodeDecodeError as e:
                logger.debug(f"GBK解码失败: {e}")
            
            # 如果都无法解码，认为是二进制文件
            logger.warning(f"无法解码，判定为二进制文件: {file_path}")
            return False
        except Exception as e:
            # 如果读取失败，保守起见认为不是文本文件
            logger.error(f"文件检测异常: {e}")
            return False
    
    def _validate_and_open_file(self, file_path):
        """【修复4】统一验证并打开文件（检查扩展名和文本类型）
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否通过验证
        """
        import os
        from PyQt6.QtWidgets import QMessageBox
        
        # 【调试】记录文件路径
        logger.info(f"尝试验证文件: {file_path}")
        logger.info(f"文件是否存在: {os.path.exists(file_path)}")
        if os.path.exists(file_path):
            logger.info(f"文件大小: {os.path.getsize(file_path)} bytes")
        
        # 检查文件扩展名
        if not file_path.lower().endswith(('.md', '.markdown')):
            reply = QMessageBox.question(
                self,
                '警告',
                f'文件 "{os.path.basename(file_path)}" 的扩展名不是 .md 或 .markdown。\n\n是否仍然打开？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return False
        
        # 检测是否为文本文件
        if not self.is_text_file(file_path):
            # 【优化】提供更详细的错误信息
            QMessageBox.warning(
                self, 
                '警告', 
                f'文件 "{os.path.basename(file_path)}" 无法识别为文本文件。\n\n'
                f'可能原因：\n'
                f'1. 文件包含二进制数据\n'
                f'2. 文件编码不受支持\n'
                f'3. 文件已损坏\n\n'
                f'建议：使用记事本打开检查文件内容。'
            )
            return False
        
        return True
    
    def open_file(self):
        """打开文件"""
        if not self.maybe_save():
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '打开Markdown文件',
            '',
            'Markdown文件 (*.md *.markdown);;所有文件 (*.*)'
        )
        
        if file_path:
            # 【修复4】使用统一的验证方法
            if not self._validate_and_open_file(file_path):
                return
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                self.editor.setPlainText(content)
                self.current_file = file_path
                filename = os.path.basename(file_path)
                self.setWindowTitle(f'快乐马MarkDown编辑器 - {filename}')
                self.statusBar().showMessage(f'已打开: {filename}')
                
                # 计算并保存当前文档的 MD5（使用 strip() 后的内容）
                import hashlib
                self.saved_md5 = hashlib.md5(content.strip().encode('utf-8')).hexdigest()
                
            except Exception as e:
                QMessageBox.critical(self, '错误', f'无法打开文件:\n{str(e)}')
    
    def open_file_by_path(self, file_path):
        """通过文件路径打开文件（用于拖放）"""
        if not self.maybe_save():
            return
        
        # 【修复4】使用统一的验证方法
        if not self._validate_and_open_file(file_path):
            return
            
        try:
            # 先设置 current_file，确保 update_preview 时 Base URL 正确
            self.current_file = file_path
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检测并清理过度转义
            cleaned_content = self.check_and_clean_escapes(content, file_path)
            
            self.editor.setPlainText(cleaned_content)
            filename = os.path.basename(file_path)
            self.setWindowTitle(f'快乐马MarkDown编辑器 - {filename}')
            self.statusBar().showMessage(f'已打开: {filename}')
            
            # 计算并保存当前文档的 MD5（使用 strip() 后的内容）
            import hashlib
            self.saved_md5 = hashlib.md5(cleaned_content.strip().encode('utf-8')).hexdigest()
            
            # 自动更新预览（此时 current_file 已经设置）
            self.update_preview()
            
        except Exception as e:
            import traceback
            logger.error(f"打开文件失败: {e}\n{traceback.format_exc()}")
            QMessageBox.critical(self, '错误', f'无法打开文件:\n{str(e)}')
                
    def save_file(self):
        """保存文件"""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_as_file()
            
    def save_as_file(self):
        """另存为文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            '保存Markdown文件',
            '',
            'Markdown文件 (*.md *.markdown);;所有文件 (*.*)'
        )
        
        if file_path:
            self.save_to_file(file_path)
            self.current_file = file_path
            filename = os.path.basename(file_path)
            self.setWindowTitle(f'快乐马MarkDown编辑器 - {filename}')
            
    def save_to_file(self, file_path, show_success_message=True):
        """保存到文件（使用原子性操作，先保存到临时文件）
        
        Args:
            file_path: 文件路径
            show_success_message: 是否显示成功提示（默认True，退出时可设为False）
            
        Returns:
            bool: 保存是否成功
        """
        import tempfile
        
        try:
            content = self.editor.toPlainText()
            
            # 【优化5】使用原子性保存：先写入临时文件，成功后再替换原文件
            dir_name = os.path.dirname(file_path)
            temp_file = tempfile.NamedTemporaryFile(
                mode='w',
                encoding='utf-8',
                dir=dir_name,
                suffix='.tmp',
                prefix='.mdeditor_',
                delete=False
            )
            temp_path = temp_file.name
            
            try:
                # 写入临时文件
                temp_file.write(content)
                temp_file.flush()
                os.fsync(temp_file.fileno())  # 确保数据写入磁盘
                temp_file.close()
                
                # 【关键】使用 os.replace() 实现原子性替换
                # os.replace() 在 Windows 和 Linux 上都能安全地覆盖已存在的文件
                # 即使在文件被其他进程打开的情况下也能工作
                os.replace(temp_path, file_path)
                
            except Exception:
                # 如果失败，清理临时文件
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                raise
            
            # 更新标题栏为保存的文件名
            filename = os.path.basename(file_path)
            self.setWindowTitle(f'快乐马MarkDown编辑器 - {filename}')
            self.statusBar().showMessage(f'已保存: {filename}')
            
            # 计算并保存当前文档的 MD5（使用 strip() 后的内容）
            import hashlib
            self.saved_md5 = hashlib.md5(content.strip().encode('utf-8')).hexdigest()
            
            if show_success_message:
                QMessageBox.information(self, '成功', '文件保存成功！')
            return True
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法保存文件:\n{str(e)}')
            return False
            
    def maybe_save(self):
        """检查是否需要保存"""
        # 如果文档为空，不需要提示保存
        current_text = self.editor.toPlainText().strip()
        if not current_text:
            return True
        
        # 使用 MD5 比较判断文档是否有修改
        import hashlib
        current_md5 = hashlib.md5(current_text.encode('utf-8')).hexdigest()
        
        # 如果当前 MD5 与保存时的 MD5 相同，说明没有修改
        # 注意：saved_md5 也是基于 strip() 后的内容计算的
        if self.saved_md5 and current_md5 == self.saved_md5:
            return True
        
        # 文档有修改，提示用户保存
        result = QMessageBox.question(
            self,
            '保存',
            '是否保存当前修改？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        if result == QMessageBox.StandardButton.Yes:
            self.save_file()
            return True
        elif result == QMessageBox.StandardButton.Cancel:
            return False
        return True
        
    def toggle_fullscreen(self):
        """切换全屏 - 带状态记忆"""
        if self.isFullScreen():
            self.showNormal()
            self.is_fullscreen = False
            self.statusBar().showMessage('已退出全屏模式')
        else:
            self.showFullScreen()
            self.is_fullscreen = True
            self.statusBar().showMessage('已进入全屏模式（按F11退出）')
    
    def show_search_dialog(self):
        """显示搜索对话框（防止多次打开）"""
        # 【优化9】如果对话框已存在且可见，则聚焦到已有对话框
        if self.search_dialog is not None and self.search_dialog.isVisible():
            self.search_dialog.raise_()
            self.search_dialog.activateWindow()
            self.search_dialog.search_input.setFocus()
            self.search_dialog.search_input.selectAll()
            return
        
        if self.search_dialog is None:
            self.search_dialog = SearchDialog(self)
        
        # 如果有选中文本，自动填充到搜索框
        selected_text = self.editor.textCursor().selectedText()
        if selected_text:
            self.search_dialog.search_input.setText(selected_text)
        
        self.search_dialog.show()
        self.search_dialog.search_input.setFocus()
        self.search_dialog.search_input.selectAll()
    
    def show_replace_dialog(self):
        """显示替换对话框（防止多次打开）"""
        # 【优化9】如果对话框已存在且可见，则聚焦到已有对话框
        if self.replace_dialog is not None and self.replace_dialog.isVisible():
            self.replace_dialog.raise_()
            self.replace_dialog.activateWindow()
            self.replace_dialog.search_input.setFocus()
            self.replace_dialog.search_input.selectAll()
            return
        
        if self.replace_dialog is None:
            self.replace_dialog = ReplaceDialog(self)
        
        # 如果有选中文本，自动填充到搜索框
        selected_text = self.editor.textCursor().selectedText()
        if selected_text:
            self.replace_dialog.search_input.setText(selected_text)
        
        self.replace_dialog.show()
        self.replace_dialog.search_input.setFocus()
        self.replace_dialog.search_input.selectAll()
    
    def perform_search(self, search_text, case_sensitive=False, find_all=False):
        """执行搜索"""
        if not search_text:
            return []
        
        # 清除之前的高亮
        self.clear_highlight()
        
        # 获取全文
        full_text = self.editor.toPlainText()
        
        # 准备搜索
        if not case_sensitive:
            search_text_lower = search_text.lower()
            full_text_lower = full_text.lower()
        else:
            search_text_lower = search_text
            full_text_lower = full_text
        
        results = []
        start = 0
        
        # 查找所有匹配项
        while True:
            pos = full_text_lower.find(search_text_lower, start)
            if pos == -1:
                break
            results.append(pos)
            start = pos + len(search_text)
        
        self.search_results = results
        self.current_search_index = -1
        self.current_search_text = search_text  # 保存搜索文本
        
        if results:
            if find_all:
                # 高亮所有结果
                self.highlight_all_results(search_text, case_sensitive)
            else:
                # 跳转到第一个结果
                self.current_search_index = 0
                self.goto_search_result(0, search_text, case_sensitive)
            
            self.statusBar().showMessage(f'找到 {len(results)} 个匹配项')
        else:
            self.statusBar().showMessage('未找到匹配项')
            QMessageBox.information(self, '搜索结果', f'未找到 "{search_text}"')
        
        return results
    
    def highlight_all_results(self, search_text, case_sensitive):
        """高亮所有搜索结果"""
        cursor = self.editor.textCursor()
        document = self.editor.document()
        
        full_text = self.editor.toPlainText()
        
        if not case_sensitive:
            search_text_lower = search_text.lower()
            full_text_lower = full_text.lower()
        else:
            search_text_lower = search_text
            full_text_lower = full_text
        
        # 创建高亮格式
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor('#FFFF00'))  # 黄色背景
        
        start = 0
        while True:
            pos = full_text_lower.find(search_text_lower, start)
            if pos == -1:
                break
            
            # 设置光标位置并高亮
            cursor.setPosition(pos)
            cursor.setPosition(pos + len(search_text), QTextCursor.MoveMode.KeepAnchor)
            cursor.mergeCharFormat(highlight_format)
            
            start = pos + len(search_text)
    
    def goto_search_result(self, index, search_text, case_sensitive):
        """跳转到指定的搜索结果"""
        if not self.search_results or index < 0 or index >= len(self.search_results):
            return
        
        pos = self.search_results[index]
        
        # 创建光标并选择文本
        cursor = self.editor.textCursor()
        cursor.setPosition(pos)
        cursor.setPosition(pos + len(search_text), QTextCursor.MoveMode.KeepAnchor)
        
        # 应用高亮格式
        cursor.mergeCharFormat(self.highlight_format)
        
        # 设置光标位置，确保可见
        self.editor.setTextCursor(cursor)
        self.editor.ensureCursorVisible()
        
        # 滚动到该行
        full_text = self.editor.toPlainText()
        line_num = full_text[:pos].count('\n')
        block = self.editor.document().findBlockByNumber(line_num)
        if block.isValid():
            cursor.setPosition(block.position())
            self.editor.setTextCursor(cursor)
            if hasattr(self.editor, 'centerCursor'):
                self.editor.centerCursor()
            else:
                self.editor.ensureCursorVisible()
    
    def find_next(self):
        """查找下一个"""
        if not self.search_results or not self.current_search_text:
            # 如果没有搜索结果，尝试从当前选中文本搜索
            selected_text = self.editor.textCursor().selectedText()
            if selected_text:
                self.perform_search(selected_text)
            else:
                QMessageBox.information(self, '提示', '请先输入搜索内容')
            return
        
        if self.current_search_index < len(self.search_results) - 1:
            self.current_search_index += 1
            self.clear_highlight()
            self.goto_search_result(self.current_search_index, self.current_search_text, False)
            self.statusBar().showMessage(f'第 {self.current_search_index + 1}/{len(self.search_results)} 个匹配项')
        else:
            self.statusBar().showMessage('已到达最后一个匹配项')
            QMessageBox.information(self, '搜索', '已到达文档末尾')
    
    def find_previous(self):
        """查找上一个"""
        if not self.search_results or not self.current_search_text:
            QMessageBox.information(self, '提示', '没有搜索结果')
            return
        
        if self.current_search_index > 0:
            self.current_search_index -= 1
            self.clear_highlight()
            self.goto_search_result(self.current_search_index, self.current_search_text, False)
            self.statusBar().showMessage(f'第 {self.current_search_index + 1}/{len(self.search_results)} 个匹配项')
        else:
            self.statusBar().showMessage('已到达第一个匹配项')
            QMessageBox.information(self, '搜索', '已到达文档开头')
    
    def check_and_clean_escapes(self, text: str, file_path: str = '') -> str:
        """
        检测并清理 Markdown 文本中的过度转义
        
        Args:
            text: 待检查的文本
            file_path: 文件路径（用于日志）
            
        Returns:
            清理后的文本
        """
        try:
            # 使用全局清理器实例
            result = ESCAPE_CLEANER.clean_and_report(text)
            
            # 如果有改进，显示提示
            if result.get('improvement') and result['improvement']['fixed_count'] > 0:
                fixed = result['improvement']['fixed_count']
                remaining = result['improvement']['after_count']
                
                msg = f"检测到 {fixed} 处过度转义并已自动修复"
                if remaining > 0:
                    msg += f"\n仍有 {remaining} 处未修复"
                
                logger.info(f"文件 {file_path}: {msg}")
                
                # 显示非阻塞提示
                self.statusBar().showMessage(msg, 5000)  # 显示5秒
            
            return result['cleaned_text']
            
        except Exception as e:
            logger.error(f"转义清理失败: {e}")
            return text  # 如果清理失败，返回原文本
            
    def show_about(self):
        """显示关于对话框"""
        about_text = (
            '快乐马MarkDown编辑器 V2.0\n\n'
            '【软件性质】\n'
            '本软件为免费自由软件，个人和商业用途均可免费使用、自由传播。禁止用于任何违法用途。\n\n'
            '【工具定位】\n'
            '专为AI时代打造的Markdown文档处理工具，聚焦解决AI生成Markdown内容的“最后一公里”问题。通过20+专业主题样式、PDF/长图/图集三种导出模式、全维度样式定制，让AI生成的Markdown文档一键变专业，适配办公、创作、教学、分享等全场景需求。\n\n'
            '【核心特性】\n'
            '1. 高颜值样式体系：20+主题（企业级/程序员专属/阅读优化等），支持代码高亮与个性化样式调整；\n'
            '2. 全场景导出：PDF（A4分页）、长图（无缝拼接）、图集（按页拆分），所见即所得；\n'
            '3. 专业编辑体验：实时双栏预览、滚动同步，兼容完整Markdown语法，支持60+编程语言代码高亮；\n'
            '4. 安全高效：全程本地处理，离线可用，配置自动保存，隐私与效率兼顾。\n\n'
            '【版权声明】\n'
            '© 2025 架构师老陈（保留署名权，适配MIT开源协议）\n'
            '1. 核心代码：独立开发，可自由查看、修改、二次分发（需保留署名）；\n'
            '2. 编译版：免费自由使用/传播（个人/商用均可，禁止违法用途）；\n'
            '3. 开源组件：使用PyQt6、markdown、PyMuPDF等开源组件，需遵守对应许可证约定（GPL/BSD/AGPL等）；\n'
            '4. 免责声明：原作者不对软件使用过程中的任何问题承担责任，使用者自行承担风险。\n\n'
            '【联系方式】\n'
            '作者署名：架构师老陈\n'
            'QQ：8108306（合作私聊）\n'
            'QQ群：950721219（架构师老陈的行业交流群-群文件里有原创免费软件、行业分析、技术资料等）\n'
            '闲鱼：架构师老陈（需要源码可到闲鱼搜用户：架构师老陈）\n'
            '抖音号：1884930310（架构师老陈日常发布和直播）'
        )
        
        QMessageBox.information(
            self,
            '关于',
            about_text
        )
    
    def show_pdf_document(self, pdf_filename):
        """显示PDF文档
        
        Args:
            pdf_filename: PDF文件名（位于docs目录下）
        """
        try:
            import os
            import sys
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget
            from PyQt6.QtGui import QPixmap, QImage
            from PyQt6.QtCore import Qt
            
            # 构建PDF文件路径
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller打包后的路径
                docs_dir = os.path.join(sys._MEIPASS, 'docs')
            else:
                # 开发环境
                docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs')
            
            pdf_path = os.path.join(docs_dir, pdf_filename)
            
            if not os.path.exists(pdf_path):
                QMessageBox.critical(self, '错误', f'文件不存在:\n{pdf_path}')
                return
            
            # 创建对话框
            dialog = QDialog(self)
            dialog.setWindowTitle(f'{os.path.splitext(pdf_filename)[0]} - 快乐马MarkDown编辑器')
            dialog.resize(900, 700)
            
            # 主布局
            main_layout = QVBoxLayout(dialog)
            
            # 创建滚动区域
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(False)  # 不允许自动调整大小
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)  # 允许水平滚动
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            
            # 创建内容容器
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setSpacing(0)  # 图片之间无空白
            content_layout.setContentsMargins(0, 0, 0, 0)  # 无边距
            
            # 使用PyMuPDF渲染PDF页面
            import fitz  # PyMuPDF
            
            doc = fitz.open(pdf_path)
            logger.info(f"PDF文档打开成功，共 {len(doc)} 页")
            
            # 渲染每一页
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # 设置缩放比例（1.3倍）
                zoom = 1.3
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # 转换为QImage
                img_data = pix.tobytes("png")
                qimage = QImage.fromData(img_data)
                pixmap = QPixmap.fromImage(qimage)
                
                # 创建标签显示原始图片，不进行缩放
                page_label = QLabel()
                page_label.setPixmap(pixmap)
                page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                page_label.setStyleSheet("background-color: white; border: 1px solid #ddd;")
                
                content_layout.addWidget(page_label)
            
            doc.close()
            
            scroll_area.setWidget(content_widget)
            main_layout.addWidget(scroll_area)
            
            # 底部按钮
            button_layout = QHBoxLayout()
            close_button = QPushButton('关闭')
            close_button.clicked.connect(dialog.close)
            button_layout.addStretch()
            button_layout.addWidget(close_button)
            
            main_layout.addLayout(button_layout)
            
            dialog.exec()
            
        except ImportError:
            QMessageBox.critical(self, '错误', '缺少PyMuPDF库，无法显示PDF。\n请安装: pip install PyMuPDF')
        except Exception as e:
            logger.error(f"打开PDF失败: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, '错误', f'无法打开PDF文件:\n{str(e)}')
    
    def export_pdf(self):
        """导出预览区为PDF文件"""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox, QDialog, QVBoxLayout, QLabel, QProgressBar
            from PyQt6.QtCore import QTimer, Qt
            from PyQt6.QtGui import QPageSize, QPageLayout
            from PyQt6.QtCore import QMarginsF, QSizeF
            import os
            
            # 从工具栏下拉框获取页面比例
            page_ratios = {
                'A3': (297.0, 420.0),
                'A4': (210.0, 297.0),
                'A5': (148.0, 210.0),
                'B5': (176.0, 250.0),
                'Letter': (215.9, 279.4),
                'Legal': (215.9, 355.6),
            }
            
            selected_ratio = self.pdf_ratio_combo.currentData()
            ratio_width, ratio_height = page_ratios[selected_ratio]
            
            # 【新增】获取导出方向
            orientation = self.pdf_orientation_combo.currentData()
            is_landscape = (orientation == 'landscape')
            
            # 如果是横屏，交换宽高
            if is_landscape:
                ratio_width, ratio_height = ratio_height, ratio_width
                logger.info(f"选择的页面比例: {selected_ratio} ({ratio_height}mm x {ratio_width}mm) - 横屏")
            else:
                logger.info(f"选择的页面比例: {selected_ratio} ({ratio_width}mm x {ratio_height}mm) - 竖屏")
            
            # 选择保存路径，默认使用当前文档的文件名
            default_filename = ''
            if self.current_file:
                base_name = os.path.splitext(os.path.basename(self.current_file))[0]
                default_filename = base_name + '.pdf'
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                '导出PDF',
                default_filename,
                'PDF 文件 (*.pdf)'
            )
            
            if not file_path:
                return
            
            if not file_path.lower().endswith('.pdf'):
                file_path += '.pdf'
            
            # 【关键】创建进度提示对话框
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle('导出PDF')
            progress_dialog.setModal(True)
            progress_dialog.setFixedSize(400, 150)
            
            layout = QVBoxLayout(progress_dialog)
            
            status_label = QLabel('正在执行操作...')
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(status_label)
            
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 0)  # 不确定进度，显示忙碌状态
            layout.addWidget(progress_bar)
            
            tip_label = QLabel('请不要关闭窗口，正在执行操作...')
            tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tip_label.setStyleSheet('color: gray; font-size: 12px;')
            layout.addWidget(tip_label)
            
            progress_dialog.show()
            
            # 调用公共方法生成PDF，传递页面比例
            self._generate_pdf_with_callback(
                file_path, 
                lambda: self._on_pdf_export_complete(file_path, progress_dialog), 
                ratio_width, 
                ratio_height
            )
            
        except Exception as e:
            logger.error(f"PDF导出异常: {e}")
            import traceback
            traceback.print_exc()
            
            # 关闭进度对话框
            if 'progress_dialog' in locals():
                progress_dialog.close()
            
            QMessageBox.critical(self, '错误', f'PDF导出失败:\n{str(e)}')
            self.statusBar().showMessage('导出失败')
    
    def _on_pdf_export_complete(self, file_path, progress_dialog=None):
        """PDF导出完成后的回调"""
        from PyQt6.QtWidgets import QMessageBox
        
        # 关闭进度对话框
        if progress_dialog:
            progress_dialog.close()
        
        QMessageBox.information(self, '成功', f'PDF导出成功！\n\n文件位置:\n{file_path}')
        self.statusBar().showMessage('PDF导出成功')
    
    def _generate_pdf_with_callback_core(self, pdf_path, callback, ratio_width=210.0, ratio_height=297.0):
        """公共方法：生成PDF文件（直接导出，不经过图片处理）
        
        Args:
            pdf_path: PDF文件保存路径
            callback: PDF生成完成后的回调函数
            ratio_width: 页面宽度(mm)，默认A4宽度210mm
            ratio_height: 页面高度(mm)，默认A4高度297mm
        """
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QTimer
            from PyQt6.QtGui import QPageSize, QPageLayout
            from PyQt6.QtCore import QMarginsF, QSizeF
            import os
            
            # 【关键】不修改任何 WebEngine 设置，完全依赖 CSS 控制样式
            # 这样确保 PDF 导出与 HTML 预览样式完全一致
            
            # 获取预览区宽度和文档高度
            preview_width = self.preview.width()
            
            js_get_size = """
                (function() {
                    var body = document.body;
                    var html = document.documentElement;
                    var scrollWidth = Math.max(body.scrollWidth, html.scrollWidth);
                    var scrollHeight = Math.max(body.scrollHeight, html.scrollHeight);
                    return {
                        scrollWidth: scrollWidth,
                        scrollHeight: scrollHeight
                    };
                })();
            """
            
            def on_size_obtained(doc_size):
                if doc_size:
                    doc_width = doc_size.get('scrollWidth', preview_width)
                    doc_height = doc_size.get('scrollHeight', 50000)
                    
                    logger.debug(f"HTML 文档尺寸: {doc_width}x{doc_height}px")
                    
                    # 【关键】增加延迟到500ms，确保JS、图片、字体全部渲染完成
                    QTimer.singleShot(500, lambda: do_export(doc_width, doc_height))
                else:
                    logger.warning("无法获取文档尺寸，使用默认值")
                    # 【关键】增加延迟到500ms
                    QTimer.singleShot(500, lambda: do_export(preview_width, 50000))
            
            self.preview.page().runJavaScript(js_get_size, on_size_obtained)
            
            def do_export(width, height):
                try:
                    # 【关键步骤1】PDF页面宽度 = HTML预览区实际宽度（已考虑缩放）
                    # width 是通过 JavaScript 获取的 scrollWidth，已经是缩放后的像素值
                    # 例如：容器宽1000px，缩放60%，则 width = 600px
                    
                    # 【关键修正】减去2像素，消除右边白边
                    pdf_width_px = width - 2
                    
                    # 将像素转换为 points (Qt WebEngine 使用 96 DPI)
                    # 1 point = 1/72 inch, 96 DPI 下: 1px = 72/96 points = 0.75 points
                    pdf_width_points = pdf_width_px * 72.0 / 96.0
                    
                    # PDF页面高度按所选比例计算
                    # 例如：A4 比例: 210mm : 297mm
                    pdf_height_points = pdf_width_points * ratio_height / ratio_width
                    
                    logger.debug(f"HTML 文档宽度: {width}px")
                    logger.debug(f"页面比例: {ratio_width}mm x {ratio_height}mm")
                    logger.debug(f"PDF 页面尺寸: {pdf_width_points:.1f}x{pdf_height_points:.1f} points")
                    logger.debug(f"预计页数: {height / (pdf_height_points * 96.0 / 72.0):.1f}")
                    
                    page_size = QPageSize(
                        QSizeF(pdf_width_points, pdf_height_points),
                        QPageSize.Unit.Point
                    )
                    
                    page_layout = QPageLayout(
                        page_size,
                        QPageLayout.Orientation.Portrait,
                        QMarginsF(0, 0, 0, 0),
                        QPageLayout.Unit.Point
                    )
                    
                    # 【关键步骤2】调用 printToPdf
                    # Qt WebEngine 会使用当前的 CSS 样式（包括 @media print）
                    self.preview.page().printToPdf(pdf_path, page_layout)
                    logger.info("已调用 printToPdf")
                    
                except Exception as e:
                    logger.error(f"PDF生成失败: {e}")
                    import traceback
                    traceback.print_exc()
                    return
                
                # 【修复2】等待PDF生成完成，增加超时机制
                max_wait_time = 30000  # 最大等待30秒
                start_time = QTimer()
                check_count = [0]  # 使用列表以便在闭包中修改
                
                def check_pdf_ready():
                    check_count[0] += 1
                    elapsed_time = check_count[0] * 200  # 每次检查间隔200ms
                    
                    if elapsed_time > max_wait_time:
                        logger.error(f"PDF生成超时（{max_wait_time}ms）")
                        from PyQt6.QtWidgets import QMessageBox
                        QMessageBox.critical(self, '错误', 'PDF生成超时，请重试。')
                        return
                    
                    if os.path.exists(pdf_path):
                        file_size = os.path.getsize(pdf_path)
                        if file_size > 1000:
                            logger.info(f"PDF已生成，大小: {file_size} bytes")
                            callback()
                        else:
                            QTimer.singleShot(200, check_pdf_ready)
                    else:
                        QTimer.singleShot(200, check_pdf_ready)
                
                QTimer.singleShot(500, check_pdf_ready)
            
        except Exception as e:
            logger.error(f"PDF生成异常: {e}")
            import traceback
            traceback.print_exc()
    
    def _generate_pdf_with_callback(self, pdf_path, callback, ratio_width=210.0, ratio_height=297.0):
        """公共方法：生成PDF文件（通过图片中转，支持裁剪和边距）
        
        Args:
            pdf_path: PDF文件保存路径
            callback: PDF生成完成后的回调函数
            ratio_width: 页面宽度(mm)，默认A4宽度210mm
            ratio_height: 页面高度(mm)，默认A4高度297mm
        """
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import QTimer
            from PyQt6.QtGui import QPageSize, QPageLayout
            from PyQt6.QtCore import QMarginsF, QSizeF
            import os
            import tempfile
            
            # 【关键】不修改任何 WebEngine 设置，完全依赖 CSS 控制样式
            # 这样确保 PDF 导出与 HTML 预览样式完全一致
            
            # 获取预览区宽度和文档高度
            preview_width = self.preview.width()
            
            js_get_size = """
                (function() {
                    var body = document.body;
                    var html = document.documentElement;
                    var scrollWidth = Math.max(body.scrollWidth, html.scrollWidth);
                    var scrollHeight = Math.max(body.scrollHeight, html.scrollHeight);
                    return {
                        scrollWidth: scrollWidth,
                        scrollHeight: scrollHeight
                    };
                })();
            """
            
            def on_size_obtained(doc_size):
                if doc_size:
                    doc_width = doc_size.get('scrollWidth', preview_width)
                    doc_height = doc_size.get('scrollHeight', 50000)
                    
                    logger.debug(f"HTML 文档尺寸: {doc_width}x{doc_height}px")
                    
                    # 【关键】增加延迟到500ms，确保JS、图片、字体全部渲染完成
                    QTimer.singleShot(500, lambda: do_export(doc_width, doc_height))
                else:
                    logger.warning("无法获取文档尺寸，使用默认值")
                    # 【关键】增加延迟到500ms
                    QTimer.singleShot(500, lambda: do_export(preview_width, 50000))
            
            self.preview.page().runJavaScript(js_get_size, on_size_obtained)
            
            def do_export(width, height):
                try:
                    # 【新增】获取导出方向
                    orientation = self.pdf_orientation_combo.currentData() if hasattr(self, 'pdf_orientation_combo') else 'portrait'
                    is_landscape = (orientation == 'landscape')
                    
                    # 【步骤1】先使用Qt WebEngine生成临时PDF
                    temp_pdf = tempfile.NamedTemporaryFile(
                        suffix='.pdf',
                        prefix='mdeditor_temp_',
                        delete=False
                    )
                    temp_pdf_path = temp_pdf.name
                    temp_pdf.close()
                    
                    # 【关键修正】减去2像素，消除右边白边
                    pdf_width_px = width - 2
                    pdf_width_points = pdf_width_px * 72.0 / 96.0
                    pdf_height_points = pdf_width_points * ratio_height / ratio_width
                    
                    logger.debug(f"HTML 文档宽度: {width}px")
                    logger.debug(f"页面比例: {ratio_width}mm x {ratio_height}mm")
                    logger.debug(f"PDF 页面尺寸: {pdf_width_points:.1f}x{pdf_height_points:.1f} points")
                    logger.debug(f"预计页数: {height / (pdf_height_points * 96.0 / 72.0):.1f}")
                    
                    page_size = QPageSize(
                        QSizeF(pdf_width_points, pdf_height_points),
                        QPageSize.Unit.Point
                    )
                    
                    page_layout = QPageLayout(
                        page_size,
                        QPageLayout.Orientation.Portrait,
                        QMarginsF(0, 0, 0, 0),
                        QPageLayout.Unit.Point
                    )
                    
                    # 调用 printToPdf 生成临时PDF
                    self.preview.page().printToPdf(temp_pdf_path, page_layout)
                    logger.info("已调用 printToPdf 生成临时PDF")
                    
                    # 等待临时PDF生成完成
                    def check_temp_pdf_ready():
                        if os.path.exists(temp_pdf_path):
                            file_size = os.path.getsize(temp_pdf_path)
                            if file_size > 1000:
                                logger.info(f"临时PDF已生成，大小: {file_size} bytes")
                                # 【步骤2】将临时PDF转换为图片，处理后再合并为新PDF
                                self._convert_images_to_pdf(temp_pdf_path, pdf_path, callback, ratio_width, ratio_height, is_landscape)
                            else:
                                QTimer.singleShot(200, check_temp_pdf_ready)
                        else:
                            QTimer.singleShot(200, check_temp_pdf_ready)
                    
                    QTimer.singleShot(500, check_temp_pdf_ready)
                    
                except Exception as e:
                    logger.error(f"PDF生成失败: {e}")
                    import traceback
                    traceback.print_exc()
                    return
            
        except Exception as e:
            logger.error(f"PDF生成异常: {e}")
            import traceback
            traceback.print_exc()
    
    def export_long_image(self):
        """导出预览区为长图（通过PDF中转）"""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox, QDialog, QVBoxLayout, QLabel, QProgressBar
            from PyQt6.QtCore import QTimer, Qt
            import os
            import tempfile
            
            # 【修复1】检查文档是否有内容
            current_text = self.editor.toPlainText().strip()
            if not current_text:
                QMessageBox.warning(self, '警告', '当前文档为空，无法导出。')
                return
            
            # 选择保存路径，默认使用当前文档的文件名
            default_filename = ''
            if self.current_file:
                base_name = os.path.splitext(os.path.basename(self.current_file))[0]
                default_filename = base_name + '.png'
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                '导出长图',
                default_filename,
                'PNG 图片 (*.png);;JPEG 图片 (*.jpg *.jpeg)'
            )
            
            if not file_path:
                return
            
            if not file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path += '.png'
            
            # 【关键】创建进度提示对话框
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle('导出长图')
            progress_dialog.setModal(True)
            progress_dialog.setFixedSize(400, 150)
            
            layout = QVBoxLayout(progress_dialog)
            
            status_label = QLabel('正在执行操作...')
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(status_label)
            
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 0)  # 不确定进度，显示忙碌状态
            layout.addWidget(progress_bar)
            
            tip_label = QLabel('请不要关闭窗口，正在执行操作...')
            tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tip_label.setStyleSheet('color: gray; font-size: 12px;')
            layout.addWidget(tip_label)
            
            progress_dialog.show()
            
            self.statusBar().showMessage('正在生成PDF...')
            
            # 【关键】使用临时文件名，避免与输出图片冲突
            output_dir = os.path.dirname(file_path) if os.path.dirname(file_path) else os.getcwd()
            # 生成唯一的临时文件名
            temp_pdf = tempfile.NamedTemporaryFile(
                suffix='.pdf',
                prefix='mdeditor_export_',
                dir=output_dir,
                delete=False  # 不自动删除，我们手动控制
            )
            pdf_path = temp_pdf.name
            temp_pdf.close()  # 关闭文件句柄，让Qt可以写入
            
            logger.debug(f"临时 PDF 路径: {pdf_path}")
            
            # 【关键】从工具栏下拉框获取页面比例
            page_ratios = {
                'A3': (297.0, 420.0),
                'A4': (210.0, 297.0),
                'A5': (148.0, 210.0),
                'B5': (176.0, 250.0),
                'Letter': (215.9, 279.4),
                'Legal': (215.9, 355.6),
            }
            selected_ratio = self.pdf_ratio_combo.currentData()
            ratio_width, ratio_height = page_ratios[selected_ratio]
            
            # 【新增】获取导出方向
            orientation = self.pdf_orientation_combo.currentData()
            is_landscape = (orientation == 'landscape')
            
            # 如果是横屏，交换宽高
            if is_landscape:
                ratio_width, ratio_height = ratio_height, ratio_width
                logger.info(f"导出长图使用PDF比例: {selected_ratio} ({ratio_height}mm x {ratio_width}mm) - 横屏")
            else:
                logger.info(f"导出长图使用PDF比例: {selected_ratio} ({ratio_width}mm x {ratio_height}mm) - 竖屏")
            
            # 复用导出PDF的逻辑生成PDF，传递用户选择的比例
            self._generate_pdf_with_callback_core(
                pdf_path, 
                lambda: self._convert_pdf_to_long_image(pdf_path, file_path, progress_dialog),
                ratio_width,
                ratio_height
            )
            
        except Exception as e:
            logger.error(f"导出长图失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 关闭进度对话框
            if 'progress_dialog' in locals():
                progress_dialog.close()
            
            QMessageBox.critical(self, '错误', f'导出长图失败:\n{str(e)}')
            self.statusBar().showMessage('导出失败')
    
    def _convert_pdf_to_long_image(self, pdf_path, image_path, progress_dialog=None):
        """将PDF转换为长图（使用PyMuPDF）
        
        Args:
            pdf_path: PDF文件路径
            image_path: 输出图片路径
            progress_dialog: 进度对话框（可选）
        """
        try:
            import fitz  # PyMuPDF
            from PIL import Image
            from PyQt6.QtWidgets import QMessageBox
            
            self.statusBar().showMessage('正在转换PDF为图片...')
            
            pdf_document = fitz.open(pdf_path)
            
            if len(pdf_document) == 0:
                raise Exception("PDF为空")
            
            images = []
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                # 使用2.0倍分辨率保证清晰度
                zoom = 2.0
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # 【关键】裁剪页面边缘的空白区域，避免拼接时出现白线
                img_cropped = self._crop_page_margins(img, page_num == 0, page_num == len(pdf_document) - 1)
                images.append(img_cropped)
            
            pdf_document.close()
            
            if len(images) == 0:
                raise Exception("PDF转换失败")
            
            # 单页直接保存，多页拼接
            if len(images) == 1:
                images[0].save(image_path, 'PNG' if image_path.lower().endswith('.png') else 'JPEG')
            else:
                total_height = sum(img.height for img in images)
                max_width = max(img.width for img in images)
                final_image = Image.new('RGB', (max_width, total_height), 'white')
                y_offset = 0
                for img in images:
                    final_image.paste(img, (0, y_offset))
                    y_offset += img.height
                final_image.save(image_path, 'PNG' if image_path.lower().endswith('.png') else 'JPEG')
            
            # 【关键】删除临时 PDF 文件
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                    logger.info(f"已删除临时 PDF: {pdf_path}")
                except Exception as e:
                    logger.warning(f"删除 PDF 失败: {e}")
            
            logger.info(f"长图已导出: {image_path}")
            self.statusBar().showMessage(f'长图已导出: {image_path}')
            
            # 关闭进度对话框
            if progress_dialog:
                progress_dialog.close()
            
            QMessageBox.information(self, '成功', f'长图已成功导出到:\n{image_path}')
            
        except ImportError:
            QMessageBox.warning(
                self, 
                '缺少依赖', 
                '需要安装 PyMuPDF 和 Pillow 才能使用此功能。\n\n'
                '请运行以下命令安装：\n'
                'pip install PyMuPDF pillow'
            )
            self.statusBar().showMessage('导出失败：缺少依赖')
            
        except Exception as e:
            logger.error(f"PDF转图片失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 清理临时 PDF 文件
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                    logger.info(f"已删除临时 PDF: {pdf_path}")
                except:
                    pass
            
            QMessageBox.critical(self, '错误', f'PDF转图片失败:\n{str(e)}')
            self.statusBar().showMessage('导出失败')
    
    def _crop_page_margins(self, img, is_first_page=False, is_last_page=False):
        """裁剪页面边缘的空白区域，避免拼接时出现白线
        
        Args:
            img: PIL Image对象
            is_first_page: 是否是第一页（长图导出时不使用）
            is_last_page: 是否是最后一页（长图导出时不使用）
            
        Returns:
            裁剪后的PIL Image对象
        """
        try:
            width, height = img.size
            
            # 【关键】所有页面都裁掉底部2像素和右侧2像素，避免白线
            crop_bottom = 2
            crop_right = 2
            
            # 执行裁剪
            if crop_bottom > 0 or crop_right > 0:
                crop_box = (0, 0, width - crop_right, height - crop_bottom)
                img_cropped = img.crop(crop_box)
                return img_cropped
            else:
                return img
                
        except Exception as e:
            logger.error(f"裁剪页面失败: {e}")
            import traceback
            traceback.print_exc()
            return img  # 如果裁剪失败，返回原图
    
    def _get_current_background_color(self):
        """获取当前样式的背景色
        
        Returns:
            RGB元组，如 (255, 255, 255) 表示白色
        """
        try:
            # 从预览区获取body的背景色
            js_get_bg_color = """
                (function() {
                    var body = document.body;
                    var bgColor = window.getComputedStyle(body).backgroundColor;
                    // 解析 rgb(r, g, b) 或 rgba(r, g, b, a)
                    var match = bgColor.match(/\\d+/g);
                    if (match && match.length >= 3) {
                        return {
                            r: parseInt(match[0]),
                            g: parseInt(match[1]),
                            b: parseInt(match[2])
                        };
                    }
                    return {r: 255, g: 255, b: 255}; // 默认白色
                })();
            """
            
            result = [None]
            def on_result(res):
                result[0] = res
            
            self.preview.page().runJavaScript(js_get_bg_color, on_result)
            
            # 等待结果（同步方式）
            import time
            for _ in range(10):  # 最多等待100ms
                if result[0] is not None:
                    break
                time.sleep(0.01)
            
            if result[0]:
                bg_data = result[0]
                color_tuple = (bg_data['r'], bg_data['g'], bg_data['b'])
                return color_tuple
            else:
                # 如果获取失败，根据当前风格返回默认背景色
                default_colors = {
                    'default': (255, 255, 255),
                    'ant': (240, 242, 245),
                    'material': (250, 250, 250),
                    'element': (255, 255, 255),
                    'arco': (247, 248, 250),
                    'fluent': (255, 255, 255),
                    'shadcn': (255, 255, 255),
                    'glass': (240, 240, 240),
                    'neumorphism': (224, 224, 224),
                    'flat': (255, 255, 255),
                    'apple': (255, 255, 255),
                    'geek': (30, 30, 30),
                    'dark_coder': (30, 30, 30),
                    'cyber_neon': (10, 10, 20),
                    'paper_eye': (245, 240, 230),
                    'magazine_bw': (240, 240, 240),
                    'business_blue': (245, 248, 250),
                    'nordic_cold': (245, 245, 245),
                    'old_newspaper': (245, 240, 230),
                    'school_fresh': (255, 255, 255),
                }
                return default_colors.get(self.current_style, (255, 255, 255))
                
        except Exception as e:
            logger.warning(f"获取背景色失败: {e}")
            return (255, 255, 255)  # 默认白色
    
    def _convert_images_to_pdf(self, temp_pdf_path, final_pdf_path, callback, ratio_width, ratio_height, is_landscape=False):
        """将临时PDF转换为图片，处理后再合并为新PDF
        
        Args:
            temp_pdf_path: 临时PDF文件路径
            final_pdf_path: 最终PDF文件路径
            callback: PDF生成完成后的回调函数
            ratio_width: 页面宽度(mm)
            ratio_height: 页面高度(mm)
            is_landscape: 是否为横屏模式（横屏时不添加上下边距）
        """
        try:
            import fitz  # PyMuPDF
            from PIL import Image
            import os
            import tempfile
            
            logger.info("正在将PDF转换为图片并处理...")
            
            pdf_document = fitz.open(temp_pdf_path)
            
            if len(pdf_document) == 0:
                raise Exception("PDF为空")
            
            # 【关键】直接使用预设的背景色，与CSS中定义完全一致
            default_colors = {
                'default': (255, 255, 255),        # 未设置，默认白色
                'ant': (240, 242, 245),            # #f0f2f5
                'material': (250, 250, 250),       # #fafafa
                'element': (245, 247, 250),        # #f5f7fa
                'arco': (247, 248, 250),           # linear-gradient起始色 #f7f8fa
                'fluent': (243, 243, 243),         # linear-gradient起始色 #f3f3f3
                'shadcn': (255, 255, 255),         # #ffffff
                'glass': (90, 111, 216),          # #5a6fd8 - 柔和紫色
                'neumorphism': (224, 229, 236),    # #e0e5ec
                'flat': (255, 255, 255),           # #ffffff
                'apple': (245, 245, 247),          # var(--apple-bg) = #f5f5f7
                'geek': (0, 0, 0),                 # var(--bg-main) = #000000 纯黑色
                'dark_coder': (26, 26, 32),        # #1a1a20
                'cyber_neon': (0, 0, 0),           # #000000 纯黑色
                'paper_eye': (245, 241, 230),      # #f5f1e6
                'magazine_bw': (255, 255, 255),    # #ffffff
                'business_blue': (248, 249, 250),  # #f8f9fa
                'nordic_cold': (247, 249, 248),    # #f7f9f8
                'old_newspaper': (242, 240, 232),  # #f2f0e8
                'school_fresh': (245, 250, 255),   # #f5faff
            }
            bg_color = default_colors.get(self.current_style, (255, 255, 255))
            logger.debug(f"使用预设背景色: RGB{bg_color} (风格: {self.current_style})")
            
            # 【关键】根据方向决定是否添加上下边距
            # 竖屏：添加上下边距（80像素）
            # 横屏：不添加边距（保持原始尺寸）
            if is_landscape:
                top_bottom_margin = 0  # 横屏时不添加边距
                logger.debug(f"横屏模式：不添加上下边距")
            else:
                top_bottom_margin = 80  # 竖屏时添加80像素边距
                logger.debug(f"竖屏模式：添加上下边距 {top_bottom_margin}px")
            
            # 创建临时目录存储处理后的图片
            temp_dir = tempfile.mkdtemp(prefix='mdeditor_pdf_')
            processed_images = []
            
            try:
                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]
                    # 使用2.0倍分辨率保证清晰度
                    zoom = 2.0
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    # 【关键】先裁剪掉右侧2像素和底部2像素，消除白边
                    width, height = img.size
                    logger.debug(f"第 {page_num + 1} 页 - 原始图片尺寸: {width}x{height}")
                    if width > 2 and height > 2:
                        img_cropped = img.crop((0, 0, width - 2, height - 2))
                        logger.debug(f"第 {page_num + 1} 页 - 裁剪后尺寸: {img_cropped.size[0]}x{img_cropped.size[1]}")
                    else:
                        img_cropped = img
                    
                    # 【关键】在上下添加边距，用HTML文档背景色填充
                    logger.debug(f"第 {page_num + 1} 页 - 开始添加边距，使用背景色: {bg_color}")
                    img_with_margins = self._add_vertical_margins(img_cropped, top_bottom_margin, bg_color)
                    logger.debug(f"第 {page_num + 1} 页 - 添加边距后尺寸: {img_with_margins.size[0]}x{img_with_margins.size[1]}")
                    
                    # 保存处理后的图片到临时目录
                    image_filename = f"page_{page_num + 1:03d}.png"
                    image_path = os.path.join(temp_dir, image_filename)
                    img_with_margins.save(image_path, 'PNG')
                    processed_images.append(image_path)
                    
                    logger.info(f"已处理第 {page_num + 1}/{len(pdf_document)} 页")
                
                pdf_document.close()
                
                # 【关键】将处理后的图片合并为新的PDF
                logger.info(f"正在将 {len(processed_images)} 张图片合并为PDF...")
                
                # 创建新的PDF文档
                new_pdf = fitz.open()
                
                for image_path in processed_images:
                    # 打开图片
                    img = Image.open(image_path)
                    img_width, img_height = img.size
                    
                    # 计算PDF页面尺寸（保持图片比例）
                    # 将像素转换为points (72 DPI)
                    page_width_points = img_width * 72.0 / 96.0
                    page_height_points = img_height * 72.0 / 96.0
                    
                    # 创建新页面
                    page = new_pdf.new_page(width=page_width_points, height=page_height_points)
                    
                    # 插入图片到页面（填满整个页面）
                    rect = fitz.Rect(0, 0, page_width_points, page_height_points)
                    page.insert_image(rect, filename=image_path)
                    
                    img.close()
                
                # 保存最终PDF
                new_pdf.save(final_pdf_path)
                new_pdf.close()
                
                logger.info(f"PDF已生成: {final_pdf_path}")
                
                # 调用回调函数
                callback()
                
            finally:
                # 清理临时目录
                import shutil
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    logger.info(f"已清理临时目录: {temp_dir}")
                
                # 清理临时PDF
                if os.path.exists(temp_pdf_path):
                    try:
                        os.remove(temp_pdf_path)
                        logger.info(f"已删除临时 PDF: {temp_pdf_path}")
                    except Exception as e:
                        logger.warning(f"删除 PDF 失败: {e}")
            
        except ImportError:
            logger.error("缺少依赖: PyMuPDF 或 Pillow")
            # 如果缺少依赖，直接调用回调
            callback()
            
        except Exception as e:
            logger.error(f"PDF转图片再合并失败: {e}")
            import traceback
            traceback.print_exc()
            # 即使失败也调用回调
            callback()
    
    def _add_vertical_margins(self, img, margin_size, bg_color):
        """在图片上下添加边距，用指定背景色填充
        
        Args:
            img: PIL Image对象
            margin_size: 上下边距大小（像素）
            bg_color: 背景色RGB元组
            
        Returns:
            添加边距后的PIL Image对象
        """
        try:
            from PIL import Image  # 【关键】导入Image模块
            
            old_width, old_height = img.size
            new_height = old_height + 2 * margin_size
            
            # 【关键】创建新图片，用背景色填充
            new_img = Image.new('RGB', (old_width, new_height), bg_color)
            
            # 【关键】将原图粘贴到新图片的中间位置（y坐标=margin_size）
            new_img.paste(img, (0, margin_size))
            
            # 验证尺寸
            final_width, final_height = new_img.size
            
            return new_img
            
        except Exception as e:
            logger.error(f"添加边距失败: {e}")
            import traceback
            traceback.print_exc()
            return img  # 如果失败，返回原图
    
    def export_image_collection(self):
        """导出预览区为图集（PDF每页转换为图片）"""
        try:
            from PyQt6.QtWidgets import QFileDialog, QMessageBox, QDialog, QVBoxLayout, QLabel, QProgressBar
            from PyQt6.QtCore import QTimer, Qt
            import os
            import tempfile
            
            # 获取文档名用于提示
            base_name = 'document'
            if self.current_file:
                base_name = os.path.splitext(os.path.basename(self.current_file))[0]
            
            # 选择保存目录
            default_dir = ''
            if self.current_file:
                default_dir = os.path.dirname(self.current_file)
            
            # 使用消息框提前告知用户将自动创建子目录
            reply = QMessageBox.question(
                self,
                '导出图集',
                f'系统将在您选择的目录中创建 "{base_name}" 目录，用来保存图集\n\n是否继续？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # 让用户选择父目录
            save_dir = QFileDialog.getExistingDirectory(
                self,
                '选择图集保存的父目录',
                default_dir
            )
            
            if not save_dir:
                return
            
            # 【关键】在用户选择的目录下创建子目录
            # 创建以文档名命名的子目录
            collection_dir = os.path.join(save_dir, base_name)
            if not os.path.exists(collection_dir):
                os.makedirs(collection_dir)
                logger.info(f"创建图集目录: {collection_dir}")
            
            # 【关键】创建进度提示对话框
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle('导出图集')
            progress_dialog.setModal(True)
            progress_dialog.setFixedSize(400, 150)
            
            layout = QVBoxLayout(progress_dialog)
            
            status_label = QLabel('正在执行操作...')
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(status_label)
            
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 0)  # 不确定进度，显示忙碌状态
            layout.addWidget(progress_bar)
            
            tip_label = QLabel('请不要关闭窗口，正在执行操作...')
            tip_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tip_label.setStyleSheet('color: gray; font-size: 12px;')
            layout.addWidget(tip_label)
            
            progress_dialog.show()
            
            self.statusBar().showMessage('正在生成PDF...')
            
            # 【关键】使用临时文件名，避免与输出图片冲突
            temp_pdf = tempfile.NamedTemporaryFile(
                suffix='.pdf',
                prefix='mdeditor_collection_',
                dir=save_dir,
                delete=False
            )
            pdf_path = temp_pdf.name
            temp_pdf.close()
            
            logger.debug(f"临时 PDF 路径: {pdf_path}")
            
            # 【关键】从工具栏下拉框获取页面比例
            page_ratios = {
                'A3': (297.0, 420.0),
                'A4': (210.0, 297.0),
                'A5': (148.0, 210.0),
                'B5': (176.0, 250.0),
                'Letter': (215.9, 279.4),
                'Legal': (215.9, 355.6),
            }
            selected_ratio = self.pdf_ratio_combo.currentData()
            ratio_width, ratio_height = page_ratios[selected_ratio]
            
            # 【新增】获取导出方向
            orientation = self.pdf_orientation_combo.currentData()
            is_landscape = (orientation == 'landscape')
            
            # 如果是横屏，交换宽高
            if is_landscape:
                ratio_width, ratio_height = ratio_height, ratio_width
                logger.info(f"导出图集使用PDF比例: {selected_ratio} ({ratio_height}mm x {ratio_width}mm) - 横屏")
            else:
                logger.info(f"导出图集使用PDF比例: {selected_ratio} ({ratio_width}mm x {ratio_height}mm) - 竖屏")
            
            # 复用导出PDF的逻辑生成PDF，传递用户选择的比例
            self._generate_pdf_with_callback_core(
                pdf_path, 
                lambda: self._convert_pdf_to_image_collection(pdf_path, collection_dir, progress_dialog, is_landscape),
                ratio_width,
                ratio_height
            )
            
        except Exception as e:
            logger.error(f"导出图集失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 关闭进度对话框
            if 'progress_dialog' in locals():
                progress_dialog.close()
            
            QMessageBox.critical(self, '错误', f'导出图集失败:\n{str(e)}')
            self.statusBar().showMessage('导出失败')
    
    def _convert_pdf_to_image_collection(self, pdf_path, save_dir, progress_dialog=None, is_landscape=False):
        """将PDF转换为图集（每页一张图片）
        
        Args:
            pdf_path: PDF文件路径
            save_dir: 图片保存目录
            progress_dialog: 进度对话框（可选）
            is_landscape: 是否为横屏模式（横屏时不添加上下边距）
        """
        try:
            import fitz  # PyMuPDF
            from PIL import Image
            from PyQt6.QtWidgets import QMessageBox
            
            self.statusBar().showMessage('正在转换PDF为图片...')
            
            pdf_document = fitz.open(pdf_path)
            
            if len(pdf_document) == 0:
                raise Exception("PDF为空")
            
            # 获取基础文件名
            base_name = 'document'
            if self.current_file:
                base_name = os.path.splitext(os.path.basename(self.current_file))[0]
            
            # 【关键】直接使用预设的背景色，与CSS中定义完全一致
            default_colors = {
                'default': (255, 255, 255),        # 未设置，默认白色
                'ant': (240, 242, 245),            # #f0f2f5
                'material': (250, 250, 250),       # #fafafa
                'element': (245, 247, 250),        # #f5f7fa
                'arco': (247, 248, 250),           # linear-gradient起始色 #f7f8fa
                'fluent': (243, 243, 243),         # linear-gradient起始色 #f3f3f3
                'shadcn': (255, 255, 255),         # #ffffff
                'glass': (90, 111, 216),          # #5a6fd8 - 柔和紫色
                'neumorphism': (224, 229, 236),    # #e0e5ec
                'flat': (255, 255, 255),           # #ffffff
                'apple': (245, 245, 247),          # var(--apple-bg) = #f5f5f7
                'geek': (0, 0, 0),                 # var(--bg-main) = #000000 纯黑色
                'dark_coder': (26, 26, 32),        # #1a1a20
                'cyber_neon': (0, 0, 0),           # #000000 纯黑色
                'paper_eye': (245, 241, 230),      # #f5f1e6
                'magazine_bw': (255, 255, 255),    # #ffffff
                'business_blue': (248, 249, 250),  # #f8f9fa
                'nordic_cold': (247, 249, 248),    # #f7f9f8
                'old_newspaper': (242, 240, 232),  # #f2f0e8
                'school_fresh': (245, 250, 255),   # #f5faff
            }
            bg_color = default_colors.get(self.current_style, (255, 255, 255))
            logger.debug(f"使用预设背景色: RGB{bg_color} (风格: {self.current_style})")
            
            # 【关键】根据方向决定是否添加上下边距
            # 竖屏：添加上下边距（80像素）
            # 横屏：不添加边距（保持原始尺寸）
            if is_landscape:
                top_bottom_margin = 0  # 横屏时不添加边距
                logger.debug(f"横屏模式：不添加上下边距")
            else:
                top_bottom_margin = 80  # 竖屏时添加80像素边距
                logger.debug(f"竖屏模式：添加上下边距 {top_bottom_margin}px")
            
            image_paths = []
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                # 使用2.0倍分辨率保证清晰度
                zoom = 2.0
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # 【关键】先裁剪掉右侧2像素和底部2像素，消除白边
                width, height = img.size
                logger.debug(f"原始图片尺寸: {width}x{height}")
                if width > 2 and height > 2:
                    img_cropped = img.crop((0, 0, width - 2, height - 2))
                    logger.debug(f"裁剪后尺寸: {img_cropped.size[0]}x{img_cropped.size[1]}")
                else:
                    img_cropped = img
                
                # 【关键】在上下添加边距，用HTML文档背景色填充
                logger.debug(f"开始添加边距，使用背景色: {bg_color}")
                img_with_margins = self._add_vertical_margins(img_cropped, top_bottom_margin, bg_color)
                logger.debug(f"添加边距后尺寸: {img_with_margins.size[0]}x{img_with_margins.size[1]}")
                
                # 保存图片
                image_filename = f"{base_name}_page_{page_num + 1:03d}.png"
                image_path = os.path.join(save_dir, image_filename)
                img_with_margins.save(image_path, 'PNG')
                image_paths.append(image_path)
                
                logger.info(f"已导出第 {page_num + 1}/{len(pdf_document)} 页: {image_filename}")
            
            pdf_document.close()
            
            # 【关键】删除临时 PDF 文件
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                    logger.info(f"已删除临时 PDF: {pdf_path}")
                except Exception as e:
                    logger.warning(f"删除 PDF 失败: {e}")
            
            logger.info(f"图集已导出到: {save_dir}，共 {len(image_paths)} 张图片")
            self.statusBar().showMessage(f'图集已导出: {len(image_paths)} 张图片')
            
            # 关闭进度对话框
            if progress_dialog:
                progress_dialog.close()
            
            QMessageBox.information(
                self, 
                '成功', 
                f'图集已成功导出到:\n{save_dir}\n\n共 {len(image_paths)} 张图片'
            )
            
        except ImportError:
            QMessageBox.warning(
                self, 
                '缺少依赖', 
                '需要安装 PyMuPDF 和 Pillow 才能使用此功能。\n\n'
                '请运行以下命令安装：\n'
                'pip install PyMuPDF pillow'
            )
            self.statusBar().showMessage('导出失败：缺少依赖')
            
        except Exception as e:
            logger.error(f"PDF转图集失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 清理临时 PDF 文件
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                    logger.info(f"已删除临时 PDF: {pdf_path}")
                except:
                    pass
            
            QMessageBox.critical(self, '错误', f'PDF转图集失败:\n{str(e)}')
            self.statusBar().showMessage('导出失败')
    
    def change_style(self, style_key):
        """切换预览风格（内部方法，由防抖定时器调用）"""
        self.current_style = style_key
        
        # 更新工具栏下拉框
        if hasattr(self, 'style_combo'):
            index = self.style_combo.findData(style_key)
            if index != -1:
                self.style_combo.blockSignals(True)  # 阻止信号循环
                self.style_combo.setCurrentIndex(index)
                self.style_combo.blockSignals(False)
        
        # 刷新预览
        self.update_preview()
        self.statusBar().showMessage(f'已切换到: {self.get_style_name(style_key)}')
    
    def get_style_name(self, style_key):
        """获取风格名称"""
        names = {
            'default': '默认风格',
            'ant': 'Ant Design',
            'material': 'Material Design',
            'element': 'Element Plus',
            'arco': 'Arco Design',
            'fluent': 'Fluent Design',
            'shadcn': 'shadcn/ui',
            'glass': '玻璃拟态',
            'neumorphism': '新拟态',
            'flat': '极简扁平风',
            'apple': '苹果风格',
            'geek': '极客复古终端',
        }
        return names.get(style_key, '未知风格')
    
    def get_style_css(self):
        """根据当前风格返回CSS样式"""
        style_functions = {
            'default': style_templates.get_default_style,
            'ant': style_templates.get_ant_style,
            'material': style_templates.get_material_style,
            'element': style_templates.get_element_style,
            'arco': style_templates.get_arco_style,
            'fluent': style_templates.get_fluent_style,
            'shadcn': style_templates.get_shadcn_style,
            'glass': style_templates.get_glass_style,
            'neumorphism': style_templates.get_neumorphism_style,
            'flat': style_templates.get_flat_style,
            'apple': style_templates.get_apple_style,
            'geek': style_templates.get_geek_style,
            'dark_coder': style_templates.get_dark_coder_style,
            'cyber_neon': style_templates.get_cyber_neon_style,
            'paper_eye': style_templates.get_paper_eye_style,
            'magazine_bw': style_templates.get_magazine_bw_style,
            'business_blue': style_templates.get_business_blue_style,
            'nordic_cold': style_templates.get_nordic_cold_style,
            'old_newspaper': style_templates.get_old_newspaper_style,
            'school_fresh': style_templates.get_school_fresh_style,
        }
        
        func = style_functions.get(self.current_style, style_templates.get_default_style)
        base_css = func()
        
        # 计算缩放比例
        zoom_scale = self.preview_zoom / 100.0
        
        # 添加动态字体设置（覆盖基础样式的字体设置）
        font_css = f"""
        html {{
            font-size: {self.base_font_size}px !important;
        }}
        body {{
            font-family: "{self.base_font_family}" !important;
            font-weight: {self.base_font_weight} !important;
        }}
        
        /* 【链接美化】统一优化所有主题的链接样式 */
        a {{
            color: #1677ff !important;  /* 主题高亮色 - 醒目的蓝色 */
            text-decoration: underline !important;  /* 始终显示下划线 */
            text-decoration-thickness: 1px !important;  /* 细下划线 */
            text-underline-offset: 2px !important;  /* 下划线与文字间距 */
            transition: all 0.2s ease !important;  /* 平滑过渡效果 */
            cursor: pointer !important;
        }}
        a:hover {{
            color: #0958d9 !important;  /* hover时颜色加深 */
            text-decoration-thickness: 2px !important;  /* hover时下划线变粗 */
            text-decoration-color: #0958d9 !important;  /* 下划线颜色也加深 */
        }}
        a:active {{
            color: #003eb3 !important;  /* 点击时颜色更深 */
        }}
        
        /* 自动链接样式（<URL>格式）与普通链接一致 */
        a[href^="http"],
        a[href^="https"],
        a[href^="mailto"] {{
            color: #1677ff !important;
        }}
        
        /* 通用标签样式支持 */
        del {{
            text-decoration: line-through;
        }}
        mark {{
            padding: 2px 4px;
            border-radius: 2px;
        }}
        /* 脚注样式 */
        .footnote-ref, .footnote-backref {{
            text-decoration: none;
            color: inherit;
        }}
        /* 隐藏脚注反向链接，避免点击导致页面空白 */
        .footnote-backref {{
            display: none !important;
        }}
        .footnotes {{
            margin-top: 2em;
            padding-top: 1em;
            border-top: 1px solid #ccc;
        }}
        .footnotes ol {{
            padding-left: 1.5em;
        }}
        .footnotes li {{
            margin: 0.5em 0;
        }}
        /* 代码块自动折行 */
        pre, pre code {{
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
            overflow-wrap: break-word !important;
            overflow-x: hidden !important;
        }}
        
        /* 数学公式样式 */
        .math-block {{
            display: block;
            margin: 1em 0;
            text-align: center;
            overflow-x: auto;
        }}
        .math-inline {{
            display: inline-block;
            vertical-align: middle;
        }}
        
        /* Mermaid 图表样式 */
        .mermaid {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 1.5em 0;
            padding: 1em;
            background-color: rgba(255, 255, 255, 0.5);
            border-radius: 8px;
            overflow-x: auto;
        }}
        .mermaid svg {{
            max-width: 100%;
            height: auto;
        }}
        
        /* 任务列表样式 */
        ul li input[type="checkbox"],
        ol li input[type="checkbox"] {{
            margin-right: 8px;
            margin-left: 0;
            cursor: default;
            transform: scale(1.3);
            vertical-align: middle;
            accent-color: #4a90e2;
        }}
        
        /* 任务列表段落样式 - 确保checkbox和文本在同一行 */
        ul li p,
        ol li p {{
            display: inline;
            margin: 0;
            padding: 0;
        }}
        
        /* 已完成任务的文本样式 */
        ul li:has(input[type="checkbox"]:checked),
        ol li:has(input[type="checkbox"]:checked) {{
            color: #6c757d;
        }}
        
        ul li:has(input[type="checkbox"]:checked) > *,
        ol li:has(input[type="checkbox"]:checked) > * {{
            text-decoration: line-through;
            opacity: 0.7;
        }}
        
        /* 打印媒体查询 - 确保所见即所得 */
        @media print {{
            /* 【关键】只保留背景色和图片，其他完全复用屏幕样式 */
            html, body {{
                overflow: visible !important;
                -webkit-print-color-adjust: exact !important;  /* 强制打印背景色和图片 */
                print-color-adjust: exact !important;
                color-adjust: exact !important;  /* 标准属性 */
            }}
            
            /* 【关键】代码块允许跨页 - 超长代码可以自然分页 */
            pre, pre code {{
                white-space: pre-wrap !important;
                word-wrap: break-word !important;
                overflow: visible !important;  /* 确保内容不被裁剪 */
                max-width: 100% !important;
                page-break-inside: auto !important;  /* 允许跨页断开 */
                break-inside: auto !important;
                display: block !important;     /* 确保是块级元素 */
            }}
            /* 图片和表格自适应 */
            img, table {{
                max-width: 100% !important;
                height: auto !important;
            }}
            /* 【关键】表格强制分页 - 每行都可以独立跨页 */
            table {{
                page-break-inside: auto !important;
                break-inside: auto !important;
            }}
            table tr {{
                page-break-inside: auto !important;  /* 允许行内分页 */
                break-inside: auto !important;
            }}
            /* 【关键】禁止表头重复 - 将thead当作普通行处理 */
            table thead {{
                display: table-row-group !important;  /* 不作为特殊表头组，不会重复 */
            }}
            /* 【关键】引用块强制分页 - 允许跨页断开 */
            blockquote {{
                page-break-inside: auto !important;
                break-inside: auto !important;
                overflow: visible !important;  /* 确保内容不被裁剪 */
                display: block !important;     /* 确保是块级元素 */
            }}
            /* 隐藏不需要打印的元素 */
            .no-print {{ display: none !important; }}
        }}
        """
        
        return base_css + font_css
    
    def get_config_path(self):
        """获取配置文件路径"""
        if hasattr(sys, '_MEIPASS'):
            # 打包后，配置文件放在exe同目录
            config_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境，放在项目根目录
            config_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(config_dir, 'editor_config.json')
    
    def load_settings(self):
        """加载上一次的设置"""
        try:
            import json
            config_path = self.get_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                # 恢复风格
                if 'current_style' in config:
                    self.current_style = config['current_style']
                
                # 恢复字体大小
                if 'base_font_size' in config:
                    font_size = config['base_font_size']
                    # 【关键】验证范围：8-72px
                    if 8 <= font_size <= 72:
                        self.base_font_size = font_size
                    else:
                        logger.warning(f"无效的字体大小: {font_size}，使用默认值15")
                        self.base_font_size = 15
                
                # 恢复字重
                if 'base_font_weight' in config:
                    font_weight = config['base_font_weight']
                    # 【关键】验证范围：100-900
                    if 100 <= font_weight <= 900:
                        self.base_font_weight = font_weight
                    else:
                        logger.warning(f"无效的字重: {font_weight}，使用默认值300")
                        self.base_font_weight = 300
                
                # 恢复字体家族
                if 'base_font_family' in config:
                    self.base_font_family = config['base_font_family']
                
                # 恢复预览区缩放
                if 'preview_zoom' in config:
                    zoom = config['preview_zoom']
                    # 【关键】验证范围：20-100%
                    if 20 <= zoom <= 100:
                        self.preview_zoom = zoom
                    else:
                        logger.warning(f"无效的缩放值: {zoom}，使用默认值78")
                        self.preview_zoom = 78
                
                # 【新增】恢复全屏状态
                if 'is_fullscreen' in config and config['is_fullscreen']:
                    self.is_fullscreen = True
                    # 延迟执行全屏，确保窗口已显示
                    QTimer.singleShot(200, lambda: self.showFullScreen())
                
                # 【新增】恢复PDF导出比例
                if 'pdf_export_ratio' in config:
                    self.pdf_export_ratio = config['pdf_export_ratio']
                
                # 【新增】恢复PDF导出方向
                if 'pdf_export_orientation' in config:
                    orientation = config['pdf_export_orientation']
                    if orientation in ['portrait', 'landscape']:
                        self.pdf_export_orientation = orientation
                    else:
                        logger.warning(f"无效的导出方向: {orientation}，使用默认值portrait")
                        self.pdf_export_orientation = 'portrait'
                    
                logger.info(f"已加载配置: 风格={self.current_style}, 字体={self.base_font_family}, "
                      f"字号={self.base_font_size}, 字重={self.base_font_weight}, 缩放={self.preview_zoom}%, 全屏={self.is_fullscreen}, PDF比例={self.pdf_export_ratio}, PDF方向={self.pdf_export_orientation}")
        except Exception as e:
            logger.warning(f"加载配置失败: {e}")
    
    def save_settings(self):
        """保存当前设置"""
        try:
            import json
            config = {
                'current_style': self.current_style,
                'base_font_size': self.base_font_size,
                'base_font_weight': self.base_font_weight,
                'base_font_family': self.base_font_family,
                'preview_zoom': self.preview_zoom,
                'is_fullscreen': self.is_fullscreen,  # 【新增】保存全屏状态
                'pdf_export_ratio': self.pdf_export_ratio,  # 【新增】保存PDF导出比例
                'pdf_export_orientation': self.pdf_export_orientation,  # 【新增】保存PDF导出方向
            }
            
            config_path = self.get_config_path()
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            logger.info(f"配置已保存: {config_path}")
        except Exception as e:
            logger.warning(f"保存配置失败: {e}")
    
    def closeEvent(self, event):
        """窗口关闭时保存设置并检查未保存的修改"""
        # 使用 MD5 判断文档是否有未保存的修改
        if not self.maybe_save():
            # 用户取消保存，不关闭窗口
            event.ignore()
            return
        
        # 保存设置
        self.save_settings()
        super().closeEvent(event)
    
    def resizeEvent(self, event):
        """窗口大小改变时更新预览区宽度"""
        super().resizeEvent(event)
        # 延迟更新，等待布局完成
        QTimer.singleShot(100, self.update_preview_width)
        # 更新拖拽提示层位置
        if self.drag_overlay and self.drag_overlay.isVisible():
            self.update_drag_overlay_position()
    
    def eventFilter(self, obj, event):
        """事件过滤器，跟踪鼠标位置并控制滚动同步定时器"""
        from PyQt6.QtCore import QEvent
        
        if obj == self.editor:
            if event.type() == QEvent.Type.Enter:
                self.mouse_in_editor = True
                self.mouse_in_preview = False
                # 【优化2】鼠标进入编辑区，停止预览区滚动同步定时器
                if self.preview_scroll_active:
                    self.preview_scroll_timer.stop()
                    self.preview_scroll_active = False
            elif event.type() == QEvent.Type.Leave:
                self.mouse_in_editor = False
        elif obj == self.preview:
            if event.type() == QEvent.Type.Enter:
                self.mouse_in_preview = True
                self.mouse_in_editor = False
                # 【优化2】鼠标进入预览区，启动滚动同步定时器
                if not self.preview_scroll_active:
                    self.preview_scroll_timer.start(100)  # 每 100ms 检查一次
                    self.preview_scroll_active = True
            elif event.type() == QEvent.Type.Leave:
                self.mouse_in_preview = False
                # 【优化2】鼠标离开预览区，停止滚动同步定时器
                if self.preview_scroll_active:
                    self.preview_scroll_timer.stop()
                    self.preview_scroll_active = False
        
        return super().eventFilter(obj, event)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入主窗口事件 - 接受所有文件"""
        if event.mimeData().hasUrls():
            # 接受所有文件，验证在dropEvent中进行
            event.acceptProposedAction()
            # 显示拖拽提示层
            self.show_drag_overlay()
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """拖拽离开主窗口事件"""
        self.hide_drag_overlay()
        event.accept()
    
    def dropEvent(self, event: QDropEvent):
        """拖拽放下事件 - 调用统一的打开方法"""
        self.hide_drag_overlay()
        
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                # 调用打开文件方法（会进行统一验证）
                self.open_file_by_path(file_path)
                break
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def show_drag_overlay(self):
        """显示拖拽提示层"""
        if self.drag_overlay is None:
            from PyQt6.QtWidgets import QLabel
            
            # 创建半透明提示层
            self.drag_overlay = QLabel('📄 释放鼠标以打开文件', self)
            self.drag_overlay.setStyleSheet("""
                QLabel {
                    background-color: rgba(74, 144, 226, 0.9);
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    border-radius: 10px;
                    padding: 30px 50px;
                }
            """)
            self.drag_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.drag_overlay.setVisible(False)
            
            # 设置提示层位置和大小
            self.update_drag_overlay_position()
        
        self.drag_overlay.setVisible(True)
        self.drag_overlay.raise_()
    
    def hide_drag_overlay(self):
        """隐藏拖拽提示层"""
        if self.drag_overlay:
            self.drag_overlay.setVisible(False)
    
    def update_drag_overlay_position(self):
        """更新拖拽提示层位置"""
        if self.drag_overlay:
            # 居中显示
            overlay_width = 300
            overlay_height = 80
            x = (self.width() - overlay_width) // 2
            y = (self.height() - overlay_height) // 2
            self.drag_overlay.setGeometry(x, y, overlay_width, overlay_height)


class SearchDialog(QDialog):
    """搜索对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
    
    def closeEvent(self, event):
        """对话框关闭事件 - 通知主窗口清理引用"""
        if self.parent_window and hasattr(self.parent_window, 'search_dialog'):
            self.parent_window.search_dialog = None
        super().closeEvent(event)
    
    def init_ui(self):
        """初始化搜索对话框界面"""
        self.setWindowTitle('查找')
        self.setFixedSize(450, 120)
        self.setModal(False)  # 非模态对话框，可以同时操作主窗口
        
        layout = QVBoxLayout()
        
        # 搜索输入框
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel('查找内容:'))
        self.search_input = QLineEdit()
        input_layout.addWidget(self.search_input)
        layout.addLayout(input_layout)
        
        # 选项和导航按钮
        options_layout = QHBoxLayout()
        self.case_sensitive_checkbox = QCheckBox('区分大小写')
        options_layout.addWidget(self.case_sensitive_checkbox)
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 上一个按钮
        prev_btn = QPushButton('↑ 上一个')
        prev_btn.setFixedWidth(80)
        prev_btn.clicked.connect(self.find_previous)
        button_layout.addWidget(prev_btn)
        
        # 下一个按钮
        next_btn = QPushButton('↓ 下一个')
        next_btn.setFixedWidth(80)
        next_btn.clicked.connect(self.find_next)
        button_layout.addWidget(next_btn)
        
        button_layout.addStretch()
        
        # 查找全部按钮
        find_all_btn = QPushButton('查找全部')
        find_all_btn.setFixedWidth(80)
        find_all_btn.clicked.connect(self.find_all)
        button_layout.addWidget(find_all_btn)
        
        # 关闭按钮
        close_btn = QPushButton('关闭')
        close_btn.setFixedWidth(60)
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 绑定回车键到查找下一个
        self.search_input.returnPressed.connect(self.find_next)
    
    def find_next(self):
        """查找下一个"""
        search_text = self.search_input.text()
        if search_text:
            case_sensitive = self.case_sensitive_checkbox.isChecked()
            # 如果搜索文本改变或没有搜索结果，重新搜索
            if search_text != self.parent_window.current_search_text or not self.parent_window.search_results:
                self.parent_window.perform_search(search_text, case_sensitive, find_all=False)
            else:
                # 否则直接跳转到下一个
                self.parent_window.find_next()
    
    def find_previous(self):
        """查找上一个"""
        search_text = self.search_input.text()
        if search_text:
            case_sensitive = self.case_sensitive_checkbox.isChecked()
            # 如果搜索文本改变或没有搜索结果，重新搜索
            if search_text != self.parent_window.current_search_text or not self.parent_window.search_results:
                self.parent_window.perform_search(search_text, case_sensitive, find_all=False)
            else:
                # 否则直接跳转到上一个
                self.parent_window.find_previous()
    
    def find_all(self):
        """查找全部"""
        search_text = self.search_input.text()
        if search_text:
            case_sensitive = self.case_sensitive_checkbox.isChecked()
            self.parent_window.perform_search(search_text, case_sensitive, find_all=True)


class ReplaceDialog(QDialog):
    """替换对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
    
    def closeEvent(self, event):
        """对话框关闭事件 - 通知主窗口清理引用"""
        if self.parent_window and hasattr(self.parent_window, 'replace_dialog'):
            self.parent_window.replace_dialog = None
        super().closeEvent(event)
    
    def init_ui(self):
        """初始化替换对话框界面"""
        self.setWindowTitle('替换')
        self.setFixedSize(450, 180)
        self.setModal(False)  # 非模态对话框，可以同时操作主窗口
        
        layout = QVBoxLayout()
        
        # 搜索输入框
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel('查找内容:'))
        self.search_input = QLineEdit()
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # 替换输入框
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel('替换为:'))
        self.replace_input = QLineEdit()
        replace_layout.addWidget(self.replace_input)
        layout.addLayout(replace_layout)
        
        # 选项
        options_layout = QHBoxLayout()
        self.case_sensitive_checkbox = QCheckBox('区分大小写')
        options_layout.addWidget(self.case_sensitive_checkbox)
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 替换按钮
        replace_btn = QPushButton('替换')
        replace_btn.setFixedWidth(80)
        replace_btn.clicked.connect(self.replace_one)
        button_layout.addWidget(replace_btn)
        
        # 全部替换按钮
        replace_all_btn = QPushButton('全部替换')
        replace_all_btn.setFixedWidth(80)
        replace_all_btn.clicked.connect(self.replace_all)
        button_layout.addWidget(replace_all_btn)
        
        button_layout.addStretch()
        
        # 关闭按钮
        close_btn = QPushButton('关闭')
        close_btn.setFixedWidth(60)
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 绑定回车键到替换
        self.replace_input.returnPressed.connect(self.replace_one)
    
    def replace_one(self):
        """替换一个匹配项"""
        search_text = self.search_input.text()
        replace_text = self.replace_input.text()
        
        if not search_text:
            QMessageBox.information(self, '提示', '请输入查找内容')
            return
        
        case_sensitive = self.case_sensitive_checkbox.isChecked()
        
        # 如果没有搜索结果或搜索文本改变，先执行搜索
        if search_text != self.parent_window.current_search_text or not self.parent_window.search_results:
            self.parent_window.perform_search(search_text, case_sensitive, find_all=False)
        
        # 如果有选中的搜索结果，执行替换
        if self.parent_window.current_search_index >= 0 and self.parent_window.current_search_index < len(self.parent_window.search_results):
            cursor = self.parent_window.editor.textCursor()
            if cursor.hasSelection():
                cursor.insertText(replace_text)
                self.parent_window.editor.setTextCursor(cursor)
                
                # 更新文档修改状态
                self.parent_window.editor.document().setModified(True)
                
                # 继续查找下一个
                self.parent_window.find_next()
                
                self.parent_window.statusBar().showMessage('已替换 1 处')
            else:
                QMessageBox.information(self, '提示', '请先选择一个匹配项')
        else:
            QMessageBox.information(self, '提示', '未找到匹配项')
    
    def replace_all(self):
        """替换所有匹配项"""
        search_text = self.search_input.text()
        replace_text = self.replace_input.text()
        
        if not search_text:
            QMessageBox.information(self, '提示', '请输入查找内容')
            return
        
        case_sensitive = self.case_sensitive_checkbox.isChecked()
        
        # 获取全文
        full_text = self.parent_window.editor.toPlainText()
        
        # 执行替换
        if case_sensitive:
            new_text = full_text.replace(search_text, replace_text)
        else:
            # 不区分大小写的替换
            import re
            new_text = re.sub(re.escape(search_text), replace_text, full_text, flags=re.IGNORECASE)
        
        # 计算替换次数
        if case_sensitive:
            count = full_text.count(search_text)
        else:
            count = len(re.findall(re.escape(search_text), full_text, re.IGNORECASE))
        
        if count > 0:
            # 设置新文本
            self.parent_window.editor.setPlainText(new_text)
            
            # 更新文档修改状态
            self.parent_window.editor.document().setModified(True)
            
            # 清除高亮
            self.parent_window.clear_highlight()
            
            # 重置搜索状态
            self.parent_window.search_results = []
            self.parent_window.current_search_index = -1
            self.parent_window.current_search_text = ''
            
            self.parent_window.statusBar().showMessage(f'已替换 {count} 处')
            QMessageBox.information(self, '替换完成', f'共替换 {count} 处')
        else:
            QMessageBox.information(self, '提示', '未找到匹配项')


def main():
    import traceback
    
    # 【优化11】创建日志文件，保存到exe同级目录的log子目录
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller打包后：log目录在exe所在目录
        log_base_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境：log目录在项目根目录（main.py所在目录）
        log_base_dir = os.path.dirname(os.path.abspath(__file__))
    
    log_dir = os.path.join(log_base_dir, 'log')
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except:
            log_dir = log_base_dir  # 如果创建失败，使用exe同级目录
    
    log_file = os.path.join(log_dir, 'error.log')
    
    try:
        logger.info("Starting Markdown Editor...")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Is frozen: {hasattr(sys, '_MEIPASS')}")
        if hasattr(sys, '_MEIPASS'):
            logger.info(f"MEIPASS: {sys._MEIPASS}")
        
        # Qt6: 在创建 QApplication 之前设置高 DPI 策略
        from PyQt6.QtGui import QGuiApplication
        from PyQt6.QtCore import Qt
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # 使用Fusion风格
        
        # 检查是否有命令行参数传入的文件路径
        file_path = None
        if len(sys.argv) > 1:
            potential_file = sys.argv[1]
            if os.path.exists(potential_file) and potential_file.lower().endswith(('.md', '.markdown')):
                file_path = potential_file
                logger.info(f"Opening file from command line: {file_path}")
        
        logger.info("Creating MainWindow...")
        editor = MarkdownEditor(file_path=file_path)
        logger.info("Showing window...")
        editor.show()
        
        logger.info("Starting event loop...")
        exit_code = app.exec()
        logger.info(f"Exit code: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        # 将错误写入文件
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        logger.critical(error_msg)
        raise


if __name__ == '__main__':
    main()
