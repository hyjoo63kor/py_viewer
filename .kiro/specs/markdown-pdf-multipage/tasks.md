# 구현 계획: Markdown 렌더링 및 PDF 멀티 페이지

## 개요

기존 PySide6 기반 뷰어에 Markdown 렌더링과 PDF 멀티 페이지 탐색 기능을 추가한다. 기존 아키텍처(file_handler → renderers → viewer)를 유지하면서 점진적으로 확장한다.

## Tasks

- [x] 1. 의존성 추가 및 파일 형식 확장
  - [x] 1.1 pyproject.toml에 `markdown>=3.7,<4` 의존성 추가
    - `dependencies` 목록에 markdown 라이브러리 추가
    - _Requirements: 2.1_
  - [x] 1.2 FileFormat 열거형에 MD 값 추가 및 detect_format 확장
    - `file_handler.py`의 `FileFormat`에 `MD = "md"` 추가
    - `SUPPORTED_EXTENSIONS`에 `".md"` 추가
    - `detect_format` 함수에 `.md` 확장자 분기 추가
    - _Requirements: 1.1, 1.2, 1.3_
  - [ ]* 1.3 file_handler 단위 테스트 추가
    - `tests/test_file_handler.py`에 `.md` 확장자 감지 테스트 추가
    - 대소문자 혼합(`.MD`, `.Md`) 처리 테스트 추가
    - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Markdown 렌더링 구현
  - [x] 2.1 renderers.py에 render_markdown 함수 구현
    - `Path.read_text("utf-8")`로 Markdown 텍스트 읽기
    - `markdown.markdown(text, extensions=["fenced_code", "tables"])`로 HTML 변환
    - `QTextDocument`에 HTML 설정, 문서 너비를 display_size.width()로 제한
    - `QTextDocument`를 `QPixmap`으로 렌더링
    - `scale_pixmap`으로 display_size에 맞게 스케일링
    - 파일 읽기 실패 시 `RenderError` 발생
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  - [x] 2.2 render_file 함수에 FileFormat.MD 분기 추가
    - `FileFormat.MD`일 때 `render_markdown` 호출
    - _Requirements: 2.1, 2.2_
  - [ ]* 2.3 render_markdown 단위 테스트 추가
    - 기본 Markdown 문법(제목, 목록, 코드 블록, 강조, 링크) 렌더링 테스트
    - 존재하지 않는 파일 → `RenderError` 테스트
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [ ]* 2.4 Property 1 속성 기반 테스트 작성
    - **Property 1: Markdown 렌더링은 유효하고 크기가 적절한 QPixmap을 생성한다**
    - 임의의 Markdown 텍스트와 양의 정수 display_size에 대해 null이 아닌 QPixmap 반환 검증
    - 반환된 QPixmap 크기가 display_size를 초과하지 않는지 검증
    - **Validates: Requirements 2.1, 2.2, 2.5**

- [x] 3. Checkpoint - Markdown 렌더링 검증
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. PDF 멀티 페이지 렌더링 확장
  - [x] 4.1 renderers.py에 get_pdf_page_count 함수 구현
    - PyMuPDF(`fitz`)로 PDF 열기, `len(doc)`으로 총 페이지 수 반환
    - PDF 열기 실패 시 `RenderError` 발생
    - _Requirements: 4.1_
  - [x] 4.2 render_pdf 함수에 page 파라미터 추가
    - `page: int = 1` 파라미터 추가 (1-based, 기본값 1로 하위 호환성 유지)
    - `doc[page - 1]`로 지정된 페이지 렌더링
    - 유효 범위(1 ~ len(doc)) 벗어나면 `RenderError` 발생
    - _Requirements: 7.1, 7.2, 7.3_
  - [x] 4.3 render_file 함수에 page 파라미터 전달
    - `render_file` 시그니처에 `page: int = 1` 추가
    - `FileFormat.PDF`일 때 `render_pdf`에 `page` 전달
    - _Requirements: 7.1_
  - [ ]* 4.4 Property 2 속성 기반 테스트 작성
    - **Property 2: PDF 페이지 수 정확성**
    - N 페이지(1 ≤ N ≤ 20) PDF를 동적 생성하여 `get_pdf_page_count`가 정확히 N을 반환하는지 검증
    - **Validates: Requirements 4.1**
  - [ ]* 4.5 Property 7 속성 기반 테스트 작성
    - **Property 7: PDF 특정 페이지 렌더링은 유효하고 크기가 적절한 QPixmap을 생성한다**
    - 유효한 페이지 번호 p에 대해 null이 아닌 QPixmap 반환 및 크기 검증
    - **Validates: Requirements 7.1, 7.3**
  - [ ]* 4.6 Property 8 속성 기반 테스트 작성
    - **Property 8: 유효 범위를 벗어난 페이지 번호는 RenderError를 발생시킨다**
    - p ≤ 0 또는 p > N인 페이지 번호에 대해 `RenderError` 발생 검증
    - **Validates: Requirements 7.2**

