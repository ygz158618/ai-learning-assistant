import streamlit as st
import requests
import json
import re
import html as html_module
import streamlit.components.v1 as components
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI 学习助手",
    page_icon="🤖",
    layout="wide",
)

st.markdown("""
<style>
:root {
    --primary-color: #1E88E5;
    --bg-color: #F5F7FA;
    --card-bg: #FFFFFF;
    --text-primary: #1F2937;
    --text-secondary: #6B7280;
    --border-color: #E5E7EB;
    --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    --radius: 16px;
}
.stApp { background-color: var(--bg-color) !important; }
.main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
.custom-card {
    background: var(--card-bg);
    border-radius: var(--radius);
    padding: 24px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border-color);
    margin-bottom: 20px;
}
.chat-container { display: flex; flex-direction: column; gap: 12px; margin: 20px 0; }
.chat-bubble {
    padding: 16px 20px;
    border-radius: 20px;
    max-width: 85%;
    box-shadow: var(--shadow);
    line-height: 1.7;
    font-size: 15px;
    word-wrap: break-word;
    white-space: pre-wrap;
}
.user-bubble {
    background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 6px;
}
.ai-bubble {
    background: var(--card-bg);
    color: var(--text-primary);
    margin-right: auto;
    border: 1px solid var(--border-color);
    border-bottom-left-radius: 6px;
}
.sidebar-title {
    font-size: 26px !important;
    font-weight: 700;
    color: var(--primary-color);
    margin-bottom: 8px;
}
.stTextInput input, .stTextArea textarea {
    border-radius: 12px !important;
    border: 1px solid var(--border-color) !important;
}
.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%) !important;
    border: none !important;
}
.welcome-title {
    font-size: 32px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
    text-align: center;
}
.welcome-subtitle {
    color: var(--text-secondary);
    text-align: center;
    font-size: 16px;
    margin-bottom: 32px;
}
.usage-tip {
    background: #FFF8E1;
    border-left: 4px solid #FFB300;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 13px;
    color: #5D4037;
}
.mini-action-btn {
    font-size: 12px !important;
    padding: 4px 10px !important;
    min-height: 0 !important;
    border-radius: 8px !important;
    background: #F0F4F8 !important;
    color: #4B5563 !important;
    border: 1px solid #E5E7EB !important;
    box-shadow: none !important;
}
.mini-action-btn:hover {
    background: #E3F2FD !important;
    color: #1565C0 !important;
    border-color: #90CAF9 !important;
}
.copy-btn-wrap button.copy-btn {
    font-size: 12px;
    padding: 4px 12px;
    border-radius: 8px;
    background: #F0F4F8;
    color: #4B5563;
    border: 1px solid #E5E7EB;
    cursor: pointer;
}
.copy-btn-wrap button.copy-btn:hover {
    background: #E3F2FD;
    color: #1565C0;
}
.copy-btn-wrap button.copy-btn.copied {
    background: #E8F5E9;
    color: #2E7D32;
    border-color: #A5D6A7;
}
div[data-testid="stDownloadButton"] button {
    font-size: 13px !important;
    padding: 6px 14px !important;
    border-radius: 8px !important;
}
@media (max-width: 768px) {
    .chat-bubble { max-width: 95%; }
    .welcome-title { font-size: 26px; }
}
</style>
""", unsafe_allow_html=True)

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEFAULT_MODEL = "deepseek-chat"
HISTORY_FILE = Path("chat_history.json")

ALL_MODES = [
    "概念解释",
    "代码生成",
    "文档翻译",
    "代码解释",
    "面试题生成",
    "学习路线规划",
]

MODE_EMOJI = {
    "概念解释": "📖",
    "代码生成": "💻",
    "文档翻译": "🌐",
    "代码解释": "🔍",
    "面试题生成": "🎯",
    "学习路线规划": "🗺️",
}

SIDEBAR_INPUT_MODES = {"代码解释", "面试题生成", "学习路线规划"}

LANG_ALIAS = {
    "python": "python",
    "javascript": "javascript",
    "java": "java",
    "c++": "cpp",
    "cpp": "cpp",
    "自动检测": "text",
}

def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return sorted(data, key=lambda x: x.get("id", ""), reverse=True)
        except Exception:
            return []
    return []


def save_history(history_list):
    sorted_list = sorted(history_list, key=lambda x: x.get("id", ""), reverse=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted_list, f, ensure_ascii=False, indent=2)


