# 요구사항 문서

## 소개

기존 PySide6 기반 이미지/문서 뷰어 애플리케이션에 Pan(이동) 기능을 추가한다. 현재 뷰어는 줌인 시 콘텐츠가 DropZone 영역보다 커지면 중앙 부분만 표시되고 가장자리가 잘려 보이지 않는 문제가 있다. 이 기능을 통해 사용자는 마우스 드래그 또는 방향 버튼(상/하/좌/우)을 사용하여 줌인된 콘텐츠의 보이지 않는 영역으로 뷰포트를 이동할 수 있다.

## 용어 정의

- **Viewer**: PySide6 기반 데스크톱 이미지/문서 뷰어 애플리케이션의 메인 윈도우 (QMainWindow)
- **Drop_Zone**: 사용자가 파일을 드래그 앤 드롭하고 콘텐츠를 표시하는 Viewer 내부 위젯 (QLabel)
- **Display_Area**: 파일 내용을 렌더링하여 표시하는 Viewer 내부 영역
- **Zoom_Level**: 현재 적용된 확대/축소 배율 (1.0 = 기본 표시 크기)
- **Pan_Offset**: 뷰포트의 현재 이동 위치를 나타내는 (x, y) 좌표 오프셋 (픽셀 단위, 초기값 (0, 0))
- **Viewport**: Drop_Zone 영역 내에서 사용자에게 실제로 보이는 콘텐츠 영역
- **Rendered_Content**: Zoom_Level이 적용되어 렌더링된 전체 콘텐츠 이미지
- **Title_Panel**: Viewer 상단에 배치되는 패널 위젯으로, 줌 컨트롤과 방향 버튼을 포함한다
- **Pan_Up_Button**: Title_Panel 내에 위치하며, 클릭 시 Viewport를 위로 이동하는 버튼
- **Pan_Down_Button**: Title_Panel 내에 위치하며, 클릭 시 Viewport를 아래로 이동하는 버튼
- **Pan_Left_Button**: Title_Panel 내에 위치하며, 클릭 시 Viewport를 왼쪽으로 이동하는 버튼
- **Pan_Right_Button**: Title_Panel 내에 위치하며, 클릭 시 Viewport를 오른쪽으로 이동하는 버튼
- **Pan_Step**: 방향 버튼 한 번 클릭 시 이동하는 픽셀 수
- **Drag_Pan**: 마우스 왼쪽 버튼을 누른 채 드래그하여 Viewport를 이동하는 동작

## 요구사항

### 요구사항 1: 마우스 드래그를 통한 Pan 이동

**사용자 스토리:** 사용자로서, 줌인된 상태에서 마우스를 드래그하여 콘텐츠의 보이지 않는 영역으로 이동할 수 있기를 원한다. 이를 통해 확대된 이미지의 원하는 부분을 자유롭게 탐색할 수 있다.

#### 인수 조건

1. WHILE Rendered_Content가 Viewport보다 큰 상태에서, WHEN 사용자가 Drop_Zone 위에서 마우스 왼쪽 버튼을 누르면, THE Viewer SHALL 드래그 시작 위치를 기록하고 Drag_Pan 모드를 활성화한다
2. WHILE Drag_Pan 모드가 활성화된 상태에서, WHEN 사용자가 마우스를 이동하면, THE Viewer SHALL 드래그 시작 위치와 현재 마우스 위치의 차이만큼 Pan_Offset을 갱신하고 Viewport를 이동한다
3. WHILE Drag_Pan 모드가 활성화된 상태에서, WHEN 사용자가 마우스 왼쪽 버튼을 놓으면, THE Viewer SHALL Drag_Pan 모드를 비활성화한다
4. WHILE Drag_Pan 모드가 활성화된 상태에서, THE Viewer SHALL 마우스 커서를 닫힌 손 모양(ClosedHandCursor)으로 변경한다
5. WHEN Drag_Pan 모드가 비활성화되면, THE Viewer SHALL 마우스 커서를 기본 화살표 모양으로 복원한다

### 요구사항 2: 방향 버튼을 통한 Pan 이동

**사용자 스토리:** 사용자로서, 방향 버튼(상/하/좌/우)을 클릭하여 줌인된 콘텐츠를 이동할 수 있기를 원한다. 이를 통해 마우스 드래그 없이도 정밀하게 원하는 방향으로 이동할 수 있다.

#### 인수 조건

