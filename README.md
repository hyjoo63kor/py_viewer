# SvgViewer

PySide6 기반 데스크톱 이미지/문서 뷰어 애플리케이션.

PNG, JPG, PDF, SVG 파일을 드래그 앤 드롭 또는 파일 열기 다이얼로그로 열고, 마우스 휠 줌과 Pan 이동으로 콘텐츠를 탐색할 수 있다.

## 주요 기능

- **드래그 앤 드롭** — PNG, JPG(JPEG), PDF, SVG 파일을 윈도우에 드롭하면 즉시 표시
- **파일 열기 다이얼로그** — "열기" 버튼으로 파일 탐색기에서 파일 선택 (지원 형식 필터 적용)
- **PDF 미리보기** — PDF 첫 페이지를 이미지로 변환하여 표시 (PyMuPDF)
- **SVG 렌더링** — Qt 내장 QSvgRenderer로 벡터 그래픽 표시
- **마우스 휠 줌** — 휠 위로 확대(×1.25), 아래로 축소(÷1.25), 범위 10%~1000%
- **줌 버튼** — 상단 패널의 +/- 버튼으로 줌 조작, 현재 배율 표시
- **줌 리셋** — "리셋" 버튼으로 줌 100% + Pan 초기화를 한 번에 복귀
- **Pan 이동** — 줌인 상태에서 마우스 드래그 또는 방향 버튼(◀▲▼▶)으로 이미지 이동
- **오류 처리** — 미지원 형식, 손상 파일, 100MB 초과 파일에 대한 안내 메시지

## 요구 환경

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) 패키지 관리자

## 설치

```bash
uv sync
```

## 실행

```bash
uv run svg-viewer
```

## 개발

### 린트

```bash
uv run ruff check src/ tests/
```

### 타입 체크

```bash
uv run mypy --strict src/my_app/
```

### 테스트

```bash
uv run pytest tests/ -v
```

### 빌드 (단일 실행 파일)

```bash
uv run pyinstaller todo-app.spec
```

`dist/SvgViewer.exe` 파일이 생성된다.

### 캐시/빌드 정리

```bash
uv run python scripts/clean.py
```

`__pycache__`, `.mypy_cache`, `.pytest_cache`, `.ruff_cache`, `build/`, `dist/` 등을 삭제한다.

## 프로젝트 구조

```
├── pyproject.toml              # 프로젝트 설정, 의존성, 도구 설정
├── todo-app.spec               # PyInstaller 빌드 설정 (onefile, console=False)
├── src/my_app/
│   ├── __init__.py
│   ├── main.py                 # 앱 진입점 (QApplication)
│   ├── viewer.py               # 메인 윈도우, 줌/Pan 상태 관리
│   ├── drop_zone.py            # 드래그 앤 드롭 + 마우스 이벤트 위젯
│   ├── title_panel.py          # 열기/줌/리셋/방향 버튼, 배율 표시 패널
│   ├── file_handler.py         # 파일 검증 (형식, 크기, 존재 여부)
│   └── renderers.py            # PNG/JPG/PDF/SVG 렌더링
└── tests/
    ├── conftest.py
    ├── test_file_handler.py
    ├── test_renderers.py
    ├── test_drop_zone.py
    └── test_viewer.py
```

## 기술 스택

| 항목 | 기술 |
|------|------|
| GUI | PySide6 (Qt 6) |
| PDF 렌더링 | PyMuPDF (fitz) |
| SVG 렌더링 | PySide6.QtSvg |
| 패키지 관리 | uv |
| 빌드 | PyInstaller |
| 린터 | ruff |
| 타입체커 | mypy (strict) |
| 테스트 | pytest, hypothesis, pytest-qt |
| Python | 3.12 |

## 라이선스

MIT
