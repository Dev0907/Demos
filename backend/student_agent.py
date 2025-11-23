from langgraph.graph import StateGraph, END
from backend.state import StudentState, Question
from backend.vector_store import search_documents, add_documents
from backend.llm import generate_json, generate_text
import pypdf
import random

# Node: PDF Extraction & Embedding (Same as Teacher)
def extract_pdf_node(state: StudentState):
    print(f"Extracting text for student from {state['pdf_path']}...")
    text = ""
    try:
        reader = pypdf.PdfReader(state['pdf_path'])
        for page in reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        text = "Error reading PDF content."

    chunks = [chunk for chunk in text.split('\n\n') if len(chunk) > 50]
    if chunks:
        add_documents(chunks, {"source": state['pdf_path'], "pdf_path": state['pdf_path']})
        
    return {"extracted_text": text}

# Node: Generate Quiz Questions
def generate_quiz_questions_node(state: StudentState):
    print("Generating quiz questions...")
    
    num_questions = state.get('num_questions', 5)
    difficulty = state.get('difficulty', 'Medium')
    pdf_path = state.get('pdf_path', '')
    
    # Search for documents from THIS specific PDF only
    context_docs = search_documents("main concepts and topics", limit=5, pdf_path=pdf_path)
    context_text = "\n".join([doc['text'] for doc in context_docs])
    
    if not context_text.strip():
        # Fallback if no context found
        context_text = "No specific context available. Please use general knowledge."
    
    prompt = f"""
    Based on the following context from the uploaded document, generate {num_questions} multiple choice questions.
    Difficulty level: {difficulty}
    
    For {difficulty} difficulty:
    - Easy: Basic recall and understanding questions
    - Medium: Application and analysis questions  
    - Hard: Complex synthesis and evaluation questions
    
    Context from uploaded PDF:
    {context_text[:3000]}
    
    Output format (JSON array):
    [
        {{
            "id": 1,
            "text": "Question text",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Correct Option Text (must match one of the options exactly)",
            "explanation": "Why this is correct",
            "difficulty": "{difficulty}",
            "type": "MCQ",
            "topic": "Topic Name"
        }}
    ]
    
    IMPORTANT: The correct_answer must EXACTLY match one of the options in the options array.
    Generate questions ONLY from the provided context, not from general knowledge.
    """
    
    questions = generate_json(prompt)
    if not questions or not isinstance(questions, list):
        # Fallback
        questions = [{
            "id": 1,
            "text": "Could not generate questions from the uploaded document. Please check the PDF content.",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "Error in generation.",
            "difficulty": difficulty,
            "type": "MCQ",
            "topic": "Error"
        }]
    
    # Assign sequential IDs
    for i, q in enumerate(questions):
        q['id'] = i + 1
        
    return {"generated_questions": questions, "current_question_index": 0}

# Node: Analysis (After answer)
def analyze_performance_node(state: StudentState):
    # Simple mock analysis for now
    return {"weak_areas": ["Cell Organelles"], "learning_path": ["Review Chapter 3"]}

# Build Graph
workflow = StateGraph(StudentState)

workflow.add_node("extract_pdf", extract_pdf_node)
workflow.add_node("generate_quiz_questions", generate_quiz_questions_node)
workflow.add_node("analyze_performance", analyze_performance_node)

workflow.set_entry_point("extract_pdf")
workflow.add_edge("extract_pdf", "generate_quiz_questions")
workflow.add_edge("generate_quiz_questions", END) 

student_graph = workflow.compile()

# Separate Chat Function with Tool Support
def chat_with_pdf(query: str, pdf_path: str):
    """Enhanced chat with tool support for math, plots, tables, and diagrams"""
    from backend.tools import math_solver, plot_generator, table_formatter, diagram_generator
    
    # Detect if query needs tools
    query_lower = query.lower()
    needs_math = any(word in query_lower for word in ['solve', 'equation', 'calculate', 'evaluate', 'math'])
    needs_plot = any(word in query_lower for word in ['plot', 'graph', 'visualize', 'chart'])
    needs_table = any(word in query_lower for word in ['table', 'compare', 'list'])
    needs_diagram = any(word in query_lower for word in ['flowchart', 'diagram', 'steps', 'process'])
    
    # RAG - Get context from specific PDF
    docs = search_documents(query, limit=3, pdf_path=pdf_path)
    context = "\n".join([d['text'] for d in docs])
    
    # Build enhanced prompt
    tool_instructions = ""
    if needs_math:
        tool_instructions += "\nIf the question involves solving equations, provide the equation in the format 'EQUATION: <equation>'"
    if needs_plot:
        tool_instructions += "\nIf visualization is needed, provide the function in the format 'PLOT: <function>'"
    if needs_diagram:
        tool_instructions += "\nIf a process needs to be shown, list steps clearly."
    
    prompt = f"""
    You are a helpful tutor. Answer the student's question based on the context provided.
    If the answer is not in the context, say so but try to help with general knowledge.
    {tool_instructions}
    
    Context:
    {context}
    
    Student Question: {query}
    
    After answering, generate 3 follow-up questions that the student might want to ask to deepen their understanding.
    Format the output as:
    Answer: [Your Answer]
    
    Follow-up Questions:
    1. [Question 1]
    2. [Question 2]
    3. [Question 3]
    """
    
    response_text = generate_text(prompt)
    
    # Post-process to add tool outputs
    tool_outputs = []
    
    # Check for equations to solve
    if "EQUATION:" in response_text:
        import re
        equations = re.findall(r'EQUATION:\s*([^\n]+)', response_text)
        for eq in equations:
            result = math_solver.solve_equation(eq.strip())
            if 'solutions' in result:
                tool_outputs.append(f"\n\n**Solution:** {', '.join(result['solutions'])}")
    
    # Check for functions to plot
    if "PLOT:" in response_text:
        import re
        functions = re.findall(r'PLOT:\s*([^\n]+)', response_text)
        for func in functions:
            result = plot_generator.create_function_plot(func.strip())
            if 'image_base64' in result:
                tool_outputs.append(f"\n\n**Graph:** [Plot generated - see visualization]")
                # In a real implementation, you'd return the image data
    
    # Combine response with tool outputs
    final_response = response_text
    if tool_outputs:
        final_response += "\n\n---\n**Tool Results:**" + "".join(tool_outputs)
    
    return final_response
