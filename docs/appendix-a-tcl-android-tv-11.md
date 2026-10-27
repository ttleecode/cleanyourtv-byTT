# 附錄 A：TCL Android TV 11 實機紀錄（55P737）

一台 TCL 55P737 從頭做到尾的具體數值、清單與怪癖。同平台（`G03_4K_GB`／`BeyondTV4`／`V8-R51MT05-*`）的機型可以直接參考；其他機型請照主章節的通用步驟。

## 機型識別

| 項目 | 值 |
|---|---|
| `ro.product.model` | Smart TV Pro（TCL 好幾個系列共用這個名字） |
| `ro.product.device` | BeyondTV4 |
| `ro.product.name` | G03_4K_GB |
| `ro.board.platform` | rtd288o（Realtek） |
| Android | 11（SDK 30），build `RP1A.200622.001`，fingerprint 結尾 `AR09` |
| 廠商軟體版本（`ro.software.version_id`） | `V8-R51MT05-LF1V620` |
| 原廠首頁 | Google TV（`com.google.android.apps.tv.launcherx`） |
| RAM | 2 GB |
| 最接近的原專案清單 | `examples/tcl-55c725`（**同一版韌體**），其次 `tcl-43c645` |

## 電視端

- 開發人員選項：**設定 → 系統 → 關於 → 「Android TV OS build」連按 7 次**。這台沒有「裝置偏好設定 → 版本號」。
- 齒輪鍵／TCL 鍵只叫出 TCL 快捷面板，要再點「設定」才是完整設定。
- 這代韌體**沒有另外的網路偵錯開關**：只開 USB 偵錯，Wi-Fi 上的 5555 埠就會開；`ro.adb.secure=1`，第一次連線會跳「允許 USB 偵錯？」。

## 四批停用清單

檔案在 [`../appendix/tcl-55p737/`](../appendix/tcl-55p737/)，全部實際套用、重開機後都維持停用（共 28 個，加上換首頁時停用的原廠首頁共 29 個）：

| 檔案 | 內容 | 數量 |
|---|---|---|
| [`1-ads-telemetry.txt`](../appendix/tcl-55p737/1-ads-telemetry.txt) | TCL 首頁推播、TCL Channel、FAST 頻道、TCL 數據分析、logkit、Google 預裝自動安裝器 | 12 |
| [`2-background.txt`](../appendix/tcl-55p737/2-background.txt) | 行事曆同步、WebView 測試瀏覽器、TCL guard／按鍵說明／使用者協議、TalkBack、電子說明書 | 8 |
| [`3-preloads-by-choice.txt`](../appendix/tcl-55p737/3-preloads-by-choice.txt) | 使用者勾掉的：T-Cast、Alexa、USB 播放器、TCL 相簿、Google TV 影片、TCL 瀏覽器、Play 遊戲 | 7 |
| [`4-setupwraith.txt`](../appendix/tcl-55p737/4-setupwraith.txt) | Google TV 設定精靈（換首頁時才停用） | 1 |

刻意保留：

| 保留 | 套件 | 理由 |
|---|---|---|
| Chromecast | `com.google.android.apps.mediashell` | 使用者有在用 |
| Miracast | `com.tcl.miracast` | 使用者有在用；開機就在背景待命 |
| Google 語音 | `com.google.android.katniss`、`com.tcl.assistant` | 使用者有在用 |
| YouTube Music | `com.google.android.youtube.tvmusic` | 使用者有在用 |
| Google TV 手機遙控服務 | `com.google.android.tv.remote.service` | 同韌體清單註明部分 TCL 遙控器麥克風靠它 |
| 韌體更新 | `com.tcl.versionUpdateApp` | 建議保留 |
| TCL WebView | `com.tcl.android.webview` | 保守保留（55C725 停用後也沒事） |
| 齒輪鍵快捷面板 | `com.tcl.dashboard` | 只去廣告不換首頁時，齒輪鍵靠它 |
| Ambient 螢幕保護 | `com.google.android.apps.tv.dreamx` | 保留 |
| TCL 帳號 | `com.tcl.usercenter` | 保留 |
| 絕對不停用 | `com.tcl.tv`、`com.tcl.tvinput`、`com.tcl.tcl_bt_rcu_service`、`com.tcl.autopair`、`com.tcl.settings`、`com.tcl.inputmethod.international`、`com.tcl.providers.config`、`com.tcl.system.server`、`com.tcl.initsetup`、`com.tcl.suspension`（Input 鍵的快捷面板）、`com.tcl.xian.StartandroidService` | 電視、HDMI、遙控器、鍵盤、設定 |

