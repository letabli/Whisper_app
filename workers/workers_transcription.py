"""
전사 워커 모듈
음성/비디오 파일 전사 작업을 비동기로 처리합니다.
"""
from typing import Optional, List
from pathlib import Path
from workers.base_worker import BaseWorker
from core import WhisperProcessor, TextSummarizer, Translator, FileHandler
from utils.logger import info, error


class TranscriptionWorker(BaseWorker):
    """
    전사 작업 워커
    
    전사 -> 요약 -> 번역 -> 파일 생성의 전체 파이프라인을 처리합니다.
    """
    
    def __init__(
        self,
        file_path: str,
        model_size: str,
        language: Optional[str] = None,
        output_formats: List[str] = None,
        enable_summary: bool = False,
        summary_ratio: float = 0.3,
        enable_translation: bool = False,
        target_language: str = 'ko'
    ):
        super().__init__()
        
        self.file_path = file_path
        self.model_size = model_size
        self.language = language
        self.output_formats = output_formats or ['txt', 'srt']
        self.enable_summary = enable_summary
        self.summary_ratio = summary_ratio
        self.enable_translation = enable_translation
        self.target_language = target_language
        
        # 결과 저장
        self.result = {
            'transcript': None,
            'summary': None,
            'translation': None,
            'files': []
        }
    
    def run(self):
        """전사 작업 실행"""
        try:
            info(f"전사 작업 시작: {self.file_path}")
            
            # === 1단계: 모델 로드 (10%) ===
            self.update_progress(0)
            self.update_status("Whisper 모델 로드 중...")
            
            processor = WhisperProcessor.get_instance()
            
            if not processor.load_model(
                self.model_size,
                progress_callback=self.update_status
            ):
                self.emit_error("모델 로드 실패")
                self.emit_finished(False)
                return
            
            if self.is_cancelled():
                self.emit_finished(False, "작업이 취소되었습니다")
                return
            
            self.update_progress(10)
            
            # === 2단계: 파일 전사 (10% -> 60%) ===
            self.update_status("음성 파일 전사 중...")
            
            transcription_result = processor.transcribe(
                self.file_path,
                self.language,
                progress_callback=self.update_status
            )
            
            if not transcription_result:
                self.emit_error("전사 실패")
                self.emit_finished(False)
                return
            
            if self.is_cancelled():
                self.emit_finished(False, "작업이 취소되었습니다")
                return
            
            self.result['transcript'] = transcription_result
            transcript_text = transcription_result['text']
            segments = transcription_result['segments']
            
            self.update_progress(60)
            
            # === 3단계: 요약 생성 (60% -> 70%) ===
            summary_text = None
            if self.enable_summary:
                self.update_status("텍스트 요약 생성 중...")
                
                summarizer = TextSummarizer()
                summary_text = summarizer.summarize(
                    transcript_text,
                    self.summary_ratio,
                    progress_callback=self.update_status
                )
                
                if summary_text:
                    self.result['summary'] = summary_text
                
                if self.is_cancelled():
                    self.emit_finished(False, "작업이 취소되었습니다")
                    return
            
            self.update_progress(70)
            
            # === 4단계: 번역 (70% -> 85%) ===
            translated_text = None
            translated_summary = None
            translated_segments = None
            
            if self.enable_translation:
                self.update_status(f"{self.target_language}로 번역 중...")
                
                translator = Translator()
                
                # 전체 텍스트 번역
                translated_text = translator.translate_text(
                    transcript_text,
                    self.target_language,
                    progress_callback=self.update_status
                )
                
                # 요약 번역
                if summary_text:
                    translated_summary = translator.translate_text(
                        summary_text,
                        self.target_language,
                        progress_callback=self.update_status
                    )
                
                # 세그먼트 번역
                translated_segments = translator.translate_segments(
                    segments,
                    self.target_language,
                    progress_callback=self.update_status
                )
                
                self.result['translation'] = {
                    'text': translated_text,
                    'summary': translated_summary,
                    'segments': translated_segments
                }
                
                if self.is_cancelled():
                    self.emit_finished(False, "작업이 취소되었습니다")
                    return
            
            self.update_progress(85)
            
            # === 5단계: 파일 생성 (85% -> 100%) ===
            self.update_status("파일 생성 중...")
            
            created_files = self._create_output_files(
                transcript_text,
                segments,
                summary_text,
                translated_text,
                translated_summary,
                translated_segments
            )
            
            if self.is_cancelled():
                self.emit_finished(False, "작업이 취소되었습니다")
                return
            
            self.result['files'] = created_files
            
            self.update_progress(100)
            self.update_status("작업 완료!")
            
            # 완료
            self.emit_finished(True, self.result)
            
        except Exception as e:
            error(f"전사 작업 중 예외 발생: {e}")
            self.emit_error(f"작업 실패: {str(e)}")
            self.emit_finished(False)
    
    def _create_output_files(
        self,
        transcript_text: str,
        segments: list,
        summary_text: Optional[str],
        translated_text: Optional[str],
        translated_summary: Optional[str],
        translated_segments: Optional[list]
    ) -> List[str]:
        """출력 파일 생성"""
        created_files = []
        file_handler = FileHandler()
        
        base_name = Path(self.file_path).stem
        output_dir = Path(self.file_path).parent
        
        # TXT 파일들
        if 'txt' in self.output_formats:
            # 원본 전사
            txt_file = FileHandler.get_output_path(self.file_path, "", "txt")
            if file_handler.create_txt(transcript_text, txt_file, self.update_status):
                created_files.append(txt_file)
            
            # 요약
            if summary_text:
                summary_file = FileHandler.get_output_path(self.file_path, "_summary", "txt")
                if file_handler.create_txt(summary_text, summary_file, self.update_status):
                    created_files.append(summary_file)
            
            # 번역
            if translated_text:
                trans_file = FileHandler.get_output_path(
                    self.file_path, f"_{self.target_language}", "txt"
                )
                if file_handler.create_txt(translated_text, trans_file, self.update_status):
                    created_files.append(trans_file)
            
            # 번역된 요약
            if translated_summary:
                trans_summary_file = FileHandler.get_output_path(
                    self.file_path, f"_summary_{self.target_language}", "txt"
                )
                if file_handler.create_txt(translated_summary, trans_summary_file, self.update_status):
                    created_files.append(trans_summary_file)
        
        # SRT 파일들
        if 'srt' in self.output_formats:
            # 원본 자막
            srt_file = FileHandler.get_output_path(self.file_path, "", "srt")
            if file_handler.create_srt(segments, srt_file, self.update_status):
                created_files.append(srt_file)
            
            # 번역된 자막
            if translated_segments:
                trans_srt_file = FileHandler.get_output_path(
                    self.file_path, f"_{self.target_language}", "srt"
                )
                if file_handler.create_srt(translated_segments, trans_srt_file, self.update_status):
                    created_files.append(trans_srt_file)
        
        # PDF 파일들
        if 'pdf' in self.output_formats:
            # 원본 PDF
            pdf_file = FileHandler.get_output_path(self.file_path, "_transcript", "pdf")
            if file_handler.create_pdf(
                segments,
                pdf_file,
                title=f"{base_name} - Transcript",
                full_text=transcript_text,
                summary_text=summary_text,
                progress_callback=self.update_status
            ):
                created_files.append(pdf_file)
            
            # 번역된 PDF
            if translated_segments:
                trans_pdf_file = FileHandler.get_output_path(
                    self.file_path, f"_transcript_{self.target_language}", "pdf"
                )
                if file_handler.create_pdf(
                    translated_segments,
                    trans_pdf_file,
                    title=f"{base_name} - Transcript ({self.target_language})",
                    full_text=translated_text,
                    summary_text=translated_summary,
                    progress_callback=self.update_status
                ):
                    created_files.append(trans_pdf_file)
        
        return created_files