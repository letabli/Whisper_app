"""
입력 검증 모듈
파일, 설정값 등의 유효성을 검사합니다.
"""
import os
from pathlib import Path
from typing import List, Tuple


class ValidationError(Exception):
    """검증 실패 예외"""
    pass


class FileValidator:
    """파일 검증 클래스"""
    
    # 지원하는 파일 확장자
    SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac']
    SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']
    
    @classmethod
    def validate_file(cls, file_path: str) -> Tuple[bool, str]:
        """
        파일 유효성 검사
        
        Args:
            file_path: 검사할 파일 경로
            
        Returns:
            (성공 여부, 메시지) 튜플
        """
        if not file_path:
            return False, "파일이 선택되지 않았습니다."
        
        path = Path(file_path)
        
        # 파일 존재 확인
        if not path.exists():
            return False, "파일을 찾을 수 없습니다."
        
        # 파일인지 확인
        if not path.is_file():
            return False, "유효한 파일이 아닙니다."
        
        # 파일 크기 확인 (최대 2GB)
        file_size = path.stat().st_size
        max_size = 2 * 1024 * 1024 * 1024  # 2GB
        if file_size > max_size:
            return False, f"파일 크기가 너무 큽니다 (최대 2GB). 현재: {file_size / (1024**3):.2f}GB"
        
        # 파일 확장자 확인
        ext = path.suffix.lower()
        supported_formats = cls.SUPPORTED_AUDIO_FORMATS + cls.SUPPORTED_VIDEO_FORMATS
        
        if ext not in supported_formats:
            return False, f"지원하지 않는 파일 형식입니다: {ext}"
        
        # 파일 읽기 권한 확인
        if not os.access(file_path, os.R_OK):
            return False, "파일 읽기 권한이 없습니다."
        
        return True, "파일 검증 성공"
    
    @classmethod
    def get_supported_formats_string(cls) -> str:
        """지원하는 파일 형식 문자열 반환"""
        audio = ', '.join(cls.SUPPORTED_AUDIO_FORMATS)
        video = ', '.join(cls.SUPPORTED_VIDEO_FORMATS)
        return f"오디오: {audio}\n비디오: {video}"


class ConfigValidator:
    """설정값 검증 클래스"""
    
    VALID_LANGUAGES = ['ko', 'en', 'ja', 'zh']
    VALID_MODEL_SIZES = ['tiny', 'base', 'small', 'medium', 'large']
    VALID_OUTPUT_FORMATS = ['txt', 'srt', 'pdf']
    
    @classmethod
    def validate_language(cls, language: str) -> bool:
        """언어 코드 검증"""
        if language is None:
            return True  # 자동 감지
        return language in cls.VALID_LANGUAGES
    
    @classmethod
    def validate_model_size(cls, model_size: str) -> bool:
        """모델 크기 검증"""
        return model_size in cls.VALID_MODEL_SIZES
    
    @classmethod
    def validate_output_formats(cls, formats: List[str]) -> bool:
        """출력 형식 검증"""
        if not formats:
            return False
        return all(fmt in cls.VALID_OUTPUT_FORMATS for fmt in formats)
    
    @classmethod
    def validate_summary_ratio(cls, ratio: float) -> bool:
        """요약 비율 검증"""
        return 0.1 <= ratio <= 0.9
    
    @classmethod
    def validate_all(cls, config: dict) -> Tuple[bool, str]:
        """
        전체 설정 검증
        
        Args:
            config: 검증할 설정 딕셔너리
            
        Returns:
            (성공 여부, 메시지) 튜플
        """
        # 언어 검증
        if 'language' in config and not cls.validate_language(config['language']):
            return False, f"유효하지 않은 언어: {config['language']}"
        
        # 모델 크기 검증
        if 'model_size' in config and not cls.validate_model_size(config['model_size']):
            return False, f"유효하지 않은 모델 크기: {config['model_size']}"
        
        # 출력 형식 검증
        if 'output_formats' in config and not cls.validate_output_formats(config['output_formats']):
            return False, f"유효하지 않은 출력 형식: {config['output_formats']}"
        
        # 요약 비율 검증
        if 'summary_ratio' in config and not cls.validate_summary_ratio(config['summary_ratio']):
            return False, f"유효하지 않은 요약 비율: {config['summary_ratio']}"
        
        return True, "설정 검증 성공"