> 停用 TCL 套件後，Google TV 首頁上方的「贊助」大橫幅仍在（那是 Google TV 首頁自己的），換新首頁後才消失。

## 換首頁

- 第一次跑 `build-and-install.ps1` 一定失敗：首頁被 `setupwraith/.RecoveryActivity` 搶走，腳本自動回滾。
- Wi-Fi 檢查結果：所有已存網路都是 `cname=android.uid.system:1000`，停用 setupwraith 沒有斷網。
- 用 `-HomeKeyService`；沒有遇到長按音量變一格的問題。

### 首頁設定

[`../appendix/tcl-55p737/config.json`](../appendix/tcl-55p737/config.json)（dock、遙控器、桌布設定都在裡面）。`live_tv_package` 是 `com.tcl.tv`。

### 遙控器 keycode（這台與同韌體 55C725 實測）

| 按鍵 | keycode | TCL 名稱 |
|---|---|---|
| Netflix | 4062 | `TCL_NETFLIX` |
| YouTube | 4065 | `TCL_YOUTUBE` |
| Prime Video | 4099 | `TCL_PRIMEVIDEO` |
| TV／節目表 | 4001 | `TCL_EPG` |
| TCL 鍵 | 4020 | `TCL_QUICK_MENU` |
| 齒輪（設定） | 4077 | `TCL_SET` |

Input、首頁、方向、音量鍵不需設定就能用。

### PS5 一鍵切換

- `dumpsys hdmi_control`：`display_name: PlayStation 5 ... port_id: 2`。
- `dumpsys tv_input`：`hdmi_port=2` 對應 `com.tcl.tvinput/.passthroughinput.TvPassThroughService/HW1413744384`（id 每台不同，要自己查）。
- 把用不到的 Prime Video 鍵改成切 HDMI 2：

```json
"app_keys": ["4099:input:com.tcl.tvinput/.passthroughinput.TvPassThroughService/HW1413744384"]
```

## 實測怪癖

- **新首頁截圖永遠全黑**，大小固定 10608 bytes；用 `uiautomator dump` 確認，看得到「早安」、時鐘、日期、「輸入來源」、Wi-Fi 名稱、「設定」等文字。
- **第一次重開機後 `accessibility_enabled` 變成 0**，`Bound services:{}`，App 快捷鍵全失靈；第二次重開機就恢復正常。修法見第 4 章「可能遇到的怪癖」。
- 單純 `settings put secure accessibility_enabled 1` 不會立刻重新綁定，要「清空再寫回」清單或重開機。
- 編譯：Android Studio 附的 JDK 25 會讓 Gradle 8.9 報 `Unsupported class file major version 69`，改用 Temurin JDK 17 後編譯成功（約 2.5 分鐘，APK 482 KB）。
- 安裝傳檔：`b64push.py` 的 md5 比對通過（同平台的 43C645 曾失敗）。

## 桌布與相片

- 100 張照片處理後約 25 MB；電視可用空間約 6.3 GB。
- 首頁桌布最短 1 分鐘換一張；10 秒一張用 `addons/photo-screensaver`，電視原本閒置 10 分鐘（`screen_off_timeout` 600000）進螢幕保護，沿用未改。
- 背景光（`ambient_glow`）會讓照片泛紅泛藍，關掉。

## 收尾

- `pm trim-caches 100G` 後可用空間多了約 310 MB（主要是停用的原廠首頁 150 MB 與 TCL Channel 37 MB 的快取）。
- 撤銷授權、關 USB 偵錯、重開機後，`tools/adb-closed.py` 回報 `refused`（exit 0）。
- 這台沒有 AirPlay；iPhone 只能用 App 內投放。
