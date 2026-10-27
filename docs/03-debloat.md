# 3. 去廣告（debloat）

以下指令都在原專案 `cleanyourtv` 資料夾、已設定 `$env:TV_HOST = '<tv-ip>'` 的 PowerShell 裡執行（Git Bash 用 `TV_HOST=<tv-ip> tools/disable.sh ...`）。

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

**驗證**：`backup\` 裡六個檔案都有內容。`backup/` 在原專案 `.gitignore` 裡；裡面有序號，不要分享。`tools/disable.sh` 另外會自動在 `~/.cleanyourtv/` 留一份還原紀錄。

## 步驟 2：找最接近的清單

到原專案 [`examples/`](https://github.com/Gathin23/cleanyourtv/tree/main/examples)（索引在 `examples/README.md`）找：

1. 同品牌、`ro.product.name` 或 `ro.product.device` 相同的資料夾，最好連韌體版本（fingerprint 或廠商版本號）都相同。
2. 沒有完全相同的，就找同品牌、同 Android 版本、同首頁 App 的。
3. 都沒有的話，原專案的流程會讓 AI 助手從 `pm list packages` 自己分類；手動做就參考同品牌的清單逐個查。

拿到清單後逐行比對：

```powershell
tools\venv\Scripts\python.exe -I tools\tv.py "pm list packages <關鍵字>"
```

**驗證**：清單中每個套件都在你的電視上（不在的刪掉或註解掉），並記下哪些原本就是停用的（`pm list packages -d`）。

不認識的套件先查用途：`tools\tv.py "dumpsys package <套件名>"`，看它有哪些 activity／service，仍不確定就保留。

## 步驟 3：依家人的使用習慣勾選

停用前先決定這些要不要留：

| 類別 | 常見套件 | 留下的理由 |
|---|---|---|
| Chromecast | `com.google.android.apps.mediashell` | 手機在 App 裡投放 |
| 螢幕鏡像（Miracast） | 各廠商不同，名字常含 `miracast`、`cast` | 手機整個畫面鏡像 |
| 語音助理 | `com.google.android.katniss`（加上廠商自己的） | 遙控器麥克風鍵 |
| Google TV 手機遙控 | `com.google.android.tv.remote.service` | 部分電視的遙控器麥克風靠它，**不確定就留** |
| 韌體更新 | 廠商的 update／ota 類 App | 原專案建議保留 |
| 串流 App | Netflix、YouTube、Disney+… | 有在用就留 |
| USB 播放器、相簿 | 廠商的 media center／gallery | 要插隨身碟看影片就留 |

**絕對不要停用**：

- 電視與 HDMI／天線輸入的 App 與服務（各品牌名稱不同，名字常含 `tv`、`tvinput`、`source`）
- 遙控器與藍牙配對服務（常含 `rcu`、`remote`、`bt`、`pair`）
- 螢幕鍵盤（`inputmethod`）、設定 App、Play 商店、Play 服務
- Android 核心套件：permission controller、package installer、ext services／shared、module metadata、`com.google.android.overlay.modules*`、`com.android.providers.*`（行事曆、聯絡人等少數例外）、`com.android.systemui`、`com.android.shell`、`com.android.phone`、`com.android.settings`、`com.android.tv.settings`、`android`。原專案的 `disable.sh` 會拒絕含這些的清單。
- 名字有 factory、fac、`mediatek.factorymenu` 的工廠／測試套件可以停用，但**連開都不要開**，有些主機板一開就會切到工廠模式。

## 步驟 4：分小批停用

把清單拆成幾個檔案（每批 5～12 個）。建議的分法：

1. 廣告、推薦內容、數據回傳（analytics、bi、logkit、feedback、partner setup、預裝自動安裝器）
2. 用不到的背景服務
3. 依步驟 3 勾掉的預裝 App
4. （換首頁時才做）Google TV 設定精靈，見第 4 章

```powershell
powershell -ExecutionPolicy Bypass -File tools\disable.ps1 -TvHost <tv-ip> <清單檔>
```

**每批的驗證**（不需要截圖）：

- 腳本輸出每行都是 `new state: disabled-user`。
- `tools\tv.py "pm list packages -d"` 包含這批所有套件。
- `tools\tv.py "cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME"` 還是原本的首頁。
- 實際看電視：首頁正常、Input 鍵能切 HDMI、能看電視。

可以截圖時：`tools\tv.py --screenshot shots\01.png HOME --wait 6`。播電視或 HDMI 時截圖常是 0 bytes，那是電視的限制，不是壞掉。

> 停用廠商套件拿不掉 Google TV 首頁本身的「贊助」橫幅與推薦列，那是 Google TV 首頁自己的。要拿掉只能開 Google 帳戶的「僅限應用程式模式」，或換成第 4 章的新首頁。

## 步驟 5：重開機驗證

```powershell
tools\venv\Scripts\python.exe -I tools\tv.py "reboot"
# 等 1～2 分鐘，直到下面這行回 1
tools\venv\Scripts\python.exe -I tools\tv.py "getprop sys.boot_completed"
tools\venv\Scripts\python.exe -I tools\tv.py "pm list packages -d"
```

**驗證**：停用的套件都還在名單裡。有些韌體每次開機會自己把特定套件打開，那種就記在清單註解裡，不用每次重停。

## 還原

```powershell
powershell -ExecutionPolicy Bypass -File tools\restore.ps1 -TvHost <tv-ip> <清單檔>
```

每一批各跑一次，順序與停用相反最保險。單一 App 打開回來：`tools\tv.py "pm enable <套件名>"`。沒有電腦時，電視「設定 → 應用程式 → 顯示系統應用程式」也能逐一啟用。

一個實際例子（四批清單與保留理由）見 [附錄 A](appendix-a-tcl-android-tv-11.md)。
