"""
번역 모듈
텍스트를 다양한 언어로 번역합니다.
"""
from googletrans import Translator as GoogleTranslator
from typing import List, Dict, Optional, Callable
from utils.logger import info, error, warning
import time


class Translator:
    """번역 클래스"""
    
    def __init__(self):
        self.translator = GoogleTranslator()
        self.supported_languages = {
            'ko': '한국어',
            'en': '영어',
            'ja': '일본어',
            'zh-cn': '중국어 (간체)',
            'zh-tw': '중국어 (번체)',
            'es': '스페인어',
            'fr': '프랑스어',
            'de': '독일어',
            'ru': '러시아어',
            'ar': '아랍어'
        }
    
    def translate_text(
        self, 
        text: str, 
        target_lang: str,
        source_lang: str = 'auto',
        progress_callback: Optional[Callable] = None
    ) -> Optional[str]:
        """
        텍스트 번역
        
        Args:
            text: 번역할 텍스트
            target_lang: 목표 언어
            source_lang: 원본 언어 (auto면 자동 감지)
            progress_callback: 진행 상황 콜백
            
        Returns:
            번역된 텍스트 또는 None (실패시)
        """
        if not text or not text.strip():
            warning("번역할 텍스트가 비어있습니다")
            return None
        
        try:
            if progress_callback:
                progress_callback(f"{target_lang}로 번역 중...")
            
            info(f"번역 시작: {len(text)} 자 -> {target_lang}")
            
            # Google Translate API 호출
            result = self.translator.translate(
                text,
                dest=target_lang,
                src=source_lang
            )
            
            translated_text = result.text
            
            info(f"번역 완료: {len(translated_text)} 자")
            
            if progress_callback:
                progress_callback("번역 완료")
            
            return translated_text
            
        except Exception as e:
            error(f"번역 실패: {e}")
            if progress_callback:
                progress_callback(f"번역 실패: {str(e)}")
            return None
    
    def translate_segments(
        self,
        segments: List[Dict],
        target_lang: str,
        source_lang: str = 'auto',
        progress_callback: Optional[Callable] = None,
        batch_size: int = 10
    ) -> Optional[List[Dict]]:
        """
        세그먼트 목록 번역 (배치 처리)
        
        Args:
            segments: 번역할 세그먼트 리스트
            target_lang: 목표 언어
            source_lang: 원본 언어
            progress_callback: 진행 상황 콜백
            batch_size: 배치 크기
            
        Returns:
            번역된 세그먼트 리스트 또는 None (실패시)
        """
        if not segments:
            warning("번역할 세그먼트가 없습니다")
            return None
        
        try:
            translated_segments = []
            total = len(segments)
            
            info(f"세그먼트 번역 시작: {total}개")
            
            for i, segment in enumerate(segments):
                if progress_callback:
                    progress = int((i / total) * 100)
                    progress_callback(f"세그먼트 번역 중... ({i+1}/{total})")
                
                # 세그먼트 복사
                translated_segment = segment.copy()
                
                # 텍스트 번역
                if segment.get('text'):
                    translated_text = self.translate_text(
                        segment['text'].strip(),
                        target_lang,
                        source_lang
                    )
                    
                    if translated_text:
                        translated_segment['text'] = translated_text
                    else:
                        # 번역 실패시 원본 유지
                        warning(f"세그먼트 {i+1} 번역 실패, 원본 유지")
                
                translated_segments.append(translated_segment)
                
                # API 제한 방지를 위한 짧은 대기
                if (i + 1) % batch_size == 0:
                    time.sleep(0.5)
            
            info(f"세그먼트 번역 완료: {len(translated_segments)}개")
            
            if progress_callback:
                progress_callback("세그먼트 번역 완료")
            
            return translated_segments
            
        except Exception as e:
            error(f"세그먼트 번역 실패: {e}")
            if progress_callback:
                progress_callback(f"세그먼트 번역 실패: {str(e)}")
            return None
    
    def detect_language(self, text: str) -> Optional[str]:
        """
        언어 감지
        
        Args:
            text: 감지할 텍스트
            
        Returns:
            언어 코드 또는 None
        """
        try:
            result = self.translator.detect(text)
            return result.lang
        except Exception as e:
            error(f"언어 감지 실패: {e}")
            return None
    
    def get_supported_languages(self) -> Dict[str, str]:
        """지원하는 언어 목록 반환"""
        return self.supported_languages.copy()