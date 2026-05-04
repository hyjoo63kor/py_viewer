# SvgViewer — 통합 스펙 문서

## 1. 프로젝트 개요

PySide6 기반 데스크톱 이미지/문서 뷰어 애플리케이션. PNG, JPG, PDF, SVG, Markdown 파일을 드래그 앤 드롭 또는 파일 열기 다이얼로그로 열고, 마우스 휠 줌, Pan 이동, 키보드 스크롤, PDF 멀티 페이지 탐색으로 콘텐츠를 탐색할 수 있다.

### 기술 스택

| 항목 | 기술 |
|------|------|
| GUI | PySide6 (Qt 6) |
| PDF 렌더링 | PyMuPDF (fitz) — 줌 크기에 맞는 해상도로 직접 렌더링 |
| SVG 렌더링 | PySide6.QtSvg (QSvgRenderer) — 줌 크기로 벡터 렌더링 |
| Markdown 렌더링 | markdown (Python) + QTextDocument — 줌 비례 폰트 크기 |
| 패키지 관리 | uv |
| 빌드 | PyInstaller (onefile, console=False) |
| 린터 | ruff |
| 타입체커 | mypy (strict) |
| 테스트 | pytest, hypothesis, pytest-qt |
| Python | 3.12 |

---

## 2. 용어 정의

| 용어 | 설명 |
|------|------|
| **Viewer** | 메인 윈도우 (QMainWindow) |
| **Drop_Zone** | 파일 드래그 앤 드롭, 마우스 휠/드래그, 키보드 이벤트를 수신하는 위젯 (QLabel) |
| **Display_Area** | 파일 내용을 렌더링하여 표시하는 영역 |
| **Title_Panel** | 상단 패널 — 열기/줌/리셋/방향/페이지 버튼, 안내 문구, 줌 레이블, 페이지 레이블 |
| **Status_Bar** | 하단 상태 바 — 파일 경로, 오류 메시지 표시 |
| **Supported_Format** | PNG, JPG(JPEG), PDF, SVG, MD |
| **Renderer** | 각 파일 형식에 맞게 내용을 렌더링하는 모듈 |
| **Zoom_Level** | 확대/축소 배율 (1.0 = 100%, 윈도우 크기 기준) |
| **Zoom_Step** | 휠/버튼 한 단위당 배율 변경 계수 (1.25) |
| **Pan_Offset** | 뷰포트 이동 위치 (x, y) 좌표 오프셋, 중앙 기준 (0, 0) |
| **Viewport** | Drop_Zone 내에서 사용자에게 보이는 콘텐츠 영역 |
| **Rendered_Content** | Zoom_Level이 적용되어 렌더링된 전체 이미지 |
| **Pan_Step** | 방향 버튼 한 번 클릭 시 이동 픽셀 수 (50px) |
| **Page_Label** | 현재 페이지/총 페이지 표시 레이블 (예: "1/5") |

---

## 3. 요구사항 통합

### 3.1 파일 열기 및 표시

| ID | 요구사항 | 인수 조건 요약 |
|----|----------|----------------|
| R1 | 애플리케이션 윈도우 | 800×600, 제목 "SvgViewer", 안내 메시지, 앱 아이콘 |
| R2 | 드래그 앤 드롭 | 시각적 피드백, 지원 형식 검증, 다중 파일 시 첫 번째만 수신 |
| R3 | PNG/JPG 렌더링 | QPixmap 로드, 종횡비 유지 스케일링, 리사이즈 대응 |
| R4 | PDF 렌더링 | PyMuPDF로 줌 크기에 맞는 해상도로 직접 렌더링, 선명한 확대 |
| R5 | SVG 렌더링 | QSvgRenderer로 줌 크기에 맞게 벡터 직접 렌더링, 선명한 확대 |
| R6 | Markdown 렌더링 | markdown→HTML→QTextDocument, 줌 비례 폰트 크기, 마진 적용 |
| R7 | 파일 교체 | 새 파일 드롭 시 기존 파일 교체, 메모리 해제 |
| R8 | 파일 열기 다이얼로그 | "열기" 버튼 → QFileDialog, 지원 형식 필터, 취소 시 상태 유지 |
| R9 | 상태 바 | 파일 경로 표시, 오류 메시지 표시 |

