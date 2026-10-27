# 4. 換新首頁

前提：第 1 章的 Android Studio 與 JDK 17 已準備好，第 3 章已完成，且 `ro.build.version.sdk` ≥ 26。

## 步驟 1：確認電視接受自行安裝的 App

少數（多為中國市場）機型會拒絕任何側載，或拒絕非原廠簽章的首頁 App。原專案 `examples/` 的清單開頭會註明；若安裝回報 `INSTALL_FAILED_VERIFICATION_FAILURE`，就停在去廣告那一半，不要重試。

## 步驟 2：編譯並安裝

```powershell
$env:JAVA_HOME = '<cleanyourtv 路徑>\tools\jdk17'
powershell -ExecutionPolicy Bypass -File launcher\build-and-install.ps1 -TvHost <tv-ip> -HomeKeyService
```

- `-HomeKeyService`：開啟一個無障礙服務，讓原本只有原廠首頁才接得住的遙控器按鍵（App 快捷鍵、設定鍵）能重新對應。Google TV 遙控器的 Input 鍵若失效，改用或加上 `-InputKeyService`。
- 腳本會先確認新首頁真的成為 Home，才停用原廠首頁；不成功就自動把原廠首頁打開回來。

**驗證**：

- 輸出最後有 `Home now resolves to com.gathin.tvhome/.MainActivity`。
- `tools\tv.py "dumpsys activity activities | grep mResumedActivity"` 是 `com.gathin.tvhome`。

### Google TV：設定精靈會搶首頁

在 Google TV 上，原廠首頁一停用，設定精靈 `com.google.android.tungsten.setupwraith` 就會跳出來搶首頁，腳本會報：

```
Home resolves to 'com.google.android.tungsten.setupwraith/.RecoveryActivity', not to the new launcher; ... was re-enabled.
```

電視不會壞（腳本已回滾）。處理方式是停用 setupwraith，**但要先確認 Wi-Fi 不歸它管**：在電視第一次開機設定時存的 Wi-Fi 屬於 setupwraith，一停用它，Android 會刪掉那組 Wi-Fi，電視就斷網、ADB 也斷了。

```powershell
tools\venv\Scripts\python.exe -I tools\tv.py "dumpsys wifi | grep -o 'cname=[^ ]*' | sort | uniq -c"
tools\venv\Scripts\python.exe -I tools\tv.py "cmd wifi list-networks"
```

- 全部是 `cname=android.uid.system:1000`（或 `com.android.tv.settings`）→ 安全。
- 有 setupwraith → 先在電視「設定」裡**忘記**那組 Wi-Fi 再重新加入，不在範圍的舊網路也用 `cmd wifi forget-network <id>` 清掉，重查一次。
- 用有線網路的電視不受影響。

然後把 setupwraith 放進一個單獨的清單、用 `disable.ps1` 停用，再跑一次 `build-and-install.ps1`。原專案的 `disable.sh` 也會自己做這個檢查。

## 步驟 3：首頁設定（dock、遙控器按鍵）

設定寫在一個資料夾裡的 `config.json`，用 `tools\theme.ps1` 推上電視，不用重新編譯：

```powershell
mkdir my-theme
# 在 my-theme\config.json 寫入設定
powershell -ExecutionPolicy Bypass -File tools\theme.ps1 -TvHost <tv-ip> my-theme
```

