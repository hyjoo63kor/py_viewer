# 구현 계획: 파일 열기 다이얼로그 & 줌 리셋

## 개요

기존 PySide6 기반 이미지/문서 뷰어에 "열기" 버튼(파일 다이얼로그)과 "리셋" 버튼(줌/Pan 초기화)을 추가한다. 기존 TitlePanel과 Viewer에 시그널/슬롯과 메서드를 추가하는 방식으로, 새로운 모듈이나 클래스는 도입하지 않는다.

## Tasks

- [x] 1. TitlePanel에 "열기" 버튼과 "리셋" 버튼 추가
  - [x] 1.1 TitlePanel에 `open_clicked`, `zoom_reset_clicked` 시그널 추가
    - `open_clicked = Signal()`, `zoom_reset_clicked = Signal()` 선언
    - _Requirements: 1.1, 1.2, 4.1, 4.2_
  - [x] 1.2 "열기" 버튼(`_open_button`)을 레이아웃 왼쪽(안내 문구 앞)에 배치
    - QPushButton 텍스트: "열기"
    - `clicked` 시그널을 `open_clicked`에 연결
    - _Requirements: 1.1_
  - [x] 1.3 "리셋" 버튼(`_zoom_reset_button`)을 줌 인 버튼 뒤에 배치
    - QPushButton 텍스트: "리셋"
    - `clicked` 시그널을 `zoom_reset_clicked`에 연결
    - 레이아웃 순서: `[열기] [안내 문구] --- stretch --- [◀][▲][▼][▶] [-][100%][+][리셋]`
    - _Requirements: 4.1, 4.2_
  - [ ]* 1.4 TitlePanel 버튼 및 시그널 단위 테스트 작성
    - "열기" 버튼 존재 및 텍스트 확인
    - "리셋" 버튼 존재 및 텍스트 확인
    - 각 버튼 클릭 시 해당 시그널 emit 확인
    - _Requirements: 1.1, 4.1, 4.2_

- [x] 2. Viewer에 파일 열기 다이얼로그 기능 구현
  - [x] 2.1 `_on_open_clicked` 메서드 구현 및 시그널 연결
    - `_FILE_FILTER = "이미지/문서 파일 (*.png *.jpg *.jpeg *.pdf *.svg)"` 상수 정의
    - `QFileDialog.getOpenFileName` 호출하여 파일 경로 획득
    - 파일 선택 시 기존 `_on_file_dropped(file_path)` 호출
    - 취소 시(빈 문자열) 아무 동작 없음
    - `__init__`에서 `self._title_panel.open_clicked.connect(self._on_open_clicked)` 연결
    - _Requirements: 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3_
  - [ ]* 2.2 파일 열기 다이얼로그 단위 테스트 작성
    - `QFileDialog.getOpenFileName`을 mock하여 올바른 필터로 호출되는지 확인
    - 파일 선택 시 `_on_file_dropped`가 호출되는지 확인
    - 다이얼로그 취소 시 상태 변경 없음 확인
    - _Requirements: 1.2, 1.3, 1.4, 2.1, 3.1, 3.2, 3.3_

- [x] 3. Viewer에 줌 리셋 기능 구현
  - [x] 3.1 `zoom_reset` 메서드 구현 및 시그널 연결
    - `_current_file_info`가 `None`이면 즉시 반환
    - `_zoom_level`이 `DEFAULT_ZOOM`이고 Pan 오프셋이 (0, 0)이면 즉시 반환
    - `_zoom_level`을 `DEFAULT_ZOOM`으로 설정 후 `_apply_zoom()` 호출
    - `__init__`에서 `self._title_panel.zoom_reset_clicked.connect(self.zoom_reset)` 연결
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 6.1, 7.1_
  - [ ]* 3.2 줌 리셋 단위 테스트 작성
    - 파일 미표시 상태에서 호출 시 아무 동작 없음 확인
    - 이미 100% + Pan (0,0) 상태에서 호출 시 재렌더링 없음 확인
    - 줌 리셋 후 줌 레이블 "100%" 갱신 확인
    - 줌 리셋 후 렌더링 수행 확인
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 6.1, 7.1_
  - [ ]* 3.3 줌 리셋 상태 초기화 속성 테스트 작성
    - **Property 1: 줌 리셋 상태 초기화**
    - hypothesis의 `floats()`와 `integers()`로 임의의 줌 레벨(MIN_ZOOM ~ MAX_ZOOM)과 Pan 오프셋 생성
    - `zoom_reset()` 호출 후 `_zoom_level == 1.0`, `_pan_offset_x == 0`, `_pan_offset_y == 0` 검증
    - **Validates: Requirements 5.1, 5.2**

- [x] 4. 최종 체크포인트
  - 모든 테스트가 통과하는지 확인하고, 질문이 있으면 사용자에게 문의한다.

## Notes

- `*` 표시된 태스크는 선택 사항이며, 빠른 MVP를 위해 건너뛸 수 있습니다
- 각 태스크는 추적 가능성을 위해 특정 요구사항을 참조합니다
- 속성 테스트는 다양한 줌/Pan 상태 조합에서 줌 리셋의 정확성을 검증합니다