### 3.2 줌 기능

| ID | 요구사항 | 인수 조건 요약 |
|----|----------|----------------|
| Z1 | 마우스 휠 줌인 | 휠 위로 → level × 1.25, MAX_ZOOM(10.0) 클램핑 |
| Z2 | 마우스 휠 줌아웃 | 휠 아래로 → level ÷ 1.25, MIN_ZOOM(0.1) 클램핑 |
| Z3 | 줌 배율 범위 | Step=1.25, Min=0.1(10%), Max=10.0(1000%), 초기=1.0 |
| Z4 | 줌 렌더링 | 즉시 재렌더링, 종횡비 유지, 리사이즈 시 줌 레벨 유지 |
| Z5 | 줌 초기화 | 새 파일 드롭/오류 시 1.0으로 리셋 |
| Z6 | 파일 미표시 시 | 줌 동작 무시 |
| Z7 | 타이틀 패널 | 안내 문구, +/- 버튼, 줌 레이블(100%), 즉시 갱신 |
| Z8 | 줌 버튼 동작 | +/- 클릭으로 줌, MIN/MAX 클램핑, 파일 미표시 시 무시 |
| Z9 | 줌 리셋 | "리셋" 버튼 → 100% + Pan(0,0), 이미 100%면 재렌더링 방지 |

### 3.3 Pan(이동) 기능

| ID | 요구사항 | 인수 조건 요약 |
|----|----------|----------------|
| P1 | 마우스 드래그 Pan | 좌클릭 드래그로 이동, ClosedHandCursor, 놓으면 복원 |
| P2 | 방향 버튼 Pan | ◀▲▼▶ 버튼, 50px 단위 이동 |
| P3 | Pan 경계 제한 | 콘텐츠 밖 이동 방지, rendered ≤ viewport이면 (0,0) 고정 |
| P4 | Pan 렌더링 | Crop 기반 — 전체 pixmap에서 viewport 크기만큼 잘라내어 표시 |
| P5 | 줌 변경 시 Pan 초기화 | zoom_in/zoom_out 시 (0,0)으로 리셋 |
| P6 | 파일 변경 시 Pan 초기화 | 새 파일 드롭 시 (0,0)으로 리셋 |
| P7 | 파일 미표시 시 | Pan 동작 무시 |
| P8 | 리사이즈 시 | Pan 오프셋 경계 재적용 |
| P9 | PgUp/PgDn 스크롤 | 뷰포트 80%만큼 수직 Pan 이동 (단일 페이지/이미지/MD) |

### 3.4 PDF 멀티 페이지

| ID | 요구사항 | 인수 조건 요약 |
|----|----------|----------------|
| M1 | 총 페이지 수 감지 | PDF 로드 시 get_pdf_page_count 호출 |
| M2 | 페이지 탐색 UI | ◁ [n/N] ▷ 버튼/레이블, 멀티 페이지일 때만 표시 |
| M3 | 페이지 이동 | 이전/다음 클릭 시 렌더링, 줌/Pan 초기화 |
| M4 | 특정 페이지 렌더링 | render_pdf에 page 파라미터 (1-based) |
| M5 | 단일 페이지 PDF | 페이지 탐색 UI 숨김 |
| M6 | PgUp/PgDn 페이지 넘기기 | 멀티 페이지 PDF에서 PgDn=다음, PgUp=이전 |

### 3.5 오류 처리

| 오류 상황 | 메시지 | 처리 위치 |
|-----------|--------|-----------|
| 미지원 파일 형식 | "지원하지 않는 파일 형식입니다" | file_handler |
| 파일 크기 초과 (>100MB) | "파일 크기가 너무 큽니다 (최대 100MB)" | file_handler |
| 파일 읽기 I/O 오류 | "파일을 읽을 수 없습니다: [파일명]" | file_handler |
| 이미지 디코딩 실패 | "이미지 파일이 손상되었습니다: [파일명]" | renderers |
| PDF 렌더링 실패 | "PDF 파일을 열 수 없습니다" | renderers |
| SVG 렌더링 실패 | "SVG 파일을 열 수 없습니다" | renderers |
| Markdown 읽기 실패 | "Markdown 파일을 읽을 수 없습니다: [파일명]" | renderers |
| PDF 유효하지 않은 페이지 | "유효하지 않은 페이지 번호입니다: N (총 M페이지)" | renderers |