常用欄位（完整清單見原專案 [`themes/README.md`](https://github.com/Gathin23/cleanyourtv/blob/main/themes/README.md)）：

```json
{
  "dock_apps": ["com.google.android.youtube.tv", "com.netflix.ninja", "com.disney.disneyplus"],
  "live_tv_package": "<你的電視 App 套件名>",
  "columns": 4,
  "settings_key_keycodes": [],
  "app_keys": []
}
```

- `dock_apps`：下方 dock 由左到右（4～7 個）；套件名用 `pm list packages -3` 查。
- `live_tv_package`：廠商的電視 App，可從 `dumpsys tv_input` 或原專案同品牌清單的註解得知。

### 找出遙控器按鍵的代碼

廠商的 App 快捷鍵、設定鍵常常送出廠商自訂的代碼，原廠首頁停用後就沒反應。查法：

1. **讀按鍵**：`tools\tv.py "getevent -lt"`，按一下遙控器按鍵，記下 scancode（`EV_KEY` 後面那個值）。按 Ctrl+C 結束。
2. **查對應的 keycode 名稱**：遙控器的對應表在電視的 `/system/usr/keylayout/*.kl`（藍牙遙控器常是 `Generic.kl`，紅外線遙控器是廠商自己的檔名），例如 `tools\tv.py "grep -h '<scancode>' /system/usr/keylayout/*.kl"`。
3. **寫進設定**：
   - App 鍵：`"app_keys": ["<keycode>:<套件名>"]`，keycode 可以是數字或 `KEYCODE_...` 名稱。
   - 多支遙控器共用同一個 keycode、或 keycode 是 `KEYCODE_UNKNOWN` 時，改用 scancode：`"scan:<scancode>:<套件名>"`。
   - 設定鍵：`"settings_key_keycodes": [<keycode>]`。
4. 原專案 `examples/` 裡同品牌的 `README.md` 常已經查好代碼表，可以先參考。

### 一顆鍵直接切到某個 HDMI（例如遊戲機）

`app_keys` 的目標可以寫 `input:<輸入來源 id>`，按下就直接切到那個 HDMI：

1. 找裝置接在哪個 HDMI：`tools\tv.py "dumpsys hdmi_control"`，在 CEC devices 裡找到裝置名稱（例如 `PlayStation 5`），記下 `port_id`。
2. 對照 `tools\tv.py "dumpsys tv_input"`：找 `hdmi_port=<同一個數字>` 的那一項，它的 id（`.../HW<數字>` 之類）就是輸入來源 id。
3. 挑一顆用不到的鍵：`"app_keys": ["<keycode>:input:<輸入來源 id>"]`。

不用寫設定的替代法：很多遊戲機有「HDMI 裝置連結」，開啟後按手把電源鍵電視會自動切過去；也可以在電視「輸入來源」設定裡幫 HDMI 改名，新首頁的「輸入來源」選單會顯示這個名字。

## 步驟 4：用真的遙控器測

從電腦送的模擬按鍵（`input keyevent`）**不會經過**按鍵服務，測不出快捷鍵有沒有作用。請逐顆實按：首頁、各 App 鍵、設定鍵、Input、音量（長按要能連續變化）、麥克風。

**驗證**按鍵服務有在運作：

```powershell
tools\venv\Scripts\python.exe -I tools\tv.py "dumpsys accessibility | grep 'Bound services'"
```

不是 `{}` 才對。

> 有些韌體在按鍵服務開啟後，長按音量會變成一次只動一格。這是取捨：要快捷鍵就接受，要連續音量就不開服務。詳見原專案 `docs/TROUBLESHOOTING.md`。

## 可能遇到的怪癖（部分韌體）

- **新首頁的截圖是全黑**：有些韌體截不到這個首頁的畫面（每次都是同樣大小的黑圖）。畫面其實正常，改用元件清單確認：

  ```powershell
  tools\venv\Scripts\python.exe -I tools\tv.py "uiautomator dump /data/local/tmp/ui.xml >/dev/null; cat /data/local/tmp/ui.xml; rm -f /data/local/tmp/ui.xml"
  ```

  看得到時鐘、日期、「輸入來源」、「設定」等字樣，就代表首頁有畫出來。

- **重開機後快捷鍵全失靈、方向鍵正常**：有些韌體開機時把無障礙總開關 `accessibility_enabled` 改成 0，按鍵服務雖在清單裡卻沒啟動（`Bound services:{}`）。清空再寫回清單，讓系統重新綁定：

  ```powershell
  tools\venv\Scripts\python.exe -I tools\tv.py "settings put secure enabled_accessibility_services ''"
  tools\venv\Scripts\python.exe -I tools\tv.py "settings put secure enabled_accessibility_services com.gathin.tvhome/.HomeKeyService"
  tools\venv\Scripts\python.exe -I tools\tv.py "settings put secure accessibility_enabled 1"
  ```

  不要 `am force-stop com.gathin.tvhome`，那會把按鍵服務一起關掉。

- **重裝首頁後按鍵服務沒綁**：同上的清空再寫回即可。
- 重開機後務必再驗證一次 Home 與 `Bound services`。

## 換回原廠首頁

```powershell
powershell -ExecutionPolicy Bypass -File tools\restore.ps1 -TvHost <tv-ip> <停用 setupwraith 的清單> <原廠首頁套件名>
```

Google TV 的原廠首頁是 `com.google.android.apps.tv.launcherx`，舊版 Android TV 是 `com.google.android.tvlauncher`。新首頁 App 會留著，要移除就到「設定 → 應用程式」解除安裝。

實際例子（遙控器代碼表、遊戲機 HDMI 設定、上述怪癖的實測）見 [附錄 A](appendix-a-tcl-android-tv-11.md)。
