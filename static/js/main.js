let currentTeacherFile = null;
let currentStudentFile = null;
let quizData = null;
let currentQuestionIndex = 0;
let quizResults = [];
let quizTimer = null;
let questionStartTime = null;
let totalTimeRemaining = 0;

function switchMode(mode) {
    document.querySelectorAll('.nav-item').forEach(btn => btn.classList.remove('active'));
    event.currentTarget.classList.add('active');
    document.querySelectorAll('.mode-view').forEach(view => view.classList.add('hidden'));
    document.getElementById(`${mode}-mode`).classList.remove('hidden');
}

// File Upload Handling
function setupFileUpload(id, infoId, type) {
    const input = document.getElementById(id);
    const dropZone = document.getElementById(id.replace('file', 'drop-zone'));
    const info = document.getElementById(infoId);

    dropZone.addEventListener('click', () => input.click());

    const handleFile = async (file) => {
        info.textContent = `Selected: ${file.name}`;
        dropZone.style.borderColor = 'var(--secondary)';

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (type === 'teacher') currentTeacherFile = data.filename;
            if (type === 'student') currentStudentFile = data.filename;
            console.log(`Uploaded ${type} file:`, data.filename);
        } catch (e) {
            console.error("Upload failed", e);
            info.textContent = `Upload failed: ${e.message}`;
        }
    };

    input.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleFile(e.target.files[0]);
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--primary)';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--border)';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--secondary)';
        if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
    });
}

setupFileUpload('teacher-file', 'teacher-file-info', 'teacher');
setupFileUpload('student-file', 'student-file-info', 'student');

// Teacher Mode
async function generateWorksheet() {
    if (!currentTeacherFile) {
        alert('Please upload a PDF first.');
        return;
    }

    const btn = document.querySelector('.action-card button');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i data-lucide="loader-2" class="spin"></i> Generating...';
    btn.disabled = true;

    const mcqCount = document.getElementById('mcq-count').value;

    try {
        const response = await fetch('/api/generate-worksheet', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: currentTeacherFile,
                mcq_count: mcqCount
            })
        });
        const data = await response.json();

        if (data.status === 'success') {
            const resultsDiv = document.getElementById('teacher-results');
            resultsDiv.classList.remove('hidden');

            const resultsGrid = resultsDiv.querySelector('.results-grid');
            resultsGrid.innerHTML = `
                <div class="result-item">
                    <i data-lucide="file-text"></i>
                    <span>Worksheet.pdf</span>
                    <a href="${data.pdf_url}" download class="btn-sm">Download PDF</a>
                </div>
                <div class="result-item">
                    <i data-lucide="file-text"></i>
                    <span>Worksheet.md</span>
                    <a href="${data.worksheet_url}" download class="btn-sm">Download Markdown</a>
                </div>
            `;
            lucide.createIcons();
        } else {
            alert('Generation failed: ' + data.message);
        }
    } catch (e) {
        console.error(e);
        alert('Error generating worksheet');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
        lucide.createIcons();
    }
}

// Student Mode - Quiz Configuration
async function startStudentSession() {
    if (!currentStudentFile) {
        alert('Please upload a chapter PDF first.');
        return;
    }

    const numQuestions = parseInt(document.getElementById('quiz-num-questions').value);
    const difficulty = document.getElementById('quiz-difficulty').value;
    const timeLimit = parseInt(document.getElementById('quiz-time-limit').value);

    const btn = document.querySelector('#student-start-btn button');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i data-lucide="loader-2" class="spin"></i> Generating Quiz...';
    btn.disabled = true;

    try {
        const response = await fetch('/api/student/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: currentStudentFile,
                num_questions: numQuestions,
                difficulty: difficulty,
                time_limit: timeLimit * 60
            })
        });
        const data = await response.json();

        if (data.status === 'success') {
            quizData = data;
            quizData.allQuestions = data.questions;
            currentQuestionIndex = 0;
            quizResults = [];
            totalTimeRemaining = data.time_limit;

            document.getElementById('student-start-btn').classList.add('hidden');
            document.getElementById('student-dashboard').classList.remove('hidden');
            document.getElementById('student-chat').classList.remove('hidden');

            startQuizTimer();
            renderQuestion(currentQuestionIndex);
        } else {
            alert('Failed to start session: ' + data.message);
        }
    } catch (e) {
        console.error(e);
        alert('Error starting session: ' + e.message);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
        lucide.createIcons();
    }
}