### 3.6 프로젝트 구조 및 빌드

- src/my_app/ 디렉토리 구조 (src layout)
- Python 3.12, PySide6, PyMuPDF, markdown 의존성
- ruff, mypy(strict), pytest 설정
- PyInstaller onefile, console=False → `SvgViewer.exe`
- uv 패키지 관리, `uv run svg-viewer`로 실행, `uv run clean`으로 정리

---

## 4. 아키텍처

### 모듈 구조

```
src/my_app/
├── main.py           # 앱 진입점 (QApplication)
├── viewer.py         # 메인 윈도우, 줌/Pan/페이지 상태 관리, 파일 다이얼로그
├── drop_zone.py      # 드래그 앤 드롭 + 마우스 휠/드래그 + 키보드 이벤트
├── title_panel.py    # 열기/줌/리셋/방향/페이지 버튼, 줌 레이블, 페이지 레이블
├── file_handler.py   # 파일 검증 (형식, 크기, 존재 여부)
├── renderers.py      # PNG/JPG/PDF/SVG/Markdown 렌더링
└── clean.py          # 캐시/빌드 정리 스크립트
```

### 시그널/슬롯 연결

```
TitlePanel → Viewer:
  open_clicked, zoom_in_clicked, zoom_out_clicked, zoom_reset_clicked
  pan_up_clicked, pan_down_clicked, pan_left_clicked, pan_right_clicked
  prev_page_clicked, next_page_clicked

DropZone → Viewer:
  file_dropped, zoom_requested
  pan_started, pan_moved, pan_finished
  page_scroll_requested

Viewer → TitlePanel:
  update_zoom_label(), set_page_info(), hide_page_nav()

Viewer → DropZone:
  display_pixmap(), show_error(), show_placeholder(), setCursor()

Viewer → StatusBar:
  showMessage()
```

### UI 레이아웃

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ [열기] 마우스 휠로 줌인/줌아웃 가능  ─stretch─  [◀▲▼▶] [◁ 1/5 ▷] [-][100%][+][리셋] │
├──────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│                              Drop_Zone / Display_Area                                │
│                                                                                      │
│                (드래그 앤 드롭 또는 "열기" 버튼으로 파일 로드)                          │
│                                                                                      │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ Status Bar: 파일 경로 또는 오류 메시지                                                │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### 렌더링 파이프라인

```
파일 입력 (드롭 또는 다이얼로그)
  → validate_file() → FileInfo
  → [PDF] get_pdf_page_count() → 페이지 UI 설정
  → render_file(file_info, zoomed_size, page) → QPixmap (전체)
      ├── PNG/JPG: QPixmap 로드 → scale_pixmap
      ├── PDF: fitz.Matrix(scale) 고해상도 렌더링
      ├── SVG: QSvgRenderer 줌 크기 벡터 렌더링
      └── MD: markdown→HTML→QTextDocument(줌 폰트) → QPixmap
  → clamp_pan_offset() → 경계 제한
  → crop_pixmap(pixmap, viewport_size) → QPixmap (잘린)
  → display_pixmap(cropped)
  → statusBar().showMessage(파일 경로)
```

---

## 5. 핵심 설계 결정

