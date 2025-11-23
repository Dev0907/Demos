from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import os
import shutil

app = FastAPI(title="EduMind Agent")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    file_location = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    return {"filename": file.filename, "path": file_location}

@app.post("/api/generate-worksheet")
async def generate_worksheet_endpoint(request: Request):
    data = await request.json()
    filename = data.get("filename")
    mcq_count = int(data.get("mcq_count", 10))
    
    if not filename:
        return {"status": "error", "message": "No file selected"}
        
    from backend.teacher_agent import teacher_graph
    
    # Initial state
    initial_state = {
        "pdf_path": f"temp/{filename}",
        "extracted_text": "",
        "topics": [],
        "mcq_count": mcq_count,
        "include_subjective": True,
        "generated_questions": [],
        "worksheet_markdown": "",
        "answer_key_markdown": ""
    }
    
    # Run Graph
    result = teacher_graph.invoke(initial_state)
    
    # Save generated worksheet markdown
    md_output_path = "static/generated/worksheet.md"
    os.makedirs("static/generated", exist_ok=True)
    with open(md_output_path, "w", encoding='utf-8') as f:
        f.write(result['worksheet_markdown'])
        
    return {
        "status": "success", 
        "worksheet_url": f"/{md_output_path}",
        "pdf_url": f"/{result['pdf_path']}" if result.get('pdf_path') else None,
        "preview": result['worksheet_markdown'][:500] + "..."
    }

@app.post("/api/student/start")
async def start_student_session(request: Request):
    data = await request.json()
    filename = data.get("filename")
    num_questions = int(data.get("num_questions", 5))
    difficulty = data.get("difficulty", "Medium")
    time_limit = int(data.get("time_limit", 600))  # Default 10 minutes
    
    if not filename:
        return {"status": "error", "message": "No file selected"}

    from backend.student_agent import student_graph
    
    initial_state = {
        "pdf_path": f"temp/{filename}",
        "extracted_text": "",
        "current_topic": "General",
        "quiz_history": [],
        "current_question": None,
        "weak_areas": [],
        "learning_path": [],
        "num_questions": num_questions,
        "difficulty": difficulty,
        "time_limit": time_limit,
        "generated_questions": [],
        "current_question_index": 0,
        "score": 0,
        "total_time_taken": 0
    }
    
    # Run Graph to generate all questions
    result = student_graph.invoke(initial_state)
    
    return {
        "status": "success",
        "questions": result['generated_questions'],
        "time_limit": time_limit,
        "num_questions": num_questions,
        "difficulty": difficulty
    }

@app.post("/api/student/submit-answer")
async def submit_answer(request: Request):
    data = await request.json()
    question_id = data.get("question_id")
    user_answer = data.get("user_answer")
    correct_answer = data.get("correct_answer")
    time_taken = data.get("time_taken", 0)
    
    is_correct = user_answer == correct_answer
    
    return {
        "is_correct": is_correct,
        "correct_answer": correct_answer
    }

@app.post("/api/student/finish-quiz")
async def finish_quiz(request: Request):
    data = await request.json()
    quiz_results = data.get("results", [])
    
    total_questions = len(quiz_results)
    correct_answers = sum(1 for r in quiz_results if r.get("is_correct"))
    score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    total_time = sum(r.get("time_taken", 0) for r in quiz_results)
    
    # Analyze weak areas
    weak_topics = {}
    for r in quiz_results:
        if not r.get("is_correct"):
            topic = r.get("topic", "Unknown")
            weak_topics[topic] = weak_topics.get(topic, 0) + 1
    
    weak_areas = sorted(weak_topics.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "status": "success",
        "score": score_percentage,
        "correct": correct_answers,
        "total": total_questions,
        "time_taken": total_time,
        "weak_areas": [{"topic": topic, "mistakes": count} for topic, count in weak_areas[:3]]
    }

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    query = data.get("query")
    filename = data.get("filename", "sample.pdf") # Default if not provided
    
    from backend.student_agent import chat_with_pdf
    
    response_text = chat_with_pdf(query, f"temp/{filename}")
    
    return {"response": response_text}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