function startQuizTimer() {
    questionStartTime = Date.now();
    updateTimerDisplay();

    quizTimer = setInterval(() => {
        totalTimeRemaining--;
        updateTimerDisplay();

        if (totalTimeRemaining <= 0) {
            clearInterval(quizTimer);
            finishQuiz();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const minutes = Math.floor(totalTimeRemaining / 60);
    const seconds = totalTimeRemaining % 60;
    document.querySelector('.timer').textContent =
        `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

function renderQuestion(index) {
    if (!quizData || index >= quizData.questions.length) return;

    const question = quizData.questions[index];
    questionStartTime = Date.now();

    document.querySelector('.question-text').textContent = `${index + 1}. ${question.text}`;
    document.getElementById('questions-count').textContent = `${index + 1}/${quizData.questions.length}`;

    let optionsHtml = '';
    question.options.forEach((opt, idx) => {
        const labels = ['A', 'B', 'C', 'D'];
        optionsHtml += `
            <button class="btn-secondary quiz-option" onclick="selectOption(this, '${opt.replace(/'/g, "\\'")}')">
                ${labels[idx]}. ${opt}
            </button>
        `;
    });
    document.querySelector('.options-grid').innerHTML = optionsHtml;
}

function selectOption(btn, option) {
    document.querySelectorAll('.quiz-option').forEach(b => {
        b.style.borderColor = 'var(--border)';
        b.style.background = 'rgba(255,255,255,0.05)';
        delete b.dataset.selected;
    });
    btn.style.borderColor = 'var(--primary)';
    btn.style.background = 'rgba(99, 102, 241, 0.1)';
    btn.dataset.selected = 'true';
}

async function submitAnswer() {
    const selectedBtn = document.querySelector('.quiz-option[data-selected="true"]');
    if (!selectedBtn) {
        alert('Please select an answer');
        return;
    }

    const userAnswer = selectedBtn.textContent.substring(3).trim();
    const question = quizData.questions[currentQuestionIndex];
    const timeTaken = Math.floor((Date.now() - questionStartTime) / 1000);

    const normalizeAnswer = (answer) => {
        return answer.replace(/^[A-D]\.\s*/i, '').trim().toLowerCase();
    };

    const normalizedUserAnswer = normalizeAnswer(userAnswer);
    const normalizedCorrectAnswer = normalizeAnswer(question.correct_answer);

    try {
        const response = await fetch('/api/student/submit-answer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question_id: question.id,
                user_answer: normalizedUserAnswer,
                correct_answer: normalizedCorrectAnswer,
                time_taken: timeTaken
            })
        });
        const data = await response.json();

        quizResults.push({
            question_id: question.id,
            topic: question.topic,
            is_correct: data.is_correct,
            time_taken: timeTaken,
            user_answer: userAnswer,
            correct_answer: question.correct_answer
        });

        if (data.is_correct) {
            selectedBtn.style.background = 'rgba(16, 185, 129, 0.2)';
            selectedBtn.style.borderColor = 'var(--secondary)';
        } else {
            selectedBtn.style.background = 'rgba(244, 63, 94, 0.2)';
            selectedBtn.style.borderColor = 'var(--accent)';
        }

        setTimeout(() => {
            currentQuestionIndex++;
            if (currentQuestionIndex < quizData.questions.length) {
                renderQuestion(currentQuestionIndex);
            } else {
                finishQuiz();
            }
        }, 1500);

    } catch (e) {
        console.error(e);
        alert('Error submitting answer');
    }
}

function nextQuestion() {
    currentQuestionIndex++;
    if (currentQuestionIndex < quizData.questions.length) {
        renderQuestion(currentQuestionIndex);
    } else {
        finishQuiz();
    }
}

async function finishQuiz() {
    if (quizTimer) clearInterval(quizTimer);

    try {
        const response = await fetch('/api/student/finish-quiz', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ results: quizResults })
        });
        const data = await response.json();

        showResults(data);
    } catch (e) {
        console.error(e);
        alert('Error finishing quiz');
    }
}

function showResults(data) {
    let feedbackHTML = '<div class="feedback-section"><h3>Question-by-Question Feedback</h3>';

    quizResults.forEach((result, idx) => {
        const question = quizData.allQuestions[idx];
        const isCorrect = result.is_correct;

        feedbackHTML += `
            <div class="feedback-item ${isCorrect ? 'correct' : 'incorrect'}">
                <h4>Question ${idx + 1}: ${isCorrect ? '✓ Correct' : '✗ Incorrect'}</h4>
                <p><strong>Question:</strong> ${question.text}</p>
                <p><strong>Your Answer:</strong> ${result.user_answer}</p>
                ${!isCorrect ? `<p><strong>Correct Answer:</strong> ${result.correct_answer}</p>` : ''}
                <div class="explanation">
                    <strong>Explanation:</strong> ${question.explanation || 'No explanation available.'}
                </div>
            </div>
        `;
    });

    feedbackHTML += '</div>';

    document.querySelector('.quiz-container').innerHTML = `
        <div style="text-align: center; padding: 2rem;">
            <h2 style="font-size: 2rem; margin-bottom: 1rem;">Quiz Completed! 🎉</h2>
            <div style="font-size: 4rem; font-weight: 700; color: var(--primary); margin: 2rem 0;">
                ${Math.round(data.score)}%
            </div>
            <p style="font-size: 1.2rem; margin-bottom: 2rem;">
                You got ${data.correct} out of ${data.total} questions correct
            </p>
            <p style="color: var(--text-muted);">
                Time taken: ${Math.floor(data.time_taken / 60)}m ${data.time_taken % 60}s
            </p>
            ${data.weak_areas.length > 0 ? `
                <div style="margin-top: 2rem; text-align: left; max-width: 400px; margin-left: auto; margin-right: auto;">
                    <h3 style="margin-bottom: 1rem;">Areas to Improve:</h3>
                    ${data.weak_areas.map(area => `
                        <div style="padding: 0.75rem; background: rgba(244, 63, 94, 0.1); border-radius: 0.5rem; margin-bottom: 0.5rem;">
                            ${area.topic} (${area.mistakes} mistakes)
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
        ${feedbackHTML}
    `;

    document.getElementById('accuracy-score').textContent = `${Math.round(data.score)}%`;
    document.getElementById('weak-areas-count').textContent = data.weak_areas.length;
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text) return;

    const chatWindow = document.getElementById('chat-window');

    chatWindow.innerHTML += `
        <div class="chat-message user">
            <p>${text}</p>
        </div>
    `;
    input.value = '';
    chatWindow.scrollTop = chatWindow.scrollHeight;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: text,
                filename: currentStudentFile
            })
        });
        const data = await response.json();

        let responseText = data.response;
        let followUpHtml = '';

        if (responseText.includes('Follow-up Questions:')) {
            const parts = responseText.split('Follow-up Questions:');
            const mainAnswer = parts[0].replace('Answer:', '').trim();
            const followUpSection = parts[1];

            const questionMatches = followUpSection.match(/\d+\.\s*(.+?)(?=\d+\.|$)/gs);

            if (questionMatches && questionMatches.length > 0) {
                followUpHtml = `
                    <div class="follow-up-section">
                        <div class="follow-up-section-title">Explore Further</div>
                        <div style="display: flex; flex-direction: column; gap: 0.75rem;">
                `;

                questionMatches.forEach((q, index) => {
                    const cleanQuestion = q.replace(/^\d+\.\s*/, '').trim();
                    followUpHtml += `
                        <button class="follow-up-btn" onclick="askFollowUp('${cleanQuestion.replace(/'/g, "\\'")}')">
                            ${cleanQuestion}
                        </button>
                    `;
                });

                followUpHtml += '</div></div>';
            }

            responseText = mainAnswer;
        }

        const formattedResponse = responseText.replace(/\n/g, '<br>');

        chatWindow.innerHTML += `
            <div class="chat-message ai">
                <p>${formattedResponse}</p>
                ${followUpHtml}
            </div>
        `;
        chatWindow.scrollTop = chatWindow.scrollHeight;
    } catch (e) {
        console.error(e);
        chatWindow.innerHTML += `
            <div class="chat-message ai">
                <p style="color:red">Error connecting to tutor.</p>
            </div>
        `;
    }
}

function askFollowUp(question) {
    const input = document.getElementById('chat-input');
    input.value = question;
    sendChatMessage();
}