def export_filename(prefix="chat_history"):
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"


def infer_lang_from_text(mode, text):
    bracket = re.search(r"\[(Python|JavaScript|Java|C\+\+|自动检测)\]", text or "")
    if bracket:
        tag = bracket.group(1)
        if tag == "自动检测":
            return "text"
        return LANG_ALIAS.get(tag.lower(), "text")
    if mode == "代码生成":
        return "python"
    if mode == "代码解释":
        return "python"
    return "text"


def fix_code_fences(text, default_lang="text"):
    if not text:
        return text

    def replacer(match):
        lang = (match.group(1) or "").strip()
        code = match.group(2)
        fence_lang = lang if lang else default_lang
        return f"```{fence_lang}\n{code.rstrip()}\n```"

    return re.sub(r"```(\w*)\n(.*?)```", replacer, text, flags=re.DOTALL)


def format_export_field(text, mode, field_type="answer"):
    if not text:
        return ""
    lang = infer_lang_from_text(mode, text)
    if field_type == "question" and mode in ("代码解释",) and "```" not in text:
        if "\n" in text.strip() or text.strip().startswith("["):
            code_body = re.sub(r"^\[[^\]]+\]\n?", "", text).strip()
            if code_body:
                return f"```{lang}\n{code_body}\n```"
    if field_type == "answer" and mode == "代码生成" and "```" not in text:
        return fix_code_fences(f"```{lang}\n{text}\n```", lang)
    return fix_code_fences(text, lang)


def generate_markdown_export(records):
    export_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# AI 学习助手 - 对话记录",
        "",
        f"> **导出时间**：{export_time}",
        f"> **记录条数**：{len(records)}",
        "",
    ]
    for idx, item in enumerate(records, 1):
        mode = item.get("mode", "未知")
        emoji = MODE_EMOJI.get(mode, "📝")
        lines.append(f"## 记录 {idx} · {emoji} {mode}")
        lines.append("")
        lines.append(f"**时间**：{item.get('time', '—')}")
        lines.append("")
        lines.append("### 用户问题")
        lines.append("")
        lines.append(format_export_field(item.get("question", ""), mode, "question"))
        lines.append("")
        lines.append("### AI 回答")
        lines.append("")
        lines.append(format_export_field(item.get("answer", ""), mode, "answer"))
        lines.append("")
        if idx < len(records):
            lines.append("---")
            lines.append("")
    return "\n".join(lines)