| 결정 | 선택 | 이유 |
|------|------|------|
| PDF 렌더링 | fitz.Matrix(scale) 고해상도 | 줌 크기에 맞는 해상도로 직접 렌더링하여 확대 시 선명 |
| SVG 렌더링 | QSvgRenderer 줌 크기 직접 렌더링 | 벡터 품질 유지, 확대 시에도 선명 |
| Markdown 렌더링 | QTextDocument + 줌 비례 폰트 | QWebEngine 없이 가볍게, 폰트 크기 조정으로 선명한 확대 |
| 이미지 표시 | QLabel + QPixmap + setSizePolicy(Ignored) | 단순하고 창 크기 변경에 안정적 |
| 줌 관리 | Viewer 중심 | 렌더링 파이프라인을 제어하는 곳에서 상태 관리 |
| 줌 방식 | 곱셈 기반 (×1.25) | 로그 스케일로 자연스러운 줌 경험 |
| Pan 방식 | Crop 기반 | QScrollArea 없이 기존 파이프라인 확장 |
| Pan 좌표계 | 중앙 기준 (0,0) | 초기화 직관적, 경계 계산 대칭적 |
| 파일 다이얼로그 | QFileDialog.getOpenFileName | 기존 _on_file_dropped 파이프라인 재사용 |
| 줌 리셋 | _apply_zoom 재사용 | Pan 초기화 + 줌 레이블 갱신 + 재렌더링 한 번에 처리 |
| PgUp/PgDn | 파일 유형별 분기 | 멀티 페이지 PDF=페이지 넘기기, 그 외=수직 Pan 스크롤 |
| 리사이즈 피드백 루프 방지 | _rendering 플래그 | 렌더링 중 resizeEvent 재귀 호출 차단 |

---

## 6. 데이터 모델

### 상수

| 상수 | 값 | 설명 |
|------|-----|------|
| SUPPORTED_EXTENSIONS | {.png, .jpg, .jpeg, .pdf, .svg, .md} | 지원 확장자 |
| MAX_FILE_SIZE | 104,857,600 (100MB) | 최대 파일 크기 |
| ZOOM_STEP | 1.25 | 줌 배율 변경 계수 |
| MIN_ZOOM | 0.1 | 최소 줌 (10%) |
| MAX_ZOOM | 10.0 | 최대 줌 (1000%) |
| DEFAULT_ZOOM | 1.0 | 초기 줌 (100%) |
| PAN_STEP | 50 | 방향 버튼 이동 픽셀 |

### FileFormat (Enum)

PNG, JPG, PDF, SVG, MD

### FileInfo (frozen dataclass)

path: Path, format: FileFormat, size: int

### Viewer 상태

| 상태 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| _current_file_info | FileInfo \| None | None | 현재 로드된 파일 |
| _zoom_level | float | 1.0 | 현재 줌 배율 |
| _pan_offset_x | int | 0 | 수평 Pan 오프셋 |
| _pan_offset_y | int | 0 | 수직 Pan 오프셋 |
| _current_page | int | 1 | 현재 PDF 페이지 (1-based) |
| _total_pages | int | 1 | 총 PDF 페이지 수 |
| _rendering | bool | False | 렌더링 중 플래그 (재귀 방지) |

### 순수 함수

- `clamp_pan_offset(pan_x, pan_y, rendered_w, rendered_h, viewport_w, viewport_h) → (int, int)`
- `compute_crop_rect(rendered_w, rendered_h, viewport_w, viewport_h, pan_x, pan_y) → (int, int, int, int)`

---

## 7. 정확성 속성 (Correctness Properties)

### 기본 뷰어

| # | 속성 | 검증 대상 |
|---|------|-----------|
| 1 | 종횡비 보존 스케일링 | scale_pixmap 결과의 종횡비 = 원본 종횡비 |
| 2 | 비지원 확장자 거부 | detect_format → FileValidationError |
| 3 | 다중 파일 드롭 시 첫 번째만 선택 | 드롭 처리 → 첫 번째 파일 경로만 반환 |
| 4 | 파일 크기 초과 거부 | validate_file → FileValidationError |

### 줌

| # | 속성 | 검증 대상 |
|---|------|-----------|
| 5 | 줌인 계산 + 클램핑 | min(level × 1.25, 10.0), MIN ≤ result ≤ MAX |
| 6 | 줌아웃 계산 + 클램핑 | max(level ÷ 1.25, 0.1), MIN ≤ result ≤ MAX |
| 7 | 줌 스케일링 종횡비 보존 | 확대 포함 scale_pixmap 종횡비 보존 |
| 8 | 리사이즈 시 줌 레벨 불변 | resizeEvent 후 zoom_level 동일 |
| 9 | 파일 드롭 시 줌 초기화 | 드롭 후 zoom_level = 1.0 |
| 10 | 파일 미표시 시 줌 무시 | zoom_in/out 후 zoom_level = 1.0 유지 |
| 11 | 줌 레이블 포맷 | f"{round(level × 100)}%" |
| 19 | 줌 리셋 상태 초기화 | zoom_reset 후 zoom=1.0, pan=(0,0) |

