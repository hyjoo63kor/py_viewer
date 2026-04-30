# 요구사항 문서

## 소개

기존 PySide6 기반 이미지/문서 뷰어 애플리케이션에 마우스 휠을 사용한 줌인/줌아웃 기능을 추가한다. 현재 뷰어는 파일을 윈도우 크기에 맞게 자동 축소하여 표시하지만, 사용자가 이미지를 확대하거나 축소할 수 있는 방법이 없다. 이 기능을 통해 사용자는 마우스 휠을 스크롤하여 표시 중인 콘텐츠를 자유롭게 확대/축소할 수 있다. 또한 화면 상단에 타이틀 패널을 배치하여 줌 기능 안내 문구, 줌인/줌아웃 버튼, 현재 줌 배율을 표시함으로써 사용자가 줌 기능을 쉽게 인지하고 활용할 수 있도록 한다.

## 용어 정의

- **Viewer**: PySide6 기반 데스크톱 이미지/문서 뷰어 애플리케이션의 메인 윈도우 (QMainWindow)
- **Drop_Zone**: 사용자가 파일을 드래그 앤 드롭하고 콘텐츠를 표시하는 Viewer 내부 위젯 (QLabel)
- **Display_Area**: 파일 내용을 렌더링하여 표시하는 Viewer 내부 영역
- **Zoom_Level**: 현재 적용된 확대/축소 배율 (1.0 = 원본 크기 대비 기본 표시 크기)
- **Zoom_Step**: 마우스 휠 한 단위 스크롤 시 변경되는 배율 증분값
- **Min_Zoom**: 허용되는 최소 축소 배율
- **Max_Zoom**: 허용되는 최대 확대 배율
- **Renderer**: 각 파일 형식에 맞게 내용을 렌더링하는 모듈
- **Title_Panel**: Viewer 상단에 배치되는 패널 위젯으로, 줌 기능 안내 문구와 줌 컨트롤 버튼을 포함한다
- **Zoom_In_Button**: Title_Panel 내에 위치하며, 클릭 시 콘텐츠를 확대하는 버튼 (+)
- **Zoom_Out_Button**: Title_Panel 내에 위치하며, 클릭 시 콘텐츠를 축소하는 버튼 (-)
- **Zoom_Label**: Title_Panel 내에 위치하며, 현재 Zoom_Level을 백분율로 표시하는 레이블 (예: "100%")

## 요구사항

### 요구사항 1: 마우스 휠 줌인

**사용자 스토리:** 사용자로서, 마우스 휠을 위로 스크롤하면 표시 중인 콘텐츠가 확대되기를 원한다. 이를 통해 이미지나 문서의 세부 사항을 자세히 확인할 수 있다.

#### 인수 조건

1. WHILE 파일이 Display_Area에 표시된 상태에서, WHEN 사용자가 마우스 휠을 위로 스크롤하면, THE Viewer SHALL 현재 Zoom_Level에 Zoom_Step을 곱하여 콘텐츠를 확대한다
2. WHILE Zoom_Level이 Max_Zoom에 도달한 상태에서, WHEN 사용자가 마우스 휠을 위로 스크롤하면, THE Viewer SHALL Zoom_Level을 Max_Zoom으로 유지하고 추가 확대를 수행하지 않는다

### 요구사항 2: 마우스 휠 줌아웃

**사용자 스토리:** 사용자로서, 마우스 휠을 아래로 스크롤하면 표시 중인 콘텐츠가 축소되기를 원한다. 이를 통해 전체 이미지를 한눈에 볼 수 있다.

#### 인수 조건

1. WHILE 파일이 Display_Area에 표시된 상태에서, WHEN 사용자가 마우스 휠을 아래로 스크롤하면, THE Viewer SHALL 현재 Zoom_Level을 Zoom_Step으로 나누어 콘텐츠를 축소한다
2. WHILE Zoom_Level이 Min_Zoom에 도달한 상태에서, WHEN 사용자가 마우스 휠을 아래로 스크롤하면, THE Viewer SHALL Zoom_Level을 Min_Zoom으로 유지하고 추가 축소를 수행하지 않는다

### 요구사항 3: 줌 배율 범위 및 단계

**사용자 스토리:** 사용자로서, 줌 배율이 합리적인 범위 내에서 일정한 단계로 변경되기를 원한다. 이를 통해 예측 가능하고 제어 가능한 줌 경험을 얻을 수 있다.

#### 인수 조건

1. THE Viewer SHALL Zoom_Step을 1.25 (25% 증가/감소)로 설정한다
2. THE Viewer SHALL Min_Zoom을 0.1 (10%)로 설정한다
3. THE Viewer SHALL Max_Zoom을 10.0 (1000%)으로 설정한다
4. THE Viewer SHALL 초기 Zoom_Level을 1.0으로 설정한다