def get_latest_qa_record():
    last_user = last_assistant = None
    for msg in st.session_state.current_chat:
        if msg["role"] == "user":
            last_user = msg
        elif msg["role"] == "assistant":
            last_assistant = msg
    if not last_user or not last_assistant:
        return None
    return {
        "mode": st.session_state.current_mode,
        "question": last_user["content"],
        "answer": last_assistant["content"],
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def render_copy_button(text, key):
    text_json = json.dumps(text, ensure_ascii=False)
    components.html(
        f"""
        <motion class="copy-btn-wrap">
            <button type="button" class="copy-btn" id="copy_{key}">📋 复制回答</button>
        </motion>
        <script>
        (function() {{
            var btn = document.getElementById("copy_{key}");
            if (!btn) return;
            btn.addEventListener("click", function() {{
                navigator.clipboard.writeText({text_json}).then(function() {{
                    btn.textContent = "已复制！";
                    btn.classList.add("copied");
                    setTimeout(function() {{
                        btn.textContent = "📋 复制回答";
                        btn.classList.remove("copied");
                    }}, 2000);
                }});
            }});
        }})();
        </script>
        """.replace("motion", "div"),
        height=40,
    )


def escape_html(text):
    return html_module.escape(str(text)).replace("\n", "<br>")


def bubble_html(role, content, timestamp):
    body = escape_html(content)
    if role == "user":
        return (
            '<div class="chat-bubble user-bubble">'
            f'<div style="font-size:12px;opacity:0.85;margin-bottom:4px;">你 · {timestamp}</div>'
            f"<div>{body}</div></div>"
        )
    return (
        '<div class="chat-bubble ai-bubble">'
        f'<div style="font-size:12px;color:#1E88E5;margin-bottom:4px;font-weight:600;">'
        f"🤖 AI 导师 · {timestamp}</div>"
        f"<div>{body}</div></div>"
    )


if "history" not in st.session_state:
    st.session_state.history = load_history()
if "selected_history" not in st.session_state:
    st.session_state.selected_history = None
if "api_key" not in st.session_state:
    try:
        st.session_state.api_key = st.secrets.get("MY_DEEPSEEK_KEY", "")
    except Exception:
        st.session_state.api_key = ""
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "概念解释"
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []
if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False
if "last_mode" not in st.session_state:
    st.session_state.last_mode = st.session_state.current_mode


def call_deepseek_api(messages, api_key, max_tokens=2500):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEFAULT_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": max_tokens,
        "stream": False,
    }
    try:
        response = requests.post(
            DEEPSEEK_API_URL, json=payload, headers=headers, timeout=90
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"❌ API 调用失败：{str(e)}"
    except KeyError:
        return "❌ API 响应格式异常，请检查 API Key 是否正确"


def get_system_prompt(mode):
    prompts = {
        "概念解释": (
            "你是一位经验丰富的技术导师，拥有多年编程教学经验。你耐心、细致，"
            "擅长用通俗易懂的语言帮助初学者理解复杂概念。"
            "请用简单语言解释技术概念，避免过多专业术语，必要时使用生活化比喻。"
        ),
        "代码生成": (
            "你是一位经验丰富的技术导师，拥有多年编程教学经验。你耐心、细致，"
            "擅长用通俗易懂的语言帮助初学者理解复杂概念。"
            "你擅长根据需求生成高质量、可直接运行的代码，并提供清晰的中文注释说明。"
        ),
        "文档翻译": (
            "你是一位经验丰富的技术导师，拥有多年编程教学经验。你耐心、细致，"
            "擅长用通俗易懂的语言帮助初学者理解复杂概念。"
            "你精通中英文技术文档翻译，能准确保留专业术语，同时让中文表达自然流畅。"
        ),
        "代码解释": (
            "你是一位资深的代码分析专家，精通多种编程语言。"
            "你擅长逐行分析代码逻辑、解释关键变量与数据结构，并评估时间/空间复杂度。"
            "回答结构清晰、耐心细致，适合初学者理解。"
        ),
        "面试题生成": (
            "你是一位资深技术面试官，曾在一线互联网公司参与数百场技术面试。"
            "你擅长根据岗位方向出高质量面试题，题目贴近实战，解析透彻。"
        ),
        "学习路线规划": (
            "你是一位专业的技术职业规划师，熟悉各技术岗位的技能树与行业要求。"
            "你擅长为学习者制定循序渐进、可执行的学习路线，并推荐优质学习资源。"
        ),
    }
    return prompts.get(mode, "你是一位经验丰富的技术导师，耐心细致地解答学习者的问题。")


def generate_explanation_prompt(term):
    return (
        f"请用通俗易懂的语言为初学者解释「{term}」这个技术概念。"
        "包含：1. 是什么 2. 为什么重要 3. 实际应用例子 4. 简单类比（如果合适）"
    )


def generate_code_prompt(description, language):
    return (
        f"用户需求：{description}\n\n"
        f"请生成{language}代码实现上述需求。要求：\n"
        "1. 代码必须可以直接运行\n2. 提供详细的中文注释\n"
        "3. 包含必要的错误处理\n4. 代码结构清晰，变量命名有意义"
    )


def generate_translation_prompt(text):
    return f"请将以下英文技术文档翻译成流畅、自然的中文，保留专业术语准确性：\n\n{text}"


def generate_code_explain_prompt(code, language):
    lang_hint = (
        "请先自动检测代码语言，再进行分析。"
        if language == "自动检测"
        else f"代码语言为：{language}。"
    )
    return (
        f"{lang_hint}\n\n"
        "请分析以下代码，严格按以下结构输出（使用 Markdown 标题）：\n\n"
        "## 一、代码功能总览\n（用 2-4 句话概括这段代码的整体作用）\n\n"
        "## 二、逐段详细解释\n"
        "（按逻辑块分段，每段说明：做了什么、关键变量含义、重要逻辑；"
        "对核心循环/递归请说明时间复杂度）\n\n"
        "## 三、要点总结\n（列出 3-5 条学习要点或注意事项）\n\n"
        f"待分析代码：\n```\n{code}\n```"
    )


def generate_interview_prompt(direction, question_type):
    return (
        f"请为「{direction}」方向生成面试题，题型要求：{question_type}。\n\n"
        "请严格按以下格式输出（使用 Markdown），对每道题：\n"
        "### 题目 N：[题型标签]\n**题目：** ...\n**答案：** ...\n**解析：** ...\n\n"
        "要求：\n"
        "- 选择题：至少 3 道，含 A/B/C/D 选项\n"
        "- 简答题：至少 2 道\n"
        "- 编程题：至少 1 道，必须包含「**测试用例：**」小节（输入/输出示例）\n"
        "- 混合：综合以上题型，共 5-8 道题\n"
        "- 题目难度适中，贴近真实面试场景"
    )


def generate_roadmap_prompt(role, level):
    level_text = level if level else "未指定（请按入门水平规划）"
    return (
        f"请为「{role}」岗位制定详细学习路线，学习者当前水平：{level_text}。\n\n"
        "请严格按以下结构输出（使用 Markdown）：\n\n"
        "## 路线总览\n（一句话说明整体路径）\n\n"
        "## 阶段一：基础阶段\n- **学习内容：** ...\n"
        "- **推荐资源：** ...\n- **预计时长：** ...\n\n"
        "## 阶段二：进阶阶段\n（同上结构）\n\n"
        "## 阶段三：实战阶段\n（同上结构，含项目实战建议）\n\n"
        "## 阶段四：面试备战\n（同上结构，含面试重点）\n\n"
        "## 学习建议\n（3-5 条可执行建议）"
    )


def add_to_history(mode, user_input, output):
    entry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "mode": mode,
        "question": user_input,
        "answer": output,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    st.session_state.history.insert(0, entry)
    save_history(st.session_state.history)


def add_to_current_chat(role, content):
    st.session_state.current_chat.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().strftime("%H:%M"),
    })


