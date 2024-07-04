import openai
import streamlit as st
import random
import time
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

openai_endpoint = "https://diasadvopenai.openai.azure.com/"
openai_key = "ba61df8ff6d641608ff1d196a77b2534"
openai_deployment_name = "diaadv4o"

search_endpoint = "https://diasadv.search.windows.net"
search_key = "xjkrKd6c7sLMVv2KBk1NSsFlWWz5kkYTIbn6wmQBxUAzSeANGg5S"
search_indices = ["i37706", "i39336", "i40452"]

client = AzureOpenAI(azure_endpoint=openai_endpoint,
                     api_key=openai_key,
                     api_version="2024-02-15-preview")

def search_documents(question):
    all_documents = []
    for index in search_indices:
        search_client = SearchClient(endpoint=search_endpoint,
                                     index_name=index,
                                     credential=AzureKeyCredential(search_key))
        search_results = search_client.search(search_text=question, top=5)
        documents = [{"content": result["content"], "filepath": result["filepath"]} for result in search_results if 'content' in result and 'filepath' in result]
        all_documents.extend(documents)
    return all_documents

def chat_completion(question):
    search_results = search_documents(question)
    
    if not search_results:
        return "Não há informações disponíveis nos índices para responder à pergunta.", []

    search_context = "\n".join([f"Conteúdo: {doc['content']}\nFilepath: {doc['filepath']}" for doc in search_results])
    prompt = f"Contexto dos resultados da pesquisa: {search_context}\n\nPergunta do usuário: {question}\nResponda estritamente com base no contexto fornecido e em português."
    
    response = client.chat.completions.create(model=openai_deployment_name,
                                              messages=[
                                                  {"role": "user", "content": prompt}
                                              ])
    response_content = response.choices[0].message.content
    filepaths = [doc['filepath'] for doc in search_results]
    
    return response_content, filepaths

st.markdown("""
    <style>
    .custom-image-container {
        background-color: #4b4e54; /* cor de fundo */
        padding: 10px; /* espaço ao redor da imagem */
        border-radius: 10px; /* borda arredondada */
        display: flex;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="custom-image-container"><img src="https://www.dsa.com.br/_2019/wp-content/themes/diasdesouza/img/logo-white.svg" width="300"></div>', unsafe_allow_html=True)

st.title("DiasGPT")
st.write("Pesquisa de dicionário, glossário jurídico e processos.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Como posso ajuda-lo?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response, filepaths = chat_completion(prompt)
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
