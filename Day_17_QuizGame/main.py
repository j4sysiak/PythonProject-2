from question_model import Question
from data import question_data
from quiz_brain import QuizBrain

# 1. Tworzymy pustą listę na obiekty pytań
question_bank =[]

# 2. Przerabiamy surowe dane ze słownika na obiekty klasy Question
for question in question_data:
    question_text = question["text"]
    question_answer = question["answer"]
    new_question = Question(q_text=question_text, q_answer=question_answer)
    question_bank.append(new_question)

# 3. Inicjalizujemy silnik quizu, przekazując mu listę obiektów
quiz = QuizBrain(question_bank)

# 4. Główna pętla gry
while quiz.still_has_questions():
    quiz.next_question()

# 5. Podsumowanie
print("You've completed the quiz")
print(f"Your final score was: {quiz.score}/{quiz.question_number}")