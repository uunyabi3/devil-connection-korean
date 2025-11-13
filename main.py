#!/usr/bin/env python3                     
import sys
import platform
import shutil
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QProgressBar,
    QFileDialog, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

try:
    from asar import extract_archive, create_archive
    ASAR_AVAILABLE = True
except ImportError:
    ASAR_AVAILABLE = False


class InstallWorker(QThread):
    log_signal = pyqtSignal(str, str)  
    finished_signal = pyqtSignal(bool, str)  

    def __init__(self, game_path, base_path):
        super().__init__()
        self.game_path = Path(game_path)
        self.base_path = base_path

    def run(self):
        try:
            self.log_signal.emit("=" * 60, "info")
            self.log_signal.emit("설치를 시작합니다...", "info")
            self.log_signal.emit("1단계: app.asar 파일 찾기...", "info")

            asar_path = self.find_app_asar_path(self.game_path)
            if not asar_path:
                raise Exception("app.asar 파일을 찾을 수 없습니다. 게임 경로를 확인해주세요.")

            self.log_signal.emit(f"app.asar 파일 위치: {asar_path}", "success")

            resources_dir = asar_path.parent
            app_folder = resources_dir / "app"
            backup_path = resources_dir / "app.asar.backup"

            self.log_signal.emit("2단계: 원본 파일 백업...", "info")
            if backup_path.exists():
                self.log_signal.emit("백업 파일이 이미 존재합니다. 기존 백업을 유지합니다.", "info")
            else:
                self.log_signal.emit("원본 파일을 백업합니다...", "info")
                shutil.copy2(asar_path, backup_path)
                self.log_signal.emit("백업 완료", "success")

                             
            self.log_signal.emit("3단계: 기존 패치 파일 정리...", "info")
            if app_folder.exists():
                self.log_signal.emit("기존 app 폴더를 삭제합니다...", "info")
                shutil.rmtree(app_folder)
                self.log_signal.emit("삭제 완료", "success")

                               
            self.log_signal.emit("4단계: app.asar 압축 해제 중... (시간이 걸릴 수 있습니다)", "info")
            extract_archive(asar_path, app_folder)
            self.log_signal.emit("압축 해제 완료", "success")


            self.log_signal.emit("5단계: 번역 파일 복사 중...", "info")


            src_scenario = self.base_path / "data/scenario"
            dst_scenario = app_folder / "data/scenario"
            if src_scenario.exists():
                dst_scenario.mkdir(parents=True, exist_ok=True)
                ks_files = list(src_scenario.glob("**/*.ks"))
                self.log_signal.emit(f"  - scenario 파일 {len(ks_files)}개 복사 중...", "info")
                for ks_file in ks_files:
                    relative_path = ks_file.relative_to(src_scenario)
                    dest_file = dst_scenario / relative_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(ks_file, dest_file)
                self.log_signal.emit("  - scenario 파일 복사 완료", "success")


            src_others = self.base_path / "data/others"
            dst_others = app_folder / "data/others"
            if src_others.exists():
                dst_others.mkdir(parents=True, exist_ok=True)
                js_files = list(src_others.glob("*.js"))
                self.log_signal.emit(f"  - others JS 파일 {len(js_files)}개 복사 중...", "info")
                for js_file in js_files:
                    shutil.copy2(js_file, dst_others / js_file.name)
                self.log_signal.emit("  - others JS 파일 복사 완료", "success")

            # MapleStory 폰트 파일 복사
            src_font = self.base_path / "data/others/MapleStoryBold.ttf"
            dst_font = app_folder / "data/others/MapleStoryBold.ttf"
            if src_font.exists():
                shutil.copy2(src_font, dst_font)
                self.log_signal.emit("  - MapleStory 폰트 복사 완료", "success")

            # plugin 폴더 복사
            src_backlog_js = self.base_path / "data/others/plugin/backlog/backlog/backlog.js"
            src_backlog_css = self.base_path / "data/others/plugin/backlog/backlog/backlog.css"
            dst_backlog_dir = app_folder / "data/others/plugin/backlog/backlog"
            if src_backlog_js.exists() or src_backlog_css.exists():
                dst_backlog_dir.mkdir(parents=True, exist_ok=True)
                if src_backlog_js.exists():
                    shutil.copy2(src_backlog_js, dst_backlog_dir / "backlog.js")
                if src_backlog_css.exists():
                    shutil.copy2(src_backlog_css, dst_backlog_dir / "backlog.css")
                self.log_signal.emit("  - backlog 플러그인 복사 완료", "success")

            src_popopo = self.base_path / "data/others/plugin/popopo_chara/main.js"
            dst_popopo_dir = app_folder / "data/others/plugin/popopo_chara"
            if src_popopo.exists():
                dst_popopo_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_popopo, dst_popopo_dir / "main.js")
                self.log_signal.emit("  - popopo_chara 플러그인 복사 완료", "success")

            # system 폴더 복사
            src_config = self.base_path / "data/system/Config.tjs"
            dst_system = app_folder / "data/system"
            if src_config.exists():
                dst_system.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_config, dst_system / "Config.tjs")
                self.log_signal.emit("  - system/Config.tjs 복사 완료", "success")


            src_lang = self.base_path / "tyrano/lang.js"
            dst_lang = app_folder / "tyrano/lang.js"
            if src_lang.exists():
                dst_lang.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_lang, dst_lang)
                self.log_signal.emit("  - tyrano/lang.js 복사 완료", "success")

            src_tyrano_css = self.base_path / "tyrano/tyrano.css"
            dst_tyrano_css = app_folder / "tyrano/tyrano.css"
            if src_tyrano_css.exists():
                shutil.copy2(src_tyrano_css, dst_tyrano_css)
                self.log_signal.emit("  - tyrano/tyrano.css 복사 완료", "success")

            src_font_css = self.base_path / "tyrano/css/font.css"
            dst_font_css_dir = app_folder / "tyrano/css"
            if src_font_css.exists():
                dst_font_css_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_font_css, dst_font_css_dir / "font.css")
                self.log_signal.emit("  - tyrano/css/font.css 복사 완료", "success")


            self.log_signal.emit("6단계: app 폴더를 app.asar로 재압축 중... (시간이 걸릴 수 있습니다)", "info")
            if asar_path.exists() and asar_path.is_file():
                asar_path.unlink()
                self.log_signal.emit("원본 app.asar 파일을 삭제했습니다.", "info")

            create_archive(app_folder, asar_path, unpack="*.node")
            self.log_signal.emit("app.asar 재압축 완료", "success")

            self.log_signal.emit("7단계: 임시 파일 정리 중...", "info")
            if app_folder.exists():
                shutil.rmtree(app_folder)
                self.log_signal.emit("app 폴더를 삭제했습니다.", "success")


            self.log_signal.emit("=" * 60, "info")
            self.log_signal.emit("한글패치가 완료되었습니다!", "success")
            self.log_signal.emit("Steam에서 게임을 실행하면 한글로 플레이하실 수 있습니다.", "success")


            if platform.system() == "Darwin":
                self.log_signal.emit("", "info")
                self.log_signal.emit("macOS 사용자 안내:", "warning")
                self.log_signal.emit("게임 실행 시 '손상되었습니다' 경고가 나타날 수 있습니다.", "info")
                self.log_signal.emit("이는 정상적인 macOS 보안 경고이며, 다음과 같이 해결하세요:", "info")
                self.log_signal.emit("1. 시스템 설정 > 개인정보 보호 및 보안 열기", "info")
                self.log_signal.emit("2. '그래도 열기' 버튼 클릭", "info")

            self.log_signal.emit("", "info")
            self.log_signal.emit("메이플스토리 서체 사용 안내:", "info")
            self.log_signal.emit("본 한글패치는 ㈜넥슨코리아의 메이플스토리 서체를 사용합니다.", "info")
            self.log_signal.emit("메이플스토리 서체의 지적 재산권은 ㈜넥슨코리아에 있습니다.", "info")
            self.log_signal.emit("=" * 60, "info")


            if platform.system() == "Darwin":
                complete_msg = (
                    "한글패치가 완료되었습니다!\n\n"
                    "Steam에서 게임을 실행하시면 됩니다.\n\n"
                    "'손상되었습니다' 경고가 나타나면:\n"
                    "시스템 설정 > 개인정보 보호 및 보안\n"
                    "에서 '그래도 열기' 버튼을 클릭하세요.\n\n"
                    "────────────────────────\n"
                    "메이플스토리 서체 사용 안내:\n"
                    "본 한글패치는 ㈜넥슨코리아의 메이플스토리 서체를 사용합니다.\n"
                    "메이플스토리 서체의 지적 재산권은 ㈜넥슨코리아에 있습니다."
                )
            else:
                complete_msg = (
                    "한글패치가 완료되었습니다!\n\n"
                    "Steam에서 게임을 실행하면 한글로 플레이하실 수 있습니다.\n\n"
                    "────────────────────────\n"
                    "메이플스토리 서체 사용 안내:\n"
                    "본 한글패치는 ㈜넥슨코리아의 메이플스토리 서체를 사용합니다.\n"
                    "메이플스토리 서체의 지적 재산권은 ㈜넥슨코리아에 있습니다."
                )

            self.finished_signal.emit(True, complete_msg)

        except Exception as e:
            self.log_signal.emit("=" * 60, "error")
            self.log_signal.emit(f"설치 중 오류 발생: {str(e)}", "error")
            self.log_signal.emit("=" * 60, "error")
            self.finished_signal.emit(False, f"설치 중 오류가 발생했습니다:\n\n{str(e)}")

    def find_app_asar_path(self, game_path):
        game_path = Path(game_path)
        system = platform.system()

        if system == "Windows":
            asar_path = game_path / "resources/app.asar"
        elif system == "Darwin":
            asar_path = game_path / "DevilConnection.app/Contents/Resources/app.asar"
        else:
            return None

        return asar_path if asar_path.exists() else None


