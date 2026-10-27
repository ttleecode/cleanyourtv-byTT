# 6. 收尾與日常

## 一定要做：關閉 ADB

5555 埠沒有加密，開著時同一個網路的裝置都可能連進電視。全部弄完後：

1. 電視：**設定 → 系統 → 開發人員選項 → 撤銷 USB 偵錯授權**（先做這步）。
2. 關掉 **USB 偵錯**。
3. 重開機。
4. 電腦確認：

```powershell
tools\venv\Scripts\python.exe -I tools\adb-closed.py <tv-ip>
```

看到 `is closed: the TV refused the connection.`（exit 0）才算完成。開發人員選項本身可以留著。以後要再調整，打開 USB 偵錯、重新按一次「允許」就好。

## 快取會不會越積越多？

不會，不用定期清。

- YouTube、Netflix 等 App 會自己控制快取大小；儲存空間不足時 Android 會自動清掉各 App 的快取。
- 重開機或待機**不會**清快取，但也不需要。
- 想手動清一次（不會刪設定或登入）：`tools\tv.py "pm trim-caches 100G"`。看效果用 `dumpsys diskstats` 的 `Data-Free`；同一個輸出裡的 `App Cache Size` 是定期才更新的統計值，不準。
- 已停用的 App（例如原廠首頁、廠商的內容頻道）的快取會留著沒用，清一次就好。

## 手機怎麼投影到電視

手機和電視要連同一個 Wi-Fi（分 2.4G／5G 兩個名稱的話，兩邊要連同一個）。

- **看影片（推薦）**：在 YouTube、Netflix、Disney+ 等 App 裡點右上角的**投放圖示**，選電視。電視自己連網播放，手機變遙控器、可以鎖螢幕。iPhone、Android 都可以。
- **整個畫面鏡像**（看照片）：Android 手機下拉快速設定 →「螢幕投放」／「Smart View」（Samsung）／「無線投影」，或用 Google Home App「投放我的螢幕」。有些電視的 Miracast 開機就在背景待命，電視端不用按任何東西；有些要先在電視上打開「螢幕分享」之類的 App。
- **iPhone**：電視若沒有 AirPlay（多數 Android TV 沒有），iPhone 無法鏡像整個畫面，只能用 App 內投放；有沒有 AirPlay 看電視規格或設定裡有沒有「AirPlay」選項。

## 韌體更新之後

更新會把停用的套件打開、首頁換回原廠的。打開 USB 偵錯後：

```powershell
tools\venv\Scripts\python.exe -I tools\check.py <清單檔>        # 列出被打開的
tools\venv\Scripts\python.exe -I tools\check.py <清單檔> --fix  # 重新套用
```

每一批清單各跑一次。

## 我想全部還原

依第 3、4 章的還原指令，每一批各跑一次 `restore.ps1`；`config.json`／桌布用 `tools\theme.ps1 -TvHost <tv-ip> -Reset` 清掉。
