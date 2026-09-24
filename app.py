import os
import json
import re
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from groq import Groq


# ============================================================
# CONFIGURACIÓN
# ============================================================

load_dotenv()

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("❌ No se encontró GROQ_API_KEY.")
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

MODEL = "openai/gpt-oss-20b"


# ============================================================
# PÁGINA
# ============================================================

st.set_page_config(
    page_title="UTP Assistant",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# ESTILOS
# ============================================================

st.markdown("""
<style>

.main-title {
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 0px;
}

.subtitle {
    font-size: 17px;
    color: #666;
    margin-bottom: 25px;
}

.tool-card {
    padding: 14px;
    border-radius: 10px;
    background-color: #262a33;
    margin-bottom: 10px;
    border: 1px solid #454b57;
    color: white;
}

.tool-card b {
    color: white;
}

.tool-card small {
    color: #d0d5dd;
}

.status-card {
    padding: 12px;
    border-radius: 10px;
    background-color: #eef7ee;
    border: 1px solid #c9e6c9;
    margin-bottom: 15px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
Eres UTP Assistant, un asistente inteligente para UTPConsult,
una empresa de consultoría de software.

Tu función es apoyar la gestión de clientes y proyectos mediante
el análisis de correos, mensajes y solicitudes.

OBJETIVOS:

1. Analizar comunicaciones de clientes y prospectos.
2. Identificar requisitos y necesidades.
3. Extraer información relevante.
4. Crear tickets de proyecto.
5. Programar reuniones.
6. Actualizar información de contactos.
7. Generar resúmenes.
8. Proponer acciones siguientes.

REGLAS:

- No inventes información.
- Utiliza únicamente la información proporcionada por el usuario.
- Si faltan datos necesarios para ejecutar una herramienta,
  solicita la información faltante.
- Utiliza herramientas solamente cuando sean necesarias.
- Verifica los datos antes de ejecutar una herramienta.
- Mantén comunicación profesional y clara.
- Explica brevemente las acciones realizadas.
- Si una herramienta presenta un error, informa al usuario.
- Cuando analices una solicitud identifica, cuando exista:
  empresa, contacto, necesidad, requisitos, prioridad y acciones.

MANEJO DE AMBIGÜEDADES:

- No conviertas expresiones relativas como "la próxima semana",
  "más adelante", "en unos días" o "mañana" en una fecha exacta
  sin que el usuario la haya confirmado.
- Para programar una reunión necesitas una fecha y hora explícitas.
- Si falta la fecha o la hora, solicita aclaración.
- No inventes fechas, horas, participantes ni datos de contacto.

IMPORTANTE SOBRE LAS INTEGRACIONES:

- Jira, Google Calendar y CRM son actualmente simulaciones.
- Nunca afirmes que se creó un ticket real en Jira.
- Nunca afirmes que se creó un evento real en Google Calendar.
- Nunca afirmes que se actualizó un registro real en un CRM.
- Cuando una herramienta sea ejecutada, indica que la operación
  fue realizada en modo simulación.
- Utiliza expresiones como "simulación", "resultado simulado"
  o "integración pendiente".
- No inventes conexiones externas que no hayan sido implementadas.
"""


# ============================================================
# FUNCIONES
# ============================================================

def crear_ticket_en_jira(
    titulo,
    descripcion,
    prioridad,
    proyecto
):

    ticket_id = f"UTP-{datetime.now().strftime('%H%M%S')}"

    return json.dumps({
        "estado": "simulado",
        "ticket_id": ticket_id,
        "titulo": titulo,
        "descripcion": descripcion,
        "prioridad": prioridad,
        "proyecto": proyecto,
        "mensaje": "Ticket creado correctamente en modo simulación."
    }, ensure_ascii=False)


def agendar_reunion_en_google_calendar(
    titulo,
    fecha,
    hora,
    duracion_minutos,
    participantes,
    descripcion
):

    evento_id = f"CAL-{datetime.now().strftime('%H%M%S')}"

    return json.dumps({
        "estado": "simulado",
        "evento_id": evento_id,
        "titulo": titulo,
        "fecha": fecha,
        "hora": hora,
        "duracion_minutos": duracion_minutos,
        "participantes": participantes,
        "descripcion": descripcion,
        "mensaje": "Reunión preparada correctamente en modo simulación."
    }, ensure_ascii=False)


def actualizar_contacto_en_crm(
    nombre,
    empresa,
    email,
    telefono,
    cargo,
    notas
):

    contacto_id = f"CRM-{datetime.now().strftime('%H%M%S')}"

    return json.dumps({
        "estado": "simulado",
        "contacto_id": contacto_id,
        "nombre": nombre,
        "empresa": empresa,
        "email": email,
        "telefono": telefono,
        "cargo": cargo,
        "notas": notas,
        "mensaje": "Contacto actualizado correctamente en modo simulación."
    }, ensure_ascii=False)


# ============================================================
# TOOLS
# ============================================================

TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "crear_ticket_en_jira",
            "description":
                "Crea un ticket de proyecto en Jira cuando se identifica "
                "una tarea, requerimiento, incidencia o actividad.",
            "parameters": {
                "type": "object",
                "properties": {

                    "titulo": {
                        "type": "string",
                        "description":
                            "Título breve y claro del ticket."
                    },

                    "descripcion": {
                        "type": "string",
                        "description":
                            "Descripción detallada del requerimiento."
                    },

                    "prioridad": {
                        "type": "string",
                        "enum": [
                            "baja",
                            "media",
                            "alta",
                            "urgente"
                        ],
                        "description":
                            "Nivel de prioridad."
                    },

                    "proyecto": {
                        "type": "string",
                        "description":
                            "Nombre del proyecto."
                    }
                },
                "required": [
                    "titulo",
                    "descripcion",
                    "prioridad",
                    "proyecto"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "agendar_reunion_en_google_calendar",
            "description":
                "Programa una reunión con un cliente, prospecto o equipo.",
            "parameters": {
                "type": "object",
                "properties": {

                    "titulo": {
                        "type": "string",
                        "description":
                            "Título de la reunión."
                    },

                    "fecha": {
                        "type": "string",
                        "description":
                            "Fecha en formato YYYY-MM-DD."
                    },

                    "hora": {
                        "type": "string",
                        "description":
                            "Hora en formato HH:MM."
                    },

                    "duracion_minutos": {
                        "type": "integer",
                        "description":
                            "Duración de la reunión en minutos."
                    },

                    "participantes": {
                        "type": "string",
                        "description":
                            "Participantes de la reunión."
                    },

                    "descripcion": {
                        "type": "string",
                        "description":
                            "Objetivo o descripción de la reunión."
                    }
                },
                "required": [
                    "titulo",
                    "fecha",
                    "hora",
                    "duracion_minutos",
                    "participantes",
                    "descripcion"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "actualizar_contacto_en_crm",
            "description":
                "Actualiza información de un contacto en el CRM.",
            "parameters": {
                "type": "object",
                "properties": {

                    "nombre": {
                        "type": "string",
                        "description":
                            "Nombre completo del contacto."
                    },

                    "empresa": {
                        "type": "string",
                        "description":
                            "Empresa del contacto."
                    },

                    "email": {
                        "type": "string",
                        "description":
                            "Correo electrónico."
                    },

                    "telefono": {
                        "type": "string",
                        "description":
                            "Teléfono."
                    },

                    "cargo": {
                        "type": "string",
                        "description":
                            "Cargo del contacto."
                    },

                    "notas": {
                        "type": "string",
                        "description":
                            "Información adicional."
                    }
                },
                "required": [
                    "nombre",
                    "empresa",
                    "email",
                    "telefono",
                    "cargo",
                    "notas"
                ]
            }
        }
    }
]


# ============================================================
# MAPA DE FUNCIONES
# ============================================================

AVAILABLE_FUNCTIONS = {
    "crear_ticket_en_jira": crear_ticket_en_jira,
    "agendar_reunion_en_google_calendar":
        agendar_reunion_en_google_calendar,
    "actualizar_contacto_en_crm":
        actualizar_contacto_en_crm
}


# ============================================================
# VALIDACIÓN DE FECHA
# ============================================================

def contiene_fecha_explicita(texto):

    patrones_fecha = [

        r"\b\d{1,2}\s+de\s+(enero|febrero|marzo|abril|mayo|junio|"
        r"julio|agosto|septiembre|octubre|noviembre|diciembre)"
        r"\s+de\s+\d{4}\b",

        r"\b\d{4}-\d{2}-\d{2}\b",

        r"\b\d{1,2}/\d{1,2}/\d{4}\b"
    ]

    texto = texto.lower()

    for patron in patrones_fecha:

        if re.search(patron, texto):
            return True

    return False


# ============================================================
# VALIDACIÓN DE HORA
# ============================================================

def contiene_hora_explicita(texto):

    patrones_hora = [

        r"\b\d{1,2}:\d{2}\b",

        r"\b\d{1,2}\s*(a\.?\s*m\.?|p\.?\s*m\.?)\b"
    ]

    texto = texto.lower()

    for patron in patrones_hora:

        if re.search(patron, texto):
            return True

    return False


# ============================================================
# EJECUTAR TOOL CALL CON VALIDACIONES
# ============================================================

def execute_tool_call(tool_call, user_prompt):

    function_name = tool_call.function.name

    if function_name not in AVAILABLE_FUNCTIONS:

        return json.dumps({
            "error":
                f"Herramienta no disponible: {function_name}"
        }, ensure_ascii=False)


    # ========================================================
    # VALIDACIÓN ESPECIAL PARA GOOGLE CALENDAR
    # ========================================================

    if function_name == "agendar_reunion_en_google_calendar":

        tiene_fecha = contiene_fecha_explicita(
            user_prompt
        )

        tiene_hora = contiene_hora_explicita(
            user_prompt
        )

        # Si falta la fecha o la hora, NO ejecutar Calendar
        if not tiene_fecha or not tiene_hora:

            datos_faltantes = []

            if not tiene_fecha:
                datos_faltantes.append("fecha exacta")

            if not tiene_hora:
                datos_faltantes.append("hora exacta")

            return json.dumps({

                "estado": "requiere_aclaracion",

                "herramienta": function_name,

                "ejecutada": False,

                "datos_faltantes":
                    datos_faltantes,

                "mensaje":
                    "No se ejecutó la programación de la reunión "
                    "porque faltan datos obligatorios."

            }, ensure_ascii=False)
    # ========================================================
    # VALIDACIÓN ESPECIAL PARA CRM
    # ========================================================

    if function_name == "actualizar_contacto_en_crm":

        try:

            arguments = json.loads(
                tool_call.function.arguments
            )

        except Exception:

            return json.dumps({

                "estado": "requiere_aclaracion",

                "herramienta": function_name,

                "ejecutada": False,

                "mensaje":
                    "No se pudo interpretar correctamente "
                    "la información del contacto."

            }, ensure_ascii=False)


        campos_obligatorios = {

            "nombre": "nombre completo",

            "empresa": "empresa",

            "email": "correo electrónico",

            "telefono": "teléfono",

            "cargo": "cargo"

        }


        datos_faltantes = []


        for campo, descripcion in campos_obligatorios.items():

            valor = arguments.get(campo)

            if valor is None or str(valor).strip() == "":

                datos_faltantes.append(
                    descripcion
                )


        if datos_faltantes:

            return json.dumps({

                "estado": "requiere_aclaracion",

                "herramienta": function_name,

                "ejecutada": False,

                "datos_faltantes":
                    datos_faltantes,

                "mensaje":
                    "No se actualizó el contacto porque "
                    "faltan datos obligatorios."

            }, ensure_ascii=False)

    # ========================================================
    # EJECUCIÓN NORMAL
    # ========================================================

    try:

        arguments = json.loads(
            tool_call.function.arguments
        )

        function = AVAILABLE_FUNCTIONS[function_name]

        return function(**arguments)

    except Exception as e:

        return json.dumps({

            "error": str(e),

            "is_error": True

        }, ensure_ascii=False)


# ============================================================
# MOSTRAR RESULTADO VISUAL
# ============================================================

def render_tool_result(function_name, result):

    try:

        data = json.loads(result)

    except Exception:

        st.markdown(result)

        return


    estado = data.get(
        "estado",
        "simulado"
    )


    # ========================================================
    # JIRA
    # ========================================================

    if function_name == "crear_ticket_en_jira":

        st.success(
            "🎫 TICKET CREADO — MODO SIMULACIÓN"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                f"**ID:** {data.get('ticket_id', '-')}"
            )

            st.markdown(
                f"**Proyecto:** {data.get('proyecto', '-')}"
            )

            st.markdown(
                f"**Prioridad:** {data.get('prioridad', '-')}"
            )

        with col2:

            st.markdown(
                f"**Título:** {data.get('titulo', '-')}"
            )

            st.markdown(
                f"**Estado:** {estado}"
            )

        st.caption(
            "ℹ️ La integración con Jira está simulada "
            "para fines académicos."
        )


    # ========================================================
    # GOOGLE CALENDAR
    # ========================================================

    elif function_name == "agendar_reunion_en_google_calendar":

        # ====================================================
        # FALTAN DATOS
        # ====================================================

        if data.get("estado") == "requiere_aclaracion":

            st.warning(
                "⚠️ **REUNIÓN NO PROGRAMADA**"
            )

            datos_faltantes = data.get(
                "datos_faltantes",
                []
            )

            if datos_faltantes:

                st.markdown(
                    "**Datos faltantes:** "
                    + ", ".join(datos_faltantes)
                )

            st.caption(
                "ℹ️ La herramienta no fue ejecutada "
                "porque faltan datos obligatorios."
            )


        # ====================================================
        # SIMULACIÓN CORRECTA
        # ====================================================

        else:

            st.success(
                "📅 **REUNIÓN PROGRAMADA — MODO SIMULACIÓN**"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    f"**ID:** {data.get('evento_id', '-')}"
                )

                st.markdown(
                    f"**Fecha:** {data.get('fecha', '-')}"
                )

                st.markdown(
                    f"**Hora:** {data.get('hora', '-')}"
                )

            with col2:

                st.markdown(
                    f"**Duración:** "
                    f"{data.get('duracion_minutos', '-')} minutos"
                )

                st.markdown(
                    f"**Participantes:** "
                    f"{data.get('participantes', '-')}"
                )

                st.markdown(
                    f"**Estado:** {estado}"
                )

            st.caption(
                "ℹ️ La integración con Google Calendar está "
                "simulada para fines académicos."
            )


    # ========================================================
    # CRM
    # ========================================================
    elif function_name == "actualizar_contacto_en_crm":

        # ====================================================
        # CASO: FALTAN DATOS
        # ====================================================

        if data.get("estado") == "requiere_aclaracion":

            st.warning(
                "⚠️ **CONTACTO NO ACTUALIZADO**"
            )

            datos_faltantes = data.get(
                "datos_faltantes",
                []
            )

            if datos_faltantes:

                st.markdown(
                    "**Datos faltantes:** "
                    + ", ".join(datos_faltantes)
                )

            st.caption(
                "ℹ️ La herramienta no fue ejecutada "
                "porque faltan datos obligatorios."
            )

        # ====================================================
        # CASO: ACTUALIZACIÓN SIMULADA CORRECTA
        # ====================================================

        else:

            st.success(
                "👤 **CONTACTO ACTUALIZADO — MODO SIMULACIÓN**"
            )

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    f"**ID:** {data.get('contacto_id', '-')}"
                )

                st.markdown(
                    f"**Nombre:** {data.get('nombre', '-')}"
                )

                st.markdown(
                    f"**Empresa:** {data.get('empresa', '-')}"
                )

            with col2:

                st.markdown(
                    f"**Cargo:** {data.get('cargo', '-')}"
                )

                st.markdown(
                    f"**Correo:** {data.get('email', '-')}"
                )

                st.markdown(
                    f"**Teléfono:** {data.get('telefono', '-')}"
                )

            st.caption(
                "ℹ️ La integración con el CRM está "
                "simulada para fines académicos."
            )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🏫 UTPConsult")

    st.markdown(
        "### 🤖 UTP Assistant"
    )

    st.write(
        "Asistente inteligente para la gestión "
        "de clientes y proyectos."
    )

    st.divider()

    st.markdown("### 🛠️ Herramientas")

    st.markdown("""
    <div class="tool-card">
    🎫 <b>Jira</b><br>
    Crear tickets de proyectos
    </div>

    <div class="tool-card">
    📅 <b>Google Calendar</b><br>
    Agendar reuniones
    </div>

    <div class="tool-card">
    👤 <b>CRM</b><br>
    Actualizar contactos
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### 🟢 Estado")

    st.markdown("""
    <div class="tool-card">
    🟢 <b>Asistente activo</b><br>
    Modelo: GPT-OSS-20B<br>
    Motor: Groq
    </div>
    """, unsafe_allow_html=True)

    if st.button(
        "🧹 Limpiar conversación",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# ENCABEZADO
# ============================================================

st.markdown(
    '<div class="main-title">🤖 UTP Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Asistente inteligente para gestión de clientes y proyectos'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# HISTORIAL
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


if len(st.session_state.messages) == 0:

    st.info(
        "👋 Hola. Soy UTP Assistant. "
        "Puedo analizar solicitudes y utilizar herramientas "
        "para gestionar tickets, reuniones y contactos."
    )

    st.markdown("### 💡 Ejemplos")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            "**🎫 Jira**\n\n"
            "Crear un ticket para un nuevo requerimiento."
        )

    with col2:

        st.markdown(
            "**📅 Calendar**\n\n"
            "Programar una reunión con un cliente."
        )

    with col3:

        st.markdown(
            "**👤 CRM**\n\n"
            "Actualizar los datos de un contacto."
        )


# ============================================================
# MOSTRAR HISTORIAL
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# CHAT
# ============================================================

user_prompt = st.chat_input(
    "Escribe una solicitud para UTP Assistant..."
)


if user_prompt:

    with st.chat_message("user"):

        st.markdown(user_prompt)

    st.session_state.messages.append({
        "role": "user",
        "content": user_prompt
    })


    messages = [

        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }

    ] + st.session_state.messages


    with st.chat_message("assistant"):

        try:

            final_response = None


            # =================================================
            # CICLO DE TOOL CALLING
            # =================================================

            for _ in range(5):

                with st.spinner(
                    "UTP Assistant está procesando..."
                ):

                    response = client.chat.completions.create(

                        model=MODEL,

                        messages=messages,

                        tools=TOOLS,

                        tool_choice="auto",

                        temperature=0.2,

                        max_completion_tokens=1200
                    )


                assistant_message = response.choices[0].message


                # =============================================
                # RESPUESTA DIRECTA
                # =============================================

                if not assistant_message.tool_calls:

                    final_response = (
                        assistant_message.content
                        or "No se pudo generar una respuesta."
                    )

                    break


                # =============================================
                # AGREGAR TOOL CALL AL HISTORIAL
                # =============================================

                assistant_dict = {

                    "role": "assistant",

                    "content":
                        assistant_message.content or "",

                    "tool_calls": []
                }


                for tc in assistant_message.tool_calls:

                    assistant_dict["tool_calls"].append({

                        "id": tc.id,

                        "type": "function",

                        "function": {

                            "name":
                                tc.function.name,

                            "arguments":
                                tc.function.arguments
                        }
                    })


                messages.append(
                    assistant_dict
                )


                # =============================================
                # EJECUTAR HERRAMIENTAS
                # =============================================

                for tool_call in assistant_message.tool_calls:

                    function_name = (
                        tool_call.function.name
                    )


                    st.info(
                        f"🔧 Ejecutando: **{function_name}**"
                    )


                    result = execute_tool_call(
                        tool_call,
                        user_prompt
                    )


                    render_tool_result(
                        function_name,
                        result
                    )


                    messages.append({

                        "role": "tool",

                        "tool_call_id":
                            tool_call.id,

                        "name":
                            function_name,

                        "content":
                            result
                    })


            # =================================================
            # RESPUESTA FINAL
            # =================================================

            if final_response is None:

                final_response = (
                    "No fue posible completar el proceso."
                )


            st.markdown(
                final_response
            )


            st.session_state.messages.append({

                "role": "assistant",

                "content":
                    final_response

            })


        except Exception as e:

            error_message = (
                f"❌ Ocurrió un error: {str(e)}"
            )

            st.error(
                error_message
            )

            st.session_state.messages.append({

                "role": "assistant",

                "content":
                    error_message

            })