1. THE Title_Panel SHALL Pan_Up_Button, Pan_Down_Button, Pan_Left_Button, Pan_Right_Button을 포함한다
2. WHEN 사용자가 Pan_Up_Button을 클릭하면, THE Viewer SHALL Pan_Offset의 y값을 Pan_Step만큼 감소시켜 Viewport를 위로 이동한다
3. WHEN 사용자가 Pan_Down_Button을 클릭하면, THE Viewer SHALL Pan_Offset의 y값을 Pan_Step만큼 증가시켜 Viewport를 아래로 이동한다
4. WHEN 사용자가 Pan_Left_Button을 클릭하면, THE Viewer SHALL Pan_Offset의 x값을 Pan_Step만큼 감소시켜 Viewport를 왼쪽으로 이동한다
5. WHEN 사용자가 Pan_Right_Button을 클릭하면, THE Viewer SHALL Pan_Offset의 x값을 Pan_Step만큼 증가시켜 Viewport를 오른쪽으로 이동한다
6. THE Viewer SHALL Pan_Step을 50 픽셀로 설정한다

### 요구사항 3: Pan 오프셋 경계 제한

**사용자 스토리:** 사용자로서, Pan 이동 시 콘텐츠 영역 밖으로 벗어나지 않기를 원한다. 이를 통해 항상 콘텐츠가 보이는 상태를 유지할 수 있다.

#### 인수 조건

1. WHEN Pan_Offset이 변경되면, THE Viewer SHALL Pan_Offset의 x값을 Rendered_Content 너비와 Viewport 너비의 차이의 절반 이내로 제한한다
2. WHEN Pan_Offset이 변경되면, THE Viewer SHALL Pan_Offset의 y값을 Rendered_Content 높이와 Viewport 높이의 차이의 절반 이내로 제한한다
3. WHILE Rendered_Content가 Viewport보다 작거나 같은 상태에서, THE Viewer SHALL Pan_Offset을 (0, 0)으로 유지한다

### 요구사항 4: Pan 오프셋이 적용된 렌더링

**사용자 스토리:** 사용자로서, Pan 이동 후 콘텐츠가 이동된 위치에 맞게 표시되기를 원한다. 이를 통해 이동 결과를 즉시 확인할 수 있다.

#### 인수 조건

1. WHEN Pan_Offset이 변경되면, THE Viewer SHALL Rendered_Content에서 Pan_Offset이 적용된 영역을 잘라내어(crop) Viewport 크기에 맞게 Display_Area에 표시한다
2. WHILE Pan_Offset이 (0, 0)인 상태에서, THE Viewer SHALL Rendered_Content의 중앙 영역을 Display_Area에 표시한다

### 요구사항 5: 줌 변경 시 Pan 오프셋 초기화

**사용자 스토리:** 사용자로서, 줌 레벨이 변경되면 Pan 위치가 중앙으로 돌아가기를 원한다. 이를 통해 줌 변경 후 항상 콘텐츠의 중앙부터 탐색을 시작할 수 있다.

#### 인수 조건

1. WHEN Zoom_Level이 변경되면, THE Viewer SHALL Pan_Offset을 (0, 0)으로 초기화한다

### 요구사항 6: 파일 변경 시 Pan 오프셋 초기화

**사용자 스토리:** 사용자로서, 새 파일을 드롭하면 Pan 위치가 초기 상태로 돌아가기를 원한다. 이를 통해 새 파일을 항상 중앙에서 볼 수 있다.

#### 인수 조건

1. WHEN 새로운 파일이 Drop_Zone에 드롭되면, THE Viewer SHALL Pan_Offset을 (0, 0)으로 초기화한다

### 요구사항 7: 파일 미표시 상태에서의 Pan 이벤트 처리

**사용자 스토리:** 사용자로서, 파일이 표시되지 않은 상태에서 Pan 동작을 시도해도 오류가 발생하지 않기를 원한다. 이를 통해 안정적인 사용 경험을 얻을 수 있다.

#### 인수 조건

1. WHILE 파일이 Display_Area에 표시되지 않은 상태에서, WHEN 사용자가 마우스 드래그를 시도하면, THE Viewer SHALL Pan 동작을 수행하지 않고 이벤트를 무시한다
2. WHILE 파일이 Display_Area에 표시되지 않은 상태에서, WHEN 사용자가 방향 버튼을 클릭하면, THE Viewer SHALL Pan 동작을 수행하지 않는다

### 요구사항 8: 윈도우 리사이즈 시 Pan 오프셋 조정

**사용자 스토리:** 사용자로서, 윈도우 크기가 변경되어도 콘텐츠가 경계 밖으로 벗어나지 않기를 원한다. 이를 통해 리사이즈 후에도 안정적인 표시 상태를 유지할 수 있다.

#### 인수 조건

1. WHEN Viewer 윈도우 크기가 변경되면, THE Viewer SHALL 현재 Pan_Offset을 새로운 Viewport 크기에 맞게 경계 제한을 재적용한다
