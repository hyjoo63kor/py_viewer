# 구현 계획: 마우스 휠 줌 기능

## 개요

기존 PySide6 기반 이미지/문서 뷰어에 마우스 휠 줌인/줌아웃 기능과 타이틀 패널(줌 안내 문구, 줌 버튼, 줌 레이블)을 추가한다. 기존 `viewer.py`, `drop_zone.py`, `renderers.py`를 수정하고, 신규 `title_panel.py`를 생성한다. 줌 로직은 `Viewer`에 집중하며, 마우스 휠과 버튼 모두 동일한 `zoom_in()`/`zoom_out()` 경로를 사용한다.

## 태스크

- [x] 1. renderers.py의 scale_pixmap 확대 지원 수정
  - [x] 1.1 `scale_pixmap` 함수를 수정하여 원본이 `display_size`보다 작을 때도 확대 스케일링을 수행하도록 변경
    - 기존: 원본이 display_size보다 작으면 원본 크기 유지 (축소만 지원)
    - 변경: display_size에 맞게 항상 스케일링 (확대/축소 모두 지원)
    - `Qt.AspectRatioMode.KeepAspectRatio`와 `Qt.TransformationMode.SmoothTransformation` 유지
    - _요구사항: 4.1, 4.2_

  - [ ]* 1.2 scale_pixmap 확대 동작에 대한 단위 테스트 추가
    - `tests/test_renderers.py`의 `TestScalePixmap` 클래스에 확대 테스트 케이스 추가
    - 원본보다 큰 display_size 전달 시 확대되는지 확인
    - 확대 시에도 종횡비가 유지되는지 확인
    - _요구사항: 4.1, 4.2_

  - [ ]* 1.3 Property 3: 줌 적용 스케일링 종횡비 보존 property-based 테스트 작성
    - **Property 3: Aspect Ratio Preservation under Zoom**
    - `tests/test_zoom_properties.py` 파일 생성
    - 임의의 (width, height, display_width, display_height) 조합으로 `scale_pixmap` 호출 후 종횡비 보존 및 크기 제한 확인 (확대 포함)
    - hypothesis의 `st.integers` 전략으로 1~5000 범위의 크기 생성
    - **Validates: Requirements 4.1, 4.2**

- [x] 2. DropZone에 wheelEvent 및 zoom_requested 시그널 추가
  - [x] 2.1 `drop_zone.py`에 `zoom_requested = Signal(int)` 시그널 추가 및 `wheelEvent` 오버라이드 구현
    - `QWheelEvent`를 import
    - `zoom_requested = Signal(int)` 클래스 변수 추가
    - `wheelEvent` 메서드에서 `event.angleDelta().y()` 값을 `zoom_requested` 시그널로 emit
    - _요구사항: 1.1, 2.1_

  - [ ]* 2.2 DropZone wheelEvent 단위 테스트 작성
    - `tests/test_drop_zone.py`에 휠 이벤트 발생 시 `zoom_requested` 시그널 emit 확인 테스트 추가
    - pytest-qt의 `qtbot.waitSignal`을 사용하여 시그널 emit 및 delta 값 검증
    - _요구사항: 1.1, 2.1_

- [x] 3. TitlePanel 위젯 신규 생성
  - [x] 3.1 `src/my_app/title_panel.py` 파일 생성 및 `TitlePanel` 클래스 구현
    - `QWidget` 상속, `QHBoxLayout` 사용
    - 왼쪽: 안내 문구 QLabel ("마우스 휠로 줌인/줌아웃 가능")
    - 가운데: QSpacerItem (stretch)
    - 오른쪽: Zoom_Out_Button (`-`), Zoom_Label (`100%`), Zoom_In_Button (`+`)
    - `zoom_in_clicked = Signal()`, `zoom_out_clicked = Signal()` 시그널 정의
    - `update_zoom_label(zoom_level: float)` 메서드 구현 — `f"{round(zoom_level * 100)}%"` 형식
    - _요구사항: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [ ]* 3.2 TitlePanel 위젯 단위 테스트 작성
    - `tests/test_title_panel.py` 파일 생성
    - 안내 문구 "마우스 휠로 줌인/줌아웃 가능" 표시 확인
    - Zoom_In_Button, Zoom_Out_Button 존재 확인
    - Zoom_Label 초기값 "100%" 확인
    - `update_zoom_label` 호출 시 레이블 갱신 확인
    - 버튼 클릭 시 `zoom_in_clicked`, `zoom_out_clicked` 시그널 emit 확인
    - _요구사항: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [ ]* 3.3 Property 7: 줌 레이블 포맷 정확성 property-based 테스트 작성
    - **Property 7: Zoom Label Format Correctness**
    - `tests/test_zoom_properties.py`에 추가
    - 임의의 유효 줌 레벨 값 (0.1 ~ 10.0)에 대해 `update_zoom_label` 호출 후 레이블 텍스트가 `f"{round(level * 100)}%"` 형식인지 확인
    - **Validates: Requirements 7.5, 7.6**

