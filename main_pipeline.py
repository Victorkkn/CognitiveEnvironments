import boto3
import cv2
import re
from difflib import SequenceMatcher
from unidecode import unidecode
import os
import face_recognition

def extrair_texto_textract(path_img):
    textract = boto3.client('textract', region_name='us-east-1')
    with open(path_img, 'rb') as f:
        resposta = textract.detect_document_text(Document={'Bytes': f.read()})
    return [b['Text'] for b in resposta['Blocks'] if b['BlockType'] == 'LINE']


def extrair_dados_cnh(linhas):
    texto = ' '.join(linhas).upper()
    nome = next((linhas[i+1].strip().title() for i, l in enumerate(linhas) if 'NOME' in l.upper()), None)
    cpf_match = re.search(r'\d{3}.\d{3}.\d{3}-\d{2}', texto)
    data_match = re.search(r'\d{2}/\d{2}/\d{4}', texto)
    return {
        'nome': nome,
        'cpf': cpf_match.group(0) if cpf_match else None,
        'data_nascimento': data_match.group(0) if data_match else None
    }


def extrair_dados_comprovante(linhas):
    nome = None
    endereco = None
    cep_index = next((i for i, l in enumerate(linhas) if re.search(r'\d{5}-\d{3}\s+[A-Z]{2}', l)), None)
    if cep_index is not None and cep_index >= 2:
        nome = linhas[cep_index - 3].strip().title()
        end1 = linhas[cep_index - 2].strip().title()
        end2 = linhas[cep_index - 1].strip().title()
        end3 = linhas[cep_index].strip().title()
        endereco = f"{end1}, {end2}, {end3}"
    return {'nome': nome, 'endereco': endereco}

def extrair_face(imagem_path, saida_path, min_bytes=10000):
    if not os.path.exists(imagem_path) or os.path.getsize(imagem_path) < min_bytes:
        raise ValueError(f"Imagem inválida ou muito pequena: {imagem_path}")

    imagem_bgr = cv2.imread(imagem_path)
    if imagem_bgr is None or imagem_bgr.size == 0:
        raise ValueError(f"Erro ao carregar imagem: {imagem_path}")

    imagem_rgb = cv2.cvtColor(imagem_bgr, cv2.COLOR_BGR2RGB)
    faces = face_recognition.face_locations(imagem_rgb)

    if len(faces) == 0:
        raise ValueError(f"Nenhuma face detectada em: {imagem_path}")

    top, right, bottom, left = faces[0]
    face_recortada = imagem_rgb[top:bottom, left:right]

    # Verifica dimensões mínimas
    h, w, _ = face_recortada.shape
    if w < 60 or h < 60:
        raise ValueError(f"Face recortada muito pequena (w={w}, h={h}) em: {imagem_path}")

    # Salva imagem RGB convertida de volta para BGR
    cv2.imwrite(saida_path, cv2.cvtColor(face_recortada, cv2.COLOR_RGB2BGR))

    # Verifica tamanho final
    if not os.path.exists(saida_path) or os.path.getsize(saida_path) < min_bytes:
        raise ValueError(f"Face recortada inválida (arquivo final corrompido): {saida_path}")

    return saida_path

def comparar_faces_rekognition(path_cnh_face, path_selfie_face):
    rekognition = boto3.client('rekognition', region_name='us-east-1')
    with open(path_cnh_face, 'rb') as f1, open(path_selfie_face, 'rb') as f2:
        r = rekognition.compare_faces(SourceImage={'Bytes': f1.read()},
                                      TargetImage={'Bytes': f2.read()},
                                      SimilarityThreshold=70)
    return r['FaceMatches'][0]['Similarity'] if r['FaceMatches'] else 0.0


def comparar_nomes(n1, n2, limiar=0.85):
    def clean(t): return unidecode(t or "").lower().strip()
    sim = SequenceMatcher(None, clean(n1), clean(n2)).ratio()
    return sim, sim >= limiar


def validar_identidade_completa(path_cnh_img, path_selfie_img, path_comprovante_img):
    # Extrai texto da CNH
    linhas_cnh = extrair_texto_textract(path_cnh_img)
    dados_cnh = extrair_dados_cnh(linhas_cnh)

    # Extrai texto do comprovante
    linhas_comp = extrair_texto_textract(path_comprovante_img)
    dados_comp = extrair_dados_comprovante(linhas_comp)

    # Extrai faces automaticamente e salva em arquivos temporários
    path_face_cnh = './face_extraction_cnh/temp_face_cnh.jpg'
    path_face_selfie = './face_extraction_selfie/temp_face_selfie.jpg'
    
    try:
        extrair_face(path_cnh_img, path_face_cnh)
    except Exception as e:
        return {"erro": f"Falha na extração da face da CNH: {e}"}
    
    try:
        extrair_face(path_selfie_img, path_face_selfie)
    except Exception as e:
        return {"erro": f"Falha na extração da face da selfie: {e}"}

    # Compara faces
    similaridade_face = comparar_faces_rekognition(path_face_cnh, path_face_selfie)

    # Compara nomes
    similaridade_nome, nome_ok = comparar_nomes(dados_cnh['nome'], dados_comp['nome'])

    # Status final
    status = (
        "✅ Aprovado" if nome_ok and similaridade_face >= 90 else
        "⚠️ Alerta: requer validação manual" if similaridade_face >= 70 else
        "❌ Reprovado"
    )

    return {
        "documento_cnh": {
                "nome": dados_cnh['nome'],
                "cpf": dados_cnh['cpf'],
                "data_nascimento": dados_cnh['data_nascimento']
            },
            "comprovante_residencia": {
                "nome": dados_comp['nome'],
                "endereco": dados_comp['endereco']
            },
            "verificacoes": {
                "similaridade_nome": f"{round(similaridade_nome * 100, 2)}%",
                "similaridade_face": f"{round(similaridade_face, 2)}%",
                "validacao_nome": "✅ Nome confere" if nome_ok else "❌ Nome divergente",
                "validacao_face": (
                    "✅ Face validada" if similaridade_face >= 90 else
                    "⚠️ Abaixo de 90% — revisão manual" if similaridade_face >= 70 else
                    "❌ Face inválida"
                )
            },
            "status_final": status
    }