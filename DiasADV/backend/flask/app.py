from flask import Flask, request, jsonify
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import json

app = Flask(__name__)

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

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({"error": "A pergunta é obrigatória"}), 400
    
    try:
        response_content = chat_completion(question)
        return app.response_class(
            response=json.dumps({"response": response_content}, ensure_ascii=False),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