def clear_current_chat():
    st.session_state.current_chat = []


def display_chat_bubbles():
    if not st.session_state.current_chat:
        return
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for i, msg in enumerate(st.session_state.current_chat):
        st.markdown(
            bubble_html(msg["role"], msg["content"], msg.get("timestamp", "")),
            unsafe_allow_html=True,
        )
        if msg["role"] == "assistant":
            render_copy_button(msg["content"], f"chat_copy_{i}")
    st.markdown("</div>", unsafe_allow_html=True)


def display_history_item(item):
    emoji = MODE_EMOJI.get(item["mode"], "📝")
    st.subheader(f"📜 {item['time']} · {emoji} {item['mode']}")
    ts = item["time"][11:16] if len(item.get("time", "")) >= 16 else item.get("time", "")
    st.markdown(bubble_html("user", item["question"], ts), unsafe_allow_html=True)
    st.markdown(bubble_html("assistant", item["answer"], ts), unsafe_allow_html=True)
    render_copy_button(item["answer"], f"hist_copy_{item['id']}")


def run_ai_and_save(mode, user_prompt, user_display, max_tokens=2500):
    if not st.session_state.get("api_key", ""):
        return False, "请先在侧边栏展开区输入 DeepSeek API Key"
    messages = [
        {"role": "system", "content": get_system_prompt(mode)},
        {"role": "user", "content": user_prompt},
    ]
    with st.spinner("AI 正在思考..."):
        output = call_deepseek_api(messages, st.session_state.get("api_key", ""), max_tokens)
    add_to_current_chat("user", user_display)
    add_to_current_chat("assistant", output)
    add_to_history(mode, user_display, output)
    return True, output


sidebar_submit = False
ce_language = ce_code = iv_direction = iv_type = rm_role = rm_level = None

