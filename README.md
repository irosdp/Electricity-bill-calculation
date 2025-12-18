# 簡易電腦電費監測儀 (Simple PC Power Monitor)

一個輕量級的 Windows 桌面工具，用於即時監測電腦耗電量並計算累積電費。
A lightweight Windows desktop tool for real-time PC power monitoring and electricity cost calculation.

![License](https://img.shields.io/github/license/LibreHardwareMonitor/LibreHardwareMonitor?label=License)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6)

![軟體截圖](screenshot.png) 

## ✨ 功能特色 (Features)

*   **即時監測 (Real-time Monitoring)**：讀取 CPU 與 GPU 的即時瓦數 (基於 LibreHardwareMonitor)。
*   **電費計算 (Cost Calculation)**：自動累加耗電度數，並換算成新台幣 (TWD)。
*   **季節電價自動切換 (Seasonal Rates)**：自動判斷台灣「夏月」(6-9月) 與「非夏月」的建議電價。
*   **單日預估 (Daily Estimate)**：根據當下負載，即時推算「如果掛網一整天」需要多少電費。
*   **大字體儀表板 (Dashboard)**：清楚顯示經過時間、總度數與總金額，適合掛機遊戲時查看。

## 🚀 下載與使用 (Download & Usage)

1.  前往本專案的 **[Releases](https://github.com/irosdp/Electricity-bill-calculation/releases)** 頁面。
2.  下載最新的 `run.exe`。
3.  **右鍵 -> 以系統管理員身分執行** (Run as Administrator)。
    *   *注意：必須使用管理員權限，否則無法讀取 CPU/GPU 硬體傳感器。*

## 🛠️ 開發與建置 (Development & Build)

如果您想自行修改原始碼或重新打包，請參考以下步驟：

### 需求環境 (Prerequisites)
*   Windows 10 / 11
*   Python **3.12** (建議版本，避免相容性問題)
*   [LibreHardwareMonitorLib.dll](https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases) (需放在同目錄)

### 安裝套件 (Install Dependencies)
```bash
pip install pythonnet pyinstaller
