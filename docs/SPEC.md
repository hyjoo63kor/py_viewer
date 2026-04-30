# SvgViewer — 통합 스펙 문서

## 1. 프로젝트 개요

PySide6 기반 데스크톱 이미지/문서 뷰어 애플리케이션. PNG, JPG, PDF, SVG 파일을 드래그 앤 드롭 또는 파일 열기 다이얼로그로 열고, 마우스 휠 줌, Pan 이동, 줌 리셋 기능으로 콘텐츠를 탐색할 수 있다.

### 기술 스택

| 항목 | 기술 |
|------|------|
| GUI | PySide6 (Qt 6) |
| PDF 렌더링 | PyMuPDF (fitz) |
| SVG 렌더링 | PySide6.QtSvg (QSvgRenderer) |
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
| **Drop_Zone** | 파일 드래그 앤 드롭 및 콘텐츠 표시 위젯 (QLabel) |
| **Display_Area** | 파일 내용을 렌더링하여 표시하는 영역 |
| **Title_Panel** | 상단 패널 — 열기/줌/리셋/방향 버튼, 안내 문구, 줌 레이블 |
| **Supported_Format** | PNG, JPG(JPEG), PDF, SVG |
| **Renderer** | 각 파일 형식에 맞게 내용을 렌더링하는 모듈 |
| **Zoom_Level** | 확대/축소 배율 (1.0 = 100%) |
| **Zoom_Step** | 휠/버튼 한 단위당 배율 변경 계수 (1.25) |
| **Pan_Offset** | 뷰포트 이동 위치 (x, y) 좌표 오프셋, 중앙 기준 (0, 0) |
| **Viewport** | Drop_Zone 내에서 사용자에게 보이는 콘텐츠 영역 |
| **Rendered_Content** | Zoom_Level이 적용되어 렌더링된 전체 이미지 |
| **Pan_Step** | 방향 버튼 한 번 클릭 시 이동 픽셀 수 (50px) |

---

## 3. 요구사항 통합

### 3.1 파일 열기 및 표시

| ID | 요구사항 | 인수 조건 요약 |
|----|----------|----------------|
| R1 | 애플리케이션 윈도우 | 800×600, 제목 "SvgViewer", 안내 메시지 표시 |
| R2 | 드래그 앤 드롭 | 시각적 피드백, 지원 형식 검증, 다중 파일 시 첫 번째만 수신 |
| R3 | PNG/JPG 렌더링 | QPixmap 로드, 종횡비 유지 스케일링, 리사이즈 대응 |
| R4 | PDF 렌더링 | PyMuPDF로 첫 페이지 이미지 변환, 손상 파일 오류 처리 |
| R5 | SVG 렌더링 | QSvgRenderer로 벡터 품질 직접 렌더링, 줌 시에도 선명 |
| R6 | 파일 교체 | 새 파일 드롭 시 기존 파일 교체, 메모리 해제 |
| R7 | 파일 열기 다이얼로그 | "열기" 버튼 → QFileDialog, 지원 형식 필터, 취소 시 상태 유지 |

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

### 3.4 오류 처리

| 오류 상황 | 메시지 | 처리 위치 |
|-----------|--------|-----------|
| 미지원 파일 형식 | "지원하지 않는 파일 형식입니다" | file_handler |
| 파일 크기 초과 (>100MB) | "파일 크기가 너무 큽니다 (최대 100MB)" | file_handler |
| 파일 읽기 I/O 오류 | "파일을 읽을 수 없습니다: [파일명]" | file_handler |
| 이미지 디코딩 실패 | "이미지 파일이 손상되었습니다: [파일명]" | renderers |
| PDF 렌더링 실패 | "PDF 파일을 열 수 없습니다" | renderers |
| SVG 렌더링 실패 | "SVG 파일을 열 수 없습니다" | renderers |

### 3.5 프로젝트 구조 및 빌드

- src/my_app/ 디렉토리 구조 (src layout)
- Python 3.12, PySide6, PyMuPDF 의존성
- ruff, mypy(strict), pytest 설정
- PyInstaller onefile, console=False → `SvgViewer.exe`
- uv 패키지 관리

---

## 4. 아키텍처

### 모듈 구조

```
src/my_app/
├── main.py           # 앱 진입점 (QApplication)
├── viewer.py         # 메인 윈도우, 줌/Pan 상태 관리, 파일 다이얼로그
├── drop_zone.py      # 드래그 앤 드롭 + 마우스 휠/드래그 이벤트
├── title_panel.py    # 열기/줌/리셋/방향 버튼, 줌 레이블
├── file_handler.py   # 파일 검증 (형식, 크기, 존재 여부)
└── renderers.py      # PNG/JPG/PDF/SVG 렌더링
```

