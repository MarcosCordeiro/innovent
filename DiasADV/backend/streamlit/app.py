import streamlit as st
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Configurar o cliente OpenAI
openai_endpoint = "https://diasadvopenai.openai.azure.com/"
openai_key = "e8bebaadc5794b62858272834a6d4008"
openai_deployment_name = "DiasADV"

# Configurar serviço de busca
search_endpoint = "https://diasadv.search.windows.net"
search_key = "xjkrKd6c7sLMVv2KBk1NSsFlWWz5kkYTIbn6wmQBxUAzSeANGg5S"
search_index = "diasindx4o"

client = AzureOpenAI(azure_endpoint=openai_endpoint,
                     api_key=openai_key,
                     api_version="2024-02-15-preview")

search_client = SearchClient(endpoint=search_endpoint,
                             index_name=search_index,
                             credential=AzureKeyCredential(search_key))

# Função para realizar a busca
def search_documents(question):
    search_results = search_client.search(search_text=question, top=5)
    documents = [{"content": result["content"], "filepath": result["filepath"]} for result in search_results if 'content' in result and 'filepath' in result]
    return documents

# Definir a consulta de chat IA/completação com contexto da busca
def chat_completion(question):
    search_results = search_documents(question)
    
    if not search_results:
        return "Não há informações disponíveis no índice para responder à pergunta.", []

    # Construir mensagem com resultados da busca
    search_context = "\n".join([f"Conteúdo: {doc['content']}\nFilepath: {doc['filepath']}" for doc in search_results])
    prompt = f"Contexto dos resultados da pesquisa: {search_context}\n\nPergunta do usuário: {question}\nResponda estritamente com base no contexto fornecido e em português."
    
    response = client.chat.completions.create(model=openai_deployment_name,
                                              messages=[
                                                  {"role": "user", "content": prompt}
                                              ])
    response_content = response.choices[0].message.content
    filepaths = [doc['filepath'] for doc in search_results]
    
    return response_content, filepaths

# Interface do Streamlit
st.set_page_config(page_title="Dias ADV - Innovent Solution", layout="wide")

st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True)

st.image("https://advocaciadias.com/wp-content/uploads/2024/02/Logo-Dias-500-redondo.png", width=200)
st.title("DIasADVGPT")
st.write("Pesquisa de dicionário, glossário jurídico e processos.")

question = st.text_input("Pergunta:")

if st.button("Enviar"):
    if question:
        with st.spinner("Processando..."):
            response_content, filepaths = chat_completion(question)
        st.write("**Resposta:**")
        st.write(response_content)
        # st.write("**Documentos relacionados:**")
        # for filepath in filepaths:
        #     st.write(filepath)
    else:
        st.write("Por favor, insira uma pergunta.")
