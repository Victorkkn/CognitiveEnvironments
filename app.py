import streamlit as st
import os
import tempfile
from PIL import Image
from pprint import pformat
from main_pipeline import validar_identidade_completa

st.set_page_config(page_title="Validador de Identidade", layout="centered")
st.title("🔍 Validador de Identidade por Imagem")

st.markdown("Faça o upload das 3 imagens para validar a identidade:")

cnh_file = st.file_uploader("CNH (foto do documento)", type=["jpg", "jpeg", "png"], key="cnh")
selfie_file = st.file_uploader("Selfie", type=["jpg", "jpeg", "png"], key="selfie")
comprovante_file = st.file_uploader("Comprovante de Residência", type=["jpg", "jpeg", "png"], key="comp")

if cnh_file and selfie_file and comprovante_file:
    with tempfile.TemporaryDirectory() as tmpdir:
        path_cnh = os.path.join(tmpdir, "cnh.jpg")
        path_selfie = os.path.join(tmpdir, "selfie.jpg")
        path_comp = os.path.join(tmpdir, "comp.jpg")

        # Salva arquivos
        with open(path_cnh, 'wb') as f: f.write(cnh_file.read())
        with open(path_selfie, 'wb') as f: f.write(selfie_file.read())
        with open(path_comp, 'wb') as f: f.write(comprovante_file.read())

        # Roda o pipeline
        with st.spinner("Analisando documentos..."):
            resultado = validar_identidade_completa(
                path_cnh_img=path_cnh,
                path_selfie_img=path_selfie,
                path_comprovante_img=path_comp
            )

        st.success("Validação concluída")

        if "erro" in resultado:
            st.error(resultado["erro"])
        else:
            st.subheader("Resultado")
            st.json(resultado)

            if "status_final" in resultado:
                st.markdown(f"### Resultado Final: **{resultado['status_final']}**")