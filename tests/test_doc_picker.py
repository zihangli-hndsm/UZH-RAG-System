import unittest

from ollama import ChatResponse

import doc_picker
import os


def test_pick_top_docs():
    doc_names = os.listdir("test_docs")
    docs = []
    for doc_name in doc_names:
        with open(os.path.join("test_docs", doc_name), "r", encoding="utf-8") as f:
            docs.append(f.read())
    query = "What is the capital of France?"
    top_n = 3
    top_docs = doc_picker.pick_top_docs(docs, query, top_n)
    assert len(top_docs) == top_n
    assert isinstance(top_docs[0], tuple)
    assert isinstance(top_docs[0][1], int)
    assert isinstance(top_docs[0][0], str)


if __name__ == "__main__":
    unittest.main()
