# UZH RAG System
This project is a multilingual RAG system, designed to support the lookup of UZH resources. You can
ask any question about UZH, and the relevant documents are retrieved, and the language model answers the 
question. The models are deployed locally on the user's machine, and the system is designed to be used in 
a web environment. The data is crawled from the web and stored in the form of markdown files.  

As a first-try project, this RAG system is built for experimental purposes. It is not meant to be used 
in a production environment. However, the performance of this system can support the use of european users,
in their own language (as long as the embedding model and the language model support it). 

## Requirements
#### Dependencies:
- Python 3.11+
- Ollama
- Chromadb  
- SentenceTransformers
#### System requirements:
- RAM: 8GB+  
- GPU: NVIDIA GPU with at least 8GB of VRAM

## Usage
IMPORTANT: in order to prevent misuse of the data, please email me to get the documents: nkdxzc@outlook.com   
To use the system, follow these steps:
1. Clone the repository
2. Install the dependencies
3. Download the embedding model and language model, which are:
    - paraphrase-multilingual-mpnet-base-v2
    - mistral:7b-instruct-v0.3-q4_K_M (You can download mistral using 'ollama run' command)
4. Set up the documents
5. Run main.py   
(On the first run, a new embeddings  database will be created, which takes about 10 minutes on my CPU i7-11800H)

## Acknowledgements
This project is built with the help of the following open-source projects:
- Ollama: https://ollama.com/
- Chromadb: https://www.trychroma.com/  

## Contributors
- Shunan He (She helped with the code of crawler)

## Scripts
- 'main.py' is the main script that runs the system.
- 'link_crawler.py' is the script that crawls the web for links and stores them in the form of markdown files.
- 'doc_separator.py' is the script that separates the markdown files into smaller chunks for processing.
- 'doc_picker.py' is the script that implements reranking and selects the top-k documents from retrieved docs.
- the test folder contains the test for inner reranking model.

## Current work
- rewrite main.py as a backend API for the frontend.
- add a frontend interface for the user to interact with the system.
