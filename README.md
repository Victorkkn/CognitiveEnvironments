# 🔍 Validador de Identidade por Imagem

Este projeto foi desenvolvido como parte do trabalho prático da disciplina **[Cognitive Environments]**, com o objetivo de validar a identidade de um usuário a partir de **três imagens**:

- Foto da CNH (documento oficial)
- Selfie
- Comprovante de residência

A aplicação utiliza os serviços **AWS Textract** (para OCR) e **AWS Rekognition** (para comparação facial), além de bibliotecas de visão computacional como `OpenCV` e `face_recognition`.

---

## 🎓 Sobre o trabalho

Este repositório contém:

- 🧪 **face_text_extraction_estudo.ipynb**\
  Notebook utilizado para experimentação com diferentes estratégias de OCR, recorte facial e chamadas AWS.

- 📆 **face_text_extraction_consolidado.ipynb**\
  Versão limpa e sequencial do fluxo completo, pronta para entrega e leitura pela banca/professor.

- 🧠 **main_pipeline.py**\
  Script com o pipeline funcional consolidado, contendo:

  - Extração de dados da CNH
  - Extração do comprovante de residência
  - Detecção e recorte automático de faces
  - Comparação de nomes (com tolerância)
  - Comparação facial com Rekognition
  - Geração de um dicionário estruturado com o resultado final

- 💻 **app.py**\
  Aplicação **Streamlit** interativa que permite upload dos 3 documentos e retorna a validação em tempo real.

---

## ⚙️ Pré-requisitos

- Python 3.12
- Conta AWS válida
- Permissões habilitadas:
  - `AmazonTextractFullAccess`
  - `AmazonRekognitionFullAccess`

---

## ☁️ Configurando credenciais da AWS

O app utiliza o SDK `boto3`, que requer que você configure suas chaves de acesso:

```bash
aws configure
```

Preencha com:

```
AWS Access Key ID:     <sua-chave>
AWS Secret Access Key: <sua-chave-secreta>
Default region name:   us-east-1
Default output format: json
```

> As credenciais também podem ser definidas via variáveis de ambiente ou arquivos `.aws/credentials`.

---

## 🖥️ Como rodar localmente

1. Clone o repositório:

```bash
git clone https://github.com/Victorkkn/CognitiveEnvironments.git
```

2. Crie e ative um ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate  # ou source .venv/bin/activate no Linux/Mac
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Execute o app:

```bash
streamlit run app.py
```

---

## 🥪 Exemplo de uso

Ao subir os 3 arquivos (CNH, selfie e comprovante), o sistema realiza:

- OCR com Textract (nome, CPF, data, endereço)
- Recorte e comparação facial com Rekognition
- Verificação de similaridade de nome entre CNH e comprovante
- Retorno estruturado com status final:

```json
{
  "documento_cnh": {
    "nome": "Victor Kennedy Kaneko Nunes",
    "cpf": "016.299.066-97",
    "data_nascimento": "09/08/1997"
  },
  "comprovante_residencia": {
    "nome": "Victor Kennedy Kaneko Nunes",
    "endereco": "Avenida Sebastiao Dayrell De L 110 Ap 303, Brasileia, 32600-266 Betim Mg"
  },
  "verificacoes": {
    "similaridade_nome": "100.0%",
    "similaridade_face": "99.84%",
    "validacao_nome": "✅ Nome confere",
    "validacao_face": "✅ Face validada"
  },
  "status_final": "✅ Aprovado"
}
```

---

## 📁 Estrutura esperada

```
📆 validador-identidade
├── app.py                        # App Streamlit
├── main_pipeline.py             # Pipeline de validação completo
├── face_text_extraction_estudo.ipynb
├── face_text_extraction_consolidado.ipynb
├── requirements.txt
└── imagens/
    ├── cnh.jpg
    ├── selfie.jpg
    └── comprovante.jpg
```
