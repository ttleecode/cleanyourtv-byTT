# CleanYourTV by TT

**任何 Android TV／Google TV** 都能用的中文實戰指南：把廠商廣告、推薦內容、數據回傳關掉，（選配）換成乾淨的 Apple TV 風格首頁，再用自己的照片當桌布。
不綁定任何 AI 助手：可以自己照著做，也可以把 [`AGENT-INSTRUCTIONS.md`](AGENT-INSTRUCTIONS.md) 整段貼給任何能執行 shell 指令的 AI 助手。

> 工具本身來自開源專案 **[Gathin23/cleanyourtv](https://github.com/Gathin23/cleanyourtv)**（MIT 授權），本指南撰寫時對照的版本是 commit `34e1c42`（2026-10-23）。
> 本 repo 只有中文說明、範例與一支桌布腳本，**不含**、也**不修改**原專案程式碼（選配章節附一份未在電視上驗證的 patch，另有警告）。

## 先看這段：它在做什麼、有什麼風險

- 全程透過 Wi-Fi 上的 ADB（Android 除錯通道）操作，**不 root、不刷機、不刪任何 App**。
- 只用 `pm disable-user` 把套件「停用」，一行還原指令就能全部打開回來；電視的「設定 → 應用程式」也能逐一打開。
- 換首頁是裝一個約 480 KB 的小型 launcher，原廠首頁只是停用，隨時可換回來。
- **風險**：停到電視需要的東西，畫面、HDMI、遙控器可能出問題，所以要小批停用、每批都檢查。修改電視軟體可能影響保固，**一切後果自負**；原專案與本指南都依現狀提供、不負任何擔保。
- **支援**：Android TV、Google TV（各品牌電視、電視盒、投影機）。**不支援**：Samsung（Tizen）、LG（webOS）。Fire TV 只能做去廣告那一半。

## 目錄

| 章節 | 內容 |
|---|---|
| [1. 事前準備（Windows）](docs/01-prerequisites.md) | Python、git、Android Studio、JDK 17 的雷 |
| [2. 電視端設定](docs/02-tv-setup.md) | 開發人員選項、USB／網路偵錯、辨識型號 |
| [3. 去廣告（debloat）](docs/03-debloat.md) | 備份、挑最接近的清單、分批停用、重開機驗證 |
| [4. 換新首頁](docs/04-launcher.md) | 編譯安裝、Google TV 設定精靈、遙控器按鍵、一鍵切 HDMI |
| [5. 用自己的照片當桌布](docs/05-wallpaper-photos.md) | 桌布輪播、10 秒一張的相片螢幕保護 |
| [6. 收尾與日常](docs/06-finish-and-faq.md) | 關閉 ADB、快取、手機投影、韌體更新後 |
| [7. 皮克斯風主題（選配）](docs/07-pixar-theme-optional.md) | 照片轉卡通風、滿版按鈕圖、寬按鈕（需改程式） |
| [附錄 A：TCL Android TV 11 實機紀錄](docs/appendix-a-tcl-android-tv-11.md) | 一台 TCL 55P737 從頭做到尾的具體數值、清單與怪癖 |

其他檔案：

- [`AGENT-INSTRUCTIONS.md`](AGENT-INSTRUCTIONS.md)：給任何 AI 助手的完整指令（安全規則、步驟、每步怎麼驗證、哪裡要先問你）。
- [`scripts/make_wallpapers.py`](scripts/make_wallpapers.py)：把照片資料夾轉成電視桌布（最多 100 張、1920×1080、去除 GPS 等拍攝資訊）。
- [`patches/dock_fill_width.diff`](patches/dock_fill_width.diff)：選配的寬按鈕修改，**尚未在電視上驗證**。

## 兩種用法

1. **交給 AI 助手**：把 [`AGENT-INSTRUCTIONS.md`](AGENT-INSTRUCTIONS.md) 「---」之間的內容貼給它，換掉型號、IP 等欄位。原專案自己的 [`PROMPT.md`](https://github.com/Gathin23/cleanyourtv/blob/main/PROMPT.md) 也可以一起給它看。
2. **自己照做**：從第 1 章開始依序做，每一步都附了確認成功的方法。

## 授權

本 repo 的文字與腳本以 MIT 授權釋出。CleanYourTV 原專案版權屬其作者，見其 [LICENSE](https://github.com/Gathin23/cleanyourtv/blob/main/LICENSE)。
文中提到的品牌、App 名稱與商標屬各自所有人，僅作說明用途。
