import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# ==========================================
# 1. 環境設定與安全性 (Setup & Security)
# ==========================================
# 從 .env 檔案載入環境變數
load_dotenv()

# 初始化 OpenAI Client，但將端點 (base_url) 指向 Groq 的伺服器
# 這樣就能用 OpenAI 的標準套件，免費呼叫 Groq 的超快模型
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ==========================================
# 2. 模擬資料函式 (Mock Data Functions)
# ==========================================
def get_exchange_rate(currency_pair: str) -> str:
    """獲取匯率的模擬函式"""
    print(f"[Debug] Executing tool: get_exchange_rate for {currency_pair}...")
    rates = {
        "USD_TWD": "32.0",
        "JPY_TWD": "0.2",
        "EUR_USD": "1.2"
    }
    
    if currency_pair in rates:
        return json.dumps({"currency_pair": currency_pair, "rate": rates[currency_pair]})
    return json.dumps({"error": "Data not found"})

def get_stock_price(symbol: str) -> str:
    """獲取股價的模擬函式"""
    print(f"[Debug] Executing tool: get_stock_price for {symbol}...")
    prices = {
        "AAPL": "260.00",
        "TSLA": "430.00",
        "NVDA": "190.00"
    }
    
    if symbol in prices:
        return json.dumps({"symbol": symbol, "price": prices[symbol]})
    return json.dumps({"error": "Data not found"})

# ==========================================
# 3. 函式對應表 (Function Map)
# ==========================================
# 滿足作業要求：不使用長串 if-else，改用 Dictionary 動態派發
available_functions = {
    "get_exchange_rate": get_exchange_rate,
    "get_stock_price": get_stock_price,
}

# ==========================================
# 4. 工具定義 (Tool Schemas - Structured Outputs)
# ==========================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "Get the current exchange rate for a specific currency pair (e.g., 'USD_TWD').",
            "parameters": {
                "type": "object",
                "properties": {
                    "currency_pair": {
                        "type": "string",
                        "description": "The currency pair to look up."
                    }
                },
                "required": ["currency_pair"],
                "additionalProperties": False # 作業規定：嚴格模式必要設定
            },
            "strict": True # 作業規定：啟用結構化輸出
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get the current stock price for a given stock ticker symbol (e.g., 'AAPL').",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The stock ticker symbol."
                    }
                },
                "required": ["symbol"],
                "additionalProperties": False # 作業規定：嚴格模式必要設定
            },
            "strict": True # 作業規定：啟用結構化輸出
        }
    }
]

# ==========================================
# 5. 穩健的代理迴圈 (Robust Agent Loop)
# ==========================================
def run_agent():
    # 系統提示詞：設定 Financial Assistant 角色與記憶能力
    messages = [
        {
            "role": "system", 
            "content": "You are a helpful Financial Assistant. You can provide stock prices and exchange rates using the provided tools. Be polite, concise, and remember user details."
        }
    ]
    
    print("Financial Assistant Started. Type 'exit' to quit.")
    print("-" * 50)

    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
            
        messages.append({"role": "user", "content": user_input})

        # 第一次 API 呼叫：讓模型決定是否需要呼叫工具 (使用 Groq 的 llama-3.3-70b-versatile 模型)
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
        except Exception as e:
            print(f"API Error: {e}")
            continue
        
        response_msg = response.choices[0].message
        tool_calls = response_msg.tool_calls

        if tool_calls:
            # 必須將 AI 的「工具呼叫請求 (Assistant message)」加入對話紀錄，否則會破壞上下文結構
            messages.append(response_msg)
            
            # 處理平行工具呼叫 (Parallel Tool Calls)
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                
                try:
                    function_args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    function_args = {}
                
                # 透過 Function Map 動態執行函式
                function_to_call = available_functions.get(function_name)
                
                if function_to_call:
                    try:
                        tool_result = function_to_call(**function_args)
                    except Exception as e:
                        tool_result = json.dumps({"error": str(e)})
                else:
                    tool_result = json.dumps({"error": f"Function {function_name} not found"})
                
                # 將每個工具執行後的「結果 (Tool message)」加回對話紀錄
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": tool_result,
                })
            
            # 第二次 API 呼叫：將多個工具回傳的數據交給 AI，整合成最終的自然語言回覆
            try:
                final_response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages
                )
                final_content = final_response.choices[0].message.content
                print(f"\nAssistant: {final_content}")
                
                # 將最終回覆存入記憶
                messages.append({"role": "assistant", "content": final_content})
            except Exception as e:
                print(f"API Error during final response: {e}")
            
        else:
            # 一般對話 (AI 判斷無需使用工具時)
            print(f"\nAssistant: {response_msg.content}")
            messages.append({"role": "assistant", "content": response_msg.content})

if __name__ == "__main__":
    run_agent()