- [x] 4. 체크포인트 — 기반 컴포넌트 검증
  - 모든 테스트를 실행하여 통과하는지 확인하고, 문제가 있으면 사용자에게 질문한다.

- [x] 5. Viewer에 줌 상태 관리 및 줌 메서드 추가
  - [x] 5.1 `viewer.py`에 줌 상수 및 줌 상태 변수 추가
    - 클래스 상수: `ZOOM_STEP = 1.25`, `MIN_ZOOM = 0.1`, `MAX_ZOOM = 10.0`, `DEFAULT_ZOOM = 1.0`
    - 인스턴스 변수: `_zoom_level: float = 1.0`
    - _요구사항: 3.1, 3.2, 3.3, 3.4_

  - [x] 5.2 `zoom_in()`, `zoom_out()` 메서드 구현
    - `zoom_in()`: 파일 미표시 시 무시, `_zoom_level = min(_zoom_level * ZOOM_STEP, MAX_ZOOM)`, `_apply_zoom()` 호출
    - `zoom_out()`: 파일 미표시 시 무시, `_zoom_level = max(_zoom_level / ZOOM_STEP, MIN_ZOOM)`, `_apply_zoom()` 호출
    - _요구사항: 1.1, 1.2, 2.1, 2.2, 6.1, 8.1, 8.2, 8.3, 8.4, 8.5_

  - [x] 5.3 `_apply_zoom()` 메서드 구현
    - 현재 줌 레벨로 `_render_file` 호출
    - TitlePanel의 `update_zoom_label` 호출하여 줌 레이블 갱신
    - _요구사항: 4.1, 7.6_

  - [x] 5.4 `_on_zoom_requested(delta: int)` 시그널 핸들러 구현
    - `delta > 0`이면 `zoom_in()`, `delta < 0`이면 `zoom_out()` 호출
    - _요구사항: 1.1, 2.1_

  - [ ]* 5.5 Property 1: 줌인 계산 정확성 property-based 테스트 작성
    - **Property 1: Zoom-In Calculation with Clamping**
    - `tests/test_zoom_properties.py`에 추가
    - 임의의 유효 줌 레벨 (0.1 ~ 10.0)에서 `zoom_in` 호출 후 결과가 `min(level * 1.25, 10.0)`과 같은지 검증
    - 결과가 항상 MIN_ZOOM 이상 MAX_ZOOM 이하인지 검증
    - **Validates: Requirements 1.1, 1.2, 8.1, 8.3**

  - [ ]* 5.6 Property 2: 줌아웃 계산 정확성 property-based 테스트 작성
    - **Property 2: Zoom-Out Calculation with Clamping**
    - `tests/test_zoom_properties.py`에 추가
    - 임의의 유효 줌 레벨 (0.1 ~ 10.0)에서 `zoom_out` 호출 후 결과가 `max(level / 1.25, 0.1)`과 같은지 검증
    - 결과가 항상 MIN_ZOOM 이상 MAX_ZOOM 이하인지 검증
    - **Validates: Requirements 2.1, 2.2, 8.2, 8.4**

  - [ ]* 5.7 Property 6: 파일 미표시 상태에서 줌 무시 property-based 테스트 작성
    - **Property 6: No Zoom Without File**
    - `tests/test_zoom_properties.py`에 추가
    - 파일 미로드 상태에서 임의 횟수의 zoom_in/zoom_out 호출 후 줌 레벨이 DEFAULT_ZOOM(1.0)으로 유지되는지 확인
    - **Validates: Requirements 6.1, 8.5**

