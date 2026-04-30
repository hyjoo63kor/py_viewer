# Implementation Plan: Image & Document Viewer

## 개요

PySide6 기반 데스크톱 이미지/문서 뷰어 애플리케이션을 구현한다. 프로젝트 구조 설정부터 시작하여 핵심 데이터 모델, 파일 검증, 렌더링 모듈, UI 위젯 순서로 점진적으로 구현하며, 각 단계에서 테스트를 통해 정확성을 검증한다.

## Tasks

- [x] 1. 프로젝트 구조 및 빌드 설정
  - [x] 1.1 pyproject.toml 생성 및 의존성 설정
    - Python 3.12 버전 지정
    - PySide6, PyMuPDF(fitz) 런타임 의존성 추가
    - ruff, mypy(strict), pytest, hypothesis, pytest-qt 개발 의존성 추가
    - `src/my_app` 패키지 레이아웃 설정
    - uv를 패키지 관리자로 사용하여 의존성 설치
    - _Requirements: 8.2, 8.3, 8.5_

  - [x] 1.2 src/my_app 디렉토리 구조 생성
    - `src/my_app/__init__.py` 생성
    - `src/my_app/main.py` 진입점 스텁 생성
    - `src/my_app/viewer.py` 스텁 생성
    - `src/my_app/drop_zone.py` 스텁 생성
    - `src/my_app/file_handler.py` 스텁 생성
    - `src/my_app/renderers.py` 스텁 생성
    - _Requirements: 8.1_

  - [x] 1.3 PyInstaller spec 파일 생성
    - `todo-app.spec` 파일을 onefile 모드, console=False 옵션으로 구성
    - 진입점을 `src/my_app/main.py`로 설정
    - _Requirements: 8.4_

  - [x] 1.4 테스트 디렉토리 구조 생성
    - `tests/conftest.py` 생성 (공통 fixture 스텁)
    - `tests/test_file_handler.py` 스텁 생성
    - `tests/test_renderers.py` 스텁 생성
    - `tests/test_drop_zone.py` 스텁 생성
    - `tests/test_viewer.py` 스텁 생성
    - _Requirements: 8.3_

- [x] 2. 파일 검증 모듈 구현 (file_handler.py)
  - [x] 2.1 FileFormat, FileInfo, FileValidationError 및 상수 정의
    - `FileFormat` Enum 정의 (PNG, JPG, PDF, SVG)
    - `FileInfo` frozen dataclass 정의 (path, format, size)
    - `FileValidationError` 예외 클래스 정의
    - `SUPPORTED_EXTENSIONS`, `MAX_FILE_SIZE` 상수 정의
    - _Requirements: 2.3, 7.3_

  - [x] 2.2 detect_format 함수 구현
    - 파일 확장자를 기반으로 `FileFormat`을 결정
    - 대소문자 무관하게 확장자 매칭
    - 지원하지 않는 확장자에 대해 `FileValidationError` 발생 ("지원하지 않는 파일 형식입니다")
    - _Requirements: 2.3_

  - [x] 2.3 validate_file 함수 구현
    - 파일 존재 여부 확인 (I/O 오류 시 "파일을 읽을 수 없습니다: [파일명]")
    - 파일 크기 확인 (100MB 초과 시 "파일 크기가 너무 큽니다 (최대 100MB)")
    - `detect_format` 호출하여 형식 검증
    - 검증 성공 시 `FileInfo` 반환
    - _Requirements: 2.2, 2.3, 7.1, 7.3_

  - [ ]* 2.4 Property 테스트: 비지원 확장자 거부
    - **Property 2: Unsupported Extension Rejection**
    - hypothesis를 사용하여 임의의 비지원 확장자 문자열 생성 후 `detect_format` 호출 시 `FileValidationError` 발생 확인
    - **Validates: Requirements 2.3**

  - [ ]* 2.5 Property 테스트: 파일 크기 초과 거부
    - **Property 4: File Size Limit Enforcement**
    - hypothesis를 사용하여 100MB 초과 크기의 임시 파일 생성 후 `validate_file` 호출 시 `FileValidationError` 발생 확인
    - **Validates: Requirements 7.3**

  - [ ]* 2.6 file_handler 단위 테스트 작성
    - 각 지원 형식(.png, .jpg, .jpeg, .pdf, .svg)에 대한 `detect_format` 정상 동작 테스트
    - 대소문자 혼합 확장자(.PNG, .Jpg) 처리 테스트
    - 존재하지 않는 파일 경로에 대한 오류 처리 테스트
    - 파일 크기 경계값(100MB 정확히, 100MB+1) 테스트
    - _Requirements: 2.3, 7.1, 7.3_

