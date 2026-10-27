# 給 AI 助手的說明（可直接整段複製貼上）

這份文件給任何**能在使用者電腦上執行 shell 指令**的 AI 助手（例如各家的 CLI 編碼助手、有終端機權限的聊天助手），也適合人類逐步照做。
不依賴任何特定助手的專屬功能：所有檢查都用指令輸出判斷，不需要看截圖。

使用方式：把下方「---」之間的內容貼給助手，並把 `<...>` 換成實際值。

---

## 任務

幫我清理家裡的 Android TV／Google TV：停用廠商廣告、推薦內容與數據回傳，（選配）換成開源專案 CleanYourTV 的乾淨首頁，最後關閉網路 ADB。

- 電視型號（機身背面標籤）：`<型號，例 55P737>`
- 電視 IP：`<tv-ip>`
- 電腦作業系統：`<Windows / macOS / Linux>`
- 要做到哪一步：`<只去廣告 / 去廣告＋換首頁>`
- 工具：使用 https://github.com/Gathin23/cleanyourtv 的 `tools/` 與 `launcher/`，**不要自己另寫工具**。參考中文指南：`<本 repo 網址>`（尤其 `docs/` 與 `examples-55p737/`）。

## 安全規則（不可違反）

1. **只停用、不解除安裝**：一律 `pm disable-user --user 0 <套件>`，一次一個套件；不用 `pm uninstall`、不 root、不刷機。每一步都要能用 `tools/restore.sh`（Windows：`restore.ps1`）還原。
2. **先備份再動手**：套件清單、已停用清單、`getprop`、`settings list system|secure|global` 存到 `backup/`。
3. **小批停用**：每批 5～12 個，每批後驗證（見下方），出問題就停下來回報。
4. **家人會用的東西先問我**：串流 App、語音助理、Chromecast、Miracast、韌體更新器、USB 播放器，用一題勾選題問我，只停我沒勾的。
5. **絕對不停用**：電視與 HDMI 輸入（TCL：`com.tcl.tv`、`com.tcl.tvinput`）、遙控器與藍牙配對、螢幕鍵盤、設定、Play 商店與 Play 服務、任何 Android 核心套件（`com.android.*` 的 permission controller、package installer、systemui、shell、settings、providers 等）。不確定的套件先 `dumpsys package <名稱>` 看用途，仍不清楚就問我。
6. **工廠／測試套件連開都不要開**（名字含 factory、fac、`mediatek.factorymenu`）。
7. **首頁保護**：新首頁裝好並確認是 Home 之後，才停用原廠首頁。停用 Google TV 設定精靈（`com.google.android.tungsten.setupwraith`）前，先確認 Wi-Fi 不屬於它（見步驟 6）。
8. **電視拒絕時就停**：`pm disable-user` 全部被拒、安裝驗證失敗、SDK 低於 26，不要重試迴圈，直接回報。
9. **結束時關閉 ADB**，並確認 5555 埠已拒絕連線。
10. **隱私**：回報、截圖、分享清單時不要附 IP、Wi-Fi 名稱、序號、帳號。

## 步驟與驗證

以下 `tv` 代表 `tools/venv/bin/python -I tools/tv.py`（Windows：`tools\venv\Scripts\python.exe -I tools\tv.py`），並先設定環境變數 `TV_HOST=<tv-ip>`。

### 1. 準備
- clone 原專案、建立 venv：`python -m venv tools/venv`，`pip install -r tools/requirements.txt`。
- 驗證：`tools/venv` 內的 python 可執行。

### 2. 連線
- 請我在電視上打開開發人員選項與 USB 偵錯。**TCL Android TV 11 的路徑是「設定 → 系統 → 關於 → Android TV OS build」連按 7 次**，不是「裝置偏好設定 → 版本號」。這代 TCL 只開 USB 偵錯，5555 埠就會開。
- 執行 `tv --probe`，**事先告訴我**電視會跳「允許 USB 偵錯？」要按允許。
- 驗證：輸出含 `ro.build.version.release` 與 `ro.product.model`。

### 3. 辨識機型
- `tv "getprop ro.product.name"`、`tv "getprop ro.build.fingerprint"`、`tv "getprop ro.software.version_id"`、`tv "cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME"`。
- 在原專案 `examples/` 找相同 product name／韌體的清單；TCL `G03_4K_GB`／`V8-R51MT05-*` 可參考 `examples/tcl-55c725`、`tcl-43c645` 與本指南 `examples-55p737/`。
- 驗證：清單中的每個套件都在 `tv "pm list packages"` 裡，且標記哪些已是停用（`pm list packages -d`）。

### 4. 備份
- 驗證：`backup/` 內有 packages-all、packages-disabled、getprop、settings-system/secure/global，且行數大於 0。