- [x] 6. Viewer 레이아웃 변경 및 시그널 연결
  - [x] 6.1 `Viewer.__init__`에서 QVBoxLayout으로 TitlePanel + DropZone 수직 배치
    - 기존 `setCentralWidget(drop_zone)` → QWidget + QVBoxLayout으로 변경
    - TitlePanel을 상단에, DropZone을 하단(stretch)에 배치
    - `TitlePanel` import 추가
    - _요구사항: 7.1_

  - [x] 6.2 줌 관련 시그널 연결
    - `drop_zone.zoom_requested` → `_on_zoom_requested` 연결
    - `title_panel.zoom_in_clicked` → `zoom_in` 연결
    - `title_panel.zoom_out_clicked` → `zoom_out` 연결
    - _요구사항: 1.1, 2.1, 8.1, 8.2_

  - [x] 6.3 `_render_file` 수정 — 줌 레벨이 적용된 display_size로 렌더링
    - `base_size = self._drop_zone.size()`
    - `zoomed_size = QSize(int(base_size.width() * self._zoom_level), int(base_size.height() * self._zoom_level))`
    - `render_file(file_info, zoomed_size)` 호출
    - _요구사항: 4.1, 4.2, 4.3_

  - [x] 6.4 `_on_file_dropped` 수정 — 줌 레벨 초기화 추가
    - 메서드 시작 부분에서 `_zoom_level = DEFAULT_ZOOM` 설정
    - TitlePanel의 `update_zoom_label(DEFAULT_ZOOM)` 호출
    - 파일 검증 실패 시에도 줌 레벨이 이미 초기화된 상태 유지
    - _요구사항: 5.1, 5.2_

  - [x] 6.5 `resizeEvent` 수정 — 줌 레벨 유지하면서 재렌더링
    - 기존 `_render_file` 호출이 이미 줌 레벨을 적용하므로 추가 변경 최소화
    - _요구사항: 4.3_

- [x] 7. 체크포인트 — 핵심 줌 기능 검증
  - 모든 테스트를 실행하여 통과하는지 확인하고, 문제가 있으면 사용자에게 질문한다.

- [ ] 8. Viewer 줌 통합 테스트 및 나머지 property 테스트 작성
  - [ ]* 8.1 Viewer 줌 통합 단위 테스트 작성
    - `tests/test_viewer.py`에 줌 관련 테스트 추가
    - 파일 로드 후 `zoom_in`/`zoom_out` 동작 확인
    - 줌 레벨 경계값(MIN_ZOOM, MAX_ZOOM) 동작 확인
    - 파일 드롭 시 줌 초기화 확인
    - 파일 미표시 상태에서 줌 무시 확인
    - 줌 버튼 클릭 시 줌 동작 확인
    - _요구사항: 1.1, 1.2, 2.1, 2.2, 5.1, 5.2, 6.1, 8.1, 8.2, 8.3, 8.4, 8.5_

  - [ ]* 8.2 Property 4: 리사이즈 시 줌 레벨 불변 property-based 테스트 작성
    - **Property 4: Zoom Level Invariance on Resize**
    - `tests/test_zoom_properties.py`에 추가
    - 임의의 줌 레벨 설정 후 `resizeEvent` 호출 시 줌 레벨 값이 변경 전과 동일한지 확인
    - **Validates: Requirements 4.3**

  - [ ]* 8.3 Property 5: 파일 드롭 시 줌 초기화 property-based 테스트 작성
    - **Property 5: Zoom Reset on File Drop**
    - `tests/test_zoom_properties.py`에 추가
    - 임의의 줌 레벨 상태에서 새로운 파일 드롭 후 줌 레벨이 항상 DEFAULT_ZOOM(1.0)으로 초기화되는지 확인
    - 파일 로드 성공/실패 여부와 관계없이 동일하게 적용
    - **Validates: Requirements 5.1, 5.2**

- [x] 9. 최종 체크포인트 — 전체 테스트 통과 확인
  - 모든 테스트를 실행하여 통과하는지 확인하고, 문제가 있으면 사용자에게 질문한다.

## 참고 사항

- `*` 표시된 태스크는 선택 사항이며 빠른 MVP를 위해 건너뛸 수 있습니다
- 각 태스크는 추적 가능성을 위해 특정 요구사항을 참조합니다
- 체크포인트는 점진적 검증을 보장합니다
- Property 테스트는 보편적 정확성 속성을 검증합니다
- 단위 테스트는 구체적인 예제와 에지 케이스를 검증합니다
- 구현 언어: Python 3.12 (PySide6)
- 테스트 프레임워크: pytest + hypothesis + pytest-qt
