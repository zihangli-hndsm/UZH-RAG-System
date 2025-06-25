from ollama import chat
from ollama import ChatResponse


def pick_top_docs(docs, query, top_n=5):
    if len(docs) < top_n:
        top_n = len(docs)
    results = []
    for i, doc in enumerate(docs):
        results.append((doc, get_relevance_score(doc, query)))
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:top_n]


def get_relevance_score(doc, query):
    prompt = f"""
    Rate the relevance between the query and the document on a scale from 1 to 100.

    Query:
    {query}

    Document:
    {doc}

    Respond only with a single integer from 1 to 100. Do not write anything else. Do not explain.
    Your output will be parsed by a program.
    """
    response: ChatResponse = chat(model='mistral:7b-instruct-v0.3-q4_K_M', messages=[
        {'role': 'system', 'content': 'You are a strict evaluation model used in a retrieval system.'},
        {'role': 'user', 'content': prompt}
    ])
    content = response['message']['content'].strip()
    score = int("".join(filter(str.isdigit, content.split('\n')[0])))
    return score

