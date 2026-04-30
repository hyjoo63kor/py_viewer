# 구현 계획: Pan(이동) 네비게이션

## 개요

기존 PySide6 기반 이미지/문서 뷰어에 Pan(이동) 기능을 추가한다. 핵심 계산 로직을 순수 함수로 추출하고, DropZone에 마우스 드래그 시그널을 추가하며, TitlePanel에 방향 버튼을 추가하고, Viewer에서 Pan 상태를 관리하여 crop 기반 Pan을 구현한다.

## Tasks

- [x] 1. 순수 함수 추출 및 Pan 핵심 계산 로직 구현
  - [x] 1.1 `viewer.py`에 `clamp_pan_offset` 순수 함수 구현
    - `clamp_pan_offset(pan_x, pan_y, rendered_w, rendered_h, viewport_w, viewport_h) -> tuple[int, int]` 모듈 수준 함수 작성
    - `max_offset_x = max(0, (rendered_w - viewport_w) // 2)` 계산 후 clamp 적용
    - rendered가 viewport보다 작거나 같으면 `(0, 0)` 반환
    - _Requirements: 3.1, 3.2, 3.3_

  - [x] 1.2 `viewer.py`에 `compute_crop_rect` 순수 함수 구현
    - `compute_crop_rect(rendered_w, rendered_h, viewport_w, viewport_h, pan_x, pan_y) -> tuple[int, int, int, int]` 모듈 수준 함수 작성
    - crop 영역의 `(x, y, width, height)` 반환
    - `pan_offset = (0, 0)`이면 중앙 영역 crop
    - _Requirements: 4.1, 4.2_

  - [ ]* 1.3 Property 테스트: Pan 오프셋 경계 제한 (Property 2)
    - **Property 2: Pan 오프셋 경계 제한**
    - `tests/test_pan_properties.py` 파일 생성
    - 임의의 rendered_size, viewport_size, pan_offset에 대해 clamp 후 `|cx| <= max(0, (rw - vw) // 2)` 검증
    - `rendered_size <= viewport_size`이면 결과가 `(0, 0)`인지 검증
    - **Validates: Requirements 3.1, 3.2, 3.3, 8.1**

  - [ ]* 1.4 Property 테스트: Crop 영역 유효성 (Property 3)
    - **Property 3: Crop 영역 유효성**
    - 임의의 rendered_size, viewport_size, 유효 pan_offset에 대해 crop 영역이 rendered pixmap 내에 있는지 검증
    - `crop_x >= 0`, `crop_y >= 0`, `crop_x + crop_w <= rw`, `crop_y + crop_h <= rh` 검증
    - `pan_offset = (0, 0)`이면 crop 영역이 정중앙인지 검증
    - **Validates: Requirements 4.1, 4.2**

- [x] 2. DropZone에 마우스 드래그 Pan 시그널 추가
  - [x] 2.1 `drop_zone.py`에 Pan 시그널 및 마우스 이벤트 핸들러 구현
    - `pan_started = Signal(int, int)`, `pan_moved = Signal(int, int)`, `pan_finished = Signal()` 시그널 추가
    - `_drag_start_pos: QPoint | None` 인스턴스 변수 추가
    - `mousePressEvent`: 왼쪽 버튼 누름 시 시작 위치 기록, `pan_started` emit
    - `mouseMoveEvent`: 시작 위치 대비 이동량 `(dx, dy)` 계산, `pan_moved` emit
    - `mouseReleaseEvent`: `pan_finished` emit, 시작 위치 초기화
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ]* 2.2 DropZone 마우스 이벤트 단위 테스트
    - `tests/test_drop_zone.py`에 테스트 추가
    - `mousePressEvent` 시 `pan_started` 시그널 emit 확인
    - `mouseMoveEvent` 시 `pan_moved` 시그널 emit 확인
    - `mouseReleaseEvent` 시 `pan_finished` 시그널 emit 확인
    - _Requirements: 1.1, 1.2, 1.3_

