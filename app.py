import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="UTP Assistant",
    page_icon="🤖"
)


# ============================================================
# CARGAR API KEY
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


if not GROQ_API_KEY:
    st.error(
        "No se encontró GROQ_API_KEY. "
        "Verifica que exista el archivo .env."
    )
    st.stop()


# ============================================================
# CONEXIÓN CON GROQ
# ============================================================

try:
    client = Groq(
        api_key=GROQ_API_KEY
    )

except Exception as e:
    st.error(f"Error conectando con Groq: {e}")
    st.stop()


# ============================================================
# MODELO
# ============================================================

MODEL = "openai/gpt-oss-20b"


# ============================================================
# PROMPT DEL SISTEMA
# ============================================================

SYSTEM_PROMPT = """
Eres UTP Assistant, asistente inteligente de UTPConsult.

Funciones:
- Analizar correos de clientes.
- Extraer requisitos.
- Identificar empresas y contactos.
- Crear resúmenes.
- Proponer acciones.

Reglas:
- No inventes información.
- Si falta información solicita aclaración.
- Mantén comunicación profesional.
"""


# ============================================================
# INTERFAZ
# ============================================================

st.title("🤖 UTP Assistant")

st.write(
    "Asistente inteligente para gestión de clientes y proyectos"
)


# ============================================================
# HISTORIAL
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# ============================================================
# ENTRADA
# ============================================================

prompt = st.chat_input(
    "Ingrese correo o consulta..."
)


# ============================================================
# PROCESAMIENTO
# ============================================================

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )


    with st.chat_message("user"):
        st.write(prompt)


    try:

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]


        # Agregar historial

        for m in st.session_state.messages:

            messages.append(
                {
                    "role": m["role"],
                    "content": m["content"]
                }
            )


        # ====================================================
        # GROQ
        # ====================================================

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.3,
            max_tokens=1024
        )


        answer = response.choices[0].message.content


        # Guardar respuesta

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


        with st.chat_message("assistant"):
            st.write(answer)


    except Exception as e:

        st.error(
            f"Error con Groq API: {e}"
        )