# 🧠 EduMind Agent

**EduMind Agent** is an AI-powered autonomous learning and assessment platform that revolutionizes educational content creation and adaptive learning. Built with LangGraph, FastAPI, and Google's Gemini AI, it provides two powerful modes: **Teacher Mode** for generating comprehensive worksheets and **Student Mode** for adaptive quizzing and interactive learning.

---

## 🌟 Features

### 🎓 Teacher Mode
- **Automated Worksheet Generation**: Upload PDF study materials (NCERT chapters, reference materials) and automatically generate structured worksheets
- **Multi-Format Questions**: Creates both Multiple Choice Questions (MCQs) and subjective questions
- **Intelligent Topic Segmentation**: Automatically identifies and segments topics from uploaded content
- **Customizable Output**: Configure number of questions, difficulty levels, and question types
- **PDF Export**: Generates professional PDF worksheets with answer keys
- **Smart Question Distribution**: Mixed difficulty levels (Easy, Medium, Hard) for comprehensive assessment

### 🎯 Student Mode
- **Adaptive Quiz System**: AI-generated quizzes tailored to uploaded study materials
- **Configurable Sessions**: Customize number of questions, difficulty level, and time limits
- **Real-time Feedback**: Instant answer validation with explanations
- **Performance Analytics**: Track accuracy, weak areas, and learning progress
- **AI Tutor Chat**: Interactive Q&A with context-aware responses from uploaded PDFs
- **Enhanced Learning Tools**:
  - Mathematical equation solver
  - Function plotting and visualization
  - Automatic follow-up question generation

### 🔧 Advanced Tools
- **Math Solver**: Symbolic equation solving using SymPy
- **Plot Generator**: Dynamic function visualization with matplotlib
- **Table Formatter**: Clean data presentation
- **Diagram Generator**: Flowchart creation for process visualization
- **Vector Store**: Qdrant-based document retrieval for contextual responses

---

## 🏗️ Architecture

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python)
- **AI/ML**:
  - `langgraph` - Agentic workflow orchestration
  - `langchain` & `langchain-openai` - LLM integration
  - `google-generativeai` - Gemini 2.0 Flash model
  - `sentence-transformers` - Text embeddings (all-MiniLM-L6-v2)
  - `torch` - Deep learning framework
- **Vector Database**: Qdrant Cloud for document storage and retrieval
- **Document Processing**:
  - `pypdf` - PDF text extraction
  - `python-docx` - Word document support
  - `openpyxl` - Excel file handling
  - `pandas` - Data manipulation

#### Frontend
- **HTML5** with Jinja2 templating
- **CSS3** with modern aesthetics


### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│  (HTML/CSS/JS - Templates/Static Files)                      │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST API
┌───────────────────────▼─────────────────────────────────────┐
│                     FastAPI Server                           │
│                      (main.py)                               │
├──────────────────────┬──────────────────────┬───────────────┤
│   Teacher Endpoints  │  Student Endpoints   │ Chat Endpoint │
└──────────────────────┴──────────────────────┴───────────────┘
         │                        │                    │
         ▼                        ▼                    ▼
┌────────────────┐    ┌────────────────────┐   ┌──────────────┐
│ Teacher Agent  │    │  Student Agent     │   │ Chat System  │
│ (LangGraph)    │    │  (LangGraph)       │   │ (RAG-based)  │
└────────┬───────┘    └─────────┬──────────┘   └──────┬───────┘
         │                      │                      │
         ├──────────────────────┴──────────────────────┤
         │                                             │
         ▼                                             ▼