### 5. 分批停用（決策點：先問我勾選題）
- 每批：`tools/disable.sh <清單>`（Windows：`powershell -ExecutionPolicy Bypass -File tools\disable.ps1 -TvHost <tv-ip> <清單>`）。
- 驗證（不需截圖）：
  - 腳本輸出每行都是 `new state: disabled-user`。
  - `tv "pm list packages -d"` 包含本批所有套件。
  - `tv "cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME"` 仍回原本的首頁。
  - `tv "dumpsys activity activities | grep -E 'mResumedActivity|topResumedActivity'"` 有前景畫面。
  - 請我實際確認：首頁正常、Input 鍵能切 HDMI、能看電視。
- 全部批次後 `tv reboot`，等 `tv "getprop sys.boot_completed"` 回 1，再比對 `pm list packages -d`。

### 6. 換首頁（只有我選了才做）
- 需要 JDK 17（**Android Studio 附的 JDK 25 太新**，Gradle 8.9 會報 `Unsupported class file major version 69`），設 `JAVA_HOME`；Gradle 會自動下載 SDK 34。
- 停用 setupwraith 前檢查 Wi-Fi 擁有者：`tv "dumpsys wifi | grep -o 'cname=[^ ]*' | sort | uniq -c"` 與 `tv "cmd wifi list-networks"`。全部是 `android.uid.system` 才可停用；否則請我先在電視上忘記並重新加入那組 Wi-Fi。
- 安裝：`launcher/build-and-install.sh`（Windows：`launcher\build-and-install.ps1 -TvHost <tv-ip> -HomeKeyService`）。若回報 Home 被 setupwraith 搶走，腳本會自動回滾；停用 setupwraith 後再跑一次。
- 驗證：
  - 輸出 `Home now resolves to com.gathin.tvhome/.MainActivity`。
  - `tv "dumpsys activity activities | grep mResumedActivity"` 是 `com.gathin.tvhome`。
  - 截圖若是全黑（TCL 已知現象），改用 `tv "uiautomator dump /data/local/tmp/ui.xml >/dev/null; cat /data/local/tmp/ui.xml; rm -f /data/local/tmp/ui.xml"`，應看到時鐘、日期、「輸入來源」、「設定」等文字。
  - `tv "dumpsys accessibility | grep 'Bound services'"` 不是 `{}`。
- 決策點：問我 dock 要放哪些 App（4～7 個、順序）、要不要把某顆遙控器鍵改成切到某個 HDMI。HDMI 的 id 用 `dumpsys hdmi_control`（看 `port_id`）對照 `dumpsys tv_input`（看 `hdmi_port=`）。
- 設定寫在主題資料夾的 `config.json`，用 `tools/theme.sh`（`theme.ps1`）推送。TCL 遙控器 keycode：Netflix 4062、YouTube 4065、Prime 4099、TV 4001、TCL 鍵 4020、齒輪 4077。
- **模擬按鍵不能證明遙控器按鍵有效**：請我用實體遙控器逐顆按。
- 重開機後再驗證一次 Home 與 `Bound services`。若 `Bound services:{}` 且 `settings get secure accessibility_enabled` 是 0：把 `enabled_accessibility_services` 先設成空字串、再設回 `com.gathin.tvhome/.HomeKeyService`，並設 `accessibility_enabled 1`。不要 `am force-stop com.gathin.tvhome`。

### 7. 桌布與相片（選配，決策點：問我照片資料夾與換圖間隔）
- 參考指南第 5 章與 `scripts/make_wallpapers.py`（最多 100 張、1920×1080、去除 EXIF/GPS）。`wallpaper_rotation_minutes` 單位是分鐘、最短 1；要 10 秒一張用原專案 `addons/photo-screensaver`（`-Seconds 10`）。
- 驗證：`tv "ls /sdcard/Android/data/com.gathin.tvhome/files/wallpapers | wc -l"` 等於張數；螢幕保護用 `tv "dumpsys dreams | grep -i current"` 或 sync 腳本最後一行確認。

### 8. 收尾
- 請我在電視上：撤銷 USB 偵錯授權 → 關閉 USB 偵錯 → 重開機。
- 驗證：`tools/adb-closed.py <tv-ip>` 回報 closed（exit 0）。
- 給我：停用清單的位置、還原指令（每批 `restore.sh <清單>`；換回原廠首頁要帶 `com.google.android.apps.tv.launcherx`）、以及韌體更新後用 `tools/check.py <清單> --fix` 重新套用的方法。

---

## 給人類讀者

不用 AI 也可以照上面的步驟手動做，詳細說明在 [README](README.md) 與 [`docs/`](docs/)。
