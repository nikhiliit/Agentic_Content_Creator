---
title: Content_Generator
app_file: app.py
sdk: gradio
sdk_version: 5.34.2
---
# Content Generator - AI Blog Writing Engine

An automated blog content generation system powered by AI agents, inspired by advanced research agent architectures. This engine creates high-quality, SEO-optimized blog posts from topic ideas using a multi-agent pipeline.

## 🚀 Features

- **Multi-Agent Pipeline**: Specialized AI agents for research, writing, and editing
- **Dual AI Models**: Choose between free Gemini 2.5 Flash or paid GPT-4o-mini
- **Dual Search Providers**: Free Gemini built-in search or paid OpenAI WebSearchTool
- **Web Research Integration**: Automated web searches for comprehensive content
- **Multiple Writing Styles**: Three distinct writing agents (Professional, Conversational, Analytical)
- **Content Safety Guardrails**: Automatic filtering of sensitive political topics
- **Structured Output**: Pydantic models ensure consistent, parseable results
- **SEO Optimization**: Automatic meta descriptions, slugs, and tags
- **Professional Formatting**: Industry-standard blog post structure
- **Async Processing**: Concurrent operations for speed and efficiency

## 🏗️ Architecture

The system follows a 5-stage pipeline:

1. **Query → Plan Searches**: Research planner agent creates structured search queries
2. **Perform Searches**: Web research agent executes parallel searches
3. **Write Reports**: Three specialized writer agents create blog drafts
4. **Pick Best Write Up**: Content editor agent evaluates and selects optimal content
5. **Transform to Blog Format**: Formatter agent creates publication-ready blog posts

## 📦 Installation

### Prerequisites
- Python 3.8+
- Google AI API key (for free Gemini Flash model)

### Local Development Setup

1. **Navigate to the project directory**:
   ```bash
   cd /Users/nikk/Desktop/projects/Content_Generator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   # Option 1: Interactive setup (recommended)
   python setup.py

   # Option 2: Manual setup
   cp env.example .env
   # Edit the .env file with your OpenAI API key
   ```

4. **Get your Google AI API key**:
   - Visit: https://aistudio.google.com/app/apikey
   - Create a new API key
   - The setup script will guide you through adding it

**Why Google Gemini?**
- **Completely FREE** - Unlike paid OpenAI models
- Excellent performance for blog writing tasks
- Built-in safety features and content filtering

### HF Spaces Deployment

For Hugging Face Spaces deployment:

