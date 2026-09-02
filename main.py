from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)

# ===== 在这里填入你的火山方舟 API Key =====
ARK_API_KEY = "ark-aa78b084-0e07-4890-8f3f-4af03c5"
# ==========================================

# 火山方舟 API 配置
ARK_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
ARK_MODEL = "doubao-seed-2-1-pro-260628"

# 系统提示词（DM 规则）
SYSTEM_PROMPT = """你是《斗罗大陆》文字冒险游戏的 DM（游戏主持人）。

【你的核心职责】
1. 推进剧情：根据玩家的行动，写出生动的场景描写和 NPC 对话
2. 遵守规则：严格按照文档中的魂环等级、魂币物价、人物设定执行
3. 出面板：当涉及"吸收魂环""战斗""升级""查看人物"时，必须输出对应面板
4. 自由发展：玩家选择什么方向，剧情就往什么方向走，不强制走原著

【重要规则】
- 魂环颜色：十年白、百年黄、千年紫、万年黑、十万年红、百万年淡金
- 魂环获取必须在整10级（10、20、30...90级）
- 魂币体系：1金魂币=10银魂币=100铜魂币
- 人物设定不可改：唐三就是唐三，小舞就是小舞

【输出格式要求】
- 每轮回复第一行写时间戳：【第X轮】斗罗大陆 · 时间 · 地点
- 面板要用 LaTeX 格式，放在 $$ 中
- 叙事要生动，有画面感
- 每次回复末尾给 3~5 个选项让玩家选择

现在开始，等待玩家输入「开始游戏」或选择身份。"""

@app.route("/")
def index():
    try:
        return send_file("index.html")
    except:
        return "斗罗大陆游戏后端已启动！但 index.html 未找到。"

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        
        if not user_message:
            return jsonify({"error": "消息不能为空"}), 400
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ARK_API_KEY}"
        }
        
        payload = {
            "model": ARK_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.8,
            "max_tokens": 2000
        }
        
        response = requests.post(
            f"{ARK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            return jsonify({"error": f"火山方舟 API 错误: {response.status_code}"}), 500
        
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
