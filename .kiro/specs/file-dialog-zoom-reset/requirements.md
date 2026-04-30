# 요구사항 문서

## 소개

기존 PySide6 기반 이미지/문서 뷰어 애플리케이션에 두 가지 기능을 추가한다. 첫째, QFileDialog를 사용한 파일 열기 다이얼로그 기능을 추가하여 드래그 앤 드롭 외에도 메뉴/버튼을 통해 파일을 선택하고 열 수 있도록 한다. 둘째, 줌 리셋 버튼을 추가하여 현재 줌 레벨을 100%(기본값)로 즉시 초기화할 수 있도록 한다. 두 기능 모두 TitlePanel에 버튼을 배치하여 사용자가 쉽게 접근할 수 있도록 한다.

## 용어 정의

- **Viewer**: PySide6 기반 데스크톱 이미지/문서 뷰어 애플리케이션의 메인 윈도우 (QMainWindow)
- **Title_Panel**: Viewer 상단에 배치되는 패널 위젯으로, 안내 문구와 줌/방향 컨트롤 버튼을 포함한다
- **Drop_Zone**: 사용자가 파일을 드래그 앤 드롭하고 콘텐츠를 표시하는 Viewer 내부 위젯 (QLabel)
- **Display_Area**: 파일 내용을 렌더링하여 표시하는 Viewer 내부 영역
- **File_Dialog**: QFileDialog를 사용하여 파일 시스템에서 파일을 선택할 수 있는 시스템 대화 상자
- **Open_Button**: Title_Panel 내에 위치하며, 클릭 시 File_Dialog를 여는 버튼 ("열기")
- **Zoom_Reset_Button**: Title_Panel 내에 위치하며, 클릭 시 Zoom_Level을 1.0(100%)으로 초기화하는 버튼
- **Zoom_Level**: 현재 적용된 확대/축소 배율 (1.0 = 원본 크기 대비 기본 표시 크기)
- **Zoom_Label**: Title_Panel 내에 위치하며, 현재 Zoom_Level을 백분율로 표시하는 레이블
- **Supported_Extensions**: 애플리케이션이 지원하는 파일 확장자 집합 (.png, .jpg, .jpeg, .pdf, .svg)
- **File_Handler**: 파일 경로를 검증하고 FileInfo를 반환하는 모듈
- **Pan_Offset**: 현재 적용된 Pan(이동) 오프셋 좌표

## 요구사항

### 요구사항 1: 파일 열기 다이얼로그 표시

**사용자 스토리:** 사용자로서, 버튼을 클릭하여 파일 선택 대화 상자를 열 수 있기를 원한다. 이를 통해 드래그 앤 드롭 없이도 파일 시스템에서 원하는 파일을 탐색하고 선택할 수 있다.

#### 인수 조건

1. THE Title_Panel SHALL Open_Button을 포함한다
2. WHEN 사용자가 Open_Button을 클릭하면, THE Viewer SHALL File_Dialog를 표시한다
3. THE File_Dialog SHALL Supported_Extensions에 해당하는 파일만 필터로 표시한다
4. THE File_Dialog SHALL 필터 표시 문자열을 "이미지/문서 파일 (*.png *.jpg *.jpeg *.pdf *.svg)" 형식으로 설정한다

### 요구사항 2: 파일 열기 다이얼로그를 통한 파일 로드

**사용자 스토리:** 사용자로서, 파일 선택 대화 상자에서 파일을 선택하면 해당 파일이 뷰어에 표시되기를 원한다. 이를 통해 드래그 앤 드롭과 동일한 결과를 얻을 수 있다.

#### 인수 조건

1. WHEN 사용자가 File_Dialog에서 파일을 선택하고 확인하면, THE Viewer SHALL 선택된 파일을 File_Handler를 통해 검증한다
2. WHEN File_Handler가 파일 검증에 성공하면, THE Viewer SHALL 해당 파일을 Display_Area에 렌더링하여 표시한다
3. WHEN File_Handler가 파일 검증에 성공하면, THE Viewer SHALL Zoom_Level을 1.0으로 초기화한다
4. WHEN File_Handler가 파일 검증에 성공하면, THE Viewer SHALL Pan_Offset을 (0, 0)으로 초기화한다
5. IF File_Handler가 파일 검증에 실패하면, THEN THE Viewer SHALL Display_Area에 오류 메시지를 표시한다

