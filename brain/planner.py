from brain.vector_memory import MEMORY
from openai import OpenAI

client = OpenAI()

def summarize_history(goal, top_n=5):
    similar = MEMORY.query(goal, k=top_n)
    if not similar:
        return "Brak podobnych tasków."
    return "\n".join([f"{h['task']} (wynik: {h.get('result','')})" for h in similar])

def plan_task(goal):
    summary = summarize_history(goal)

    prompt = f"""
    Jesteś Jarvis Planner. Rozbij cel na listę tasków.
    Cel: {goal}
    Podobne wcześniejsze taski:
    {summary}
    Wypisz taski w formacie numerowanym:
    1. ...
    2. ...
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.3
    )
    text = response.choices[0].message.content
    tasks = []
    for line in text.splitlines():
        line = line.strip()
        if line and line[0].isdigit() and line[1] in [".", ")"]:
            task = line.split(".",1)[1].strip()
            tasks.append({"task": task, "status":"pending", "priority":0})
    return tasks