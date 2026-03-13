import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

with open("knowledge/payment_faq.txt") as f:
    KNOWLEDGE = f.read()


async def ask_llm(user_text):

    prompt = f"""
You are a payment support AI.

Knowledge base:
{KNOWLEDGE}

User question:
{user_text}

Answer clearly.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content