- [x] 3. Checkpoint - 파일 검증 모듈 확인
  - ruff, mypy 검사 통과 확인
  - 모든 테스트 통과 확인
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. 렌더링 모듈 구현 (renderers.py)
  - [x] 4.1 RenderError 예외 및 scale_pixmap 함수 구현
    - `RenderError` 예외 클래스 정의
    - `scale_pixmap` 함수 구현: `Qt.AspectRatioMode.KeepAspectRatio`로 종횡비 유지 축소
    - 원본이 display_size보다 작으면 원본 크기 유지
    - _Requirements: 3.3, 4.2, 5.2_

  - [ ]* 4.2 Property 테스트: 종횡비 보존 축소
    - **Property 1: Aspect Ratio Preservation**
    - hypothesis를 사용하여 임의의 (width, height, display_width, display_height) 조합으로 `scale_pixmap` 호출 후 종횡비 보존 및 크기 제한 확인
    - **Validates: Requirements 3.3, 4.2, 5.2**

  - [x] 4.3 render_image 함수 구현 (PNG/JPG)
    - `QPixmap`으로 PNG/JPG 이미지 로드
    - 로드 실패 시 `RenderError` 발생 ("이미지 파일이 손상되었습니다: [파일명]")
    - `scale_pixmap`으로 display_size에 맞게 축소
    - _Requirements: 3.1, 3.2, 3.3, 7.2_

  - [x] 4.4 render_pdf 함수 구현
    - PyMuPDF(fitz)로 PDF 첫 페이지를 `page.get_pixmap()`으로 변환
    - QImage → QPixmap 변환
    - 렌더링 실패 시 `RenderError` 발생 ("PDF 파일을 열 수 없습니다")
    - `scale_pixmap`으로 display_size에 맞게 축소
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 4.5 render_svg 함수 구현
    - `QSvgRenderer`로 SVG 로드
    - `QPainter`를 사용하여 QPixmap에 렌더링
    - 렌더링 실패 시 `RenderError` 발생 ("SVG 파일을 열 수 없습니다")
    - `scale_pixmap`으로 display_size에 맞게 축소
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 4.6 render_file 디스패치 함수 구현
    - `FileInfo.format`에 따라 적절한 렌더러 함수 호출
    - PNG/JPG → `render_image`, PDF → `render_pdf`, SVG → `render_svg`
    - _Requirements: 3.1, 3.2, 4.1, 5.1_

  - [ ]* 4.7 renderers 단위 테스트 작성
    - 테스트용 PNG/JPG 파일 렌더링 성공 테스트
    - 테스트용 PDF 파일 첫 페이지 렌더링 성공 테스트
    - 테스트용 SVG 파일 렌더링 성공 테스트
    - 손상된 파일에 대한 `RenderError` 발생 테스트
    - `scale_pixmap` 축소 동작 단위 테스트
    - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 5.1, 5.2, 5.3, 7.2_

