"""
텍스트 요약 모듈
긴 텍스트를 짧게 요약합니다.
"""
import nltk
from nltk.tokenize import sent_tokenize
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from typing import Optional, Callable
from utils.logger import info, error, warning


class TextSummarizer:
    """텍스트 요약 클래스"""
    
    def __init__(self):
        self._ensure_nltk_data()
    
    def _ensure_nltk_data(self):
        """NLTK 데이터 확인 및 다운로드"""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            info("NLTK punkt 데이터 다운로드 중...")
            try:
                nltk.download('punkt', quiet=True)
                info("NLTK punkt 데이터 다운로드 완료")
            except Exception as e:
                error(f"NLTK 데이터 다운로드 실패: {e}")
    
    def summarize(
        self, 
        text: str, 
        ratio: float = 0.3,
        min_sentences: int = 1,
        max_sentences: Optional[int] = None,
        progress_callback: Optional[Callable] = None
    ) -> Optional[str]:
        """
        텍스트 요약
        
        Args:
            text: 요약할 텍스트
            ratio: 요약 비율 (0.1 ~ 0.9)
            min_sentences: 최소 문장 수
            max_sentences: 최대 문장 수 (None이면 제한 없음)
            progress_callback: 진행 상황 콜백 함수
            
        Returns:
            요약된 텍스트 또는 None (실패시)
        """
        if not text or not text.strip():
            warning("요약할 텍스트가 비어있습니다")
            return None
        
        try:
            if progress_callback:
                progress_callback("텍스트 분석 중...")
            
            # 문장 분리
            sentences = sent_tokenize(text)
            sentence_count = len(sentences)
            
            info(f"전체 문장 수: {sentence_count}")
            
            # 문장이 너무 적으면 원본 반환
            if sentence_count <= min_sentences:
                warning(f"문장 수가 너무 적어 요약하지 않습니다: {sentence_count}")
                return text
            
            # 요약할 문장 수 계산
            summary_sentence_count = max(min_sentences, int(sentence_count * ratio))
            
            if max_sentences is not None:
                summary_sentence_count = min(summary_sentence_count, max_sentences)
            
            info(f"요약 문장 수: {summary_sentence_count}")
            
            if progress_callback:
                progress_callback(f"요약 생성 중 ({summary_sentence_count}/{sentence_count} 문장)...")
            
            # LSA 요약 수행
            parser = PlaintextParser.from_string(text, Tokenizer("english"))
            summarizer = LsaSummarizer()
            
            summary = summarizer(parser.document, summary_sentence_count)
            summary_text = ' '.join([str(sentence) for sentence in summary])
            
            info(f"요약 완료: {len(summary_text)} 자")
            
            if progress_callback:
                progress_callback("요약 완료")
            
            return summary_text
            
        except Exception as e:
            error(f"요약 생성 실패: {e}")
            if progress_callback:
                progress_callback(f"요약 실패: {str(e)}")
            return None
    
    def get_summary_stats(self, original: str, summary: str) -> dict:
        """
        요약 통계 반환
        
        Args:
            original: 원본 텍스트
            summary: 요약 텍스트
            
        Returns:
            통계 딕셔너리
        """
        original_sentences = sent_tokenize(original)
        summary_sentences = sent_tokenize(summary)
        
        return {
            'original_length': len(original),
            'summary_length': len(summary),
            'original_sentences': len(original_sentences),
            'summary_sentences': len(summary_sentences),
            'compression_ratio': len(summary) / len(original) if len(original) > 0 else 0
        }
