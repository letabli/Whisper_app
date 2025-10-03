"""
설정 관리 모듈
사용자 설정을 JSON 파일로 저장하고 불러옵니다.
"""
import json
from pathlib import Path
from typing import Any, Dict
from utils.logger import AppLogger


class Config:
    """설정 관리 싱글톤 클래스"""
    
    _instance = None
    _config_file = Path.home() / '.whisper_app' / 'config.json'
    _config_data = {}
    
    # 기본 설정값
    _defaults = {
        'language': None,  # 자동 감지
        'model_size': 'medium',
        'output_formats': ['txt', 'srt', 'pdf'],
        'enable_summary': False,
        'summary_ratio': 0.3,
        'enable_translation': False,
        'target_language': 'ko',
        'last_directory': str(Path.home()),
        'window_geometry': None,
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """설정 파일 로드"""
        try:
            if self._config_file.exists():
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    self._config_data = json.load(f)
                AppLogger.info(f"설정 파일 로드 완료: {self._config_file}")
            else:
                # 기본 설정 사용
                self._config_data = self._defaults.copy()
                self._save_config()
                AppLogger.info("기본 설정으로 초기화됨")
        except Exception as e:
            AppLogger.error(f"설정 파일 로드 실패: {e}")
            self._config_data = self._defaults.copy()
    
    def _save_config(self):
        """설정 파일 저장"""
        try:
            # 디렉토리 생성
            self._config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # JSON 저장
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=2, ensure_ascii=False)
            
            AppLogger.debug("설정 파일 저장 완료")
        except Exception as e:
            AppLogger.error(f"설정 파일 저장 실패: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정값 가져오기"""
        return self._config_data.get(key, default)
    
    def set(self, key: str, value: Any):
        """설정값 저장하기"""
        self._config_data[key] = value
        self._save_config()
    
    def get_all(self) -> Dict[str, Any]:
        """모든 설정값 가져오기"""
        return self._config_data.copy()
    
    def reset_to_defaults(self):
        """기본 설정으로 초기화"""
        self._config_data = self._defaults.copy()
        self._save_config()
        AppLogger.info("설정이 기본값으로 초기화되었습니다")
    
    @classmethod
    def instance(cls):
        """Config 인스턴스 반환"""
        return cls()


# 편의를 위한 전역 함수들
def get_config(key: str, default: Any = None) -> Any:
    """설정값 가져오기"""
    return Config.instance().get(key, default)


def set_config(key: str, value: Any):
    """설정값 저장하기"""
    Config.instance().set(key, value)


def reset_config():
    """설정 초기화"""
    Config.instance().reset_to_defaults()