┌─────────────────┐                          ┌─────────────────┐
│  Gemini 2.0     │                          │  Qdrant Vector  │
│  Flash Model    │                          │  Store (Cloud)  │
│  (LLM)          │                          │  (Embeddings)   │
└─────────────────┘                          └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│               Advanced Tools Layer                           │
│  • Math Solver    • Plot Generator    • PDF Exporter        │
│  • Table Formatter    • Diagram Generator                    │
└─────────────────────────────────────────────────────────────┘
```

### Agent Workflows

#### Teacher Agent Pipeline
```
PDF Upload → Extract Text → Segment Topics → Generate MCQs → 
Generate Subjective Questions → Format Worksheet → Export PDF
```

#### Student Agent Pipeline
```
PDF Upload → Extract & Embed → Generate Quiz Questions → 
Present Questions → Validate Answers → Analyze Performance
```

---

## 📁 Project Structure

```
Demos/
├── backend/
│   ├── __init__.py
│   ├── config.py              # Configuration & API keys
│   ├── llm.py                 # Gemini LLM interface
│   ├── state.py               # LangGraph state definitions
│   ├── teacher_agent.py       # Teacher mode workflow
│   ├── student_agent.py       # Student mode workflow
│   ├── tools.py               # Advanced tools (math, plots, etc.)
│   └── vector_store.py        # Qdrant vector database interface
│
├── static/
│   ├── css/
│   │   ├── style.css          # Main application styles
│   │   └── chat.css           # Chat interface styles
│   ├── js/
│   │   └── main.js            # Frontend JavaScript
│   └── generated/             # Generated worksheets & outputs
│
├── templates/
│   └── index.html             # Main application template
│
├── temp/                      # Uploaded PDF storage
│
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (API keys)
└── README.md                  # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)
- **Git** (for cloning)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd Demos
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   QDRANT_URL=your_qdrant_url
   QDRANT_API_KEY=your_qdrant_api_key
   ```

   **How to get API keys:**
   - **Gemini API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - **Qdrant**: Sign up at [Qdrant Cloud](https://cloud.qdrant.io/) for free tier

5. **Run the application**
   ```bash
   python main.py
   ```

   The server will start at `http://127.0.0.1:8000`

6. **Access the application**
   
   Open your browser and navigate to `http://127.0.0.1:8000`

---

## 📖 Usage Guide

### Teacher Mode

1. **Upload Study Material**
   - Click on "Teacher Mode" in the sidebar
   - Drag & drop a PDF file or click to browse
   - Supported: NCERT chapters, textbooks, reference materials

2. **Configure Worksheet Settings**
   - **MCQ Count**: Choose 10, 20, or 50 questions
   - **Difficulty**: Select Mixed, Easy, or Hard
   - **Options**: 
     - ✅ Include Subjective Questions
     - ✅ Generate Answer Key

3. **Generate Worksheet**
   - Click "Generate Worksheet"
   - Wait for the AI to process (may take 1-2 minutes)
   - Download the generated PDF worksheet and answer key

4. **Output Files**
   - Worksheet PDF with all questions
   - Answer key with explanations
   - Markdown version in `static/generated/`

### Student Mode

1. **Upload Study Material**
   - Click on "Student Mode" in the sidebar
   - Upload your chapter PDF

2. **Configure Quiz Settings**
   - **Number of Questions**: 5, 10, 15, or 20
   - **Difficulty Level**: Easy, Medium, or Hard
   - **Time Limit**: 5-30 minutes

3. **Take the Quiz**
   - Click "Start Adaptive Quiz"
   - Answer questions one by one
   - Get instant feedback on each answer
   - View explanations for correct answers

4. **Review Performance**
   - See your accuracy score
   - Identify weak areas
   - Review missed questions

5. **Use AI Tutor Chat**
   - After uploading a PDF, the chat interface becomes available
   - Ask questions about the content
   - Get contextual answers with follow-up suggestions
   - Request math solutions, plots, or explanations

### AI Chat Features

**Example Queries:**
- "Explain the concept of photosynthesis"
- "Solve the equation: x^2 - 5x + 6 = 0"
- "Plot the function: sin(x) + cos(x)"
- "Compare mitochondria and chloroplasts in a table"
- "Show me the steps for cellular respiration"

---

## 🔧 API Endpoints

### Public Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application interface |
| `/api/upload` | POST | Upload PDF file |
| `/api/generate-worksheet` | POST | Generate worksheet (Teacher Mode) |
| `/api/student/start` | POST | Start quiz session (Student Mode) |
| `/api/student/submit-answer` | POST | Submit answer and get validation |
| `/api/student/finish-quiz` | POST | Complete quiz and get results |
| `/api/chat` | POST | Chat with AI tutor |

### Request Examples

**Upload File:**
```bash
curl -X POST "http://127.0.0.1:8000/api/upload" \
  -F "file=@chapter.pdf"
```

**Generate Worksheet:**
```bash
curl -X POST "http://127.0.0.1:8000/api/generate-worksheet" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "chapter.pdf",
    "mcq_count": 10
  }'
```

