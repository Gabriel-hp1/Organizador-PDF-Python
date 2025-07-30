import os
import pdfplumber
import re
from pypdf import PdfWriter, PdfReader

def listar_pdfs(caminho_pasta):
    pdfs_encontrados = []

    if not os.path.isdir(caminho_pasta):
        print (f"Erro: A pasta '{caminho_pasta}' não foi encontrada ou não é um diretório válido.")
        return pdfs_encontrados
    
    for item in os.listdir(caminho_pasta):
        caminho_completo_item = os.path.join (caminho_pasta, item)

        if os.path.isfile(caminho_completo_item) and item.lower().endswith('.pdf'):
            pdfs_encontrados.append(item)
    
    return pdfs_encontrados

def ler_texto_pdf(caminho_arquivo_pdf):

    texto_extraido = ""
    try:
        with pdfplumber.open(caminho_arquivo_pdf) as pdf:
            for pagina in pdf.pages:
                texto_extraido += pagina.extract_text() + "\n"
        
        print(f"DEBUG: Texto bruto extraído (repr): {repr(texto_extraido[:500])}...")        

        print (f"Texto extraído de '{os.path.basename(caminho_arquivo_pdf)}' (primeiras 200 letras):\n{texto_extraido[:200]}...")

    except Exception as e:
        print(f"Erro ao ler o PDF '{caminho_arquivo_pdf}':{e}")
        texto_extraido =""
    return texto_extraido

