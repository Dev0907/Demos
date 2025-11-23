from typing import List, TypedDict, Optional

class Question(TypedDict):
    id: int
    text: str
    options: Optional[List[str]]
    correct_answer: str
    explanation: str
    difficulty: str
    type: str # 'MCQ' or 'Subjective'
    topic: str

class TeacherState(TypedDict):
    pdf_path: str
    extracted_text: str
    topics: List[str]
    mcq_count: int
    include_subjective: bool
    generated_questions: List[Question]
    worksheet_markdown: str
    answer_key_markdown: str
    pdf_path: str  # Path to generated PDF

class StudentState(TypedDict):
    pdf_path: str
    extracted_text: str
    current_topic: str
    quiz_history: List[dict] # {question_id, user_answer, is_correct, time_taken}
    current_question: Optional[Question]
    weak_areas: List[str]
    learning_path: List[str]
    # Quiz configuration
    num_questions: int
    difficulty: str
    time_limit: int  # in seconds
    # Quiz tracking
    generated_questions: List[Question]
    current_question_index: int
    score: int
    total_time_taken: int