**Chat Query:**
```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain Newton's laws",
    "filename": "physics.pdf"
  }'
```

---

## 🧪 Advanced Features

### Mathematical Problem Solving

The system can solve equations and evaluate expressions:

```python
# Automatically triggered when queries contain math keywords
Query: "Solve x^2 - 4 = 0"
Response: Solutions: [2, -2]
```

### Function Plotting

Visualize mathematical functions:

```python
Query: "Plot x^2 + 2*x + 1"
# Generates a graph with proper axes and grid
```

### Intelligent Follow-ups

After each answer, the AI generates 3 follow-up questions to deepen understanding:

```
Answer: [Your Answer]

Follow-up Questions:
1. How does this concept relate to...?
2. Can you explain the practical application of...?
3. What would happen if...?
```

---

## 🔐 Security & Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | ✅ Yes |
| `QDRANT_URL` | Qdrant cloud instance URL | ✅ Yes |
| `QDRANT_API_KEY` | Qdrant authentication key | ✅ Yes |

### Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use environment-specific configurations** for development/production
3. **Rotate API keys** regularly
4. **Implement rate limiting** for production deployments
5. **Sanitize file uploads** to prevent malicious files

---

## 🎨 Customization

### Changing the AI Model

Edit `backend/config.py`:
```python
GEMINI_MODEL_NAME = "gemini-2.0-flash"  # Change to desired model
```

### Adjusting Question Generation

Modify prompts in:
- `backend/teacher_agent.py` - Worksheet generation
- `backend/student_agent.py` - Quiz generation

### Customizing UI Theme

Edit `static/css/style.css` to change:
- Color scheme
- Typography
- Layout and spacing
- Animations

---

## 🐛 Troubleshooting

### Common Issues

**Issue: "Error reading PDF content"**
- **Solution**: Ensure the PDF is not password-protected and contains extractable text

**Issue: "Connection to Qdrant failed"**
- **Solution**: Verify `QDRANT_URL` and `QDRANT_API_KEY` in `.env` file

**Issue: "Gemini API rate limit exceeded"**
- **Solution**: Wait a few minutes or upgrade your API quota

**Issue: "Torch/CUDA errors"**
- **Solution**: CPU-only mode is sufficient. Install with: `pip install torch --index-url https://download.pytorch.org/whl/cpu`

**Issue: "Module not found"**
- **Solution**: Reinstall dependencies: `pip install -r requirements.txt`

---

## 📊 Performance Optimization

### For Large PDFs
- PDFs are chunked into smaller segments for better processing
- Vector embeddings are cached in Qdrant
- Consider splitting very large documents (>100 pages)

### For Faster Response Times
- Use a local Qdrant instance instead of cloud
- Enable GPU acceleration for torch if available
- Increase API rate limits

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Add docstrings to all functions
- Test thoroughly before submitting
- Update documentation for new features

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Google Gemini AI** for powerful language model capabilities
- **LangChain & LangGraph** for agentic workflow framework
- **Qdrant** for vector database infrastructure
- **FastAPI** for modern web framework
- **Open source community** for various tools and libraries

---

## 📧 Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Email: [your-email@example.com]
- Documentation: [Wiki/Docs URL]

---

## 🗺️ Roadmap

### Upcoming Features
- [ ] Multi-language support
- [ ] Support for more document formats (Word, Excel, PowerPoint)
- [ ] Advanced analytics dashboard
- [ ] Student progress tracking over time
- [ ] Collaborative learning features
- [ ] Mobile app version
- [ ] Integration with popular LMS platforms
- [ ] Voice-based question answering
- [ ] Gamification elements (badges, leaderboards)
- [ ] Export to multiple formats (Word, LaTeX, HTML)

---

## 📸 Screenshots

### Teacher Mode
![Teacher Mode Interface](static/screenshots/teacher-mode.png)

### Student Mode
![Student Mode Quiz](static/screenshots/student-mode.png)

### AI Tutor Chat
![Chat Interface](static/screenshots/chat-interface.png)

---

## 💡 Use Cases

1. **Educators**: Generate practice worksheets from textbook chapters
2. **Students**: Self-assessment and adaptive learning
3. **Tutors**: Create personalized question banks
4. **Educational Institutions**: Automated content generation
5. **Self-learners**: Interactive learning with AI assistance

---

## ⚡ Quick Start Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Access at
http://127.0.0.1:8000
```

---