- [x] 3. TitlePanel에 방향 버튼 추가
  - [x] 3.1 `title_panel.py`에 방향 버튼 4개 및 시그널 추가
    - `pan_up_clicked`, `pan_down_clicked`, `pan_left_clicked`, `pan_right_clicked` 시그널 추가
    - `Pan_Left_Button(◀)`, `Pan_Up_Button(▲)`, `Pan_Down_Button(▼)`, `Pan_Right_Button(▶)` 버튼 생성
    - 기존 줌 컨트롤 왼쪽에 방향 버튼 배치, `setFixedWidth(30)` 적용
    - 각 버튼 클릭 시 해당 시그널 emit 연결
    - _Requirements: 2.1_

  - [ ]* 3.2 TitlePanel 방향 버튼 단위 테스트
    - `tests/test_viewer.py` 또는 별도 테스트 파일에 테스트 추가
    - 4개 방향 버튼 존재 확인
    - 각 버튼 클릭 시 해당 시그널 emit 확인 (pytest-qt `qtbot.waitSignal`)
    - _Requirements: 2.1_

- [x] 4. Checkpoint - 기본 컴포넌트 검증
  - ruff, mypy 검사 통과 확인
  - 기존 테스트 통과 확인
  - 질문이 있으면 사용자에게 문의

- [x] 5. Viewer에 Pan 상태 관리 및 렌더링 파이프라인 통합
  - [x] 5.1 Viewer에 Pan 상태 변수 및 상수 추가
    - `PAN_STEP: int = 50` 클래스 상수 추가
    - `_pan_offset_x: int = 0`, `_pan_offset_y: int = 0` 인스턴스 변수 추가
    - `_drag_start_pos: QPoint | None = None`, `_drag_start_offset: tuple[int, int] = (0, 0)` 인스턴스 변수 추가
    - `_reset_pan_offset` 메서드 구현
    - _Requirements: 2.6, 5.1, 6.1_

  - [x] 5.2 Viewer에 `_clamp_pan_offset` 및 `_crop_pixmap` 메서드 구현
    - `_clamp_pan_offset`: 순수 함수 `clamp_pan_offset`을 호출하여 인스턴스 변수 갱신
    - `_crop_pixmap`: 순수 함수 `compute_crop_rect`를 호출하여 QPixmap crop 수행
    - `_apply_pan`: 현재 pan_offset으로 재렌더링+crop 수행
    - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2_

  - [x] 5.3 Viewer `_render_file` 메서드에 crop 단계 추가
    - 기존 전체 pixmap 렌더링 후 `_crop_pixmap`으로 viewport 크기에 맞게 crop
    - crop된 pixmap을 `display_pixmap`에 전달
    - _Requirements: 4.1, 4.2_

  - [x] 5.4 Viewer에 마우스 드래그 Pan 핸들러 구현 및 시그널 연결
    - `_on_pan_started(x, y)`: 드래그 시작 위치와 현재 offset 기록, ClosedHandCursor 설정
    - `_on_pan_moved(dx, dy)`: `drag_start_offset + (dx, dy)` 계산, clamp, `_apply_pan` 호출
    - `_on_pan_finished()`: 드래그 상태 초기화, ArrowCursor 복원
    - DropZone의 `pan_started`, `pan_moved`, `pan_finished` 시그널 연결
    - 파일 미표시 상태에서는 Pan 동작 무시 (guard 조건)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 7.1_

  - [x] 5.5 Viewer에 방향 버튼 Pan 핸들러 구현 및 시그널 연결
    - `_on_pan_up`: `pan_offset_y -= PAN_STEP`, clamp, `_apply_pan`
    - `_on_pan_down`: `pan_offset_y += PAN_STEP`, clamp, `_apply_pan`
    - `_on_pan_left`: `pan_offset_x -= PAN_STEP`, clamp, `_apply_pan`
    - `_on_pan_right`: `pan_offset_x += PAN_STEP`, clamp, `_apply_pan`
    - TitlePanel의 `pan_*_clicked` 시그널 연결
    - 파일 미표시 상태에서는 Pan 동작 무시 (guard 조건)
    - _Requirements: 2.2, 2.3, 2.4, 2.5, 2.6, 7.2_

  - [x] 5.6 기존 `_apply_zoom` 및 `_on_file_dropped` 메서드에 Pan 초기화 추가
    - `_apply_zoom`에서 `_reset_pan_offset()` 호출 추가
    - `_on_file_dropped`에서 `_reset_pan_offset()` 호출 추가
    - _Requirements: 5.1, 6.1_

  - [x] 5.7 `resizeEvent`에서 Pan 오프셋 경계 재적용
    - 리사이즈 시 `_clamp_pan_offset`을 새 viewport 크기로 호출
    - clamp된 offset으로 재렌더링
    - _Requirements: 8.1_

  - [ ]* 5.8 Property 테스트: 방향 버튼 Pan 오프셋 변경 (Property 1)
    - **Property 1: 방향 버튼 Pan 오프셋 변경**
    - 임의의 초기 pan_offset과 방향에 대해 PAN_STEP(50)만큼 변경 후 clamp 적용 검증
    - **Validates: Requirements 2.2, 2.3, 2.4, 2.5**

  - [ ]* 5.9 Property 테스트: 드래그 Pan 오프셋 계산 (Property 4)
    - **Property 4: 드래그 Pan 오프셋 계산**
    - 임의의 드래그 시작/현재 위치와 초기 offset에 대해 `(ox + (sx - cx), oy + (sy - cy))` 검증
    - **Validates: Requirements 1.2**

  - [ ]* 5.10 Property 테스트: 줌 변경 시 Pan 초기화 (Property 5)
    - **Property 5: 줌 변경 시 Pan 초기화**
    - 임의의 pan_offset 상태에서 zoom_in/zoom_out 후 pan_offset == (0, 0) 검증
    - **Validates: Requirements 5.1**

  - [ ]* 5.11 Property 테스트: 파일 드롭 시 Pan 초기화 (Property 6)
    - **Property 6: 파일 드롭 시 Pan 초기화**
    - 임의의 pan_offset 상태에서 파일 드롭 후 pan_offset == (0, 0) 검증
    - **Validates: Requirements 6.1**

  - [ ]* 5.12 Property 테스트: 파일 미표시 상태에서 Pan 무시 (Property 7)
    - **Property 7: 파일 미표시 상태에서 Pan 무시**
    - 파일 미로드 상태에서 임의의 pan 동작 후 pan_offset == (0, 0) 검증
    - **Validates: Requirements 7.1, 7.2**

