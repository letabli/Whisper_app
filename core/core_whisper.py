"""
Whisper 전사 처리 모듈
음성/비디오 파일을 텍스트로 변환합니다.
"""
import whisper
import torch
from typing import Dict, Optional, Callable
from utils.logger import info, error, debug


class WhisperProcessor:
    """Whisper 전사 프로세서 (싱글톤)"""
    
    _instance = None
    _models = {}  # 모델 캐시
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.current_model = None
        self.current_model_size = None
    
    def get_device_info(self) -> Dict[str, any]:
        """GPU/CPU 정보 반환"""
        cuda_available = torch.cuda.is_available()
        device_info = {
            'cuda_available': cuda_available,
            'device': 'cuda' if cuda_available else 'cpu'
        }
        
        if cuda_available:
            device_info['gpu_name'] = torch.cuda.get_device_name(0)
            device_info['gpu_memory'] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        
        return device_info
    
    def load_model(self, model_size: str, progress_callback: Optional[Callable] = None) -> bool:
        """
        Whisper 모델 로드 (캐싱 지원)
        
        Args:
            model_size: 모델 크기 (tiny, base, small, medium, large)
            progress_callback: 진행 상황 콜백 함수
            
        Returns:
            성공 여부
        """
        try:
            # 이미 로드된 모델이면 재사용
            if model_size == self.current_model_size and self.current_model is not None:
                info(f"캐시된 {model_size} 모델 사용")
                if progress_callback:
                    progress_callback(f"캐시된 {model_size} 모델 사용")
                return True
            
            # 캐시에서 찾기
            if model_size in self._models:
                info(f"캐시에서 {model_size} 모델 로드")
                self.current_model = self._models[model_size]
                self.current_model_size = model_size
                if progress_callback:
                    progress_callback(f"캐시에서 {model_size} 모델 로드 완료")
                return True
            
            # 새로 로드
            if progress_callback:
                progress_callback(f"{model_size} 모델 다운로드 및 로드 중...")
            
            info(f"{model_size} 모델 로드 시작")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = whisper.load_model(model_size, device=device)
            
            # 캐시에 저장
            self._models[model_size] = model
            self.current_model = model
            self.current_model_size = model_size
            
            info(f"{model_size} 모델 로드 완료 (device: {device})")
            if progress_callback:
                progress_callback(f"{model_size} 모델 로드 완료")
            
            return True
            
        except Exception as e:
            error(f"모델 로드 실패: {e}")
            if progress_callback:
                progress_callback(f"모델 로드 실패: {str(e)}")
            return False
    
    def transcribe(
        self, 
        file_path: str, 
        language: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> Optional[Dict]:
        """
        파일 전사
        
        Args:
            file_path: 전사할 파일 경로
            language: 언어 코드 (None이면 자동 감지)
            progress_callback: 진행 상황 콜백 함수
            
        Returns:
            전사 결과 딕셔너리 또는 None (실패시)
        """
        if self.current_model is None:
            error("모델이 로드되지 않았습니다")
            return None
        
        try:
            if progress_callback:
                progress_callback(f"파일 전사 중: {file_path}")
            
            info(f"전사 시작: {file_path}")
            
            # Whisper 전사 실행
            result = self.current_model.transcribe(
                file_path,
                language=language,
                verbose=False
            )
            
            info(f"전사 완료: {len(result['segments'])} 세그먼트")
            if progress_callback:
                progress_callback("전사 완료")
            
            return result
            
        except Exception as e:
            error(f"전사 실패: {e}")
            if progress_callback:
                progress_callback(f"전사 실패: {str(e)}")
            return None
    
    def clear_cache(self):
        """모델 캐시 클리어"""
        self._models.clear()
        self.current_model = None
        self.current_model_size = None
        info("모델 캐시 클리어됨")
    
    @classmethod
    def get_instance(cls):
        """싱글톤 인스턴스 반환"""
        return cls()
