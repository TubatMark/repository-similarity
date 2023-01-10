import logging
import PyPDF2
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv
import numpy as np
import pandas as pd
from io import StringIO
from .models import StudentUsers
logger = logging.getLogger(__name__)
import warnings
import os
from .models import RepositoryFiles

# upload enrolled students csv file
def csv_enrolled_students(file):
    df = pd.read_excel(file)
    rows_to_keep = []
    seen_student_ids = set()
    for index, row in df.iterrows():
        student_id = row['Student ID']
        if student_id not in seen_student_ids:
            # This is the first time we're seeing this student ID, so keep this row
            rows_to_keep.append(row)
            seen_student_ids.add(student_id)
    # Now we have a list of rows that we want to keep, so we can create the StudentUsers objects
    for row in rows_to_keep:
        data = StudentUsers(sn=row['sn'], Student_Id=row['Student ID'], Student_Name=row['Student Name'], Email=row['Email'], Contact_Number=row['Contact No.'],
                            Course=row['Course'], SUBJECT_CODE=row['SUBJ_CODE'], SUBJECT_DESCRIPTION=row['SUBJ_DESC'], YR_SEC=row['YR_SEC'], SEM=row['SEM'], SY=row['SY'])
        data.save()


def preprocess(data):
    # Convert to lower case
    data = np.char.lower(data)

    # Remove punctuation
    symbols = "!\"#$%&()*+-./:;<=>?@[\]^_`{|}~\n"
    for i in range(len(symbols)):
        data = np.char.replace(data, symbols[i], ' ')
        data = np.char.replace(data, "  ", " ")
        data = np.char.replace(data, ',', '')

    # Remove stop words
    stop_words = stopwords.words('english')
    words = word_tokenize(str(data))
    new_text = ""
    for w in words:
        if w not in stop_words and len(w) > 1:
            new_text = new_text + " " + w
    data = new_text

    # Perform stemming
    stemmer = PorterStemmer()
    words = word_tokenize(str(data))
    new_text = ""
    for w in words:
        new_text = new_text + " " + stemmer.stem(w)
    data = new_text

    # Perform lemmatization
    lemmatizer = WordNetLemmatizer()
    words = word_tokenize(str(data))
    new_text = ""
    for w in words:
        new_text = new_text + " " + lemmatizer.lemmatize(w)
    data = new_text

    return data

def extract_pdf_text(pdf_file, repository_file):
    # open the PDF file
    pdf = PyPDF2.PdfFileReader(pdf_file)
    
    # extract the text from each page and save it in a list
    text_list = [pdf.getPage(page).extractText() for page in range(pdf.getNumPages())]

    # join all the texts from the list and save it as a single string
    text = "\n".join(text_list)

    # convert the text to UTF-8 format
    text = text.encode("utf-8").decode("utf-8")
    
    path = 'media/ExtractedFiles'
    if not os.path.exists(path):
        os.makedirs(path)
    text_file_name = pdf_file.name.replace('.pdf', '.txt')
    text_file = os.path.join(path, text_file_name)
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(text)
    
    # Save the file path to the database
    repository_file.text_file = text_file
    repository_file.save()

    # preprocess the text using NLTK
    text = preprocess(text) 

    # generate a NMF matrix using the preprocessed text
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([text])
    nmf = NMF(n_components=200, random_state=0)
    nmf_matrix = nmf.fit_transform(X)

    # Save the LSA matrix to the RepositoryFiles model
    repository_file.lsa_matrix = nmf_matrix.tobytes()
    repository_file.save()


def compare_documents(query_doc):
    # Load the LSA matrices from the database
    repository_files = RepositoryFiles.objects.all()
    matrices = [np.frombuffer(f.lsa_matrix, dtype=np.float64) for f in repository_files]
    matrices = np.array(matrices)

    # Generate the LSA matrix for the query document
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform([query_doc])
    nmf = NMF(n_components=200, random_state=0)
    query_matrix = nmf.fit_transform(X)

    # Compute the cosine similarities between the query matrix and the matrices in the database
    similarities = cosine_similarity(query_matrix, matrices)
    
    # Find the indices of the most similar documents
    most_similar_indices = np.argmax(similarities, axis=1).astype(int)
    
    # Print the titles and similarity scores of the most similar documents
    for i, index in enumerate(most_similar_indices):
        repository_file = repository_files[index]
        title = repository_file.title
        score = similarities[i][index]
        # Convert the similarity score to percentage form
        percentage_score = round(score * 100, 2)
        print(f"Title: {title}, Similarity score: {percentage_score}%")
        
def student_pdf_text(pdf_file):
    # open the PDF file
    try:
        pdf = PyPDF2.PdfFileReader(pdf_file)
    except PyPDF2.PdfReadError as e:
        logger.error(f"Error reading PDF file: {e}")
        return

    # extract the text from each page and save it in a list
    text_list = []
    for page in range(pdf.getNumPages()):
        text_list.append(pdf.getPage(page).extractText())

    # join all the texts from the list and save it as a single string
    text = "\n".join(text_list)

    # convert the text to UTF-8 format
    text = text.encode("utf-8").decode("utf-8")

    # preprocess the text using NLTK
    text = preprocess(text)
    
    return text
