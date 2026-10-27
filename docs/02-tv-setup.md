# 2. 電視端設定

## 打開開發人員選項

Android 的通則是：在「關於」頁裡找**版本號（build）那一行**，用遙控器 OK 連按 7 次。路徑與名稱依品牌不同：

- 常見路徑：**設定 → 裝置偏好設定 → 關於 → 版本號（Build）**
- 有些品牌放在：**設定 → 系統 → 關於 → Android TV OS build**（中文可能叫「Android TV 作業系統版本」之類）
- 找不到時：在「關於」頁逐行往下看，找含「build」「版本號」「作業系統版本」的那一行；**不是**「Android 版本：11」那一行。
- 遙控器的齒輪鍵或品牌鍵有時只叫出快捷面板，要再點「設定」／「更多設定」才是完整設定。

連按 7 次後會出現「您現在是開發人員」，返回上一層就會看到**開發人員選項**。

## 打開偵錯

- 開發人員選項 → 打開 **USB 偵錯**。
- 如果另外有「網路偵錯」「ADB 偵錯」或「無線偵錯」，也打開。有些韌體只開 USB 偵錯，Wi-Fi 上的 5555 埠就會開；有些（多為新版 Google TV）只提供「無線偵錯」配對碼，見原專案 [`PROMPT.md`](https://github.com/Gathin23/cleanyourtv/blob/main/PROMPT.md) 的 Connect 一節。
- 到「設定 → 網路」點目前連線，記下電視 IP（下文寫作 `<tv-ip>`）。
- 部分電視盒在 USB 偵錯開著時會切斷 USB 供電（USB 喇叭、隨身碟、USB 網卡會失效），建議一次做完。

## 第一次連線

```powershell
$env:TV_HOST = '<tv-ip>'
tools\venv\Scripts\python.exe -I tools\tv.py --probe
```

電視會跳出「**允許 USB 偵錯？**」，勾「一律允許這部電腦」再按允許。

**驗證**：輸出有 `ro.product.model`、`ro.build.version.release` 等欄位。

> `--probe` 與 `getprop` 的完整輸出含序號等識別資訊，分享時只留型號、Android 版本、韌體版本。

## 辨識你的型號與韌體

商品名稱常常是好幾個系列共用的（例如好幾台都回報同一個 `ro.product.model`），真正要比對的是：

```powershell
tools\venv\Scripts\python.exe -I tools\tv.py "getprop ro.product.name"
tools\venv\Scripts\python.exe -I tools\tv.py "getprop ro.product.device"
tools\venv\Scripts\python.exe -I tools\tv.py "getprop ro.build.fingerprint"
tools\venv\Scripts\python.exe -I tools\tv.py "getprop ro.build.version.sdk"
tools\venv\Scripts\python.exe -I tools\tv.py "cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME"
```

- `ro.product.name`／`device`／`fingerprint`：用來在原專案 `examples/` 找同平台的清單（第 3 章）。
- `ro.build.version.sdk`：新首頁需要 26（Android 8.0）以上。
- 最後一行是目前的首頁 App：`com.google.android.apps.tv.launcherx` 是 Google TV 首頁，`com.google.android.tvlauncher` 是舊版 Android TV 首頁，其他則是廠商自己的首頁。

廠商的軟體版本有時另存在 `getprop` 的其他欄位（例如 `ro.software.version_id`），可以用 `getprop | findstr /i version` 找。