### 요구사항 4: 줌 상태에서의 렌더링

**사용자 스토리:** 사용자로서, 줌 배율이 변경되면 콘텐츠가 해당 배율에 맞게 즉시 다시 렌더링되기를 원한다. 이를 통해 확대/축소 결과를 바로 확인할 수 있다.

#### 인수 조건

1. WHEN Zoom_Level이 변경되면, THE Renderer SHALL 현재 파일을 Zoom_Level이 적용된 크기로 다시 렌더링하여 Display_Area에 표시한다
2. WHILE 줌이 적용된 상태에서, THE Renderer SHALL 콘텐츠의 종횡비를 유지한다
3. WHILE 줌이 적용된 상태에서, WHEN Viewer 윈도우 크기가 변경되면, THE Viewer SHALL 현재 Zoom_Level을 유지하면서 콘텐츠를 새로운 Display_Area 크기에 맞게 재조정한다

### 요구사항 5: 줌 초기화

**사용자 스토리:** 사용자로서, 새 파일을 드롭하면 줌 배율이 초기 상태로 돌아가기를 원한다. 이를 통해 새 파일을 항상 기본 크기로 볼 수 있다.

#### 인수 조건

1. WHEN 새로운 파일이 Drop_Zone에 드롭되면, THE Viewer SHALL Zoom_Level을 1.0으로 초기화한다
2. WHEN 파일 로드 중 오류가 발생하면, THE Viewer SHALL Zoom_Level을 1.0으로 초기화한다

### 요구사항 6: 파일 미표시 상태에서의 휠 이벤트 처리

**사용자 스토리:** 사용자로서, 파일이 표시되지 않은 상태에서 마우스 휠을 스크롤해도 오류가 발생하지 않기를 원한다. 이를 통해 안정적인 사용 경험을 얻을 수 있다.

#### 인수 조건

1. WHILE 파일이 Display_Area에 표시되지 않은 상태에서, WHEN 사용자가 마우스 휠을 스크롤하면, THE Viewer SHALL 줌 동작을 수행하지 않고 이벤트를 무시한다

### 요구사항 7: 타이틀 패널

**사용자 스토리:** 사용자로서, 화면 상단에 줌 기능에 대한 안내 문구와 줌 컨트롤이 표시되기를 원한다. 이를 통해 마우스 휠 줌 기능의 존재를 쉽게 인지하고, 버튼으로도 줌을 조작할 수 있다.

#### 인수 조건

1. THE Viewer SHALL 화면 상단에 Title_Panel을 배치한다
2. THE Title_Panel SHALL 줌 기능 안내 문구 "마우스 휠로 줌인/줌아웃 가능"을 표시한다
3. THE Title_Panel SHALL Zoom_In_Button을 포함한다
4. THE Title_Panel SHALL Zoom_Out_Button을 포함한다
5. THE Title_Panel SHALL Zoom_Label을 포함하여 현재 Zoom_Level을 백분율 형식(예: "100%")으로 표시한다
6. WHEN Zoom_Level이 변경되면, THE Zoom_Label SHALL 변경된 Zoom_Level을 백분율 형식으로 즉시 갱신한다

### 요구사항 8: 줌 버튼 동작

**사용자 스토리:** 사용자로서, 줌인/줌아웃 버튼을 클릭하여 콘텐츠를 확대하거나 축소할 수 있기를 원한다. 이를 통해 마우스 휠 없이도 줌 기능을 사용할 수 있다.

#### 인수 조건

1. WHEN 사용자가 Zoom_In_Button을 클릭하면, THE Viewer SHALL 현재 Zoom_Level에 Zoom_Step을 곱하여 콘텐츠를 확대한다
2. WHEN 사용자가 Zoom_Out_Button을 클릭하면, THE Viewer SHALL 현재 Zoom_Level을 Zoom_Step으로 나누어 콘텐츠를 축소한다
3. WHILE Zoom_Level이 Max_Zoom에 도달한 상태에서, WHEN 사용자가 Zoom_In_Button을 클릭하면, THE Viewer SHALL Zoom_Level을 Max_Zoom으로 유지하고 추가 확대를 수행하지 않는다
4. WHILE Zoom_Level이 Min_Zoom에 도달한 상태에서, WHEN 사용자가 Zoom_Out_Button을 클릭하면, THE Viewer SHALL Zoom_Level을 Min_Zoom으로 유지하고 추가 축소를 수행하지 않는다
5. WHILE 파일이 Display_Area에 표시되지 않은 상태에서, WHEN 사용자가 Zoom_In_Button 또는 Zoom_Out_Button을 클릭하면, THE Viewer SHALL 줌 동작을 수행하지 않는다
