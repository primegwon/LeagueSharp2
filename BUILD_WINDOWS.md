# Windows 단일 EXE 빌드 가이드 (PyInstaller)

이 문서는 `app.py`를 **설치 없이 더블클릭 실행 가능한 1개 EXE 파일**로 빌드하는 절차입니다.

## 1) 사전 준비

1. Windows PC에 Python 3.10+ 설치
2. 명령 프롬프트(CMD) 또는 PowerShell 실행
3. `app.py`가 있는 폴더로 이동

```powershell
cd C:\path\to\LeagueSharp2
```

## 2) 가상환경(권장) 생성 및 활성화

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

## 3) PyInstaller 설치

```powershell
python -m pip install --upgrade pip
python -m pip install pyinstaller
```

## 4) EXE 1개 파일 빌드

```powershell
pyinstaller --onefile --noconsole --name TestApp app.py
```

- `--onefile`: EXE 1개 파일 생성
- `--noconsole`: GUI 앱 실행 시 콘솔 창 숨김
- `--name TestApp`: 결과 파일명 지정

## 5) 결과물 위치

빌드 완료 후 아래 파일이 생성됩니다.

- 최종 EXE: `dist\TestApp.exe`
- 빌드 중간 파일: `build\`
- 스펙 파일: `TestApp.spec`

직원 배포 시에는 **`dist\TestApp.exe` 파일 하나만 전달**하면 됩니다.

## 6) 실행 테스트 방법

1. `dist\TestApp.exe`를 더블클릭
2. 창이 뜨면 `테스트 버튼` 클릭
3. `버튼이 정상적으로 동작합니다! ✅` 메시지가 보이면 성공

## 7) (선택) 빌드 산출물 정리 후 재빌드

```powershell
rmdir /s /q build
rmdir /s /q dist
del TestApp.spec
pyinstaller --onefile --noconsole --name TestApp app.py
```
