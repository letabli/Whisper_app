"""
커스텀 위젯 모듈
재사용 가능한 커스텀 UI 컴포넌트들
"""
from PyQt5.QtWidgets import (QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, 
                             QLabel, QComboBox, QRadioButton, QButtonGroup,
                             QCheckBox, QSpinBox)
from PyQt5.QtCore import pyqtSignal


class LanguageSelector(QGroupBox):
    """언어 선택 위젯"""
    
    language_changed = pyqtSignal(object)  # None 또는 언어 코드
    
    def __init__(self, title="원본 언어 선택", parent=None):
        super().__init__(title, parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.combo = QComboBox()
        self.combo.addItem("자동 감지", None)
        self.combo.addItem("한국어", "ko")
        self.combo.addItem("영어", "en")
        self.combo.addItem("일본어", "ja")
        self.combo.addItem("중국어", "zh")
        
        self.combo.currentIndexChanged.connect(
            lambda: self.language_changed.emit(self.combo.currentData())
        )
        
        layout.addWidget(self.combo)
    
    def get_language(self):
        """선택된 언어 코드 반환"""
        return self.combo.currentData()
    
    def set_language(self, language):
        """언어 설정"""
        for i in range(self.combo.count()):
            if self.combo.itemData(i) == language:
                self.combo.setCurrentIndex(i)
                break


class ModelSelector(QGroupBox):
    """모델 크기 선택 위젯"""
    
    model_changed = pyqtSignal(str)
    
    def __init__(self, title="모델 크기", parent=None):
        super().__init__(title, parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.button_group = QButtonGroup(self)
        
        models = [
            ("tiny", "Tiny (가장 빠름, 낮은 정확도)"),
            ("base", "Base"),
            ("small", "Small"),
            ("medium", "Medium (권장)"),
            ("large", "Large (가장 느림, 높은 정확도)")
        ]
        
        for value, label in models:
            radio = QRadioButton(label)
            self.button_group.addButton(radio)
            radio.toggled.connect(lambda checked, v=value: 
                                self.model_changed.emit(v) if checked else None)
            layout.addWidget(radio)
        
        # 기본값: medium
        self.button_group.buttons()[3].setChecked(True)
    
    def get_model_size(self):
        """선택된 모델 크기 반환"""
        models = ["tiny", "base", "small", "medium", "large"]
        for i, button in enumerate(self.button_group.buttons()):
            if button.isChecked():
                return models[i]
        return "medium"
    
    def set_model_size(self, model_size):
        """모델 크기 설정"""
        models = ["tiny", "base", "small", "medium", "large"]
        if model_size in models:
            index = models.index(model_size)
            self.button_group.buttons()[index].setChecked(True)


class OutputFormatSelector(QGroupBox):
    """출력 형식 선택 위젯"""
    
    formats_changed = pyqtSignal(list)
    
    def __init__(self, title="출력 형식", parent=None):
        super().__init__(title, parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.txt_check = QCheckBox("텍스트 파일 (.txt)")
        self.srt_check = QCheckBox("자막 파일 (.srt)")
        self.pdf_check = QCheckBox("PDF 문서 (.pdf)")
        
        # 기본값
        self.txt_check.setChecked(True)
        self.srt_check.setChecked(True)
        self.pdf_check.setChecked(True)
        
        # 시그널 연결
        self.txt_check.toggled.connect(self._emit_formats)
        self.srt_check.toggled.connect(self._emit_formats)
        self.pdf_check.toggled.connect(self._emit_formats)
        
        layout.addWidget(self.txt_check)
        layout.addWidget(self.srt_check)
        layout.addWidget(self.pdf_check)
    
    def _emit_formats(self):
        """선택된 형식 리스트 시그널 발생"""
        self.formats_changed.emit(self.get_formats())
    
    def get_formats(self):
        """선택된 출력 형식 리스트 반환"""
        formats = []
        if self.txt_check.isChecked():
            formats.append('txt')
        if self.srt_check.isChecked():
            formats.append('srt')
        if self.pdf_check.isChecked():
            formats.append('pdf')
        return formats
    
    def set_formats(self, formats):
        """출력 형식 설정"""
        self.txt_check.setChecked('txt' in formats)
        self.srt_check.setChecked('srt' in formats)
        self.pdf_check.setChecked('pdf' in formats)


class SummaryOptions(QGroupBox):
    """요약 옵션 위젯"""
    
    options_changed = pyqtSignal(bool, float)  # enabled, ratio
    
    def __init__(self, title="요약 옵션", parent=None):
        super().__init__(title, parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.enable_check = QCheckBox("텍스트 요약 생성")
        self.enable_check.toggled.connect(self._emit_options)
        
        ratio_layout = QHBoxLayout()
        ratio_layout.addWidget(QLabel("요약 비율:"))
        
        self.ratio_spin = QSpinBox()
        self.ratio_spin.setRange(10, 90)
        self.ratio_spin.setValue(30)
        self.ratio_spin.setSuffix("%")
        self.ratio_spin.valueChanged.connect(self._emit_options)
        
        ratio_layout.addWidget(self.ratio_spin)
        ratio_layout.addStretch()
        
        self.enable_check.toggled.connect(self.ratio_spin.setEnabled)
        self.ratio_spin.setEnabled(False)
        
        layout.addWidget(self.enable_check)
        layout.addLayout(ratio_layout)
    
    def _emit_options(self):
        """옵션 변경 시그널 발생"""
        self.options_changed.emit(
            self.enable_check.isChecked(),
            self.ratio_spin.value() / 100.0
        )
    
    def get_options(self):
        """요약 옵션 반환"""
        return {
            'enabled': self.enable_check.isChecked(),
            'ratio': self.ratio_spin.value() / 100.0
        }
    
    def set_options(self, enabled, ratio):
        """요약 옵션 설정"""
        self.enable_check.setChecked(enabled)
        self.ratio_spin.setValue(int(ratio * 100))


class TranslationOptions(QGroupBox):
    """번역 옵션 위젯"""
    
    options_changed = pyqtSignal(bool, str)  # enabled, target_language
    
    def __init__(self, title="번역 옵션", parent=None):
        super().__init__(title, parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.enable_check = QCheckBox("번역 생성")
        self.enable_check.toggled.connect(self._emit_options)
        
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("번역 언어:"))
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("한국어", "ko")
        self.lang_combo.addItem("영어", "en")
        self.lang_combo.addItem("일본어", "ja")
        self.lang_combo.addItem("중국어", "zh")
        self.lang_combo.currentIndexChanged.connect(self._emit_options)
        
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        
        self.enable_check.toggled.connect(self.lang_combo.setEnabled)
        self.lang_combo.setEnabled(False)
        
        layout.addWidget(self.enable_check)
        layout.addLayout(lang_layout)
    
    def _emit_options(self):
        """옵션 변경 시그널 발생"""
        self.options_changed.emit(
            self.enable_check.isChecked(),
            self.lang_combo.currentData()
        )
    
    def get_options(self):
        """번역 옵션 반환"""
        return {
            'enabled': self.enable_check.isChecked(),
            'target_language': self.lang_combo.currentData()
        }
    
    def set_options(self, enabled, target_language):
        """번역 옵션 설정"""
        self.enable_check.setChecked(enabled)
        for i in range(self.lang_combo.count()):
            if self.lang_combo.itemData(i) == target_language:
                self.lang_combo.setCurrentIndex(i)
                break
