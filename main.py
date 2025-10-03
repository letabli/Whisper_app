"""
Whisper 자막 변환 도구 v2.0
메인 진입점
"""
import sys
from PyQt5.QtWidgets import QApplication
from ui import MainWindow
from utils import info, error


def main():
    """애플리케이션 메인 함수"""
    try:
        info("=" * 50)
        info("Whisper 자막 변환 도구 v2.0 시작")
        info("=" * 50)
        
        # Qt 애플리케이션 생성
        app = QApplication(sys.argv)
        app.setApplicationName("Whisper 자막 변환 도구")
        app.setApplicationVersion("2.0")
        
        # 메인 윈도우 생성 및 표시
        window = MainWindow()
        window.show()
        
        # 이벤트 루프 시작
        sys.exit(app.exec_())
        
    except Exception as e:
        error(f"치명적 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()