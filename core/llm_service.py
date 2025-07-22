from openai import OpenAI
import random

client = OpenAI(api_key="")

def generate_question(jd, resume, project, experience):
    level = "basic" if experience <= 2 else "intermediate" if experience <= 5 else "advanced"
    prompt = f"""
    You are a technical interviewer. Based on the following:
    - Job Description: {jd}
    - Resume: {resume}
    - Project Requirements: {project}
    - Candidate experience: {experience} years
    Ask a {level} technical interview question.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def evaluate_answer(question, answer):
    prompt = f"""
    Evaluate this candidate answer.
    Question: {question}
    Answer: {answer}

    Give a score from 1 to 10 based on the correctness, completeness, and depth of the answer.
    Just reply with the number only.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        score = int(response.choices[0].message.content.strip())
        return min(max(score, 1), 10)
    except:
        return random.randint(4, 7)

def generate_feedback(df):
    questions = "\n".join(df["Question"])
    answers = "\n".join(df["Answer"])
    prompt = f"""
    Based on the following questions and answers, give a brief performance feedback:

    Questions:
    {questions}

    Answers:
    {answers}

    Provide strengths, weaknesses, and areas of improvement.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
