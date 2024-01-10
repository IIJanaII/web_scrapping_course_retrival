import streamlit as st
import os
import pandas as pd

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Suppress the deprecation message
#st.set_option('deprecation.showfileUploaderEncoding', False)

# Load Course dataset

df_course=pd.read_csv('C:/Users/jega_/web_scrapping_course_retrival/dataframecourse_final2.csv')


filtered_documents=df_course.copy()


@st.cache_data(persist=True)
def get_tfidf_vectorizer(description):
    # Create a TF-IDF vectorizer with specific settings
    tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    return tfidf_vectorizer.fit(description)

# Retrieve the TF-IDF vectorizer, cached for efficiency
tfidf_vectorizer = get_tfidf_vectorizer(filtered_documents['description'])

@st.cache_data(persist=True)
def retrieve_top_documents(query_summary, k=10):
    # Transform the query summary into a TF-IDF vector
    query_vector = tfidf_vectorizer.transform([query_summary])
    
    # Calculate cosine similarity between the query and all articles
    similarity_scores = linear_kernel(query_vector, tfidf_vectorizer.transform(filtered_documents['description']))
    
    # Sort document indices by similarity score in descending order
    document_indices = similarity_scores[0].argsort()[:-k-1:-1]
    
    # Retrieve the top-k documents based on their indices
    top_documents = filtered_documents.iloc[document_indices] 
   
    
    
    return similarity_scores, top_documents  # Return similarity_scores


if 'page_index' not in st.session_state:
    st.session_state.page_index = 0

st.title("📚 What would you like to learn today ? 📚")
with st.sidebar:
    st.header("🎛️ Filters")

    # Dropdown for 'type' column
    selected_types = st.multiselect("📚 Select Course Types", df_course['type'].unique())

    # Dropdown for 'level' column
    selected_level = st.selectbox("📶 Select Level", df_course['level'].unique(),index=None)

    # Multi-choice selector for 'formateur' column
    selected_formateurs = st.multiselect("🦉 Select Formateurs", df_course['provider'].unique())


    #Add filter for 'Duration'
    min_duration, max_duration = st.slider("⌛Select Duration Range", min_value=0.0, max_value=df_course['duration_hour'].max(), value=(0.0, df_course['duration_hour'].max()))
    

    # Add filter for 'Price'
    min_price, max_price = st.slider("💵 Select Price Range", min_value=0.0, max_value=df_course['new_price_column'].max(), value=(0.0, df_course['new_price_column'].max()))

# if selected_formateurs:
#     filtered_documents = filtered_documents[filtered_documents['formateur'].isin(selected_formateurs)]
# if selected_level:
#     # Filter the DataFrame based on selected filters
#     filtered_documents = filtered_documents[filtered_documents['level'] == selected_level]
# if min_price and max_price:
#     filtered_documents = filtered_documents[(filtered_documents['price'] >= min_price) & (filtered_documents['price'] <= max_price)]

# Filter the DataFrame based on selected duration
#filtered_documents = filtered_documents[(filtered_documents['Duration'] >= min_duration) & (filtered_documents['Duration'] <= max_duration)]

def filter_data(data,selected_types, level, formateurs, min_price, max_price):
    filtered_data = data.copy()
    if selected_types:
        filtered_data = filtered_data[filtered_data['type'].isin(selected_types)]
    if len(formateurs)>0:
        filtered_data = filtered_data[filtered_data['provider'].isin(formateurs)]
    if level is not None:
        filtered_data = filtered_data[filtered_data['level'] == level]
    if min_price is not None and max_price is not None:
        filtered_data = filtered_data[(filtered_data['new_price_column'] >= min_price) & (filtered_data['new_price_column'] <= max_price)]
    return filtered_data







query_summary = st.text_area("✏️ Enter your request summary:")

