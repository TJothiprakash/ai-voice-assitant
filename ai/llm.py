import os
from groq import Groq
from ai.rag import search
from ai.faq import check_faq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# Global system prompt (defines assistant behavior)
SYSTEM_PROMPT = """
You are an AI voice support agent for OpenSox.ai.

Your role is to help customers by answering questions about the product
using the provided knowledge base.

Guidelines:
- Always use the retrieved knowledge context to answer.
- If the answer is not found in the knowledge context, say you do not have that information.
- Keep responses short and conversational since the response will be spoken over a phone call.
- Prefer 1–2 sentences.
- Be polite, friendly, and professional.
"""


# Opening greeting played when the call starts
OPENING_MESSAGE = """
Hello, thank you for calling OpenSox AI support.
How can I help you today?
"""


async def ask_llm(user_text):

    # Step 1: Check FAQ first (fast response)
    faq_answer = check_faq(user_text)

    if faq_answer:
        print("\n===== FAQ MATCH =====")
        print(faq_answer)
        return faq_answer

    # Step 2: Retrieve knowledge using RAG
    context_chunks = search(user_text)

    context = "\n\n".join(context_chunks)

    prompt = f"""
Knowledge Context:
{context}

User Question:
{user_text}

Answer using the knowledge context.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content