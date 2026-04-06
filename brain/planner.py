# brain/planner.py
from typing import List
import openai  # lub inny LLM, np. Claude API

# jeśli używasz Claude Code lub lokalnego Claude, tu podłączasz SDK / REST

def plan_task(goal: str, history: list = None) -> List[str]:
    """
    Rozbija cel na listę tasków.
    :param goal: Cel, który agent ma osiągnąć
    :param history: opcjonalna historia poprzednich tasków
    :return: lista tasków
    """
    similar = MEMORY.query(goal, k=5)
    history_text = "\n".join([f"{h['task']}" for h in similar])
    prompt = f"""
    Jesteś Jarvis Planner.
    Goal: {goal}
    History: {history_text}
    
    Rozbij cel na prostą listę kroków (tasków) w formacie:
    1. ...
    2. ...
    """
    
    # jeśli Claude lokalny / API
    # response = claude.send(prompt)
    # dla przykładu użyjmy OpenAI GPT
    response = openai.ChatCompletion.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    text = response.choices[0].message.content
    # prosty parser: dzieli po liniach zaczynających się od numeru
    tasks = []
    for line in text.splitlines():
        line = line.strip()
        if line and (line[0].isdigit() and line[1] in [".", ")"]):
            task = line.split(".", 1)[1].strip()
            tasks.append(task)
    return tasks