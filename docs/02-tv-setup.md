# 2. 電視端設定

## 打開開發人員選項（TCL 的路徑跟原專案寫的不一樣）

原專案寫的是「設定 → 裝置偏好設定 → 關於 → 版本號（Build）連按 7 次」，**TCL Android TV 11 找不到這一項**。正確路徑：

1. 遙控器齒輪鍵或 TCL 鍵常常只叫出 TCL 快捷面板，要再點「設定」或「更多設定」進入完整設定。
2. **設定 → 系統 → 關於**，往下找「**Android TV OS build**」（中文介面可能叫「Android TV 作業系統版本」之類），注意不是「Android 版本：11」那一行。
3. 選中它，遙控器 OK 連按 **7 次**，看到「您現在是開發人員」。
4. 返回，**設定 → 系統 → 開發人員選項** 出現了。

## 打開 USB 偵錯

- 開發人員選項 → **USB 偵錯** 打開。
- 這代 TCL 韌體**沒有另外的「網路偵錯／ADB 偵錯」開關**，只開 USB 偵錯，Wi-Fi 上的 5555 埠就會打開。
- 到「設定 → 網路與網際網路」點目前連線，記下電視的 **IP**（下文寫作 `<tv-ip>`）。

## 第一次連線

```powershell
$env:TV_HOST = '<tv-ip>'
tools\venv\Scripts\python.exe -I tools\tv.py --probe
```

電視會跳出「**允許 USB 偵錯？**」，勾「一律允許這部電腦」再按允許。成功會印出型號與版本，例如：

```
ro.product.model = Smart TV Pro
ro.product.device = BeyondTV4
ro.build.version.release = 11
```

> 注意：`--probe` 與 `getprop` 的完整輸出含序號等識別資訊，分享截圖或貼文時只留型號、Android 版本、韌體版本。

## 確認你的型號與韌體

「Smart TV Pro」是 TCL 好幾個系列共用的名稱，真正要比對的是：

```powershell
tools\venv\Scripts\python.exe -I tools\tv.py "getprop ro.product.name"
tools\venv\Scripts\python.exe -I tools\tv.py "getprop ro.build.fingerprint"
tools\venv\Scripts\python.exe -I tools\tv.py "getprop ro.software.version_id"
tools\venv\Scripts\python.exe -I tools\tv.py "cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME"
```

本指南的 55P737 是 `G03_4K_GB`、`BeyondTV4`、`V8-R51MT05-LF1V620`，首頁是 Google TV（`com.google.android.apps.tv.launcherx`）。
同一組數字的機型（例如原專案 `examples/tcl-55c725`、`tcl-43c645`）可以直接參考同一份清單。
