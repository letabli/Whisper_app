"""
로깅 설정 모듈
애플리케이션 전체의 로깅을 관리합니다.
"""
import logging
import os
from datetime import datetime
from pathlib import Path


class AppLogger:
    """애플리케이션 로거 싱글톤 클래스"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        """로거 초기 설정"""
        # 로그 디렉토리 생성
        log_dir = Path.home() / '.whisper_app' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # 로그 파일명 (날짜별)
        log_file = log_dir / f'whisper_app_{datetime.now():%Y%m%d}.log'
        
        # 로거 생성
        self._logger = logging.getLogger('WhisperApp')
        self._logger.setLevel(logging.DEBUG)
        
        # 기존 핸들러 제거 (중복 방지)
        self._logger.handlers.clear()
        
        # 파일 핸들러
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        # 핸들러 추가
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
    
    def get_logger(self):
        """로거 인스턴스 반환"""
        return self._logger
    
    @classmethod
    def debug(cls, message):
        """디버그 로그"""
        logger = cls().get_logger()
        logger.debug(message)
    
    @classmethod
    def info(cls, message):
        """정보 로그"""
        logger = cls().get_logger()
        logger.info(message)
    
    @classmethod
    def warning(cls, message):
        """경고 로그"""
        logger = cls().get_logger()
        logger.warning(message)
    
    @classmethod
    def error(cls, message):
        """에러 로그"""
        logger = cls().get_logger()
        logger.error(message)
    
    @classmethod
    def critical(cls, message):
        """치명적 에러 로그"""
        logger = cls().get_logger()
        logger.critical(message)


# 편의를 위한 전역 함수들
def debug(message):
    AppLogger.debug(message)

def info(message):
    AppLogger.info(message)

def warning(message):
    AppLogger.warning(message)

def error(message):
    AppLogger.error(message)

def critical(message):
    AppLogger.critical(message)