if st.button("🔍 Retrieve your course"):
    if not query_summary:
        st.warning("Please enter a request ")
    else:
        st.session_state.page_index = 0
        
        print("query is",query_summary)
        similarity_scores, top_k_documents = retrieve_top_documents(query_summary, k=50)
        print("level",selected_level)
        print("formateur",selected_formateurs)

        top_k_documents=filter_data(top_k_documents,selected_types,selected_level,selected_formateurs,min_price,max_price)
        
        st.session_state.top_documents=top_k_documents
        #top_documents=top_k_documents
        
        st.header(" Top Course for your request ")
        page_size = 10
        start_index = st.session_state.page_index * page_size
        end_index = start_index + page_size
        print(st.session_state.page_index)

        # Display the top 10 results in card-like expandersc
        for i, document in enumerate(st.session_state.top_documents.iloc[start_index:end_index].itertuples(), start= 1):
            

            container_image_title = st.columns([1, 4])  # Adjust the column ratios as needed

            # Display the image and title in the container
            with container_image_title[0]:
                st.image(document.img, caption='Course Image', use_column_width=True)

            with container_image_title[1]:
                st.title(document.title)
                st.write(f"Type: {document.type}")
                st.write(f"Duration: {document.duration}")
            
            with st.expander(f"Course {i}: {document.title}"):
                st.write(f"**🎯 Title:** {document.title}")
                st.write(f"**📚 Type:** {document.type}")
                st.write(f"**📶 Level:** {document.level}")
                st.write(f"**⌛ Duration:** {document.duration}")



                # Display the image using the image source
                #st.image(document.image_source, caption='Course Image', use_column_width=True)
                st.write(f"**🌱 Carbon cost:** {document.cost_per_co}")
                st.write(f"**💵 Price:** {document.price}")
                st.write(f"**Link:** {document.link}")
                st.write(f"**Formateur:** {document.provider}")
                st.write(f"**Certification:** {document.certificate}")
                st.write(f"**Description:** {document.description}")

        st.write(f"Showing courses {start_index + 1} to {min(end_index, len(st.session_state.top_documents))} of {len(st.session_state.top_documents)}")
            # Previous Page button
        # if st.session_state.page_index > 0:
        #     if st.button("Previous Page"):
        #         st.session_state.page_index -= page_size

        # Next Page button
if st.session_state.page_index < 50:
    next_page_button = st.button("Next Page")
    if next_page_button:
        page_size = 10
        st.session_state.page_index += page_size
        
        print("st page",st.session_state.page_index)
        start_index = st.session_state.page_index 
        end_index = start_index + page_size
        print(st.session_state.page_index)
        print(len(st.session_state.top_documents))

        # Display the top 10 results in card-like expandersc
        for i, document in enumerate(st.session_state.top_documents.iloc[start_index:end_index].itertuples(), start= 1+st.session_state.page_index):
            
            
            container_image_title = st.columns([1, 4])  # Adjust the column ratios as needed

            # Display the image and title in the container
            with container_image_title[0]:
                st.image(document.img, caption='Course Image', use_column_width=True)

            with container_image_title[1]:
                st.title(document.title)
                st.write(f"Type: {document.type}")
                st.write(f"Duration: {document.duration}")
            
            with st.expander(f"Course {i}: {document.title}"):
                st.write(f"**🎯 Title:** {document.title}")
                st.write(f"**📚 Type:** {document.type}")
                st.write(f"**📶 Level:** {document.level}")
                st.write(f"**⌛ Duration:** {document.duration}")

                # Display the image using the image source
                #st.image(document.image_source, caption='Course Image', use_column_width=True)
                
                st.write(f"**🌱 Carbon cost:** {document.cost_per_co}")
                st.write(f"**💵 Price:** {document.price}")

                st.write(f"**Link:** {document.link}")
                st.write(f"**Formateur:** {document.provider}")
                st.write(f"**Certification:** {document.certificate}")
                st.write(f"**Description:** {document.description}")

if st.session_state.page_index>0:
    previous_page_button = st.button("Previous Page")
    if previous_page_button:
        page_size = 10
        st.session_state.page_index -= page_size
        
        print("st page",st.session_state.page_index)
        start_index = st.session_state.page_index 
        end_index = start_index + page_size
        print(st.session_state.page_index)
        print(len(st.session_state.top_documents))

        # Display the top 10 results in card-like expandersc
        for i, document in enumerate(st.session_state.top_documents.iloc[start_index:end_index].itertuples(), start= 1+st.session_state.page_index):
            
            
            container_image_title = st.columns([1, 4])  # Adjust the column ratios as needed

            # Display the image and title in the container
            with container_image_title[0]:
                st.image(document.img, caption='Course Image', use_column_width=True)

            with container_image_title[1]:
                st.title(document.title)
                st.write(f"Type: {document.type}")
                st.write(f"Duration: {document.duration}")
            
            with st.expander(f"Course {i}: {document.title}"):
                st.write(f"**🎯 Title:** {document.title}")
                st.write(f"**📚 Type:** {document.type}")
                st.write(f"**📶 Level:** {document.level}")
                st.write(f"**⌛ Duration:** {document.duration}")

                # Display the image using the image source
                #st.image(document.image_source, caption='Course Image', use_column_width=True)
                st.write(f"**🌱 Carbon cost:** {document.cost_per_co}")
                st.write(f"**💵 Price:** {document.price}")
                st.write(f"**Link:** {document.link}")
                st.write(f"**Formateur:** {document.provider}")
                st.write(f"**Certification:** {document.certificate}")
                st.write(f"**Description:** {document.description}")

        

  