- [ ] 6. Viewer Pan 통합 단위 테스트
  - [ ]* 6.1 Viewer Pan 통합 단위 테스트 작성
    - `tests/test_viewer.py`에 테스트 추가
    - 파일 로드 후 방향 버튼으로 pan 이동 확인
    - 드래그 시작 시 ClosedHandCursor, 종료 시 ArrowCursor 확인
    - 줌 변경 시 pan_offset 초기화 확인
    - 파일 드롭 시 pan_offset 초기화 확인
    - 파일 미표시 상태에서 pan 무시 확인
    - PAN_STEP == 50 확인
    - _Requirements: 1.4, 1.5, 2.6, 5.1, 6.1, 7.1, 7.2_

- [x] 7. 최종 Checkpoint - 전체 검증
  - ruff, mypy 검사 통과 확인
  - 전체 테스트 스위트 통과 확인 (`pytest`)
  - 질문이 있으면 사용자에게 문의

## Notes

- `*` 표시된 태스크는 선택 사항이며 빠른 MVP를 위해 건너뛸 수 있습니다
- 각 태스크는 추적 가능성을 위해 특정 요구사항을 참조합니다
- Checkpoint를 통해 점진적 검증을 수행합니다
- Property 테스트는 보편적 정확성 속성을 검증합니다
- 단위 테스트는 구체적인 예제와 에지 케이스를 검증합니다
- 순수 함수(`clamp_pan_offset`, `compute_crop_rect`)를 먼저 구현하여 Qt 의존성 없이 핵심 로직을 테스트할 수 있게 합니다
