import streamlit as st
import os
import pandas as pd

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Suppress the deprecation message
st.set_option('deprecation.showfileUploaderEncoding', False)

# Load Course dataset
df_course=pd.read_csv('C:/Users/jega_/dataframecourseV2.csv')

@st.cache(persist=True)
def get_tfidf_vectorizer(description):
    # Create a TF-IDF vectorizer with specific settings
    tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    return tfidf_vectorizer.fit(description)

# Retrieve the TF-IDF vectorizer, cached for efficiency
tfidf_vectorizer = get_tfidf_vectorizer(df_course['Title'])

@st.cache(persist=True)
def retrieve_top_documents(query_summary, k=10):
    # Transform the query summary into a TF-IDF vector
    query_vector = tfidf_vectorizer.transform([query_summary])
    
    # Calculate cosine similarity between the query and all articles
    similarity_scores = linear_kernel(query_vector, tfidf_vectorizer.transform(df_course['Title']))
    
    # Sort document indices by similarity score in descending order
    document_indices = similarity_scores[0].argsort()[:-k-1:-1]
    
    # Retrieve the top-k documents based on their indices
    top_documents = df_course.iloc[document_indices] 
    
    return similarity_scores, top_documents  # Return similarity_scores

st.title("📚 What would you like to learn today ? 📚")
with st.sidebar:
    st.header("🎛️ Filters")

    # Dropdown for 'level' column
    selected_level = st.selectbox("Select Level", df_course['level'].unique())

    # Multi-choice selector for 'formateur' column
    selected_formateurs = st.multiselect("Select Formateurs", df_course['formateur'].unique())

# Filter the DataFrame based on selected filters
filtered_documents = df_course[df_course['level'] == selected_level]
if selected_formateurs:
    filtered_documents = filtered_documents[filtered_documents['formateur'].isin(selected_formateurs)]

query_summary = st.text_area("✏️ Enter your request summary:")

if st.button("🔍 Retrieve your course"):
    if not query_summary:
        st.warning("Please enter a request ")
    else:
        similarity_scores, top_k_documents = retrieve_top_documents(query_summary, k=10)
        st.header("📜 Top Course for your request 📜")
        for i, document in enumerate(top_k_documents.itertuples(), start=1):
            st.subheader(f"🏆 Rank {i}:")
            st.write(f"**Title:** {document.Title}")
            st.write(f"**Duration:** {document.Duration}")
            st.write(f"**Level:** {document.level}")
            st.write(f"**Link:** {document.lien}")
            st.write(f"**Formateur:** {document.formateur}")
            st.write(f"**Certification:** {document.Certification}")