1. **Create a new Space** on [Hugging Face](https://huggingface.co/spaces)
2. **Upload your files** or connect your GitHub repo
3. **Set environment variables** in Space secrets:
   - Name: `GOOGLE_API_KEY`
   - Value: `your-google-gemini-api-key-here`
4. **The root-level `app.py` will automatically import from the organized structure**
5. **The app will automatically detect HF Spaces environment**

**Note**: Uses **Gemini 2.0 Flash** (free model) instead of OpenAI GPT

**Note**: HF Spaces runs the root-level `app.py` which imports from the organized `src/` structure.

## 🎯 Usage

## Web Interface (Recommended)

Launch the modern web interface:

```bash
python run.py
# or
python src/web/web_app.py
```

Then open your browser to `http://localhost:7860` for a stunning experience featuring:

### 🎨 **Modern UI Design**
- **Hero Header**: Eye-catching gradient design with animated background
- **Two-Panel Layout**: Efficient use of horizontal space with control panel and content area
- **Responsive Design**: Adapts beautifully to desktop and mobile screens
- **Professional Styling**: Modern cards, gradients, and smooth animations

### ⚡ **Interactive Features**
- **Real-time Generation**: Live status updates and progress feedback
- **Visual Blog Preview**: Professional HTML formatting with SEO elements
- **Model Selection**: Choose between Gemini 2.5 Flash (free) or GPT-4o-mini (paid)
- **Search Provider Options**: Select Gemini search (free) or OpenAI WebSearchTool (paid)
- **Configurable Research**: Slider control for search depth (1-7 searches)
- **Smart Save System**: One-click JSON export with metadata
- **Content Safety**: Visual indicators for filtered sensitive content

### 📱 **User Experience**
- **Intuitive Controls**: Clean input groups with helpful labels
- **Status Indicators**: Color-coded messages (success/error/warning)
- **Feature Showcase**: Interactive cards highlighting capabilities
- **Sticky Sidebar**: Control panel stays accessible while scrolling

## Command Line Interface

For automation and scripting, use the CLI:

```bash
# Basic usage (free Gemini search)
python run.py --cli "The Future of Artificial Intelligence in 2025"

# Use GPT-4o-mini model with Gemini search
python run.py --cli "Machine Learning Best Practices" --model gpt-4o-mini

# Use paid OpenAI search with Gemini model
python run.py --cli "Digital Marketing Trends" --search-provider openai --model gemini

# Configure everything: model, search provider, and depth
python run.py --cli "Sustainable Technology" --model gpt-4o-mini --search-provider openai --searches 7

# Save results with custom settings
python run.py --cli "AI Ethics" --output blog.json --model gemini --search-provider gemini --searches 5

# Direct CLI usage
python src/cli/cli.py "Your topic" --model gpt-4o-mini --search-provider openai --searches 3
```

### CLI Examples

```bash
# Technology topics (comprehensive research)
python cli.py "How Cloud Computing is Changing Business" --searches 6

# Business topics (focused research)
python cli.py "Digital Marketing Trends for 2025" --searches 3

# Educational content (detailed research)
python cli.py "Python Best Practices for Data Science" --searches 5

# Industry insights (broad research)
python cli.py "Sustainable Technology Solutions" --searches 7
```

### Safety Features

The engine automatically filters out sensitive topics:

❌ **Blocked**: Political topics, elections, government policies
✅ **Allowed**: Technology, business, education, industry trends

## 🔧 Configuration

### Adjusting Search Depth
Modify `HOW_MANY_SEARCHES` in `agents.py`:
```python
HOW_MANY_SEARCHES = 5  # Increase for more comprehensive research
```

### Custom Writing Styles
Add new writer agents in `agents.py`:
```python
WRITER_4_INSTRUCTIONS = """Your custom writing style..."""
writer_agent_4 = Agent(name="CustomWriter", instructions=WRITER_4_INSTRUCTIONS, ...)
```

## 📁 Project Structure

```
Content_Generator/
├── app.py              # 🚀 HF Spaces entry point (imports from src/web/)
├── run.py              # 🚀 Local launcher (web/cli/setup)
├── .gitignore          # 🔒 Git ignore rules
├── README.md           # 📖 Documentation
├── requirements.txt    # 📦 Dependencies
├── config/
│   └── env.example     # 🔐 Environment template
├── scripts/
│   └── setup.py        # ⚙️ Setup wizard
└── src/
    ├── __init__.py
    ├── core/           # 🧠 Core business logic
    │   ├── __init__.py
    │   ├── schemas.py      # 📋 Pydantic data models
    │   ├── blog_agents.py  # 🤖 AI agent definitions
    │   └── orchestrator.py # 🎯 Pipeline coordination
    ├── web/            # 🌐 Web interface
    │   ├── __init__.py
    │   └── web_app.py       # 🎨 Modern Gradio UI
    ├── cli/            # 💻 Command line interface
    │   ├── __init__.py
    │   └── cli.py          # ⌨️ CLI interface
    └── utils/          # 🔧 Utility functions
        ├── __init__.py
        ├── tools.py        # 🛠️ Utility functions
        └── guardrails.py   # 🛡️ Content safety filters
```

## 🧠 Agent Roles

### ResearchPlanner (Gemini Flash)
- Analyzes topics and creates research strategies
- Generates targeted web search queries
- Ensures comprehensive coverage of subjects
- Powered by Google's free Gemini 2.0 Flash model

### WebResearcher (Gemini Flash)
- Executes web searches using OpenAI's WebSearchTool
- Summarizes findings concisely with AI analysis
- Focuses on actionable insights and data
- Powered by Google's free Gemini 2.0 Flash model

### Writing Agents (3 styles - Gemini Flash)
- **ProfessionalWriter**: Clear, authoritative content
- **ConversationalWriter**: Engaging, relatable tone
- **AnalyticalWriter**: Data-driven, trend-focused
- All powered by Google's free Gemini 2.0 Flash model

### ContentEditor (Gemini Flash)
- Evaluates multiple drafts intelligently
- Applies safety guardrails automatically
- Selects optimal content based on quality metrics
- Powered by Google's free Gemini 2.0 Flash model

### BlogFormatter (Gemini Flash)
- Creates SEO-friendly elements automatically
- Formats content for professional publishing
- Generates metadata, tags, and structured content
- Powered by Google's free Gemini 2.0 Flash model

## 🔒 Safety & Compliance

- **Political Content Filter**: Automatically blocks sensitive topics
- **Content Validation**: Structured outputs prevent malformed content
- **Error Handling**: Robust error management throughout pipeline
- **Rate Limiting**: Built-in delays prevent API abuse

## 📊 Output Format

Generated blog posts include:

- **Title**: SEO-optimized headline
- **Meta Description**: Search-friendly summary
- **URL Slug**: SEO-friendly permalink
- **HTML Content**: Properly formatted blog post
- **Reading Time**: Estimated duration
- **Tags**: Categorization keywords
- **Featured Image Alt**: Accessibility text

## 🚦 Cost Considerations

- **WebSearchTool**: ~$0.025 per search (OpenAI pricing)
- **GPT-4o-mini**: Low-cost for planning and writing
- **Concurrent Processing**: Multiple searches run simultaneously

Monitor usage at: https://platform.openai.com/usage

## 🔍 Troubleshooting

### Common Issues

**"Missing API Key"**
```bash
# Ensure .env file exists with:
OPENAI_API_KEY=sk-your-key-here
```

**"Topic Safety Check Failed"**
- Avoid political or controversial topics
- Focus on technology, business, education

**"Import Errors"**
```bash
pip install -r requirements.txt
```

## 🤝 Contributing

The modular architecture makes it easy to extend:

- Add new writing styles
- Integrate additional research tools
- Create custom formatting templates
- Add new safety guardrails

## 🚀 Deployment

### Hugging Face Spaces

Deploy the web interface to Hugging Face Spaces:

1. **Create a new Space** on [Hugging Face](https://huggingface.co/spaces)
2. **Upload your files** or connect your GitHub repo
3. **Set environment variables** in Space secrets:
   - `OPENAI_API_KEY`: Your OpenAI API key
4. **Set the startup command**:
   ```bash
   python app.py
   ```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your API keys

# Run web interface
python app.py

# Or use CLI
python cli.py "Your blog topic" --searches 4
```

## 📊 Performance Notes

- **Search Depth Impact**: More searches = more comprehensive research but slower generation
- **Recommended Settings**:
  - Simple topics: 2-3 searches
  - Complex topics: 4-5 searches
  - Research-heavy topics: 6-7 searches

## 🔒 Security & Compliance

- **API Key Protection**: Never commit API keys to version control
- **Content Filtering**: Automatic blocking of sensitive topics
- **Rate Limiting**: Built-in delays prevent API abuse
- **Data Privacy**: Generated content stored locally only

## 📝 License

This project demonstrates advanced AI agent orchestration patterns. Use responsibly and in compliance with OpenAI's terms of service.

## 🙏 Acknowledgments

Inspired by OpenAI Agents SDK research patterns and multi-agent system architectures. Gradio interface design inspired by modern web application patterns.
