import ollama

#pip install ollama 
def ask_deepseek(question, model="deepseek-r1:1.5B"):
    response = ollama.generate(
        model=model,
        prompt=f"Responda de forma concisa e técnica e em português brasil por favor: {question}",
        options={'temperature': 0.1} 
    )
    return response['response']

pergunta = " "
resposta = ask_deepseek(pergunta)

print("Pergunta:\n", pergunta)
print("\nResposta do DeepSeek:\n", resposta)

