import ollama

def ask_ollama(question):
    """Ask in English, get concise English answers"""
    prompt = (
        f"Answer in 1-2 short sentences. Be technical and precise.\n"
        f"Question: {question}\n"
        "Answer:"
    )
    
    response = ollama.generate(
        model="phi",
        prompt=prompt,
        options={'temperature': 0, 'num_ctx': 1024}
    )
    return response['response']

# Test cases
questions = [
    "What is the capital of France?",
    "List Brazilian states starting with 'A'",
    "Explain Newton's First Law"
]

for q in questions:
    answer = ask_ollama(q)
    print(f"\nQ: {q}\nA: {answer}\n")