### Pan

| # | 속성 | 검증 대상 |
|---|------|-----------|
| 12 | 방향 버튼 Pan 오프셋 변경 | 해당 축 ±50, clamp 적용 |
| 13 | Pan 오프셋 경계 제한 | \|offset\| ≤ max(0, (rendered - viewport) // 2) |
| 14 | Crop 영역 유효성 | crop 영역이 rendered pixmap 내에 존재 |
| 15 | 드래그 Pan 계산 | offset = start_offset + (start_pos - current_pos) |
| 16 | 줌 변경 시 Pan 초기화 | zoom 후 pan = (0, 0) |
| 17 | 파일 드롭 시 Pan 초기화 | 드롭 후 pan = (0, 0) |
| 18 | 파일 미표시 시 Pan 무시 | pan 동작 후 offset = (0, 0) 유지 |

### Markdown/PDF 멀티 페이지

| # | 속성 | 검증 대상 |
|---|------|-----------|
| 20 | Markdown 렌더링 유효성 | render_markdown → null이 아닌 QPixmap, 크기 ≤ display_size |
| 21 | PDF 페이지 수 정확성 | get_pdf_page_count → 정확한 N |
| 22 | 페이지 레이블 형식 | set_page_info → "n/N" 형식 |
| 23 | 네비게이션 버튼 활성화 | current==1→Prev 비활성화, current==total→Next 비활성화 |
| 24 | 페이지 이동 ±1 | next/prev → current_page ±1 |
| 25 | 페이지 변경 시 줌/Pan 초기화 | 페이지 변경 후 zoom=1.0, pan=(0,0) |
| 26 | 유효 범위 밖 페이지 → RenderError | render_pdf(invalid_page) → 예외 |

---

## 8. 개발 이력

| 단계 | 기능 | 주요 변경 |
|------|------|-----------|
| 1 | 기본 뷰어 | 프로젝트 구조, 드래그 앤 드롭, PNG/JPG/PDF/SVG 렌더링, 오류 처리 |
| 2 | 마우스 휠 줌 | TitlePanel 신규, DropZone wheelEvent, Viewer 줌 상태 관리, scale_pixmap 확대 지원 |
| 3 | 줌 버그 수정 | setSizePolicy(Ignored)로 창 확장 방지, _rendering 플래그로 재귀 방지 |
| 4 | Pan 네비게이션 | DropZone 마우스 드래그, TitlePanel 방향 버튼, Viewer crop 파이프라인, 순수 함수 추출 |
| 5 | 파일 다이얼로그 + 줌 리셋 | TitlePanel "열기"/"리셋" 버튼, Viewer QFileDialog/zoom_reset |
| 6 | SVG 벡터 품질 | render_svg를 줌 크기로 직접 벡터 렌더링하도록 수정 |
| 7 | 앱 이름 변경 | SvgViewer로 리브랜딩, 스크립트 엔트리포인트 추가 |
| 8 | Markdown 렌더링 | FileFormat.MD, render_markdown (HTML→QTextDocument→QPixmap) |
| 9 | PDF 멀티 페이지 | get_pdf_page_count, render_pdf(page), TitlePanel 페이지 네비게이션 |
| 10 | PDF 고해상도 | fitz.Matrix(scale)로 줌 크기에 맞는 해상도 직접 렌더링 |
| 11 | Markdown 줌 품질 | 줌 비례 폰트 크기 + 비례 마진으로 선명한 확대 |
| 12 | 상태 바 + PgUp/PgDn | QMainWindow statusBar, 키보드 스크롤 (PDF=페이지 넘기기, 그 외=Pan) |
| 13 | 앱 아이콘 | resources/icon.svg, PyInstaller 번들 대응 |
| 14 | clean 스크립트 | `uv run clean`으로 캐시/빌드 정리 |
