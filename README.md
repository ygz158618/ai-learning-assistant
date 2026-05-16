# AI 学习助手 (AI Learning Assistant)

一个基于 Streamlit + DeepSeek API 的 AI 学习助手网页工具，帮助新手快速理解技术概念、生成代码和翻译技术文档。

## 功能特性

- **概念解释模式**：用通俗易懂的语言解释技术名词，适合编程新手
- **代码生成模式**：根据自然语言描述生成 Python 或 JavaScript 代码（带详细注释）
- **文档翻译模式**：将英文技术文档翻译成流畅的中文
- **对话历史**：自动保存每轮问答，支持侧边栏点击查看历史记录
- **侧边栏配置**：输入 DeepSeek API Key，选择功能模式

## 技术栈

- Python + Streamlit（前端界面）
- requests（调用 DeepSeek Chat API）
- python-dotenv（管理 API Key）

## 安装与运行

### 1. 克隆或下载项目

```bash
git clone <your-repo>
cd ai-learning-assistant
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

### 3. 配置 API Key

复制 `.env.example` 为 `.env` 并填入你的 DeepSeek API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
DEEPSEEK_API_KEY=sk-your-real-api-key-here
```

> 获取 DeepSeek API Key：访问 [DeepSeek 平台](https://platform.deepseek.com/) 注册并创建 API Key。

### 4. 运行应用

```bash
streamlit run app.py
```

应用将在浏览器中自动打开（默认 http://localhost:8501）。

## 使用说明

1. 在侧边栏输入 DeepSeek API Key（首次使用需填写）
2. 选择功能模式（概念解释 / 代码生成 / 文档翻译）
3. 根据模式填写输入内容，点击「开始学习」按钮
4. AI 响应会显示在主界面，同时自动保存到侧边栏历史记录
5. 点击历史记录可重新查看之前的问答详情

## 项目结构

```
ai-learning-assistant/
├── app.py              # 主程序（Streamlit 界面 + API 调用）
├── requirements.txt    # Python 依赖
├── .env.example        # API Key 配置示例
└── README.md           # 项目说明
```

## 注意事项

- API Key 存储在 `.env` 文件中，切勿提交到 Git
- DeepSeek API 按 token 计费，合理使用
- 代码生成仅供参考，实际使用前请自行测试
- 支持 Python 和 JavaScript 代码生成

## License

MIT License

---

Made with ❤️ for AI learning beginners.