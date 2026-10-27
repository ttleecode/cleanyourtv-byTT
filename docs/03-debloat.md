# 3. 去廣告（debloat）

以下指令都在原專案 `cleanyourtv` 資料夾、已設定 `$env:TV_HOST = '<tv-ip>'` 的 PowerShell 裡執行（Git Bash 用 `TV_HOST=<tv-ip> tools/disable.sh ...` 也可以）。

## 步驟 1：先備份

```powershell
$tv = 'tools\venv\Scripts\python.exe'
mkdir backup
& $tv -I tools\tv.py "pm list packages -f"  > backup\packages-all.txt
& $tv -I tools\tv.py "pm list packages -d"  > backup\packages-disabled.txt
& $tv -I tools\tv.py "pm list packages -3"  > backup\packages-user.txt
& $tv -I tools\tv.py "getprop"              > backup\getprop.txt
foreach ($ns in 'system','secure','global') { & $tv -I tools\tv.py "settings list $ns" > backup\settings-$ns.txt }
```

`backup/` 在原專案的 `.gitignore` 裡，不會被誤上傳；裡面有序號，不要分享。`tools/disable.sh` 另外會自動在 `~/.cleanyourtv/` 留一份還原紀錄。

## 步驟 2：挑最接近的清單

到原專案 [`examples/`](https://github.com/Gathin23/cleanyourtv/tree/main/examples) 找型號、`ro.product.name`、韌體版本最接近的資料夾。TCL 有 50 多份。
同韌體 `V8-R51MT05-LF1V620` 的 55P737 直接用了 `examples/tcl-55c725` 的內容。

逐行比對清單裡的套件你的電視有沒有、是不是已停用（例：`pm list packages -f` 裡有沒有這個名字）。

## 步驟 3：依你的使用習慣勾選

停用前先問清楚家裡在用什麼。這台的選擇與理由：

| 保留 | 套件 | 理由 |
|---|---|---|
| Chromecast | `com.google.android.apps.mediashell` | 手機投放要用 |
| Miracast 螢幕鏡像 | `com.tcl.miracast` | 手機鏡像要用 |
| Google 語音助理 | `com.google.android.katniss`、`com.tcl.assistant` | 遙控器麥克風鍵 |
| Google TV 手機遙控服務 | `com.google.android.tv.remote.service` | **安全起見保留**：同韌體清單註明有些 TCL 遙控器的麥克風靠它 |
| 韌體更新 | `com.tcl.versionUpdateApp` | 原專案建議保留 |
| TCL WebView | `com.tcl.android.webview` | 只去廣告不換首頁時保守保留 |
| 齒輪鍵快捷面板 | `com.tcl.dashboard` | 不換首頁時，齒輪鍵靠它 |
| 螢幕保護（ambient） | `com.google.android.apps.tv.dreamx` | 不換首頁時保留 |
| 設定精靈 | `com.google.android.tungsten.setupwraith` | **只有換首頁時才停用**，見第 4 章 |

**絕對不要停用**：`com.tcl.tv`、`com.tcl.tvinput`（HDMI 與電視訊號）、`com.tcl.tcl_bt_rcu_service`、`com.tcl.autopair`（遙控器配對）、`com.tcl.settings`、`com.tcl.inputmethod.international`（螢幕鍵盤）、`com.tcl.providers.config`、`com.tcl.system.server`、`com.tcl.initsetup`，以及任何 `com.android.*` 核心套件、Play 商店與 Play 服務。工廠／測試類套件（名字有 factory、fac）**連開都不要開**。

## 步驟 4：分小批停用，每批截圖

把清單拆成幾個檔案，一次套一批。本 repo 的 [`examples-55p737/`](../examples-55p737/) 就是這台實際用的四批：

| 檔案 | 內容 | 數量 |
|---|---|---|
| `1-ads-telemetry.txt` | TCL 首頁推播、TCL Channel、FAST 頻道、TCL 數據分析、logkit、Google 預裝自動安裝器 | 12 |
| `2-background.txt` | 用不到的背景服務（行事曆同步、WebView 測試瀏覽器、TCL guard／說明書等） | 8 |
| `3-preloads-by-choice.txt` | 依使用者勾選停用的預裝 App（T-Cast、Alexa、USB 播放器、相簿、TCL 瀏覽器等） | 7 |
| `4-setupwraith.txt` | Google TV 設定精靈，**換首頁時才用** | 1 |

```powershell
powershell -ExecutionPolicy Bypass -File tools\disable.ps1 -TvHost <tv-ip> <本 repo 路徑>\examples-55p737\1-ads-telemetry.txt
tools\venv\Scripts\python.exe -I tools\tv.py --screenshot shots\01.png HOME --wait 6
```

每批跑完看截圖：首頁出得來、Input 鍵能切 HDMI、能看電視，才繼續下一批。
看電視或 HDMI 時截圖會是 0 bytes，那是電視的限制，不是壞掉。

> 停用 TCL 的東西拿不掉 Google TV 首頁最上面的「贊助」大橫幅，那是 Google TV 首頁自己的。要拿掉它，只能開 Google 帳戶的「僅限應用程式模式」，或換成第 4 章的新首頁。

## 步驟 5：重開機驗證

```powershell
tools\venv\Scripts\python.exe -I tools\tv.py "reboot"
# 等 1～2 分鐘後
tools\venv\Scripts\python.exe -I tools\tv.py "pm list packages -d"
```

比對清單裡的套件是不是都還在停用名單裡。有些韌體每次開機會自己打開某些套件，這台沒有。

## 還原

```powershell
powershell -ExecutionPolicy Bypass -File tools\restore.ps1 -TvHost <tv-ip> <本 repo 路徑>\examples-55p737\3-preloads-by-choice.txt
```

每一批各跑一次；順序與停用相反最保險。單一 App 打開回來：`tools\tv.py "pm enable <套件名>"`，例如要插隨身碟看影片就 `pm enable com.tcl.ui_mediaCenter`。
