# 요구사항 문서

## 소개

기존 PySide6 기반 이미지/문서 뷰어(SvgViewer)에 두 가지 기능을 추가한다.

1. **Markdown 렌더링**: `.md` 파일을 로드하여 HTML로 변환 후 이미지로 렌더링하여 표시한다.
2. **PDF 멀티 페이지 탐색**: 멀티 페이지 PDF 파일에서 이전/다음 페이지 버튼과 페이지 표시 레이블을 통해 모든 페이지를 탐색할 수 있도록 한다.

## 용어 사전

- **Viewer**: 메인 윈도우. TitlePanel과 DropZone을 포함하는 QMainWindow 기반 위젯
- **TitlePanel**: Viewer 상단에 배치되는 컨트롤 패널. 열기, 줌, 방향 버튼 등을 포함
- **DropZone**: 파일 드래그 앤 드롭을 수신하고 렌더링된 콘텐츠를 표시하는 QLabel 기반 위젯
- **File_Handler**: 파일 경로 검증, 확장자 감지, FileFormat 열거형을 관리하는 모듈
- **Renderer**: 파일 형식별 렌더링 로직을 담당하는 모듈. render_file 함수를 통해 QPixmap을 반환
- **FileFormat**: 지원하는 파일 형식을 나타내는 열거형 (PNG, JPG, PDF, SVG)
- **FileInfo**: 검증된 파일의 경로, 형식, 크기를 담는 데이터 클래스
- **Page_Label**: TitlePanel에 표시되는 현재 페이지 번호와 총 페이지 수 레이블 (예: "1/5")
- **Prev_Button**: TitlePanel에 배치되는 이전 페이지 이동 버튼 ("◁")
- **Next_Button**: TitlePanel에 배치되는 다음 페이지 이동 버튼 ("▷")
- **Markdown_Library**: Python `markdown` 라이브러리. Markdown 텍스트를 HTML로 변환하는 데 사용

## 요구사항

### 요구사항 1: Markdown 파일 형식 지원

**사용자 스토리:** 개발자로서, `.md` 파일을 뷰어에서 열어 렌더링된 Markdown 콘텐츠를 확인하고 싶다.

#### 인수 기준

1. THE File_Handler SHALL 지원 확장자 목록에 `.md`를 포함한다.
2. THE FileFormat SHALL Markdown 파일을 나타내는 `MD` 값을 포함한다.
3. WHEN `.md` 확장자를 가진 파일이 제공되면, THE File_Handler SHALL FileFormat.MD를 반환한다.

### 요구사항 2: Markdown 렌더링

**사용자 스토리:** 개발자로서, Markdown 파일을 열었을 때 서식이 적용된 상태로 보고 싶다.

#### 인수 기준

1. WHEN FileFormat.MD 파일이 렌더링 요청되면, THE Renderer SHALL Markdown 텍스트를 HTML로 변환한다.
2. WHEN HTML 변환이 완료되면, THE Renderer SHALL 변환된 HTML을 이미지(QPixmap)로 렌더링하여 반환한다.
3. THE Renderer SHALL Markdown 렌더링 시 제목, 목록, 코드 블록, 강조, 링크 등 기본 Markdown 문법을 지원한다.
4. IF Markdown 파일 읽기에 실패하면, THEN THE Renderer SHALL RenderError 예외를 발생시킨다.
5. THE Renderer SHALL Markdown 렌더링 결과를 display_size에 맞게 스케일링한다.

### 요구사항 3: Markdown 파일 드래그 앤 드롭 및 열기 지원

**사용자 스토리:** 사용자로서, Markdown 파일을 드래그 앤 드롭하거나 열기 다이얼로그에서 선택하여 열고 싶다.

#### 인수 기준

