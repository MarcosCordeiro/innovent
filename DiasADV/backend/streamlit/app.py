import streamlit as st
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Configurar o cliente OpenAI
openai_endpoint = "https://gptdiasadv.openai.azure.com/"
openai_key = "fd9814a748fc46179852b680e6c2fc11"
openai_deployment_name = "DiasADVGPT"

# Configurar serviço de busca
search_endpoint = "https://diasadvsearch.search.windows.net"
search_key = "ZDaDpiuX7zhpk73uA0VszYCqdSXNlM6U9aJSajnSMzAzSeBoVlvX"
search_index = "idxfiles"

client = AzureOpenAI(azure_endpoint=openai_endpoint,
                     api_key=openai_key,
                     api_version="2024-02-15-preview")

search_client = SearchClient(endpoint=search_endpoint,
                             index_name=search_index,
                             credential=AzureKeyCredential(search_key))

# Função para realizar a busca
def search_documents(question):
    search_results = search_client.search(search_text=question, top=5)
    documents = [result for result in search_results]
    return documents

# Definir a consulta de chat IA/completação com contexto da busca
def chat_completion(question):
    search_results = search_documents(question)
    
    if not search_results:
        return "Não há informações disponíveis no índice para responder à pergunta."

    # Construir mensagem com resultados da busca
    search_context = "\n".join([doc['content'] for doc in search_results if 'content' in doc])
    prompt = f"Contexto dos resultados da pesquisa: {search_context}\n\nPergunta do usuário: {question}\nResponda estritamente com base no contexto fornecido e em português."
    
    response = client.chat.completions.create(model=openai_deployment_name,
                                              messages=[
                                                  {"role": "user", "content": prompt}
                                              ])
    
    return response.choices[0].message.content

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
st.write("Pesquisa de dicionário e glossário jurídico.")


question = st.text_input("Pergunta:")

if st.button("Enviar"):
    if question:
        with st.spinner("Processando..."):
            response_content = chat_completion(question)
        st.write("**Resposta:**")
        st.write(response_content)
    else:
        st.write("Por favor, insira uma pergunta.")