with st.sidebar:
    st.markdown('<div class="sidebar-title">🤖 AI 学习助手</div>', unsafe_allow_html=True)
    st.divider()

    with st.expander("🔑 API Key 设置", expanded=False):
        api_key_input = st.text_input(
            "DeepSeek API Key",
            value=st.session_state.get("api_key", ""),
            type="password",
            placeholder="sk-xxxxxxxxxxxxxxxx",
            help="从 https://platform.deepseek.com/ 获取 API Key",
        )
        if api_key_input:
            st.session_state.api_key = api_key_input

    st.divider()

    st.subheader("🎯 功能模式")
    mode_index = ALL_MODES.index(st.session_state.current_mode)
    selected_mode = st.selectbox(
        "选择模式",
        ALL_MODES,
        index=mode_index,
        format_func=lambda m: f"{MODE_EMOJI.get(m, '📝')} {m}",
        label_visibility="collapsed",
    )
    if selected_mode != st.session_state.last_mode:
        st.session_state.current_mode = selected_mode
        st.session_state.last_mode = selected_mode
        clear_current_chat()
        st.rerun()
    st.session_state.current_mode = selected_mode
    mode = selected_mode

    st.divider()

    if mode == "代码解释":
        st.subheader("🔍 代码解释配置")
        ce_language = st.selectbox(
            "代码语言",
            ["Python", "JavaScript", "Java", "C++", "自动检测"],
            key="ce_lang",
        )
        ce_code = st.text_area(
            "粘贴代码",
            placeholder="请粘贴需要解释的代码...",
            height=200,
            key="ce_code",
        )
        sidebar_submit = st.button("🚀 开始解释代码", type="primary", use_container_width=True)

    elif mode == "面试题生成":
        st.subheader("🎯 面试题配置")
        iv_direction = st.selectbox(
            "技术方向",
            ["Python", "JavaScript", "数据结构与算法", "计算机网络", "操作系统"],
            key="iv_dir",
        )
        iv_type = st.selectbox(
            "题型",
            ["选择题", "简答题", "编程题", "混合"],
            key="iv_type",
        )
        sidebar_submit = st.button("🚀 生成面试题", type="primary", use_container_width=True)

    elif mode == "学习路线规划":
        st.subheader("🗺️ 学习路线配置")
        rm_role = st.text_input(
            "目标岗位",
            placeholder="例如：Python后端开发、前端工程师、数据分析师",
            key="rm_role",
        )
        rm_level = st.selectbox(
            "当前水平（可选）",
            ["入门", "初级", "中级"],
            index=0,
            key="rm_level",
        )
        sidebar_submit = st.button("🚀 生成学习路线", type="primary", use_container_width=True)

    st.divider()

    st.subheader("📚 对话历史 (最近20条)")
    if st.session_state.history:
        for item in st.session_state.history[:20]:
            emoji = MODE_EMOJI.get(item["mode"], "📝")
            summary = item["question"][:30] + ("..." if len(item["question"]) > 30 else "")
            label = f"{emoji} {item['mode']} · {summary}"
            if st.button(label, key=f"hist_{item['id']}", use_container_width=True):
                st.session_state.selected_history = item
                st.rerun()

        st.divider()
        if st.button("🗑️ 清空全部历史", use_container_width=True):
            st.session_state.confirm_clear = True
    else:
        st.caption("暂无历史记录")

    if st.session_state.confirm_clear:
        st.warning("⚠️ 确定要清空所有历史记录吗？此操作不可恢复！")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ 确认清空", use_container_width=True):
                st.session_state.history = []
                if HISTORY_FILE.exists():
                    HISTORY_FILE.unlink()
                st.session_state.confirm_clear = False
                st.session_state.selected_history = None
                st.rerun()
        with c2:
            if st.button("❌ 取消", use_container_width=True):
                st.session_state.confirm_clear = False
                st.rerun()

    st.divider()
    st.markdown("""
    <div class="usage-tip">
        <strong>💡 使用提示</strong><br>
        1. 下拉菜单切换 6 种功能模式<br>
        2. 代码解释/面试题/路线在侧边栏配置<br>
        3. 每轮对话自动保存到本地 JSON<br>
        4. 点击历史可查看完整问答
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    if st.session_state.history:
        md_all = generate_markdown_export(st.session_state.history)
        st.download_button(
            label="📥 导出为 Markdown",
            data=md_all,
            file_name=export_filename("chat_history"),
            mime="text/markdown",
            use_container_width=True,
            help="导出全部历史记录",
        )
    else:
        st.caption("暂无记录可导出")

    st.caption("Made with ❤️ for AI learning beginners.")


if sidebar_submit and mode in SIDEBAR_INPUT_MODES:
    if mode == "代码解释":
        if not ce_code or not ce_code.strip():
            st.sidebar.warning("请粘贴需要解释的代码")
        else:
            preview = ce_code[:200] + ("..." if len(ce_code) > 200 else "")
            user_display = f"[{ce_language}]\n{preview}"
            ok, err = run_ai_and_save(
                mode,
                generate_code_explain_prompt(ce_code, ce_language),
                user_display,
                max_tokens=3000,
            )
            if not ok:
                st.sidebar.error(err)
            else:
                st.rerun()
    elif mode == "面试题生成":
        user_display = f"[{iv_direction}] {iv_type}"
        ok, err = run_ai_and_save(
            mode,
            generate_interview_prompt(iv_direction, iv_type),
            user_display,
            max_tokens=3500,
        )
        if not ok:
            st.sidebar.error(err)
        else:
            st.rerun()
    elif mode == "学习路线规划":
        if not rm_role or not rm_role.strip():
            st.sidebar.warning("请输入目标岗位")
        else:
            user_display = f"{rm_role} · 水平：{rm_level}"
            ok, err = run_ai_and_save(
                mode,
                generate_roadmap_prompt(rm_role, rm_level),
                user_display,
                max_tokens=3500,
            )
            if not ok:
                st.sidebar.error(err)
            else:
                st.rerun()


st.markdown('<div class="welcome-title">有什么我可以帮你的？</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="welcome-subtitle">经验丰富的技术导师 · 耐心解答你的每一个问题</div>',
    unsafe_allow_html=True,
)

if st.session_state.selected_history:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    display_history_item(st.session_state.selected_history)
    hist_record = [st.session_state.selected_history]
    st.download_button(
        label="📋 导出此对话",
        data=generate_markdown_export(hist_record),
        file_name=export_filename("chat_single"),
        mime="text/markdown",
        key="export_hist_view",
    )
    if st.button("← 返回主界面", use_container_width=True):
        st.session_state.selected_history = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

if st.session_state.current_chat:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    display_chat_bubbles()
    action_col1, action_col2, _ = st.columns([1, 1, 4])
    with action_col1:
        current_record = get_latest_qa_record()
        if current_record:
            st.download_button(
                label="📋 导出此对话",
                data=generate_markdown_export([current_record]),
                file_name=export_filename("chat_single"),
                mime="text/markdown",
                key="export_current_chat",
            )
    with action_col2:
        if st.button("🧹 清空当前对话", use_container_width=True):
            clear_current_chat()
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

if mode not in SIDEBAR_INPUT_MODES:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)

    if mode == "概念解释":
        st.header("📖 概念解释")
        st.caption("输入技术名词，AI 将用通俗语言为你详细讲解")
        term = st.text_input(
            "技术名词",
            placeholder="例如：Transformer、Docker、REST API、React Hooks...",
            key="term_input",
        )
        if st.button("🚀 开始解释", type="primary", use_container_width=True):
            if not term.strip():
                st.warning("请输入技术名词")
            else:
                ok, err = run_ai_and_save(mode, generate_explanation_prompt(term), term)
                if not ok:
                    st.error(err)
                else:
                    st.rerun()

    elif mode == "代码生成":
        st.header("💻 代码生成")
        st.caption("用自然语言描述需求，AI 生成带注释的 Python / JavaScript 代码")
        c1, c2 = st.columns([3, 1])
        with c1:
            description = st.text_area(
                "需求描述",
                placeholder="例如：写一个函数，接收列表，返回所有偶数的平方和...",
                height=120,
                key="code_input",
            )
        with c2:
            language = st.selectbox("目标语言", ["Python", "JavaScript"], index=0)
        if st.button("🚀 生成代码", type="primary", use_container_width=True):
            if not description.strip():
                st.warning("请描述你的需求")
            else:
                user_msg = f"[{language}] {description}"
                ok, err = run_ai_and_save(
                    mode, generate_code_prompt(description, language), user_msg
                )
                if not ok:
                    st.error(err)
                else:
                    st.rerun()

    elif mode == "文档翻译":
        st.header("🌐 文档翻译")
        st.caption("粘贴英文技术文档片段，AI 翻译成流畅的中文")
        english_text = st.text_area(
            "英文文档内容",
            placeholder="Paste English technical documentation here...",
            height=180,
            key="translate_input",
        )
        if st.button("🚀 翻译成中文", type="primary", use_container_width=True):
            if not english_text.strip():
                st.warning("请粘贴需要翻译的英文内容")
            else:
                user_msg = (
                    english_text[:80] + "..."
                    if len(english_text) > 80
                    else english_text
                )
                ok, err = run_ai_and_save(
                    mode, generate_translation_prompt(english_text), user_msg
                )
                if not ok:
                    st.error(err)
                else:
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    hints = {
        "代码解释": "请在左侧侧边栏粘贴代码并点击「开始解释代码」。",
        "面试题生成": "请在左侧侧边栏选择技术方向与题型，点击「生成面试题」。",
        "学习路线规划": "请在左侧侧边栏填写目标岗位，点击「生成学习路线」。",
    }
    st.info(hints.get(mode, ""))
    st.markdown("</div>", unsafe_allow_html=True)

st.caption("💡 提示：切换模式会清空当前对话，历史记录永久保存在 chat_history.json")