- [x] 5. Checkpoint - 렌더링 모듈 확인
  - ruff, mypy 검사 통과 확인
  - 모든 테스트 통과 확인
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. DropZone 위젯 구현 (drop_zone.py)
  - [x] 6.1 DropZone 클래스 기본 구조 구현
    - `QLabel` 상속, `file_dropped` Signal(str) 정의
    - `setAcceptDrops(True)` 설정
    - 초기 안내 메시지 표시: "파일을 여기에 드래그 앤 드롭하세요 (PNG, JPG, PDF, SVG)"
    - 텍스트 중앙 정렬, 스타일 설정
    - _Requirements: 1.3_

  - [x] 6.2 드래그 앤 드롭 이벤트 핸들러 구현
    - `dragEnterEvent`: URL 포함 시 수락, 시각적 피드백(테두리 강조) 표시
    - `dragLeaveEvent`: 시각적 피드백 제거
    - `dropEvent`: 첫 번째 파일 경로만 추출하여 `file_dropped` 시그널 emit
    - 여러 파일 드롭 시 첫 번째 파일만 처리
    - _Requirements: 2.1, 2.2, 2.4_

  - [ ]* 6.3 Property 테스트: 다중 파일 드롭 시 첫 번째 파일만 선택
    - **Property 3: First File Selection**
    - hypothesis를 사용하여 임의 길이의 파일 경로 목록 생성 후 첫 번째 파일만 선택되는지 확인
    - **Validates: Requirements 2.4**

  - [x] 6.4 display_pixmap, show_error, show_placeholder 메서드 구현
    - `display_pixmap`: QPixmap을 QLabel에 표시
    - `show_error`: 오류 메시지를 빨간색 텍스트로 표시
    - `show_placeholder`: 초기 안내 메시지로 복원
    - _Requirements: 1.3, 7.1, 7.2_

  - [ ]* 6.5 DropZone 위젯 테스트 작성 (pytest-qt)
    - 초기 안내 메시지 표시 확인
    - 드래그 진입/이탈 시 시각적 피드백 확인
    - 드롭 이벤트 시 `file_dropped` 시그널 발생 확인
    - _Requirements: 1.3, 2.1, 2.2, 2.4_

- [x] 7. Viewer 메인 윈도우 구현 (viewer.py)
  - [x] 7.1 Viewer 클래스 기본 구조 구현
    - `QMainWindow` 상속
    - 윈도우 크기 800x600, 제목 "Image & Document Viewer" 설정
    - `DropZone`을 중앙 위젯으로 설정
    - `file_dropped` 시그널을 `_on_file_dropped` 슬롯에 연결
    - _Requirements: 1.1, 1.2_

  - [x] 7.2 _on_file_dropped 및 _render_file 메서드 구현
    - `_on_file_dropped`: `validate_file` 호출 → `_render_file` 호출
    - `_render_file`: `render_file` 호출 → `display_pixmap` 호출
    - `FileValidationError`, `RenderError` 포착하여 `show_error` 호출
    - 원본 QPixmap을 인스턴스 변수에 저장 (리사이즈 대응)
    - _Requirements: 2.2, 2.3, 3.1, 3.2, 4.1, 5.1, 7.1, 7.2_

  - [x] 7.3 _cleanup_previous 및 resizeEvent 구현
    - `_cleanup_previous`: 이전 파일의 QPixmap 리소스 해제
    - `resizeEvent`: 저장된 원본 QPixmap을 새 크기에 맞게 `scale_pixmap` 재호출
    - _Requirements: 3.4, 6.1, 6.2_

  - [ ]* 7.4 Viewer 통합 테스트 작성 (pytest-qt)
    - 윈도우 크기(800x600) 및 제목 확인
    - 파일 교체 동작 확인
    - 윈도우 리사이즈 시 이미지 재조정 확인
    - 오류 발생 시 오류 메시지 표시 확인
    - _Requirements: 1.1, 1.2, 3.4, 6.1, 6.2_

- [x] 8. 애플리케이션 진입점 구현 (main.py)
  - [x] 8.1 main 함수 구현 및 연결
    - `QApplication` 인스턴스 생성
    - `Viewer` 윈도우 생성 및 `show()` 호출
    - `sys.exit(app.exec())`로 이벤트 루프 실행
    - `if __name__ == "__main__"` 블록 추가
    - _Requirements: 1.1, 1.2, 1.3_

- [x] 9. Final Checkpoint - 전체 통합 확인
  - ruff 린트 검사 통과 확인
  - mypy strict 모드 타입 검사 통과 확인
  - 모든 pytest 테스트 통과 확인
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- `*` 표시된 태스크는 선택 사항이며 빠른 MVP를 위해 건너뛸 수 있습니다
- 각 태스크는 추적 가능성을 위해 특정 요구사항을 참조합니다
- Checkpoint에서 점진적 검증을 수행합니다
- Property 테스트는 보편적 정확성 속성을 검증합니다
- 단위 테스트는 구체적인 예제와 에지 케이스를 검증합니다