- [x] 5. Checkpoint - PDF 렌더링 확장 검증
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. TitlePanel 페이지 네비게이션 UI 추가
  - [x] 6.1 TitlePanel에 페이지 네비게이션 위젯 및 시그널 추가
    - `prev_page_clicked`, `next_page_clicked` 시그널 추가
    - `_prev_button("◁")`, `_page_label`, `_next_button("▷")` 위젯 추가
    - 방향 버튼과 줌 컨트롤 사이에 배치
    - 초기 상태: 숨김(`setVisible(False)`)
    - _Requirements: 5.1, 5.6_
  - [x] 6.2 set_page_info 메서드 구현
    - `set_page_info(current: int, total: int)` 메서드 구현
    - total ≤ 1이면 네비게이션 위젯 숨김
    - total > 1이면 위젯 표시, Page_Label을 "current/total" 형식으로 갱신
    - current == 1이면 Prev_Button 비활성화, current == total이면 Next_Button 비활성화
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 8.1_
  - [x] 6.3 hide_page_nav 메서드 구현
    - 페이지 네비게이션 위젯을 숨기는 메서드
    - _Requirements: 5.5, 5.6_
  - [ ]* 6.4 Property 3 속성 기반 테스트 작성
    - **Property 3: 페이지 레이블 형식 정확성**
    - 유효한 (current, total) 쌍에 대해 Page_Label 텍스트가 "current/total" 형식인지 검증
    - **Validates: Requirements 5.2**
  - [ ]* 6.5 Property 4 속성 기반 테스트 작성
    - **Property 4: 네비게이션 버튼 활성화/비활성화 정확성**
    - current == 1이면 Prev 비활성화, current == total이면 Next 비활성화, 그 외 둘 다 활성화 검증
    - **Validates: Requirements 5.3, 5.4**

- [x] 7. Viewer에 PDF 페이지 탐색 로직 통합
  - [x] 7.1 Viewer에 페이지 상태 및 시그널 연결 추가
    - `_current_page: int = 1`, `_total_pages: int = 1` 상태 추가
    - `prev_page_clicked`, `next_page_clicked` 시그널을 `_on_prev_page`, `_on_next_page`에 연결
    - _Requirements: 4.2, 6.1, 6.2_
  - [x] 7.2 _on_file_dropped에서 PDF 페이지 정보 초기화
    - PDF 파일 로드 시 `get_pdf_page_count` 호출하여 `_total_pages` 설정
    - `_current_page`를 1로 초기화
    - `set_page_info(1, total_pages)` 호출
    - PDF가 아닌 파일 로드 시 `hide_page_nav()` 호출
    - _Requirements: 4.1, 4.2, 5.1, 5.5, 8.1_
  - [x] 7.3 _on_prev_page, _on_next_page 메서드 구현
    - `_on_next_page`: current_page < total_pages일 때 current_page += 1, 줌/Pan 초기화, 재렌더링
    - `_on_prev_page`: current_page > 1일 때 current_page -= 1, 줌/Pan 초기화, 재렌더링
    - 페이지 변경 후 `set_page_info` 호출하여 UI 갱신
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  - [x] 7.4 _render_file에서 page 파라미터 전달
    - `render_file` 호출 시 `page=self._current_page` 전달
    - _Requirements: 7.1_
  - [ ]* 7.5 Property 5 속성 기반 테스트 작성
    - **Property 5: 페이지 이동은 현재 페이지를 ±1 변경한다**
    - next_page 호출 시 current_page가 정확히 1 증가, prev_page 호출 시 1 감소 검증
    - **Validates: Requirements 6.1, 6.2**
  - [ ]* 7.6 Property 6 속성 기반 테스트 작성
    - **Property 6: 페이지 변경 시 줌과 Pan 초기화**
    - 페이지 변경 후 줌 레벨이 1.0, Pan 오프셋이 (0, 0)인지 검증
    - **Validates: Requirements 6.3, 6.4**

- [x] 8. UI 텍스트 및 파일 필터 업데이트
  - [x] 8.1 DropZone 안내 메시지에 MD 추가
    - `_PLACEHOLDER_TEXT`에 "MD" 포함하도록 변경
    - _Requirements: 3.1_
  - [x] 8.2 Viewer 파일 열기 다이얼로그 필터에 *.md 추가
    - `_FILE_FILTER`에 `*.md` 추가
    - _Requirements: 3.2_

- [x] 9. Final checkpoint - 전체 통합 검증
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- `*` 표시된 태스크는 선택 사항이며 빠른 MVP를 위해 건너뛸 수 있습니다
- 각 태스크는 특정 요구사항을 참조하여 추적 가능합니다
- 체크포인트에서 점진적 검증을 수행합니다
- 속성 기반 테스트는 보편적 정확성 속성을 검증합니다
- 단위 테스트는 구체적인 예시와 에지 케이스를 검증합니다