### 요구사항 3: 파일 열기 다이얼로그 취소 처리

**사용자 스토리:** 사용자로서, 파일 선택 대화 상자에서 취소를 누르면 현재 표시 중인 콘텐츠가 그대로 유지되기를 원한다. 이를 통해 실수로 대화 상자를 열어도 기존 작업에 영향이 없다.

#### 인수 조건

1. WHEN 사용자가 File_Dialog에서 취소 버튼을 클릭하거나 대화 상자를 닫으면, THE Viewer SHALL 현재 Display_Area의 콘텐츠를 변경하지 않는다
2. WHEN 사용자가 File_Dialog에서 취소하면, THE Viewer SHALL 현재 Zoom_Level을 유지한다
3. WHEN 사용자가 File_Dialog에서 취소하면, THE Viewer SHALL 현재 Pan_Offset을 유지한다

### 요구사항 4: 줌 리셋 버튼 배치

**사용자 스토리:** 사용자로서, 줌 레벨을 100%로 즉시 되돌릴 수 있는 버튼이 있기를 원한다. 이를 통해 확대/축소 후 기본 보기 상태로 빠르게 복귀할 수 있다.

#### 인수 조건

1. THE Title_Panel SHALL Zoom_Reset_Button을 Zoom_Label 옆에 배치한다
2. THE Zoom_Reset_Button SHALL "리셋" 텍스트를 표시한다

### 요구사항 5: 줌 리셋 동작

**사용자 스토리:** 사용자로서, 줌 리셋 버튼을 클릭하면 줌 레벨이 100%로 초기화되고 콘텐츠가 기본 크기로 다시 표시되기를 원한다. 이를 통해 여러 번 줌 조작 후에도 한 번의 클릭으로 원래 상태로 돌아갈 수 있다.

#### 인수 조건

1. WHEN 사용자가 Zoom_Reset_Button을 클릭하면, THE Viewer SHALL Zoom_Level을 1.0으로 설정한다
2. WHEN 사용자가 Zoom_Reset_Button을 클릭하면, THE Viewer SHALL Pan_Offset을 (0, 0)으로 초기화한다
3. WHEN 사용자가 Zoom_Reset_Button을 클릭하면, THE Viewer SHALL 현재 파일을 Zoom_Level 1.0으로 다시 렌더링하여 Display_Area에 표시한다
4. WHEN 사용자가 Zoom_Reset_Button을 클릭하면, THE Zoom_Label SHALL "100%"로 갱신한다

### 요구사항 6: 줌 리셋 — 파일 미표시 상태 처리

**사용자 스토리:** 사용자로서, 파일이 표시되지 않은 상태에서 줌 리셋 버튼을 클릭해도 오류가 발생하지 않기를 원한다. 이를 통해 안정적인 사용 경험을 얻을 수 있다.

#### 인수 조건

1. WHILE 파일이 Display_Area에 표시되지 않은 상태에서, WHEN 사용자가 Zoom_Reset_Button을 클릭하면, THE Viewer SHALL 줌 리셋 동작을 수행하지 않는다

### 요구사항 7: 줌 리셋 — 이미 100% 상태 처리

**사용자 스토리:** 사용자로서, 줌 레벨이 이미 100%인 상태에서 줌 리셋 버튼을 클릭해도 불필요한 재렌더링이 발생하지 않기를 원한다. 이를 통해 효율적인 동작을 보장받을 수 있다.

#### 인수 조건

1. WHILE Zoom_Level이 1.0인 상태에서, WHEN 사용자가 Zoom_Reset_Button을 클릭하면, THE Viewer SHALL 재렌더링을 수행하지 않는다
