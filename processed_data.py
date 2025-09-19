import os
import time
import re
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd
import json
import PyPDF2
from database import db_session
from site_content.sample_class import SampleClass
import logging
from typing import List
import requests  # For making HTTP requests to Ollama

logger = logging.getLogger(__name__)

DATA_DIR = 'data'
EMBEDDINGS_FILE = os.path.join(DATA_DIR, 'embeddings.npz')
CONTENT_FILE = os.path.join(DATA_DIR, 'content.json')
INDEX_FILE = os.path.join(DATA_DIR, 'faiss_index.index')
# RANDOM_QUESTIONS_FILE = os.path.join(DATA_DIR, 'random_questions.json')  ## This may get removed permanantly

MANUAL_UPLOAD_DIR = 'manual_upload'

def read_text_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_csv_file(file_path: str) -> str:
    data = pd.read_csv(file_path)
    return data.to_string()  # Convert all CSV content to a string

def read_pdf_file(file_path: str) -> str:
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        return ' '.join([page.extract_text() for page in reader.pages])

def read_file(file_path: str) -> str:
    _, ext = os.path.splitext(file_path)
    if ext.lower() == '.txt':
        return read_text_file(file_path)
    elif ext.lower() == '.csv':
        return read_csv_file(file_path)
    elif ext.lower() == '.pdf':
        return read_pdf_file(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def fetch_database_content() -> list[str]:
    content = []
    samples = db_session.query(SampleClass).all()
    for sample in samples:
        content.append(f"{sample.name}: url - {sample.url}, content - {sample.description}")
    return content

def combine_data() -> list[str]:
    content = fetch_database_content()
    for filename in os.listdir(MANUAL_UPLOAD_DIR):
        file_path = os.path.join(MANUAL_UPLOAD_DIR, filename)
        try:
            file_content = read_file(file_path)
            content.append(file_content)
        except Exception as e:
            print(f"Error reading file {filename}: {str(e)}")
    return content

def preprocess(text: str) -> str:
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text.lower()

def is_data_stale() -> bool:
    if not all(os.path.exists(f) for f in [
        EMBEDDINGS_FILE, 
        CONTENT_FILE, 
        INDEX_FILE 
        # RANDOM_QUESTIONS_FILE
        ]):
        return True
    if time.time() - os.path.getmtime(INDEX_FILE) > 20 * 60:  # 20 minutes
        return True
    return False

# def are_random_questions_stale() -> bool:
#     if not os.path.exists(RANDOM_QUESTIONS_FILE):
#         return True
#     if time.time() - os.path.getmtime(RANDOM_QUESTIONS_FILE) > 2 * 60:  # 2 minutes
#         return True
    
#     # Check if random questions file is empty
#     with open(RANDOM_QUESTIONS_FILE, 'r', encoding='utf-8') as f:
#         questions = json.load(f)
#     if not questions or len(questions) == 0:  # Ensure the file is not empty
#         return True
    
#     return False

def update_data() -> None:
    content = combine_data()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    preprocessed_content = [preprocess(text) for text in content]
    embeddings = model.encode(preprocessed_content)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    
    np.savez_compressed(EMBEDDINGS_FILE, embeddings=embeddings)
    with open(CONTENT_FILE, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings.astype('float32'))
    faiss.write_index(index, INDEX_FILE)

    # Always update random questions when updating data
    ## update_random_questions()

# def update_random_questions() -> None:
#     questions = generate_questions_from_content()
#     with open(RANDOM_QUESTIONS_FILE, 'w', encoding='utf-8') as f:
#         json.dump(questions, f, ensure_ascii=False, indent=2)
#     print(f"Updated random questions file with {len(questions)} questions.")

# def generate_questions_from_content() -> List[str]:
#     all_questions = []
#     print("Generating questions from relevant content")
    
#     # Get all content
#     with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
#         all_content = json.load(f)
    
#     # Combine all content
#     combined_content = " ".join(all_content[:5])  # Limit to first 5 content items
    
#     prompt = f"""Based on the following content, generate 20 unique individual questions:

#     {combined_content}

#     Each question should:
#     1. Be a complete sentence ending with a question mark.
#     2. Be no longer than 12 words long.
#     3. Be directly related to the provided content.
#     4. Not be numbered in the output.
#     5. Do not add name of specific product or the site.
#     6. Do not create a question that cannot be explicitly answered.
#     """

#     try:
#         response = requests.post('http://localhost:11434/api/generate', json={
#             "model": "llama3.2",
#             "prompt": prompt,
#             "stream": False
#         })
#         print(f"Ollama API response status: {response.status_code}")
#         if response.status_code == 200:
#             response_json = response.json()
#             if 'response' in response_json:
#                 questions = response_json['response'].strip().split('\n')
#                 for question in questions:
#                     question = question.strip()
#                     if question and question.endswith('?'):
#                         all_questions.append(question)
#                     if len(all_questions) >= 20:
#                         break
#         else:
#             print(f"Error generating questions: {response.text}")
#     except Exception as e:
#         print(f"Exception in generate_questions_from_content: {str(e)}")
    
#     print(f"Total questions generated: {len(all_questions)}")
#     return all_questions[:20]

def load_data() -> tuple[np.ndarray, list[str], faiss.Index]:
    with np.load(EMBEDDINGS_FILE) as data:
        embeddings = data['embeddings']
    with open(CONTENT_FILE, 'r') as f:
        content = json.load(f)
    index = faiss.read_index(INDEX_FILE)
    return embeddings, content, index

def get_relevant_content(question: str) -> list[str]:
    logger.debug(f"Getting relevant content for question: {question}")
    if is_data_stale():
        logger.info("Data is stale, updating...")
        update_data()
    
    logger.debug("Encoding question")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    question_embedding = model.encode([question])[0]
    
    logger.debug("Searching for relevant content")
    index = faiss.read_index(INDEX_FILE)
    k = 5  # Number of nearest neighbors to retrieve
    D, I = index.search(question_embedding.reshape(1, -1).astype('float32'), k)
    
    logger.debug("Loading content")
    with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    relevant_content = [content[i] for i in I[0]]
    logger.debug(f"Found {len(relevant_content)} relevant content items")
    return relevant_content

if __name__ == "__main__":
    data_stale = is_data_stale()
    # questions_stale = are_random_questions_stale()
    
    # if data_stale or questions_stale:
    #     print("Data or random questions are stale. Updating...")
    #     update_data()
    #     print("Data and random questions updated successfully.")
    # else:
    #     print("Data and random questions are up to date.")
