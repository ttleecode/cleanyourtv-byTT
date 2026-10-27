# CleanYourTV 中文實戰指南（以 TCL Android TV 11 為例）

把 Android TV／Google TV 的廣告、推薦內容、數據回傳關掉，再換成乾淨的 Apple TV 風格首頁。
這份指南是一次在 **TCL 55P737（Smart TV Pro）** 上從頭做到尾的完整紀錄，整理成朋友照著做就能完成的步驟，並標出每一個踩過的雷。

> 工具本身來自開源專案 **[Gathin23/cleanyourtv](https://github.com/Gathin23/cleanyourtv)**（MIT 授權），本指南撰寫時對照的版本是 commit `34e1c42`（2026-10-23）。
> 本 repo 只是中文說明與範例，**不含**、也**不修改**原專案的程式碼（選配章節附一份未在電視上驗證的 patch，另有警告）。

## 先看這段：它在做什麼、有什麼風險

- 全程透過 Wi-Fi 上的 ADB（Android 除錯通道）操作，**不 root、不刷機、不刪任何 App**。
- 只用 `pm disable-user` 把套件「停用」，一行還原指令就能全部打開回來；電視的「設定 → 應用程式」也能逐一打開。
- 換首頁是裝一個約 480 KB 的小型 launcher，原廠首頁只是停用，隨時可換回來。
- **風險**：停到電視需要的東西，畫面、HDMI、遙控器可能出問題，所以要小批停用、每批都檢查。修改電視軟體可能影響保固，**一切後果自負**；原專案與本指南都依現狀提供、不負任何擔保。
- **支援**：Android TV、Google TV。**不支援**：Samsung（Tizen）、LG（webOS）。Fire TV 只能做去廣告那一半。

## 目錄

| 章節 | 內容 |
|---|---|
| [1. 事前準備（Windows）](docs/01-prerequisites.md) | Python、git、Android Studio、JDK 17 的雷 |
| [2. 電視端設定](docs/02-tv-setup.md) | 開發人員選項、USB 偵錯（TCL 路徑不一樣） |
| [3. 去廣告（debloat）](docs/03-debloat.md) | 備份、挑清單、分批停用、重開機驗證 |
| [4. 換新首頁](docs/04-launcher.md) | 編譯安裝、setupwraith、遙控器按鍵、一鍵切 HDMI |
| [5. 用自己的照片當桌布](docs/05-wallpaper-photos.md) | 桌布輪播、相片螢幕保護 10 秒一張 |
| [6. 收尾與日常](docs/06-finish-and-faq.md) | 關閉 ADB、快取、手機投影、韌體更新後 |
| [7. 皮克斯風主題（選配）](docs/07-pixar-theme-optional.md) | 照片轉皮克斯風、滿版按鈕圖、寬按鈕（需改程式） |

範例檔：

- [`examples-55p737/`](examples-55p737/)：這台 TCL 實際用過的四批停用清單與首頁設定 `config.json`。
- [`scripts/make_wallpapers.py`](scripts/make_wallpapers.py)：把一個照片資料夾轉成電視桌布（最多 100 張、1920×1080、去除 GPS 等拍攝資訊）。
- [`patches/dock_fill_width.diff`](patches/dock_fill_width.diff)：選配的寬按鈕修改，**尚未在電視上驗證**。

## 最快的做法：讓 AI 助手帶你做

**任何能執行 shell 指令的 AI 助手都可以**：把 [`AGENT-INSTRUCTIONS.md`](AGENT-INSTRUCTIONS.md) 整段貼給它（換掉型號與 IP），裡面有安全規則、指令順序、每一步怎麼驗證、哪些地方要先問你。

原專案的設計是把 [`PROMPT.md`](https://github.com/Gathin23/cleanyourtv/blob/main/PROMPT.md) 貼給有 shell 權限的 AI 編碼助手（Claude Code、Codex、Gemini CLI），它會照安全規則一步步做、每步截圖驗證。
本指南第 2～6 章就是這個流程在 TCL 上實際跑出來的樣子，可以拿來對照，也可以完全手動照做。

## 這台電視的實際結果

- 停用 29 個套件（TCL 首頁推播、TCL Channel、FAST 頻道、TCL 數據分析、Google 預裝自動安裝器、用不到的預裝 App、Google TV 設定精靈、原廠首頁），重開機後全部維持。
- 新首頁：dock 放 YouTube、Netflix、Disney+、YouTube Music；遙控器 YouTube／Netflix／齒輪鍵照常；一顆鍵直接切到接 PS5 的 HDMI。
- 桌布是自己的旅遊照片輪播，閒置時另有 10 秒一張的相片螢幕保護。
- 最後關閉 ADB 並確認 5555 埠已拒絕連線。

## 授權

本 repo 的文字與腳本以 MIT 授權釋出。CleanYourTV 原專案版權屬其作者，見其 [LICENSE](https://github.com/Gathin23/cleanyourtv/blob/main/LICENSE)。
YouTube、Netflix、Disney+、TCL、Google TV 等名稱與商標屬各自所有人，本指南僅作說明用途。
