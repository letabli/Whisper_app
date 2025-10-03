"""
메인 윈도우 모듈
애플리케이션의 메인 UI
"""
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QMessageBox,
                             QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.widgets import (LanguageSelector, ModelSelector, OutputFormatSelector,
                        SummaryOptions, TranslationOptions)
from ui.progress_dialog import ProgressDialog
from workers import TranscriptionWorker
from utils import (FileValidator, ConfigValidator, get_config, set_config,
                  info, error)


class MainWindow(QMainWindow):
    """메인 윈도우 클래스"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Whisper 자막 변환 도구 v2.0")
        self.setGeometry(100, 100, 900, 750)
        
        self.current_file = None
        self.worker = None
        self.progress_dialog = None
        
        self._setup_ui()
        self._load_settings()
        
        info("애플리케이션 시작됨")
    
    def _setup_ui(self):
        """UI 구성"""
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        
        # === 제목 ===
        title_label = QLabel("🎙️ Whisper 자막 변환 도구")
        title_font = QFont("Arial", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # === 파일 선택 섹션 ===
        file_group = QGroupBox("📁 파일 선택")
        file_layout = QHBoxLayout(file_group)
        
        self.file_label = QLabel("선택된 파일 없음")
        self.file_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        
        self.browse_button = QPushButton("파일 찾기")
        self.browse_button.setMinimumWidth(120)
        self.browse_button.clicked.connect(self._browse_file)
        
        file_layout.addWidget(self.file_label, 1)
        file_layout.addWidget(self.browse_button)
        
        main_layout.addWidget(file_group)
        
        # === 옵션 섹션 ===
        options_layout = QHBoxLayout()
        
        # 왼쪽 열
        left_column = QVBoxLayout()
        
        self.language_selector = LanguageSelector()
        self.model_selector = ModelSelector()
        
        left_column.addWidget(self.language_selector)
        left_column.addWidget(self.model_selector)
        left_column.addStretch()
        
        # 오른쪽 열
        right_column = QVBoxLayout()
        
        self.format_selector = OutputFormatSelector()
        self.summary_options = SummaryOptions()
        self.translation_options = TranslationOptions()
        
        right_column.addWidget(self.format_selector)
        right_column.addWidget(self.summary_options)
        right_column.addWidget(self.translation_options)
        
        options_layout.addLayout(left_column, 1)
        options_layout.addLayout(right_column, 1)
        
        main_layout.addLayout(options_layout)
        
        # === 실행 버튼 ===
        self.start_button = QPushButton("🚀 변환 시작")
        self.start_button.setMinimumHeight(50)
        self.start_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.start_button.clicked.connect(self._start_conversion)
        
        main_layout.addWidget(self.start_button)
        
        # === 상태바 ===
        self.statusBar().showMessage("준비")
        
        # === 메뉴바 ===
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("파일")
        file_menu.addAction("열기", self._browse_file, "Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("종료", self.close, "Ctrl+Q")
        
        help_menu = menubar.addMenu("도움말")
        help_menu.addAction("정보", self._show_about)
    
    def _browse_file(self):
        """파일 탐색 다이얼로그"""
        last_dir = get_config('last_directory', os.path.expanduser('~'))
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "변환할 파일 선택",
            last_dir,
            "모든 파일 (*);;비디오 파일 (*.mp4 *.avi *.mkv *.mov);;오디오 파일 (*.mp3 *.wav *.ogg *.flac)"
        )
        
        if file_path:
            # 파일 검증
            is_valid, message = FileValidator.validate_file(file_path)
            
            if is_valid:
                self.current_file = file_path
                self.file_label.setText(file_path)
                
                # 마지막 디렉토리 저장
                set_config('last_directory', os.path.dirname(file_path))
                
                info(f"파일 선택됨: {file_path}")
                self.statusBar().showMessage(f"파일 선택됨: {os.path.basename(file_path)}")
            else:
                QMessageBox.warning(self, "파일 검증 실패", message)
                error(f"파일 검증 실패: {message}")
    
    def _start_conversion(self):
        """변환 시작"""
        # 파일 확인
        if not self.current_file:
            QMessageBox.warning(self, "경고", "파일을 선택해주세요!")
            return
        
        # 출력 형식 확인
        output_formats = self.format_selector.get_formats()
        if not output_formats:
            QMessageBox.warning(self, "경고", "하나 이상의 출력 형식을 선택해주세요!")
            return
        
        # 설정 저장
        self._save_settings()
        
        # 워커 생성
        summary_opts = self.summary_options.get_options()
        translation_opts = self.translation_options.get_options()
        
        self.worker = TranscriptionWorker(
            file_path=self.current_file,
            model_size=self.model_selector.get_model_size(),
            language=self.language_selector.get_language(),
            output_formats=output_formats,
            enable_summary=summary_opts['enabled'],
            summary_ratio=summary_opts['ratio'],
            enable_translation=translation_opts['enabled'],
            target_language=translation_opts['target_language']
        )
        
        # 진행률 다이얼로그 생성
        self.progress_dialog = ProgressDialog(self, "변환 진행 중")
        
        # 시그널 연결
        self.worker.progress_updated.connect(self.progress_dialog.update_progress)
        self.worker.status_updated.connect(self.progress_dialog.update_status)
        self.worker.error_occurred.connect(self.progress_dialog.show_error)
        self.worker.finished.connect(self._on_conversion_finished)
        
        # 취소 버튼 연결
        self.progress_dialog.cancel_button.clicked.connect(self.worker.cancel)
        
        # UI 비활성화
        self.start_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        
        # 워커 시작
        self.worker.start()
        
        # 다이얼로그 표시
        self.progress_dialog.exec_()
    
    def _on_conversion_finished(self, success, result):
        """변환 완료 콜백"""
        # UI 활성화
        self.start_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        
        if success:
            self.progress_dialog.show_success("모든 작업이 완료되었습니다!")
            
            # 결과 메시지
            files = result.get('files', [])
            
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("변환 완료")
            msg.setText(f"✅ 변환이 완료되었습니다!\n\n생성된 파일 수: {len(files)}")
            
            if files:
                files_text = "\n".join([f"• {os.path.basename(f)}" for f in files])
                msg.setDetailedText(f"생성된 파일:\n{files_text}")
            
            open_folder_btn = msg.addButton("폴더 열기", QMessageBox.ActionRole)
            msg.addButton("확인", QMessageBox.AcceptRole)
            
            msg.exec_()
            
            # 폴더 열기
            if msg.clickedButton() == open_folder_btn and files:
                output_dir = os.path.dirname(files[0])
                if os.name == 'nt':  # Windows
                    os.startfile(output_dir)
                elif os.name == 'posix':  # macOS, Linux
                    import subprocess
                    subprocess.Popen(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', output_dir])
            
            info("변환 성공")
            self.statusBar().showMessage("변환 완료!", 5000)
        else:
            info("변환 실패 또는 취소됨")
            self.statusBar().showMessage("변환 실패", 5000)
    
    def _load_settings(self):
        """설정 불러오기"""
        self.language_selector.set_language(get_config('language'))
        self.model_selector.set_model_size(get_config('model_size', 'medium'))
        self.format_selector.set_formats(get_config('output_formats', ['txt', 'srt', 'pdf']))
        
        self.summary_options.set_options(
            get_config('enable_summary', False),
            get_config('summary_ratio', 0.3)
        )
        
        self.translation_options.set_options(
            get_config('enable_translation', False),
            get_config('target_language', 'ko')
        )
        
        # 윈도우 지오메트리 복원
        geometry = get_config('window_geometry')
        if geometry:
            self.restoreGeometry(geometry)
        
        info("설정 로드 완료")
    
    def _save_settings(self):
        """설정 저장하기"""
        set_config('language', self.language_selector.get_language())
        set_config('model_size', self.model_selector.get_model_size())
        set_config('output_formats', self.format_selector.get_formats())
        
        summary_opts = self.summary_options.get_options()
        set_config('enable_summary', summary_opts['enabled'])
        set_config('summary_ratio', summary_opts['ratio'])
        
        translation_opts = self.translation_options.get_options()
        set_config('enable_translation', translation_opts['enabled'])
        set_config('target_language', translation_opts['target_language'])
        
        info("설정 저장 완료")
    
    def _show_about(self):
        """정보 다이얼로그"""
        QMessageBox.about(
            self,
            "Whisper 자막 변환 도구 정보",
            """
            <h3>Whisper 자막 변환 도구 v2.0</h3>
            
            <p>OpenAI의 Whisper 모델을 사용한 음성/비디오 자막 변환 도구</p>
            
            <p><b>주요 기능:</b></p>
            <ul>
                <li>다양한 언어 지원 (자동 감지)</li>
                <li>여러 모델 크기 선택 가능</li>
                <li>텍스트 요약 생성</li>
                <li>다국어 번역</li>
                <li>SRT, TXT, PDF 출력</li>
                <li>실시간 진행률 표시</li>
                <li>작업 취소 기능</li>
            </ul>
            
            <p><b>기술 스택:</b></p>
            <ul>
                <li>OpenAI Whisper</li>
                <li>PyQt5</li>
                <li>Google Translate API</li>
                <li>Sumy (LSA 요약)</li>
            </ul>
            
            <p>© 2024 Whisper App. All rights reserved.</p>
            """
        )
    
    def closeEvent(self, event):
        """윈도우 닫기 이벤트"""
        # 윈도우 지오메트리 저장
        set_config('window_geometry', self.saveGeometry())
        
        # 진행 중인 작업이 있으면 경고
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "확인",
                "작업이 진행 중입니다. 정말 종료하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.worker.cancel()
                self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
        
        info("애플리케이션 종료")
