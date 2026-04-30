# 요구사항 문서

## 소개

PySide6 기반 데스크톱 이미지/문서 뷰어 애플리케이션이다. 사용자가 PNG, JPG, PDF, SVG 파일을 드래그 앤 드롭으로 애플리케이션 창에 놓으면 해당 파일의 내용을 화면에 표시한다. 프로젝트는 uv로 관리하고, PyInstaller로 단일 실행 파일로 빌드하며, ruff(린터), mypy(strict 타입체커), pytest(테스트)를 사용한다.

## 용어 정의

- **Viewer**: PySide6 기반 데스크톱 이미지/문서 뷰어 애플리케이션의 메인 윈도우
- **Drop_Zone**: 사용자가 파일을 드래그 앤 드롭할 수 있는 Viewer 내부 영역
- **Display_Area**: 파일 내용을 렌더링하여 표시하는 Viewer 내부 영역
- **Supported_Format**: PNG, JPG(JPEG), PDF, SVG 파일 형식을 포함하는 지원 파일 형식 집합
- **Renderer**: 각 파일 형식에 맞게 내용을 렌더링하는 모듈

## 요구사항

### 요구사항 1: 애플리케이션 윈도우 표시

**사용자 스토리:** 사용자로서, 애플리케이션을 실행하면 파일을 드롭할 수 있는 윈도우가 표시되기를 원한다. 이를 통해 파일을 쉽게 열 수 있다.

#### 인수 조건

1. THE Viewer SHALL 실행 시 기본 크기(800x600 픽셀)의 윈도우를 화면에 표시한다
2. THE Viewer SHALL 윈도우 제목을 "Image & Document Viewer"로 표시한다
3. WHILE 파일이 로드되지 않은 상태에서, THE Drop_Zone SHALL "파일을 여기에 드래그 앤 드롭하세요 (PNG, JPG, PDF, SVG)" 안내 메시지를 표시한다

### 요구사항 2: 드래그 앤 드롭 파일 수신

**사용자 스토리:** 사용자로서, 파일을 윈도우에 드래그 앤 드롭하여 파일을 열고 싶다. 이를 통해 파일 탐색기에서 직접 파일을 열 수 있다.

#### 인수 조건

1. WHEN 사용자가 Supported_Format 파일을 Drop_Zone 위로 드래그하면, THE Drop_Zone SHALL 시각적 피드백(테두리 강조 등)을 표시하여 드롭 가능 상태임을 알린다
2. WHEN 사용자가 Supported_Format 파일을 Drop_Zone에 드롭하면, THE Viewer SHALL 해당 파일을 수신하고 렌더링 프로세스를 시작한다
3. WHEN 사용자가 Supported_Format이 아닌 파일을 Drop_Zone에 드롭하면, THE Viewer SHALL "지원하지 않는 파일 형식입니다" 오류 메시지를 표시한다
4. WHEN 사용자가 여러 파일을 동시에 Drop_Zone에 드롭하면, THE Viewer SHALL 첫 번째 파일만 수신하고 나머지는 무시한다

### 요구사항 3: PNG 및 JPG 이미지 렌더링

**사용자 스토리:** 사용자로서, PNG 또는 JPG 이미지를 드롭하면 화면에 표시되기를 원한다. 이를 통해 이미지를 빠르게 확인할 수 있다.

#### 인수 조건

1. WHEN PNG 파일이 수신되면, THE Renderer SHALL 해당 PNG 이미지를 Display_Area에 렌더링한다
2. WHEN JPG(JPEG) 파일이 수신되면, THE Renderer SHALL 해당 JPG 이미지를 Display_Area에 렌더링한다
3. WHILE 이미지가 Display_Area보다 큰 경우, THE Renderer SHALL 이미지의 종횡비를 유지하면서 Display_Area에 맞게 축소하여 표시한다
4. WHEN Viewer 윈도우 크기가 변경되면, THE Renderer SHALL 현재 표시 중인 이미지를 새로운 Display_Area 크기에 맞게 재조정한다

### 요구사항 4: PDF 파일 렌더링