class KoreanPatchInstaller(QMainWindow):
    def __init__(self):
        super().__init__()

                  
        if getattr(sys, 'frozen', False):
            self.base_path = Path(sys._MEIPASS)
        else:
            self.base_path = Path(__file__).parent

        self.worker = None
        self.init_ui()

                       
        if not ASAR_AVAILABLE:
            self.add_log("asar 라이브러리가 설치되어 있지 않습니다.", "warning")
            self.add_log("터미널에서 'pip install asar' 명령어로 설치해주세요.", "warning")

    def init_ui(self):
        self.setWindowTitle("でびるコネクショん 한글패치")
        self.setFixedSize(800, 650)

               
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

                 
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)

                
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)

        title_label = QLabel("でびるコネクショん")
        title_label.setFont(QFont(get_system_font(), 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title_label)

        subtitle_label = QLabel("한글패치 프로그램")
        subtitle_label.setFont(QFont(get_system_font(), 11))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #718096;")
        title_layout.addWidget(subtitle_label)

        main_layout.addLayout(title_layout)
        main_layout.addSpacing(10)

                  
        path_card = self.create_card()
        path_layout = QVBoxLayout()
        path_layout.setContentsMargins(20, 20, 20, 20)
        path_layout.setSpacing(12)

        path_title = QLabel("게임 경로")
        path_title.setFont(QFont(get_system_font(), 10, QFont.Weight.Bold))
        path_layout.addWidget(path_title)

               
        self.path_input = QLineEdit()
        self.path_input.setFont(QFont(get_system_font(), 10))
        self.path_input.setPlaceholderText("게임이 설치된 경로를 선택하세요")
        self.path_input.setMinimumHeight(40)
        path_layout.addWidget(self.path_input)

                 
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

                  
        self.auto_btn = QPushButton("자동 감지")
        self.auto_btn.setFont(QFont(get_system_font(), 10))
        self.auto_btn.setMinimumHeight(40)
        self.auto_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.auto_btn.clicked.connect(self.auto_detect_path)
        button_layout.addWidget(self.auto_btn)

                 
        self.browse_btn = QPushButton("찾아보기")
        self.browse_btn.setFont(QFont(get_system_font(), 10))
        self.browse_btn.setMinimumHeight(40)
        self.browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_btn.clicked.connect(self.browse_path)
        button_layout.addWidget(self.browse_btn)

               
        self.install_btn = QPushButton("설치 시작")
        self.install_btn.setFont(QFont(get_system_font(), 11, QFont.Weight.Bold))
        self.install_btn.setMinimumHeight(40)
        self.install_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.install_btn.clicked.connect(self.start_installation)
        button_layout.addWidget(self.install_btn)

        path_layout.addLayout(button_layout)
        path_card.setLayout(path_layout)
        main_layout.addWidget(path_card)

                  
        progress_card = self.create_card()
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(20, 15, 20, 15)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)            
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        progress_card.setLayout(progress_layout)
        main_layout.addWidget(progress_card)

               
        log_card = self.create_card()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(20, 20, 20, 20)
        log_layout.setSpacing(10)

        log_title = QLabel("설치 로그")
        log_title.setFont(QFont(get_system_font(), 10, QFont.Weight.Bold))
        log_layout.addWidget(log_title)

        self.log_text = QTextEdit()
        self.log_text.setFont(QFont(get_monospace_font(), 9))
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(250)
        log_layout.addWidget(self.log_text)

        log_card.setLayout(log_layout)
        main_layout.addWidget(log_card, 1)

                  
        self.apply_styles()


        self.add_log("でびるコネクショん 한글패치 프로그램을 시작합니다.", "info")
        self.add_log("", "info")
        self.add_log("'자동 감지' 버튼을 클릭하거나 게임 경로를 직접 선택해주세요.", "info")
        self.add_log("", "info")
        self.add_log("=" * 60, "info")
        self.add_log("메이플스토리 서체 사용 안내", "info")
        self.add_log("본 프로그램은 ㈜넥슨코리아의 메이플스토리 서체를 사용합니다.", "info")
        self.add_log("메이플스토리 서체의 지적 재산권은 ㈜넥슨코리아에 있습니다.", "info")
        self.add_log("=" * 60, "info")

    def create_card(self):
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        return card

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QLabel {
                color: #2d3748;
                background: transparent;
                border: none;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                background-color: white;
                color: #2d3748;
            }
            QLineEdit:focus {
                border: 1px solid #4a5568;
            }
            QPushButton {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 10px 20px;
                color: #2d3748;
            }
            QPushButton:hover {
                background-color: #f7fafc;
                border-color: #cbd5e0;
            }
            QPushButton:pressed {
                background-color: #edf2f7;
            }
            QPushButton:disabled {
                background-color: #f7fafc;
                color: #a0aec0;
            }
            QPushButton#install_btn {
                background-color: #48bb78;
                color: white;
                border: none;
            }
            QPushButton#install_btn:hover {
                background-color: #38a169;
            }
            QPushButton#install_btn:pressed {
                background-color: #2f855a;
            }
            QPushButton#install_btn:disabled {
                background-color: #c6f6d5;
            }
            QTextEdit {
                border: none;
                background-color: #fafafa;
                color: #2d3748;
                border-radius: 6px;
                padding: 10px;
            }
            QProgressBar {
                border: none;
                background-color: #e2e8f0;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #48bb78;
                border-radius: 4px;
            }
        """)

                      
        self.install_btn.setObjectName("install_btn")

    def add_log(self, message, level="info"):
        color_map = {
            "info": "#2d3748",
            "success": "#48bb78",
            "error": "#f56565",
            "warning": "#ed8936"
        }

        color = color_map.get(level, "#2d3748")
        formatted_message = f'<span style="color: {color};">{message}</span>'

        self.log_text.append(formatted_message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "Devil Connection 게임 폴더를 선택하세요",
            ""
        )
        if path:
            self.path_input.setText(path)
            self.add_log(f"게임 경로 선택: {path}", "success")

    def auto_detect_path(self):
        self.add_log("게임 경로를 자동으로 검색 중...", "info")

        system = platform.system()
        possible_paths = []

        if system == "Windows":
                              
            steam_paths = [
                Path("C:/Program Files (x86)/Steam"),
                Path("C:/Program Files/Steam"),
            ]

                         
            for drive in "DEFGHIJ":
                steam_paths.extend([
                    Path(f"{drive}:/Steam"),
                    Path(f"{drive}:/Program Files (x86)/Steam"),
                    Path(f"{drive}:/Program Files/Steam"),
                    Path(f"{drive}:/SteamLibrary"),
                ])

            for steam_path in steam_paths:
                game_path = steam_path / "steamapps/common/でびるコネクショん"
                if game_path.exists():
                    possible_paths.append(game_path)

        elif system == "Darwin":         
                            
            steam_path = Path.home() / "Library/Application Support/Steam"
            game_path = steam_path / "steamapps/common/でびるコネクショん"
            if game_path.exists():
                possible_paths.append(game_path)

        if possible_paths:
            detected_path = str(possible_paths[0])
            self.path_input.setText(detected_path)
            self.add_log("게임을 찾았습니다!", "success")
            self.add_log(f"경로: {detected_path}", "info")
        else:
            self.add_log("게임 경로를 자동으로 찾지 못했습니다.", "warning")
            self.add_log("'찾아보기' 버튼으로 직접 선택해주세요.", "info")
            QMessageBox.warning(
                self,
                "경로 감지 실패",
                "게임 경로를 자동으로 찾지 못했습니다.\n\n'찾아보기' 버튼을 눌러 직접 선택해주세요."
            )

    def start_installation(self):
        if not ASAR_AVAILABLE:
            QMessageBox.critical(
                self,
                "설치 오류",
                "asar 라이브러리가 설치되어 있지 않습니다.\n\n"
                "터미널에서 다음 명령어를 실행해주세요:\n"
                "pip install asar"
            )
            return

        game_path = self.path_input.text().strip()
        if not game_path:
            QMessageBox.warning(self, "경로 없음", "게임 경로를 먼저 선택해주세요.")
            return

                 
        self.install_btn.setEnabled(False)
        self.auto_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.progress_bar.setVisible(True)

                   
        self.worker = InstallWorker(game_path, self.base_path)
        self.worker.log_signal.connect(self.add_log)
        self.worker.finished_signal.connect(self.installation_finished)
        self.worker.start()

    def installation_finished(self, success, message):                
        self.install_btn.setEnabled(True)
        self.auto_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

                
        if success:
            QMessageBox.information(self, "설치 완료", message)
        else:
            QMessageBox.critical(self, "설치 오류", message)


def get_system_font():
    system = platform.system()
    if system == "Darwin":         
        return "Apple SD Gothic Neo"
    elif system == "Windows":
        return "Malgun Gothic"
    else:         
        return "Noto Sans CJK KR"


def get_monospace_font():
    system = platform.system()
    if system == "Darwin":         
        return "Menlo"
    elif system == "Windows":
        return "Consolas"
    else:         
        return "DejaVu Sans Mono"


def main():
    app = QApplication(sys.argv)

                  
    font = QFont(get_system_font(), 10)
    app.setFont(font)

    installer = KoreanPatchInstaller()
    installer.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
