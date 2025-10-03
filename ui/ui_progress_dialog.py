"""
진행률 다이얼로그 모듈
작업 진행 상황을 표시하고 취소를 허용합니다.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QPushButton, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ProgressDialog(QDialog):
    """
    진행률 표시 다이얼로그
    
    Features:
        - 진행률 바 (0-100%)
        - 상태 메시지
        - 상세 로그
        - 취소 버튼
    """
    
    def __init__(self, parent=None, title="작업 진행 중"):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        self._setup_ui()
        self._cancelled = False
    
    def _setup_ui(self):
        """UI 구성"""
        layout = QVBoxLayout(self)
        
        # 상태 레이블
        self.status_label = QLabel("준비 중...")
        self.status_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.status_label)
        
        # 진행률 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)
        
        # 로그 영역
        log_label = QLabel("상세 로그:")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)
        
        # 버튼 영역
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("취소")
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)
        
        self.close_button = QPushButton("닫기")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setEnabled(False)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def update_progress(self, value: int):
        """
        진행률 업데이트
        
        Args:
            value: 진행률 (0-100)
        """
        self.progress_bar.setValue(value)
        
        # 완료시 버튼 상태 변경
        if value >= 100:
            self.cancel_button.setEnabled(False)
            self.close_button.setEnabled(True)
    
    def update_status(self, message: str):
        """
        상태 메시지 업데이트
        
        Args:
            message: 상태 메시지
        """
        self.status_label.setText(message)
        self.log_text.append(message)
        
        # 스크롤을 항상 아래로
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def show_error(self, message: str):
        """
        에러 메시지 표시
        
        Args:
            message: 에러 메시지
        """
        self.status_label.setText(f"❌ 에러: {message}")
        self.log_text.append(f"\n❌ 에러: {message}\n")
        
        self.progress_bar.setStyleSheet("""
            QProgressBar::chunk {
                background-color: #ff4444;
            }
        """)
        
        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)
    
    def show_success(self, message: str = "작업 완료!"):
        """
        성공 메시지 표시
        
        Args:
            message: 성공 메시지
        """
        self.status_label.setText(f"✅ {message}")
        self.log_text.append(f"\n✅ {message}\n")
        
        self.progress_bar.setStyleSheet("""
            QProgressBar::chunk {
                background-color: #44ff44;
            }
        """)
        
        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)
    
    def _on_cancel(self):
        """취소 버튼 클릭"""
        self._cancelled = True
        self.cancel_button.setEnabled(False)
        self.status_label.setText("⏸ 취소 요청됨...")
        self.log_text.append("\n⏸ 사용자가 작업 취소를 요청했습니다.\n")
    
    def is_cancelled(self) -> bool:
        """취소 여부 반환"""
        return self._cancelled
    
    def reset(self):
        """다이얼로그 초기화"""
        self._cancelled = False
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("")
        self.status_label.setText("준비 중...")
        self.log_text.clear()
        self.cancel_button.setEnabled(True)
        self.close_button.setEnabled(False)