**사용자 스토리:** 사용자로서, PDF 파일을 드롭하면 첫 번째 페이지가 화면에 표시되기를 원한다. 이를 통해 PDF 내용을 빠르게 미리 볼 수 있다.

#### 인수 조건

1. WHEN PDF 파일이 수신되면, THE Renderer SHALL 해당 PDF의 첫 번째 페이지를 이미지로 변환하여 Display_Area에 렌더링한다
2. WHILE PDF 페이지 이미지가 Display_Area보다 큰 경우, THE Renderer SHALL 종횡비를 유지하면서 Display_Area에 맞게 축소하여 표시한다
3. IF PDF 파일이 손상되었거나 읽을 수 없는 경우, THEN THE Viewer SHALL "PDF 파일을 열 수 없습니다" 오류 메시지를 Display_Area에 표시한다

### 요구사항 5: SVG 파일 렌더링

**사용자 스토리:** 사용자로서, SVG 파일을 드롭하면 화면에 표시되기를 원한다. 이를 통해 벡터 그래픽을 빠르게 확인할 수 있다.

#### 인수 조건

1. WHEN SVG 파일이 수신되면, THE Renderer SHALL 해당 SVG를 Display_Area에 렌더링한다
2. WHILE SVG 콘텐츠가 Display_Area보다 큰 경우, THE Renderer SHALL 종횡비를 유지하면서 Display_Area에 맞게 축소하여 표시한다
3. IF SVG 파일이 손상되었거나 읽을 수 없는 경우, THEN THE Viewer SHALL "SVG 파일을 열 수 없습니다" 오류 메시지를 Display_Area에 표시한다

### 요구사항 6: 파일 교체

**사용자 스토리:** 사용자로서, 이미 파일이 표시된 상태에서 새 파일을 드롭하면 기존 파일이 새 파일로 교체되기를 원한다. 이를 통해 여러 파일을 연속으로 확인할 수 있다.

#### 인수 조건

1. WHILE 파일이 Display_Area에 표시된 상태에서, WHEN 사용자가 새로운 Supported_Format 파일을 Drop_Zone에 드롭하면, THE Viewer SHALL 기존 표시 내용을 제거하고 새 파일을 렌더링한다
2. WHEN 새 파일이 성공적으로 렌더링되면, THE Viewer SHALL 이전 파일에 사용된 메모리 리소스를 해제한다

### 요구사항 7: 오류 처리

**사용자 스토리:** 사용자로서, 파일 로드 중 오류가 발생하면 명확한 오류 메시지를 보고 싶다. 이를 통해 문제를 파악할 수 있다.

#### 인수 조건

1. IF 파일 읽기 중 I/O 오류가 발생하면, THEN THE Viewer SHALL "파일을 읽을 수 없습니다: [파일명]" 오류 메시지를 Display_Area에 표시한다
2. IF 이미지 파일이 손상되어 디코딩할 수 없는 경우, THEN THE Viewer SHALL "이미지 파일이 손상되었습니다: [파일명]" 오류 메시지를 Display_Area에 표시한다
3. IF 파일 크기가 100MB를 초과하는 경우, THEN THE Viewer SHALL "파일 크기가 너무 큽니다 (최대 100MB)" 오류 메시지를 표시하고 파일 로드를 중단한다

### 요구사항 8: 프로젝트 구조 및 빌드 설정

**사용자 스토리:** 개발자로서, 표준화된 프로젝트 구조와 빌드 설정을 원한다. 이를 통해 일관된 개발 환경을 유지할 수 있다.

#### 인수 조건

1. THE 프로젝트 SHALL src/my_app/ 디렉토리 구조를 따르며 __init__.py와 main.py를 포함한다
2. THE pyproject.toml SHALL Python 3.12 버전을 지정하고 PySide6 의존성을 포함한다
3. THE pyproject.toml SHALL ruff(린터), mypy(strict 모드 타입체커), pytest(테스트) 설정을 포함한다
4. THE todo-app.spec SHALL PyInstaller onefile 모드와 console=False 옵션으로 빌드를 구성한다
5. THE 프로젝트 SHALL uv를 패키지 관리자로 사용하여 의존성을 관리한다
