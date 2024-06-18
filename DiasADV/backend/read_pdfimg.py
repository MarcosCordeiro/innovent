import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
import os

# Especificar o caminho para o executável do Tesseract, se necessário
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Função para extrair texto de uma página
def extract_text_from_page(page, pdf_document):
    text = page.get_text()  # Extrai texto diretamente
    images = page.get_images(full=True)  # Lista de imagens na página

    for img_index, img in enumerate(images):
        xref = img[0]
        base_image = pdf_document.extract_image(xref)
        image_bytes = base_image["image"]

        # Abrir a imagem
        image = Image.open(io.BytesIO(image_bytes))

        # Usar OCR para extrair texto da imagem
        text += pytesseract.image_to_string(image)
    
    return text

# Função para processar um PDF
def process_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    full_text = ''
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        full_text += extract_text_from_page(page, pdf_document)
    
    # Salvar o texto extraído em um arquivo de texto
    output_text_file = pdf_path.replace('.pdf', '.txt')
    with open(output_text_file, 'w', encoding='utf-8') as text_file:
        text_file.write(full_text)

# Função para buscar PDFs em um diretório e processá-los
def process_pdfs_in_directory(directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                print(f'Processando: {pdf_path}')
                process_pdf(pdf_path)
                print(f'Texto extraído salvo em: {pdf_path.replace(".pdf", ".txt")}')

# Caminho do diretório onde estão os arquivos PDF
directory_path = '../dataset/processos/39336'

# Processar todos os PDFs no diretório
process_pdfs_in_directory(directory_path)
