# 給 AI 助手的說明（可直接整段複製貼上）

這份文件給任何**能在使用者電腦上執行 shell 指令**的 AI 助手（各家 CLI 編碼助手、有終端機權限的聊天助手都可以），也適合人類逐步照做。
不依賴任何特定助手的功能：所有檢查都用指令輸出判斷，不需要看截圖。

使用方式：把下方兩條「---」之間的內容貼給助手，並把 `<...>` 換成實際值。

---

## 任務

幫我清理家裡的 Android TV／Google TV：停用廠商廣告、推薦內容與數據回傳，（選配）換成開源專案 CleanYourTV 的乾淨首頁，最後關閉網路 ADB。

- 電視品牌與型號（機身背面標籤）：`<品牌 型號>`
- 電視 IP：`<tv-ip>`
- 電腦作業系統：`<Windows / macOS / Linux>`
- 要做到哪一步：`<只去廣告 / 去廣告＋換首頁 / 再加照片桌布>`
- 工具：使用 https://github.com/Gathin23/cleanyourtv 的 `tools/` 與 `launcher/`，**不要自己另寫工具**；先讀它的 `PROMPT.md` 與 `AGENTS.md`。中文指南：https://github.com/ttleecode/cleanyourtv-byTT 的 `docs/`。
- **如果電視是 TCL Android TV 11（`ro.product.device` 是 BeyondTV4 或 `ro.product.name` 是 G03_*），另外讀指南的附錄 A（`docs/appendix-a-tcl-android-tv-11.md`）。**

## 安全規則（不可違反）

1. **只停用、不解除安裝**：一律 `pm disable-user --user 0 <套件>`，一個 shell 呼叫一個套件；不用 `pm uninstall`、不 root、不刷機。每一步都要能用 `tools/restore.sh` 還原。
2. **先備份再動手**：套件清單、已停用清單、`getprop`、`settings list system|secure|global` 存到 `backup/`。
3. **小批停用**：每批 5～12 個，每批後驗證（見下方）；出問題就停下來回報，不要繼續下一批。
4. **家人會用的東西先問我**：串流 App、語音助理、Chromecast、螢幕鏡像、韌體更新器、USB 播放器，用一題勾選題問我，只停我沒勾的。
5. **絕對不停用**：電視與 HDMI／天線輸入的 App 與服務、輸入來源選單、遙控器與藍牙配對、螢幕鍵盤、設定、Play 商店與 Play 服務、Android 核心套件（permission controller、package installer、ext services／shared、module metadata、`com.google.android.overlay.modules*`、`com.android.providers.*`、`com.android.systemui`、`com.android.shell`、`com.android.phone`、`com.android.settings`、`com.android.tv.settings`、`android`）。不確定的套件先 `dumpsys package <名稱>` 看用途，仍不清楚就問我。
6. **工廠／測試套件連開都不要開**（名字含 factory、fac、`mediatek.factorymenu`）。
7. **首頁保護**：新首頁裝好並確認是 Home 之後，才停用原廠首頁。Google TV 上停用設定精靈（`com.google.android.tungsten.setupwraith`）前，先確認 Wi-Fi 不屬於它（見步驟 6）。
8. **電視拒絕時就停**：`pm disable-user` 全部被拒、安裝驗證失敗、SDK 低於 26，不要重試迴圈，直接回報。
9. **結束時關閉 ADB**，並確認 5555 埠已拒絕連線。
10. **隱私**：回報與分享時不要附 IP、Wi-Fi 名稱、序號、帳號。

## 步驟與驗證

以下 `tv` 代表 `tools/venv/bin/python -I tools/tv.py`（Windows：`tools\venv\Scripts\python.exe -I tools\tv.py`），並先設定環境變數 `TV_HOST=<tv-ip>`。

### 1. 準備
- clone 原專案；`python -m venv tools/venv`；`pip install -r tools/requirements.txt`。
- 驗證：venv 的 python 可執行。

### 2. 連線（決策點：請我操作電視）
- 請我打開開發人員選項：在「設定 → 裝置偏好設定（或系統）→ 關於」找**版本號／build 那一行**連按 7 次（名稱依品牌不同，例如「Build」或「Android TV OS build」），再打開 **USB 偵錯**，有「網路偵錯／ADB 偵錯」也打開。
- 執行 `tv --probe`，**事先告訴我**電視會跳「允許 USB 偵錯？」要按允許。
- 5555 埠連不上時，可能只有「無線偵錯」，照原專案 `PROMPT.md` 的配對流程。
- 驗證：輸出含 `ro.build.version.release` 與 `ro.product.model`。

### 3. 辨識機型
- `tv "getprop ro.product.name"`、`tv "getprop ro.product.device"`、`tv "getprop ro.build.fingerprint"`、`tv "getprop ro.build.version.sdk"`、`tv "cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME"`。
- 在原專案 `examples/`（索引 `examples/README.md`）找同品牌、相同 product name／device／韌體的清單；沒有就找最接近的，並告訴我差在哪。
- 驗證：清單中每個套件都在 `tv "pm list packages"` 裡；標出哪些已是停用（`pm list packages -d`）。

### 4. 備份
- 驗證：`backup/` 內有 packages-all、packages-disabled、getprop、settings-system/secure/global，且都非空。

