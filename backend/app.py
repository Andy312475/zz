from flask import Flask, jsonify, request, g
from flask_cors import CORS
import json
import os
import sqlite3
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# 数据库路径
DATABASE = 'app.db'

# 加载题库
with open('../data/questions.json', 'r', encoding='utf-8') as f:
    questions = json.load(f)

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_URL = 'https://api.deepseek.com/v1/chat/completions'
ai_cache = {}

# ---------- 数据库工具 ----------
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                user_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                topic TEXT
            )
        ''')
        db.commit()

app.teardown_appcontext(close_db)

# ---------- 路由 ----------
@app.route('/api/questions', methods=['GET'])
def get_questions():
    return jsonify(questions)

@app.route('/api/submit', methods=['POST'])
def submit_answer():
    data = request.get_json()
    q_id = data.get('id')
    user_answer = data.get('answer')

    q = next((q for q in questions if q['id'] == q_id), None)
    if not q:
        return jsonify({"error": "题目不存在"}), 404

    is_correct = (user_answer.strip().upper() == q['answer'])

    # 记录到数据库
    db = get_db()
    db.execute(
        "INSERT INTO answers (question_id, user_answer, is_correct, topic) VALUES (?, ?, ?, ?)",
        (q_id, user_answer, int(is_correct), q.get('topic', '未分类'))
    )
    db.commit()

    return jsonify({
        "correct": is_correct,
        "analysis": q['analysis'],
        "correct_answer": q['answer']
    })

@app.route('/api/ai-explain', methods=['POST'])
def ai_explain():
    data = request.get_json()
    q_id = data.get('id')
    user_answer = data.get('user_answer', '')

    q = next((q for q in questions if q['id'] == q_id), None)
    if not q:
        return jsonify({"error": "题目不存在"}), 404

    cache_key = str(q_id)
    if cache_key in ai_cache:
        return jsonify({"explanation": ai_cache[cache_key], "cached": True})

    prompt = f"""你是一位数据结构辅导老师。请为下面这道题目提供分步骤的详细讲解：

题目：{q['title']}
选项：{', '.join(q['options'])}
正确答案：{q['answer']}
用户选择了：{user_answer}
静态解析：{q['analysis']}

请按以下结构输出：
1. 考点分析：这道题考察什么知识点？
2. 解题思路：如何一步步选出正确答案？
3. 选项辨析：每个选项为什么对/错？
4. 要点总结：记住什么关键点？"""

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个专业的数据结构教师，请用中文回答，讲解清晰易懂。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1024
    }

    try:
        resp = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        explanation = result['choices'][0]['message']['content']
        ai_cache[cache_key] = explanation
        return jsonify({"explanation": explanation, "cached": False})
    except Exception as e:
        print("AI调用失败:", e)
        return jsonify({"error": "AI讲解生成失败，请稍后重试"}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    db = get_db()
    # 总刷题数和正确数
    total = db.execute("SELECT COUNT(*) FROM answers").fetchone()[0]
    correct = db.execute("SELECT COUNT(*) FROM answers WHERE is_correct=1").fetchone()[0]

    # 各知识点统计
    rows = db.execute("""
        SELECT topic, 
               COUNT(*) as total, 
               SUM(is_correct) as correct
        FROM answers
        GROUP BY topic
    """).fetchall()

    topics = []
    for row in rows:
        topics.append({
            "topic": row['topic'],
            "total": row['total'],
            "correct": row['correct'],
            "accuracy": round(row['correct'] / row['total'], 2) if row['total'] > 0 else 0
        })

    return jsonify({
        "total": total,
        "correct": correct,
        "accuracy": round(correct / total, 2) if total > 0 else 0,
        "topics": topics
    })

# ---------- AI 生成题目 ----------
@app.route('/api/generate', methods=['POST'])
def generate_question():
    data = request.get_json()
    topic = data.get('topic', '线性表')
    difficulty = data.get('difficulty', '中等')  # 简单/中等/困难

    # 获取当前最大 id
    if not questions:
        max_id = 0
    else:
        max_id = max(q['id'] for q in questions)

    prompt = f"""你是一位数据结构题库专家。请生成一道关于“{topic}”的单项选择题，难度为“{difficulty}”。

要求：
1. 题目表述清晰，有且仅有四个选项（A、B、C、D）。
2. 必须返回严格的 JSON 格式，不包含任何其他文字，格式如下：
{{
  "title": "题目内容",
  "options": ["A. 选项A", "B. 选项B", "C. 选项C", "D. 选项D"],
  "answer": "标准答案字母（大写）",
  "analysis": "详细的题目解析，说明每个选项对或错的原因",
  "topic": "{topic}"
}}
3. 题目必须考察“{topic}”的核心概念，选项要有迷惑性，解析要详尽。"""

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个专业的数据结构出题老师，请严格按照 JSON 格式输出。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,   # 较高温度增加题目多样性
        "max_tokens": 512
    }

    try:
        resp = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        content = result['choices'][0]['message']['content'].strip()
        # 尝试解析 JSON（可能被包裹在 ```json ... ``` 中）
        if content.startswith('```'):
            # 去掉代码块标记
            lines = content.split('\n')
            content = '\n'.join(lines[1:-1])
        generated = json.loads(content)

        # 补全必要字段
        new_q = {
            "id": max_id + 1,
            "title": generated['title'],
            "options": generated['options'],
            "answer": generated['answer'].upper(),
            "analysis": generated['analysis'],
            "topic": topic
        }
        # 追加到内存和 JSON 文件
        questions.append(new_q)
        with open('../data/questions.json', 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

        return jsonify({"success": True, "question": new_q})
    except Exception as e:
        print("题目生成失败:", e)
        return jsonify({"error": "题目生成失败，请稍后再试"}), 500
    
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)