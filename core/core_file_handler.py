"""
파일 핸들러 모듈
SRT, TXT, PDF 등의 파일을 생성합니다.
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Callable
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from utils.logger import info, error, warning


class FileHandler:
    """파일 생성 및 관리 클래스"""
    
    @staticmethod
    def format_time(seconds: float) -> str:
        """
        초를 SRT 시간 형식으로 변환
        
        Args:
            seconds: 초 단위 시간
            
        Returns:
            HH:MM:SS,mmm 형식 문자열
        """
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        secs = seconds % 60
        millisecs = int((secs - int(secs)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{int(secs):02d},{millisecs:03d}"
    
    @staticmethod
    def create_srt(
        segments: List[Dict],
        output_file: str,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        SRT 자막 파일 생성
        
        Args:
            segments: 세그먼트 리스트
            output_file: 출력 파일 경로
            progress_callback: 진행 상황 콜백
            
        Returns:
            성공 여부
        """
        try:
            if progress_callback:
                progress_callback(f"SRT 파일 생성 중: {output_file}")
            
            info(f"SRT 파일 생성 시작: {output_file}")
            
            with open(output_file, "w", encoding="utf-8") as f:
                for i, segment in enumerate(segments):
                    f.write(f"{i+1}\n")
                    
                    start_time = FileHandler.format_time(segment["start"])
                    end_time = FileHandler.format_time(segment["end"])
                    f.write(f"{start_time} --> {end_time}\n")
                    
                    text = segment['text'].strip()
                    f.write(f"{text}\n\n")
            
            info(f"SRT 파일 생성 완료: {output_file}")
            
            if progress_callback:
                progress_callback("SRT 파일 생성 완료")
            
            return True
            
        except Exception as e:
            error(f"SRT 파일 생성 실패: {e}")
            if progress_callback:
                progress_callback(f"SRT 파일 생성 실패: {str(e)}")
            return False
    
    @staticmethod
    def create_txt(
        text: str,
        output_file: str,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        텍스트 파일 생성
        
        Args:
            text: 저장할 텍스트
            output_file: 출력 파일 경로
            progress_callback: 진행 상황 콜백
            
        Returns:
            성공 여부
        """
        try:
            if progress_callback:
                progress_callback(f"TXT 파일 생성 중: {output_file}")
            
            info(f"TXT 파일 생성 시작: {output_file}")
            
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)
            
            info(f"TXT 파일 생성 완료: {output_file}")
            
            if progress_callback:
                progress_callback("TXT 파일 생성 완료")
            
            return True
            
        except Exception as e:
            error(f"TXT 파일 생성 실패: {e}")
            if progress_callback:
                progress_callback(f"TXT 파일 생성 실패: {str(e)}")
            return False
    
    @staticmethod
    def _wrap_text(text: str, max_width: int = 60) -> List[str]:
        """텍스트를 지정된 너비로 래핑"""
        lines = []
        current_line = ""
        words = text.split()
        
        for word in words:
            test_line = f"{current_line} {word}" if current_line else word
            if len(test_line) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    @staticmethod
    def create_pdf(
        segments: List[Dict],
        output_file: str,
        title: str = "Transcript",
        full_text: Optional[str] = None,
        summary_text: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        PDF 문서 생성
        
        Args:
            segments: 세그먼트 리스트
            output_file: 출력 파일 경로
            title: 문서 제목
            full_text: 전체 텍스트 (선택)
            summary_text: 요약 텍스트 (선택)
            progress_callback: 진행 상황 콜백
            
        Returns:
            성공 여부
        """
        try:
            if progress_callback:
                progress_callback(f"PDF 파일 생성 중: {output_file}")
            
            info(f"PDF 파일 생성 시작: {output_file}")
            
            c = canvas.Canvas(output_file, pagesize=letter)
            width, height = letter
            
            # 여백 설정
            left_margin = 72  # 1 inch
            right_margin = width - 72
            top_margin = height - 72
            bottom_margin = 72
            
            y_position = top_margin
            line_height = 15
            
            # 제목
            c.setFont("Helvetica-Bold", 16)
            c.drawString(left_margin, y_position, title)
            y_position -= line_height * 2
            
            # 요약 (있는 경우)
            if summary_text:
                c.setFont("Helvetica-Bold", 14)
                c.drawString(left_margin, y_position, "요약:")
                y_position -= line_height * 1.5
                
                c.setFont("Helvetica", 12)
                summary_lines = FileHandler._wrap_text(summary_text, 80)
                for line in summary_lines:
                    if y_position < bottom_margin:
                        c.showPage()
                        y_position = top_margin
                        c.setFont("Helvetica", 12)
                    
                    c.drawString(left_margin + 10, y_position, line)
                    y_position -= line_height
                
                y_position -= line_height
            
            # 상세 내용
            c.setFont("Helvetica-Bold", 14)
            if y_position < bottom_margin:
                c.showPage()
                y_position = top_margin
                c.setFont("Helvetica-Bold", 14)
            
            c.drawString(left_margin, y_position, "상세 내용:")
            y_position -= line_height * 1.5
            
            # 세그먼트별 내용
            for segment in segments:
                # 페이지 넘기기 체크
                if y_position < bottom_margin + line_height * 3:
                    c.showPage()
                    y_position = top_margin
                
                # 타임스탬프
                start_time = FileHandler.format_time(segment["start"])
                end_time = FileHandler.format_time(segment["end"])
                time_text = f"[{start_time} - {end_time}]"
                
                c.setFont("Helvetica-Bold", 10)
                c.drawString(left_margin, y_position, time_text)
                y_position -= line_height
                
                # 텍스트
                c.setFont("Helvetica", 12)
                text_lines = FileHandler._wrap_text(segment['text'].strip(), 80)
                
                for line in text_lines:
                    if y_position < bottom_margin:
                        c.showPage()
                        y_position = top_margin
                        c.setFont("Helvetica", 12)
                    
                    c.drawString(left_margin + 10, y_position, line)
                    y_position -= line_height
                
                y_position -= line_height * 0.5
            
            c.save()
            
            info(f"PDF 파일 생성 완료: {output_file}")
            
            if progress_callback:
                progress_callback("PDF 파일 생성 완료")
            
            return True
            
        except Exception as e:
            error(f"PDF 파일 생성 실패: {e}")
            if progress_callback:
                progress_callback(f"PDF 파일 생성 실패: {str(e)}")
            return False
    
    @staticmethod
    def get_output_path(input_file: str, suffix: str, extension: str) -> str:
        """
        출력 파일 경로 생성
        
        Args:
            input_file: 입력 파일 경로
            suffix: 파일명 접미사 (예: "_summary", "_ko")
            extension: 파일 확장자 (예: "txt", "srt")
            
        Returns:
            출력 파일 경로
        """
        input_path = Path(input_file)
        output_dir = input_path.parent
        base_name = input_path.stem
        
        output_filename = f"{base_name}{suffix}.{extension}"
        return str(output_dir / output_filename)
