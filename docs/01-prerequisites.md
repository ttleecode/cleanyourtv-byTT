# 1. 事前準備（Windows）

電腦要和電視連**同一個 Wi-Fi**（或同一個區網）。

## 只去廣告：需要 Python 與 git

1. 安裝 [Python 3](https://www.python.org/downloads/)（安裝時勾 Add to PATH）與 [Git for Windows](https://git-scm.com/download/win)。
2. 下載原專案並建立 Python 環境（PowerShell）：

```powershell
git clone https://github.com/Gathin23/cleanyourtv
cd cleanyourtv
python -m venv tools\venv
tools\venv\Scripts\python.exe -m pip install -r tools\requirements.txt
```

原專案的 `tools/tv.py` 是純 Python 的 ADB 用戶端，不需要另外裝 adb。

## 要換新首頁：另外需要 Android Studio＋JDK 17

### Android Studio

- 有些 Windows 11 Home 沒有 `winget`（會出現 `winget is not recognized`）。不用修，直接到 **https://developer.android.com/studio** 下載安裝檔。
- 用預設選項安裝（會裝在 `C:\Program Files\Android\Android Studio`），打開一次：選 Standard、左側每份授權都點 Accept、等 SDK 下載完再關掉。

### 雷：Android Studio 附的 Java 太新

新版 Android Studio 附的是 JDK 25，但 launcher 用的 Gradle 8.9 跑不動，編譯會直接失敗：

```
BUG! exception in phase 'semantic analysis' ... Unsupported class file major version 69
```

解法：另外準備一份**免安裝版 Eclipse Temurin JDK 17**，只給編譯用，不影響 Android Studio。

1. 到 [adoptium.net](https://adoptium.net/temurin/releases/?version=17&os=windows&arch=x64&package=jdk) 下載 Windows x64 的 JDK 17 **zip**（約 190 MB）。
2. **核對 SHA-256**：官方 API `https://api.adoptium.net/v3/assets/latest/17/hotspot?architecture=x64&image_type=jdk&os=windows&vendor=eclipse` 會列出 `checksum`，和 `certutil -hashfile <檔名>.zip SHA256` 的結果一致才用。
3. 解壓到例如 `cleanyourtv\tools\jdk17`（解壓後裡面要直接看到 `bin\java.exe`）。
4. 編譯前在同一個 PowerShell 視窗設定：

```powershell
$env:JAVA_HOME = '<cleanyourtv 路徑>\tools\jdk17'
```

### SDK 34

launcher 需要 Android SDK platform 34。Android Studio 首次設定可能只裝了更新的版本（例如 36、37），沒關係：**第一次編譯時 Gradle 會自動下載缺的 SDK 34**（幾十 MB）。

## 檢查清單

- [ ] `python --version`、`git --version` 有回應
- [ ] `cleanyourtv\tools\venv\Scripts\python.exe` 存在
- [ ] （換首頁才需要）`<JDK17>\bin\java.exe -version` 顯示 17.x
