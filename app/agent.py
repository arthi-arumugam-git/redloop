"""EvalPilot loop: propose eval -> run -> audit grader -> report."""
from .model import chat
def audit(item, answer, grade):
    msg = f"Question: {item}\nAnswer: {answer}\nGrader said: {grade}\nIs the grade correct? Reply JSON {{ok, reason}}."
    return chat([{"role": "user", "content": msg}])
if __name__ == "__main__":
    print(audit("2+2?", "4", "incorrect"))
