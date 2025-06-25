import chromadb
import os

from chromadb.errors import NotFoundError
from chromadb.utils import embedding_functions
from ollama import chat
from ollama import ChatResponse
import tkinter as tk
from tkhtmlview import HTMLScrolledText
import markdown
import random
import doc_picker


def query():
    q = text_input_1.get("1.0", tk.END).strip()
    raw_docs = collection.query(query_texts=q, n_results=50)['documents'][0]
    results = doc_picker.pick_top_docs(docs=raw_docs, query=q, top_n=5)
    prompt = f"""You are a helpful assistant in a RAG system.

    Below is a user query:
    {q}

    And here are five retrieved documents that may contain relevant information, along with their relevance scores (0-100):
    [Document 1] (Relevance score: {results[0][1]})
    {results[0][0]}

    [Document 2] (Relevance score: {results[1][1]})
    {results[1][0]}
    
    [Document 3] (Relevance score: {results[2][1]})
    {results[2][0]}

    [Document 4] (Relevance score: {results[3][1]})
    {results[3][0]}

    [Document 5] (Relevance score: {results[4][1]})
    {results[4][0]}

    TASK:
    1. Analyze the user's query.
    2. Use ONLY the information from the documents above.
    3. Provide a concise, informative answer.
    4. Do NOT invent or assume anything beyond the content.
    5. Respond strictly in the same language as the query: detect the language from the query and answer accordingly.
    6. Always answer only using the given documents and in the same language as the query.

    Now give your response:"""
    text_input_1.insert(tk.END, '\nRetrieval completed. Generating output...')
    response: ChatResponse = chat(model='mistral:7b-instruct-v0.3-q4_K_M', messages=[
        {'role': 'system',
         'content': 'You are a multilingual assistant for a RAG system.'},
        {'role': 'user', 'content': prompt}
    ])
    html_text = markdown.markdown(response['message']['content'])
    text_output.set_html(html_text)


def example():
    with open("examples.txt", "r", encoding="utf-8") as f:
        example_queries = f.readlines()
        text_input_1.delete("1.0", tk.END)
        text_input_1.insert("1.0", example_queries[random.randint(0, len(example_queries)-1)])


def create_collection(collection_name: str, c_client: chromadb.PersistentClient):
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embedding_model_name)
    c_collection = c_client.create_collection(collection_name, embedding_function=ef)
    if os.path.exists("./chromaClient/docs"):
        for file in os.listdir("./chromaClient/docs"):
            if file.endswith(".md"):
                with open(os.path.join("./chromaClient/docs", file), "r", encoding="utf-8") as f:
                    content = f.read()
                    c_collection.add(documents=[content],
                                     ids=[file[:-3].replace(".html", "")])
    else:
        raise FileNotFoundError("docs folder not found")
    return c_collection


embedding_model_name = "paraphrase-multilingual-mpnet-base-v2"
client = chromadb.PersistentClient("./chromaClient/db")
try:
    collection = client.get_collection(name="uzh")
except NotFoundError:
    print("Creating collection...")
    collection = create_collection(collection_name="uzh", c_client=client)


# 窗口程序
root = tk.Tk()
root.title("UZH RAG")
root.geometry("1280x720")

# 查询
tk.Label(root, text="Your query here").pack()
example_query_button = tk.Button(root, text="Give me an example!", command=example)
example_query_button.pack(pady=10)
text_input_1 = tk.Text(root, height=4, width=70)
text_input_1.pack(fill="both", expand=True)
query_button = tk.Button(root, text='Send Query', command=query)
query_button.pack(pady=10)

# 输出
tk.Label(root, text="Response").pack()
text_output = HTMLScrolledText(root)
text_output.pack(fill="both", expand=True)

root.mainloop()