### 5. 分批停用（決策點：先問我勾選題）
- 每批：`tools/disable.sh <清單>`（Windows：`powershell -ExecutionPolicy Bypass -File tools\disable.ps1 -TvHost <tv-ip> <清單>`）。
- 驗證（不需截圖）：
  - 腳本輸出每行都是 `new state: disabled-user`。
  - `tv "pm list packages -d"` 包含本批所有套件。
  - `tv "cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME"` 仍是原本的首頁。
  - `tv "dumpsys activity activities | grep -E 'mResumedActivity|topResumedActivity'"` 有前景畫面。
  - 請我實際確認：首頁正常、Input 鍵能切 HDMI、能看電視。
- 全部批次後 `tv reboot`，等 `tv "getprop sys.boot_completed"` 回 1，再比對 `pm list packages -d`。

### 6. 換首頁（只有我選了才做）
- 需要 JDK 17。**新版 Android Studio 附的 JDK 25 太新**，Gradle 8.9 會報 `Unsupported class file major version 69`；用免安裝版 Temurin 17（核對 api.adoptium.net 的 SHA-256），設 `JAVA_HOME`。Gradle 會自動下載 SDK 34。
- Google TV：停用 setupwraith 前檢查 Wi-Fi 擁有者：`tv "dumpsys wifi | grep -o 'cname=[^ ]*' | sort | uniq -c"` 與 `tv "cmd wifi list-networks"`。全部屬於 `android.uid.system`／`com.android.tv.settings` 才可停用；否則請我先在電視上忘記並重新加入那組 Wi-Fi。
- 安裝：`launcher/build-and-install.sh`（Windows：`launcher\build-and-install.ps1 -TvHost <tv-ip> -HomeKeyService`）。若回報 Home 被 setupwraith 搶走，腳本已自動回滾；停用 setupwraith 後再跑一次。
- 驗證：
  - 輸出有 `Home now resolves to com.gathin.tvhome/.MainActivity`。
  - `tv "dumpsys activity activities | grep mResumedActivity"` 是 `com.gathin.tvhome`。
  - 截圖若是全黑（部分韌體已知現象），改用 `tv "uiautomator dump /data/local/tmp/ui.xml >/dev/null; cat /data/local/tmp/ui.xml; rm -f /data/local/tmp/ui.xml"`，應看到時鐘、日期、「輸入來源」、「設定」等文字。
  - `tv "dumpsys accessibility | grep 'Bound services'"` 不是 `{}`。
- 決策點：問我 dock 要放哪些 App（4～7 個、順序）、哪些遙控器鍵要對應到哪個 App 或 HDMI。
- 遙控器鍵：請我按鍵的同時跑 `tv "getevent -lt"` 讀 scancode，再對照電視 `/system/usr/keylayout/*.kl` 找 keycode；寫進主題 `config.json` 的 `app_keys`（`"<keycode>:<套件>"`，或 `"scan:<scancode>:<套件>"`）與 `settings_key_keycodes`。原專案同品牌 `examples/*/README.md` 常已有代碼表。
- 一鍵切 HDMI：`tv "dumpsys hdmi_control"` 找裝置的 `port_id`，對照 `tv "dumpsys tv_input"` 中 `hdmi_port=<同號>` 的輸入 id，寫成 `"<keycode>:input:<輸入 id>"`。
- 主題用 `tools/theme.sh <資料夾>` 推送。
- **模擬按鍵不能證明遙控器按鍵有效**：請我用實體遙控器逐顆按，並請我長按音量確認還會連續變化。
- 重開機後再驗證 Home 與 `Bound services`。若 `Bound services:{}` 且 `tv "settings get secure accessibility_enabled"` 是 0：把 `enabled_accessibility_services` 先設成空字串、再設回 `com.gathin.tvhome/.HomeKeyService`，並設 `accessibility_enabled 1`。不要 `am force-stop com.gathin.tvhome`。

### 7. 桌布與相片（選配；決策點：問我照片資料夾與換圖間隔）
- 參考指南第 5 章與 `scripts/make_wallpapers.py`（最多 100 張、1920×1080、去除 EXIF/GPS）。`wallpaper_rotation_minutes` 單位是分鐘、最短 1，且只在首頁可見時計時；10 秒一張用原專案 `addons/photo-screensaver`（`-Seconds 10`）。建議 `"ambient_glow": false`。
- 驗證：`tv "ls /sdcard/Android/data/com.gathin.tvhome/files/wallpapers | wc -l"` 等於張數；相片螢幕保護看 sync 腳本最後一行的 `mCurrentDreamName`。

### 8. 收尾（決策點：請我操作電視）
- 請我在電視上：撤銷 USB 偵錯授權 → 關閉 USB 偵錯（與網路偵錯）→ 重開機。
- 驗證：`tools/adb-closed.py <tv-ip>` 回報 closed（exit 0）。
- 交給我：每批清單的位置、還原指令（每批 `restore.sh <清單>`；換回原廠首頁時帶原廠首頁套件名）、韌體更新後用 `tools/check.py <清單> --fix` 重新套用的方法。

---

## 給人類讀者

不用 AI 也可以照上面的步驟手動做，詳細說明在 [README](README.md) 與 [`docs/`](docs/)。
