NCU CS - LLM Agent Assignment 1: Financial Assistant
這是一個基於 大語言模型 (LLM) 開發的命令列財務助手代理人 (Financial Assistant Agent)。本專案展示了如何利用 Function Calling (工具呼叫)、Parallel Tool Use (平行工具處理) 以及 Context Management (上下文記憶) 來構建一個實用的 AI 代理。

🌟 核心功能 (Features)
身份識別 (Task A)：具備明確的 Financial Assistant 角色設定。

財務資訊查詢 (Task B)：支援單一股票價格與匯率查詢。

平行工具處理 (Task C)：能夠在單次對話中同時處理多個工具呼叫（例如：同時比較兩支股票價格）。

個人化記憶 (Task D)：具備對話上下文記憶能力，能記住使用者的姓名（如：侯詠倫）。

穩健的錯誤處理 (Task E)：當工具回傳查無資料（如：GOOG）時，能優雅地向使用者說明而非程式崩潰。

🛠️ 技術棧 (Tech Stack)
語言：Python 3.10+

SDK：OpenAI Python SDK (相容 Groq/Gemini API 端點)

模型：llama-3.3-70b-versatile (透過 Groq API 提供極速響應)

關鍵技術：

Strict Mode 工具定義（確保結構化輸出）。

available_functions 字典映射路由（取代傳統 if-else）。

.env 環境變數管理（保護 API 金鑰安全）。

🚀 快速開始 (Quick Start)
1. 安裝必要套件
Bash
pip install -r requirements.txt
2. 環境變數設定
在專案根目錄建立 .env 檔案，並填入你的 API 金鑰：

Plaintext
GROQ_API_KEY=your_api_key_here

3. 執行程式
python main.py
📂 檔案結構 (Project Structure)
