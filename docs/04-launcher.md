# 4. 換新首頁

前提：第 1 章的 Android Studio 與 JDK 17 已準備好，第 3 章已完成。

## 步驟 1：編譯並安裝

```powershell
$env:JAVA_HOME = '<cleanyourtv 路徑>\tools\jdk17'
powershell -ExecutionPolicy Bypass -File launcher\build-and-install.ps1 -TvHost <tv-ip> -HomeKeyService
```

`-HomeKeyService` 會開啟一個無障礙服務，讓原本只有原廠首頁才接得住的遙控器按鍵（Netflix、YouTube、齒輪）能重新對應。

## 雷：第一次一定失敗，因為設定精靈搶走首頁

Google TV 的設定精靈 `com.google.android.tungsten.setupwraith` 在原廠首頁被停用後會跳出來搶首頁。腳本偵測到首頁不是新的 launcher，就會**自動把原廠首頁打開回來**並報錯：

```
Home resolves to 'com.google.android.tungsten.setupwraith/.RecoveryActivity', not to the new launcher; ... was re-enabled.
```

電視不會壞，照下面處理後再跑一次。

### 停用 setupwraith 之前，先確認 Wi-Fi 不歸它管

如果家裡的 Wi-Fi 是在電視第一次開機設定時存的，它屬於 setupwraith；一停用它，Android 會刪掉那組 Wi-Fi，電視就斷網、ADB 也斷了。

```powershell
tools\venv\Scripts\python.exe -I tools\tv.py "dumpsys wifi | grep -o 'cname=[^ ]*' | sort | uniq -c"
tools\venv\Scripts\python.exe -I tools\tv.py "cmd wifi list-networks"
```

- 全部是 `cname=android.uid.system:1000` → 安全，可以停用。
- 有 setupwraith → 先在電視「設定」裡**忘記**那組 Wi-Fi 再重新加入（就會改屬系統），舊的、不在範圍的也要 `cmd wifi forget-network <id>` 清掉。

然後：

```powershell
powershell -ExecutionPolicy Bypass -File tools\disable.ps1 -TvHost <tv-ip> <本 repo 路徑>\examples-55p737\4-setupwraith.txt
powershell -ExecutionPolicy Bypass -File launcher\build-and-install.ps1 -TvHost <tv-ip> -HomeKeyService
```

看到 `Home now resolves to com.gathin.tvhome/.MainActivity` 就成功了。

## 步驟 2：首頁設定（dock、遙控器按鍵）

設定寫在一個資料夾裡的 `config.json`，用 `tools\theme.ps1` 推上電視，不用重新編譯。範例：[`examples-55p737/config.json`](../examples-55p737/config.json)。

```powershell
mkdir my-theme
copy <本 repo 路徑>\examples-55p737\config.json my-theme\
powershell -ExecutionPolicy Bypass -File tools\theme.ps1 -TvHost <tv-ip> my-theme
```

重點欄位（完整清單見原專案 [`themes/README.md`](https://github.com/Gathin23/cleanyourtv/blob/main/themes/README.md)）：

| 欄位 | 範例 | 說明 |
|---|---|---|
| `dock_apps` | YouTube、Netflix、Disney+、YouTube Music 的套件名 | 下方 dock 由左到右；套件名用 `pm list packages -3` 查 |
| `live_tv_package` | `com.tcl.tv` | TCL 的電視 App |
| `settings_key_keycodes` | `[4077]` | 齒輪鍵開設定 |
| `app_keys` | `"4062:com.netflix.ninja"` | 遙控器按鍵 → App |

### TCL 遙控器按鍵代碼（這台與同韌體 55C725 實測）

| 按鍵 | keycode |
|---|---|
| Netflix | 4062 |
| YouTube | 4065 |
| Prime Video | 4099 |
| TV／節目表 | 4001 |
| TCL 鍵 | 4020 |
| 齒輪（設定） | 4077 |

不同遙控器可能不同，原專案 `examples/tcl-55c725/README.md` 有用 `getevent -lt` 讀 scancode 的方法。

### 一顆鍵直接切到 HDMI（例：PS5）

`app_keys` 的目標可以寫成 `input:<輸入來源 id>`，按下就直接切到那個 HDMI。

1. 找 PS5 接在哪個 HDMI：`tools\tv.py "dumpsys hdmi_control"`，找 `display_name: PlayStation 5` 那行的 `port_id`（這台是 2）。
2. 對照 `tools\tv.py "dumpsys tv_input"` 裡 `hdmi_port=2` 的 id（這台是 `com.tcl.tvinput/.passthroughinput.TvPassThroughService/HW1413744384`，**每台不同，要自己查**）。
3. 挑一顆用不到的鍵，例如 Prime Video：

```json
"app_keys": ["4099:input:com.tcl.tvinput/.passthroughinput.TvPassThroughService/HW1413744384"]
```

另一個不用寫程式的做法：PS5「設定 → 系統 → HDMI → 啟用 HDMI 裝置連結」打開後，按手把 PS 鍵通常電視就會自動切過去；也可以在電視「頻道與輸入 → 輸入」把 HDMI 2 改名「PS5」，新首頁的「輸入來源」選單會顯示這個名字。

## 步驟 3：一定要用真的遙控器測

從電腦送出的模擬按鍵（`input keyevent`）**不會經過**按鍵服務，所以測不出 Netflix／YouTube／齒輪鍵有沒有作用。逐顆實按：首頁鍵、App 鍵、齒輪、Input、音量（長按要能連續變化）、麥克風鍵。

## 已知怪癖

- **新首頁截圖永遠是全黑**（這台固定 10608 bytes）。畫面其實正常，改用元件清單確認：

  ```powershell
  tools\venv\Scripts\python.exe -I tools\tv.py "uiautomator dump /data/local/tmp/ui.xml >/dev/null; cat /data/local/tmp/ui.xml; rm -f /data/local/tmp/ui.xml"
  ```

  看得到時鐘、日期、「輸入來源」、「設定」等字樣就代表首頁有畫出來。

- **重開機後遙控器快捷鍵全失靈、方向鍵正常**：這台第一次重開機後，系統把無障礙總開關 `accessibility_enabled` 改成 0，按鍵服務雖在清單裡卻沒啟動（`dumpsys accessibility` 顯示 `Bound services:{}`）。第二次重開機就正常。再發生時，清空再寫回清單讓它重新綁定：

  ```powershell
  tools\venv\Scripts\python.exe -I tools\tv.py "settings put secure enabled_accessibility_services ''"
  tools\venv\Scripts\python.exe -I tools\tv.py "settings put secure enabled_accessibility_services com.gathin.tvhome/.HomeKeyService"
  tools\venv\Scripts\python.exe -I tools\tv.py "settings put secure accessibility_enabled 1"
  tools\venv\Scripts\python.exe -I tools\tv.py "dumpsys accessibility | grep 'Bound services'"
  ```

  注意不要 `am force-stop com.gathin.tvhome`，那會把按鍵服務關掉。

- 「早安」問候語是小字；首頁換圖只有停在首頁時才計時（見第 5 章）。

## 換回原廠首頁

```powershell
powershell -ExecutionPolicy Bypass -File tools\restore.ps1 -TvHost <tv-ip> <本 repo 路徑>\examples-55p737\4-setupwraith.txt com.google.android.apps.tv.launcherx
```

新首頁 App 會留著，要移除就到電視「設定 → 應用程式」解除安裝。
