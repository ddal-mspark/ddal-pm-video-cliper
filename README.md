# Video Clipper App v4

간단한 웹 기반 비디오 클리핑 및 변환 도구입니다.

## 주요 기능

- 비디오 업로드 및 미리보기
- 타임라인 기반 구간 선택 (시작 시간, 재생 시간)
- 비디오 클리핑 (해상도, FPS, 음소거 옵션)
- GIF 변환 (품질 프리셋 지원)
- 얼굴 익명화 (deface 통합)

## 필수 요구사항

- Python 3.7+
- FFmpeg (시스템에 설치 필요)
- (선택) deface - 얼굴 익명화 기능 사용 시

### FFmpeg 설치

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
[FFmpeg 공식 사이트](https://ffmpeg.org/download.html)에서 다운로드

## 설치 및 실행

1. 저장소 클론
```bash
git clone https://github.com/ddal-mspark/ddal-pm-video-cliper.git
cd ddal-pm-video-cliper
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 서버 실행
```bash
python app.py
```

4. 브라우저에서 접속
```
http://localhost:5252
```

## 사용 방법

1. **비디오 업로드**: "Upload Video" 버튼 클릭하여 비디오 선택
2. **작업 선택**:
   - **Video Clip**: 비디오 구간 자르기 및 변환
   - **GIF**: 비디오를 GIF로 변환
   - **Face Anonymization**: 얼굴 익명화 (deface 필요)
3. **옵션 설정**:
   - Start Time: 시작 시간 (초 또는 MM:SS, HH:MM:SS 형식)
   - Duration: 재생 시간 (초 또는 MM:SS, HH:MM:SS 형식)
   - Resolution: 출력 해상도 너비 (예: 1920)
   - FPS: 프레임률
   - Mute: 오디오 제거
4. **처리**: "Process" 버튼 클릭
5. **다운로드**: 처리 완료 후 "Download" 버튼으로 결과 파일 다운로드

## GIF 품질 프리셋

- **Tiny**: 360px, 8fps - 매우 작은 파일 크기
- **Small**: 480px, 10fps - 작은 파일 크기
- **Medium**: 640px, 12fps - 균형잡힌 품질
- **High**: 720px, 15fps - 높은 품질
- **Custom**: 사용자 정의 설정

## 디렉토리 구조

```
video-clipper-app-v4/
├── app.py              # Flask 백엔드 서버
├── requirements.txt    # Python 의존성
├── templates/
│   └── index.html      # HTML 템플릿
├── static/
│   ├── app.js          # 프론트엔드 JavaScript
│   └── styles.css      # 스타일시트
├── uploads/            # 업로드된 비디오 (git에서 제외)
└── processed/          # 처리된 비디오 (git에서 제외)
```

## 기술 스택

- **Backend**: Flask (Python)
- **Frontend**: Vanilla JavaScript
- **Video Processing**: FFmpeg
- **최대 업로드 크기**: 2GB

## 라이선스

MIT
