"""
기본 워커 모듈
취소 가능한 비동기 작업의 베이스 클래스
"""
from PyQt5.QtCore import QThread, pyqtSignal
from utils.logger import info, warning, error


class BaseWorker(QThread):
    """
    취소 가능한 기본 워커 클래스
    
    Signals:
        progress_updated: 진행 상황 업데이트 (int: 0-100)
        status_updated: 상태 메시지 업데이트 (str)
        finished: 작업 완료 (bool: 성공 여부, object: 결과)
        error_occurred: 에러 발생 (str: 에러 메시지)
    """
    
    progress_updated = pyqtSignal(int)  # 진행률 (0-100)
    status_updated = pyqtSignal(str)    # 상태 메시지
    finished = pyqtSignal(bool, object)  # 성공 여부, 결과
    error_occurred = pyqtSignal(str)    # 에러 메시지
    
    def __init__(self):
        super().__init__()
        self._is_cancelled = False
    
    def run(self):
        """
        실행 메서드 (서브클래스에서 오버라이드)
        """
        raise NotImplementedError("서브클래스에서 run() 메서드를 구현해야 합니다")
    
    def cancel(self):
        """작업 취소 요청"""
        info("작업 취소 요청됨")
        self._is_cancelled = True
        self.requestInterruption()
    
    def is_cancelled(self) -> bool:
        """취소 여부 확인"""
        return self._is_cancelled or self.isInterruptionRequested()
    
    def update_progress(self, value: int):
        """
        진행률 업데이트
        
        Args:
            value: 진행률 (0-100)
        """
        if not self.is_cancelled():
            self.progress_updated.emit(max(0, min(100, value)))
    
    def update_status(self, message: str):
        """
        상태 메시지 업데이트
        
        Args:
            message: 상태 메시지
        """
        if not self.is_cancelled():
            self.status_updated.emit(message)
    
    def emit_error(self, message: str):
        """
        에러 발생 알림
        
        Args:
            message: 에러 메시지
        """
        error(message)
        self.error_occurred.emit(message)
    
    def emit_finished(self, success: bool, result: object = None):
        """
        작업 완료 알림
        
        Args:
            success: 성공 여부
            result: 결과 객체
        """
        if success:
            info("작업 완료")
        else:
            warning("작업 실패")
        
        self.finished.emit(success, result)
