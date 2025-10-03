# Whisper 자막 변환 도구 v2.0

OpenAI의 Whisper 모델을 사용한 음성/비디오 자막 변환 도구입니다.

## 🎯 주요 기능

- ✅ **다양한 언어 지원**: 한국어, 영어, 일본어, 중국어 등 (자동 감지 가능)
- ✅ **5가지 모델 크기**: tiny, base, small, medium, large
- ✅ **텍스트 요약**: LSA 알고리즘을 통한 자동 요약
- ✅ **다국어 번역**: Google Translate API 활용
- ✅ **다양한 출력 형식**: TXT, SRT, PDF
- ✅ **실시간 진행률 표시**: 각 단계별 진행 상황 확인
- ✅ **작업 취소 기능**: 언제든지 작업 중단 가능
- ✅ **설정 저장**: 마지막 설정 자동 저장
- ✅ **GPU 가속**: CUDA 지원 시 자동 사용

## 📁 프로젝트 구조

```
whisper_app/
├── main.py                      # 메인 진입점
├── core/                        # 핵심 기능 모듈
│   ├── __init__.py
│   ├── whisper_processor.py    # Whisper 전사 처리
│   ├── summarizer.py           # 텍스트 요약
│   ├── translator.py           # 다국어 번역
│   └── file_handler.py         # 파일 생성 (SRT, TXT, PDF)
├── ui/                         # 사용자 인터페이스
│   ├── __init__.py
│   ├── main_window.py          # 메인 윈도우
│   ├── progress_dialog.py      # 진행률 다이얼로그
│   └── widgets.py              # 커스텀 위젯들
├── workers/                    # 비동기 작업 처리
│   ├── __init__.py
│   ├── base_worker.py          # 기본 워커 클래스
│   └── transcription_worker.py # 전사 워커
└── utils/                      # 유틸리티
    ├── __init__.py
    ├── logger.py               # 로깅 관리
    ├── config.py               # 설정 관리
    └── validators.py           # 입력 검증
```

## 🚀 설치 방법

### 1. 필수 요구사항

- Python 3.8 이상
- pip 패키지 관리자

### 2. 의존성 설치

```bash
pip install openai-whisper
pip install torch torchvision torchaudio
pip install PyQt5
pip install googletrans==4.0.0rc1
pip install sumy
pip install nltk
pip install reportlab
```

또는 requirements.txt 사용:

```bash
pip install -r requirements.txt
```

### 3. NLTK 데이터 다운로드

첫 실행 시 자동으로 다운로드되지만, 수동으로 설치하려면:

```python
import nltk
nltk.download('punkt')
```

## 💻 사용 방법

### 기본 실행

```bash
python main.py
```

### 단계별 사용법

1. **파일 선택**: "파일 찾기" 버튼을 클릭하여 음성/비디오 파일 선택
2. **옵션 설정**:
   - 원본 언어 선택 (자동 감지 권장)
   - 모델 크기 선택 (medium 권장)
   - 출력 형식 선택 (TXT, SRT, PDF)
   - 요약 생성 옵션 (선택)
   - 번역 옵션 (선택)
3. **변환 시작**: "🚀 변환 시작" 버튼 클릭
4. **진행 상황 확인**: 진행률 다이얼로그에서 실시간 확인
5. **완료**: 생성된 파일 확인

## 📊 모델 크기별 특성

| 모델    | 속도  | 정확도 | 메모리 | 권장 용도           |
|---------|-------|--------|--------|---------------------|
| tiny    | 매우 빠름 | 낮음   | ~1GB   | 테스트/빠른 전사    |
| base    | 빠름  | 보통   | ~1GB   | 일반적인 용도       |
| small   | 보통  | 좋음   | ~2GB   | 균형잡힌 선택       |
| medium  | 느림  | 매우 좋음 | ~5GB   | **권장 (기본값)**   |
| large   | 매우 느림 | 최고   | ~10GB  | 최고 품질 필요 시   |

## 🎨 주요 개선사항 (v2.0)

### v1.0 대비 개선점

1. **모듈화된 구조**
   - 코드를 기능별로 분리하여 유지보수성 향상
   - 각 모듈을 독립적으로 테스트 가능

2. **명확한 진행률 표시**
   - 0-100% 정확한 진행률
   - 각 단계별 상세 로그
   - 실시간 상태 업데이트

3. **작업 취소 기능**
   - 언제든지 안전하게 작업 중단 가능
   - QThread.requestInterruption() 활용

4. **설정 관리**
   - 마지막 설정 자동 저장/복원
   - JSON 기반 설정 파일
   - 윈도우 위치/크기 기억

5. **에러 처리 강화**
   - 각 단계별 에러 핸들링
   - 사용자 친화적인 에러 메시지
   - 로그 파일 자동 생성

6. **성능 최적화**
   - Whisper 모델 캐싱 (재사용)
   - 번역 배치 처리
   - 메모리 효율적인 파일 생성

7. **UI/UX 개선**
   - 직관적인 커스텀 위젯
   - 깔끔한 레이아웃
   - 드래그 앤 드롭 지원 (향후)

## 📝 설정 파일 위치

- **Windows**: `C:\Users\<사용자명>\.whisper_app\config.json`
- **macOS/Linux**: `~/.whisper_app/config.json`

로그 파일도 동일한 디렉토리의 `logs/` 폴더에 저장됩니다.

## 🔧 트러블슈팅

### GPU를 사용할 수 없습니다

CUDA가 설치되어 있는지 확인:
```python
import torch
print(torch.cuda.is_available())
```

### googletrans 에러

구버전 사용:
```bash
pip uninstall googletrans
pip install googletrans==4.0.0rc1
```

### NLTK 데이터 에러

수동으로 다운로드:
```python
import nltk
nltk.download('punkt')
```

### 메모리 부족

- 더 작은 모델 사용 (medium → small → base)
- 다른 프로그램 종료
- 파일을 짧게 분할

## 🤝 기여하기

버그 리포트나 기능 제안은 환영합니다!

## 📄 라이선스

MIT License

## 🙏 감사의 말

- OpenAI Whisper 팀
- PyQt5 개발자들
- 모든 오픈소스 기여자들

---

**Version**: 2.0  
**Last Updated**: 2024  
**Author**: Whisper App Development Team