### 시그널/슬롯 연결

```
TitlePanel → Viewer:
  open_clicked, zoom_in_clicked, zoom_out_clicked, zoom_reset_clicked
  pan_up_clicked, pan_down_clicked, pan_left_clicked, pan_right_clicked

DropZone → Viewer:
  file_dropped, zoom_requested
  pan_started, pan_moved, pan_finished

Viewer → TitlePanel:
  update_zoom_label()

Viewer → DropZone:
  display_pixmap(), show_error(), show_placeholder(), setCursor()
```

### UI 레이아웃

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ [열기] 마우스 휠로 줌인/줌아웃 가능  ─stretch─  [◀][▲][▼][▶] [-][100%][+][리셋] │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                          Drop_Zone / Display_Area                            │
│                                                                              │
│              (드래그 앤 드롭 또는 "열기" 버튼으로 파일 로드)                    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 렌더링 파이프라인

```
파일 입력 (드롭 또는 다이얼로그)
  → validate_file() → FileInfo
  → render_file(file_info, zoomed_size) → QPixmap (전체)
  → clamp_pan_offset() → 경계 제한
  → crop_pixmap(pixmap, viewport_size) → QPixmap (잘린)
  → display_pixmap(cropped)
```

---

## 5. 핵심 설계 결정

| 결정 | 선택 | 이유 |
|------|------|------|
| PDF 렌더링 | PyMuPDF (fitz) | 빠르고 QPixmap과 자연스럽게 연동 |
| SVG 렌더링 | QSvgRenderer 직접 렌더링 | 줌 크기로 벡터 렌더링하여 확대 시에도 선명 |
| 이미지 표시 | QLabel + QPixmap | 단순하고 메모리 효율적 |
| 줌 관리 | Viewer 중심 | 렌더링 파이프라인을 제어하는 곳에서 상태 관리 |
| 줌 방식 | 곱셈 기반 (×1.25) | 로그 스케일로 자연스러운 줌 경험 |
| Pan 방식 | Crop 기반 | QScrollArea 없이 기존 파이프라인 확장 |
| Pan 좌표계 | 중앙 기준 (0,0) | 초기화 직관적, 경계 계산 대칭적 |
| 파일 다이얼로그 | QFileDialog.getOpenFileName | 기존 _on_file_dropped 파이프라인 재사용 |
| 줌 리셋 | _apply_zoom 재사용 | Pan 초기화 + 줌 레이블 갱신 + 재렌더링 한 번에 처리 |

---

## 6. 데이터 모델

### 상수

| 상수 | 값 | 설명 |
|------|-----|------|
| SUPPORTED_EXTENSIONS | {.png, .jpg, .jpeg, .pdf, .svg} | 지원 확장자 |
| MAX_FILE_SIZE | 104,857,600 (100MB) | 최대 파일 크기 |
| ZOOM_STEP | 1.25 | 줌 배율 변경 계수 |
| MIN_ZOOM | 0.1 | 최소 줌 (10%) |
| MAX_ZOOM | 10.0 | 최대 줌 (1000%) |
| DEFAULT_ZOOM | 1.0 | 초기 줌 (100%) |
| PAN_STEP | 50 | 방향 버튼 이동 픽셀 |

### FileFormat (Enum)

PNG, JPG, PDF, SVG

### FileInfo (frozen dataclass)

path: Path, format: FileFormat, size: int

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

### 줌 리셋

| # | 속성 | 검증 대상 |
|---|------|-----------|
| 19 | 줌 리셋 상태 초기화 | zoom_reset 후 zoom=1.0, pan=(0,0) |

---

## 8. 개발 이력

| 단계 | 기능 | 주요 변경 |
|------|------|-----------|
| 1 | 기본 뷰어 | 프로젝트 구조, 드래그 앤 드롭, PNG/JPG/PDF/SVG 렌더링, 오류 처리 |
| 2 | 마우스 휠 줌 | TitlePanel 신규, DropZone wheelEvent, Viewer 줌 상태 관리, scale_pixmap 확대 지원 |
| 3 | Pan 네비게이션 | DropZone 마우스 드래그, TitlePanel 방향 버튼, Viewer crop 파이프라인, 순수 함수 추출 |
| 4 | 파일 다이얼로그 + 줌 리셋 | TitlePanel "열기"/"리셋" 버튼, Viewer QFileDialog/zoom_reset |
| 5 | SVG 벡터 품질 | render_svg를 줌 크기로 직접 벡터 렌더링하도록 수정 |
| 6 | 앱 이름 변경 | SvgViewer로 리브랜딩, 스크립트 엔트리포인트 추가 |
