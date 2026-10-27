# 5. 用自己的照片當桌布

## 首頁桌布輪播

新首頁支援一個 `wallpapers/` 資料夾的照片輪播。限制：

- 最多讀 **100 張**、每張 10 MB 以內，檔名只能有英數、`_`、`-`、`.`。
- 會置中裁切成 16:9，所以直式照片會被切掉頭腳。
- 換圖間隔 `wallpaper_rotation_minutes` 的單位是**分鐘**，最短 1 分鐘，而且**只有停在首頁時才計時**（剛設好看起來「沒在輪播」通常是這個原因）。

### 用 `scripts/make_wallpapers.py` 處理照片

需要 Pillow（`python -m pip install pillow`）。

```powershell
python -I <本 repo 路徑>\scripts\make_wallpapers.py "<你的照片資料夾>" my-theme\wallpapers
```

它會：

- 橫式照片全收；照片超過 100 張時，直式照片平均抽樣補滿 100 張。
- 全部縮成 1920×1080；直式照片完整置中，兩側用同一張照片模糊、調暗後的版本填滿，不會裁到人。
- **重新存檔時去掉 EXIF（含 GPS 位置）**，每張壓在約 300 KB 以內。

### 對應的 `config.json` 欄位

```json
"wallpaper": true,
"wallpaper_rotation_minutes": 1,
"wallpaper_order": "shuffle",
"wallpaper_dim": 35,
"wallpaper_true_color": true,
"dock_opacity": 70,
"ambient_glow": false
```

| 欄位 | 說明 |
|---|---|
| `wallpaper_dim` | 照片調暗 %，讓時鐘和按鈕看得清楚 |
| `dock_opacity` | 下方 dock 底板透明度 |
| `wallpaper_true_color` | 32 位元色彩，2 GB RAM 以上的電視才開 |
| `ambient_glow` | **建議 `false`**：預設游標停在哪個 App，背景就泛出那個 App 的顏色（YouTube 紅、Disney 藍），會讓照片色彩怪怪的 |

推送：`powershell -ExecutionPolicy Bypass -File tools\theme.ps1 -TvHost <tv-ip> my-theme`。100 張約 25 MB，再推一次會整批取代，不會越積越多。

## 10 秒一張：Photos 相片螢幕保護（原專案附加程式）

首頁桌布最短 1 分鐘；想要像相框一樣 10 秒換一張，用原專案的 [`addons/photo-screensaver`](https://github.com/Gathin23/cleanyourtv/tree/main/addons/photo-screensaver)：淡入淡出、緩慢推移，電視閒置時自動播放，首頁也會多一個「Photos」磚塊（第一次出現時在電視上按允許）。

```powershell
$env:JAVA_HOME = '<cleanyourtv 路徑>\tools\jdk17'
copy launcher\local.properties addons\photo-screensaver\local.properties
powershell -ExecutionPolicy Bypass -File addons\photo-screensaver\build-and-install.ps1 -TvHost <tv-ip>
powershell -ExecutionPolicy Bypass -File addons\photo-screensaver\sync.ps1 -TvHost <tv-ip> <照片資料夾> -Seconds 10 -Start
```

- 它照**檔名順序**播放，想要隨機就先把檔名打亂（例如用 Python `random.shuffle` 後重新命名成 `p001.jpg`…）。
- 不加 `-IdleMinutes` 就不會改動電視原本的閒置時間。
- 換回原本的螢幕保護：`sync.ps1 -TvHost <tv-ip> -Off`。
- 天氣選項預設關閉；關閉時這個 App 完全不連網。