1. THE DropZone SHALL 안내 메시지에 MD 형식을 포함하여 표시한다.
2. THE Viewer SHALL 파일 열기 다이얼로그의 필터에 `*.md` 확장자를 포함한다.
3. WHEN `.md` 파일이 드래그 앤 드롭되면, THE Viewer SHALL 해당 파일을 렌더링하여 표시한다.

### 요구사항 4: PDF 총 페이지 수 감지

**사용자 스토리:** 사용자로서, PDF 파일을 열었을 때 총 페이지 수를 알고 싶다.

#### 인수 기준

1. WHEN PDF 파일이 로드되면, THE Renderer SHALL 해당 PDF의 총 페이지 수를 반환한다.
2. THE Viewer SHALL PDF 파일의 총 페이지 수와 현재 페이지 번호를 상태로 관리한다.

### 요구사항 5: PDF 페이지 탐색 UI

**사용자 스토리:** 사용자로서, PDF 파일의 페이지를 이전/다음 버튼으로 탐색하고 현재 위치를 확인하고 싶다.

#### 인수 기준

1. WHEN PDF 파일이 로드되면, THE TitlePanel SHALL Prev_Button("◁"), Page_Label, Next_Button("▷")을 표시한다.
2. THE Page_Label SHALL 현재 페이지 번호와 총 페이지 수를 "n/N" 형식으로 표시한다 (예: "1/5").
3. WHILE 현재 페이지가 첫 번째 페이지인 동안, THE TitlePanel SHALL Prev_Button을 비활성화한다.
4. WHILE 현재 페이지가 마지막 페이지인 동안, THE TitlePanel SHALL Next_Button을 비활성화한다.
5. WHEN PDF가 아닌 파일이 로드되면, THE TitlePanel SHALL Prev_Button, Page_Label, Next_Button을 숨긴다.
6. WHEN 파일이 로드되지 않은 상태에서, THE TitlePanel SHALL Prev_Button, Page_Label, Next_Button을 숨긴다.

### 요구사항 6: PDF 페이지 이동

**사용자 스토리:** 사용자로서, 이전/다음 버튼을 클릭하여 PDF 페이지를 이동하고 싶다.

#### 인수 기준

1. WHEN Next_Button이 클릭되면, THE Viewer SHALL 현재 페이지 번호를 1 증가시키고 해당 페이지를 렌더링한다.
2. WHEN Prev_Button이 클릭되면, THE Viewer SHALL 현재 페이지 번호를 1 감소시키고 해당 페이지를 렌더링한다.
3. WHEN 페이지가 변경되면, THE Viewer SHALL 줌 레벨을 기본값(100%)으로 초기화한다.
4. WHEN 페이지가 변경되면, THE Viewer SHALL Pan 오프셋을 (0, 0)으로 초기화한다.
5. WHEN 페이지가 변경되면, THE Page_Label SHALL 갱신된 페이지 번호를 반영한다.

### 요구사항 7: PDF 특정 페이지 렌더링

**사용자 스토리:** 개발자로서, PDF의 특정 페이지를 지정하여 렌더링할 수 있어야 한다.

#### 인수 기준

1. WHEN 페이지 번호가 지정되면, THE Renderer SHALL 해당 페이지를 이미지(QPixmap)로 변환하여 반환한다.
2. IF 지정된 페이지 번호가 유효 범위(1 ~ 총 페이지 수)를 벗어나면, THEN THE Renderer SHALL RenderError 예외를 발생시킨다.
3. THE Renderer SHALL 지정된 페이지의 렌더링 결과를 display_size에 맞게 스케일링한다.

### 요구사항 8: 단일 페이지 PDF 처리

**사용자 스토리:** 사용자로서, 단일 페이지 PDF를 열었을 때 불필요한 페이지 탐색 UI가 표시되지 않기를 원한다.

#### 인수 기준

1. WHEN 총 페이지 수가 1인 PDF 파일이 로드되면, THE TitlePanel SHALL Prev_Button, Page_Label, Next_Button을 숨긴다.