def extrair_data_do_texto (texto):
    padrao_dd_mm_aaaa = r'\b(\d{2}[/.-]\d{2}[/.-]\d{4})\b'
    padrao_aaaa_mm_dd = r'\b(\d{4}[-]\d{2}[-]\d{2})\b'

    padroes = [
        padrao_dd_mm_aaaa,
        padrao_aaaa_mm_dd
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            data_encontrada = match.group(1)
            if '/' in data_encontrada or '.' in data_encontrada:
                partes = re.split('[/.-]', data_encontrada)
                if len(partes) == 3:
                    return f"{partes[2]}-{partes[1]}-{partes[0]}"
            return data_encontrada
    return ""

def extrair_info_pessoa_do_texto(texto):
    cpf_encontrado = ""
    nome_encontrado = ""

    texto_limpo = re.sub(r'\s+', ' ', texto)
    texto_limpo = re.sub(r'[^0-9a-zA-Z./\-\s]', '', texto_limpo)
    
    print(f"DEBUG: Texto limpo para CPF: '{repr(texto_limpo[:200])}'")

    padrao_cpf = r'\b(\d{3}[\.\/-]\d{3}[\.\/-]\d{3}[\.\/-]\d{2}|\d{11})\b'

    match_cpf = re.search(padrao_cpf, texto_limpo)
    if match_cpf:
        cpf_encontrado = match_cpf.group(1)
        
        if re.fullmatch(r'\d{11}', cpf_encontrado):
            cpf_encontrado = f"{cpf_encontrado[:3]}.{cpf_encontrado[3:6]}.{cpf_encontrado[6:9]}-{cpf_encontrado[9:]}"
    
    return cpf_encontrado, nome_encontrado       

def unificar_pdfs(caminho_pasta, ordem_crescente=True, nome_arquivo_saida="documento_unificado.pdf"):
    
    escritor_pdf = PdfWriter()
    arquivos_pdf = []

    if not os.path.isdir(caminho_pasta):
        print (f"Erro: A pasta '{caminho_pasta}' não foi encontrada para unificação.")
        return
    
    print(f"\nProcurando PDFs na unificar em:'{caminho_pasta}'")
    for item in os.listdir(caminho_pasta):
        caminho_completo_item = os.path.join(caminho_pasta, item)
        if os.path.isfile(caminho_completo_item) and item.lower().endswith(".pdf"):
            arquivos_pdf.append(caminho_completo_item)

    if ordem_crescente:
        arquivos_pdf.sort()
        print("Ordenando PDFs em ordem CRESCENTE...")
    else:
        arquivos_pdf.sort(reverse=True)
        print("Ordenando PDFs em ordem DECRESCENTE...")

    if not arquivos_pdf:
        print("Nenhum arquivo PDF encontrado para unificar na pasta especificada.")
        return

    print ("\nArquivos PDF que serão unificado (nesta ordem):")
    for arquivo in arquivos_pdf:
        print(f"- {os.path.basename(arquivo)}")

    print ("\nAdicionando páginas dos PDFs ao documento unificado...")

    for arquivo_pdf in arquivos_pdf:
        try:
            leitor_pdf = PdfReader(arquivo_pdf)
            for pagina in leitor_pdf.pages:
                escritor_pdf.add_page(pagina)
            print(f" - Páginas de '{os.path.basename(arquivo_pdf)}' adicionadas.")
        except Exception as e: 
            print(f" - ERRO: Não foi possível ler ou adicionar páginas de '{os.path.basename(arquivo_pdf)}': {e}")
            continue
        
    caminho_saida_completo = os.path.join(caminho_pasta, nome_arquivo_saida)      

    try:
        with open(caminho_saida_completo, "wb") as saida_pdf:
            escritor_pdf.write(saida_pdf)
        print (f"\nPDFs unificados com sucesso em: '{caminho_saida_completo}'")
    except Exception as e:
        print(f" ERRO: Não foi possível salvar o arquivo PDF unificado em '{caminho_saida_completo}': {e}")                

def main():
    print('Iniciando o Organizador de PDF...')

    pasta_de_busca = ""

    while not os.path.isdir(pasta_de_busca):
        pasta_digitada = input ("Por favor, digite o caminho COMPLETO da pasta para organizar os PDFs (ex: C:\\Users\\SeuUsuario\\Documentos ou /home/seu_usuario/Documentos):")
        
        pasta_de_busca = os.path.expanduser(pasta_digitada)

        if not os.path.isdir(pasta_de_busca):
            print (f"Caminho inválido: '{pasta_de_busca}'. Por favor, tente novamente.")

    nome_pessoa_para_organizar = input ("Por favor, digite o NOME COMPLETO da pessoa para organizar os PDFs igual está no holerite:")        

    print(f"\nProcurando PDFs na pasta: '{pasta_de_busca}'")

    pdfs = listar_pdfs(pasta_de_busca)    

    if pdfs:
        print("\nPDFs encontrados:")
        for pdf in pdfs:
            print(f"-{pdf}")
            
            caminho_completo_pdf = os.path.join(pasta_de_busca, pdf)
            texto_do_pdf = ler_texto_pdf (caminho_completo_pdf)

            data_encontrada = extrair_data_do_texto(texto_do_pdf)
            if data_encontrada:
                print (f" Data encontrada no PDF: {data_encontrada}")
            else:
                print (" Nenhuma data encontrada neste PDF com os padrões atuais.")
    
            cpf_encontrado, nome_encontrado = extrair_info_pessoa_do_texto(texto_do_pdf)
            if cpf_encontrado:
                print (f" CPF encontrado no PDF: {cpf_encontrado}")
            else:
                print (" Nenhum CPF encontrado neste PDF com os padrões atuais.")

            if data_encontrada:
                novo_nome_base = data_encontrada
                extensao_pdf = ".pdf"

                contador = 0
                novo_nome_final = f"{novo_nome_base}{extensao_pdf}"
                novo_caminho_final_pdf = os.path.join(pasta_de_busca, novo_nome_final)

                while os.path.exists (novo_caminho_final_pdf) and novo_caminho_final_pdf !=caminho_completo_pdf:
                    contador += 1
                    novo_nome_final = f"{novo_nome_base}_{contador}{extensao_pdf}"
                    novo_caminho_final_pdf = os.path.join(pasta_de_busca, novo_nome_final)

                try:
                    os.rename(caminho_completo_pdf, novo_caminho_final_pdf)
                    print(f"Arquivo '{pdf}' renomeado para '{novo_nome_final}'")
                except OSError as e:
                    print (f"ERRO: Não foi possível renomear '{pdf}' para '{novo_nome_final}': {e}")        
            else:
                print (f"AVISO: PDF '{pdf}' não foi renomeado, pois nenhuma data foi encontrada.")

        escolha_ordem = ""
        while escolha_ordem not in ['1', '2']:
            escolha_ordem = input("\nEscolha a ordem para unificar os PDFs:\n1 - Ordem Crescente (do mais antigo para o mais novo)\n2 - Ordem Decrescente (do mais novo para o mais antigo)\nDigite 1 ou 2: ").strip()

            if escolha_ordem == '1':
                unificar_em_crescente = True
                print("Ordem de unificação selecionada: Crescente.")
            elif escolha_ordem == '2':
                unificar_em_crescente = False
                print("Ordem de unificação selecionada:Decrescente.")
            else:
                print("Opção inválida. Por favor, dia 1 para Crescente ou 2 para Decrescente.")

        nome_arquivo_saida_usuario = input("Digite o nome para o arquivo PDF unificado (ex: holerites_consolidados.pdf): ").strip()
        if not nome_arquivo_saida_usuario.lower().endswith(".pdf"):
            nome_arquivo_saida_usuario += ".pdf"
        print(f"O arquivo final será salvo como: '{nome_arquivo_saida_usuario}'")

        unificar_pdfs(
            caminho_pasta=pasta_de_busca,
            ordem_crescente=unificar_em_crescente,
            nome_arquivo_saida=nome_arquivo_saida_usuario
        )    
    else:
        print("\nNenhum PDF encontrado nesta pasta.")
    
    
    print ("\n Organizador de PDF finalizado")
    print("Até a próxima!")

if __name__ == "__main__":
    main()
    