import re
from flask import Flask, render_template, request

app = Flask(__name__)

# 1. CENTRALIZACIÓN DE REGLAS (SINGLE SOURCE OF TRUTH)
# Modifica los patrones solo aquí, y se actualizarán en toda la aplicación y la interfaz.
REGLAS_LENGUAJE = [
    {"token": "ID_PRODUCTO", "patron": r"^[A-Z]{4}-[0-9]{3}$", "ejemplo": "PROD-100", "desc": "4 letras mayúsculas, guion y 3 números"},
    {"token": "CANTIDAD", "patron": r"^[1-9][0-9]*$", "ejemplo": "50", "desc": "Número entero positivo sin ceros a la izquierda"},
    {"token": "PRECIO", "patron": r"^[0-9]+.[0-9]+$", "ejemplo": "12.50", "desc": "Número entero o decimal con punto"},
    {"token": "FIN_ORDEN", "patron": r"^;$", "ejemplo": ";", "desc": "Delimitador punto y coma de cierre de orden"}
]

# 2. GENERACIÓN AUTOMÁTICA DE VARIABLES BASADAS EN LAS REGLAS
PATRONES = [(regla["token"], regla["patron"]) for regla in REGLAS_LENGUAJE]

ENUNCIADO = {
    "titulo": "Desarrollo de un analizador léxico y sintáctico para la automatización de validación documental",
    "empresa": "TechLogis - Lima 2026",
    "descripcion": (
        "El proyecto resuelve el problema de la introducción manual de pedidos en el sector logístico, "
        "reduciendo errores tipográficos críticos que provocan interrupciones en el sistema ERP mediante "
        "un analizador determinista basado en Autómatas Finitos Deterministas (DFA) y Gramáticas Libres de Contexto (CFG)."
    ),
    "reglas": REGLAS_LENGUAJE,
    "cfg": "Orden -> ID_PRODUCTO CANTIDAD PRECIO FIN_ORDEN"
}

EJEMPLO_CODIGO = "PROD-100 50 12.50;"

def analizar_lexico(texto):
    tokens = []
    # Preprocesar para aislar los ';' si están pegados a los números
    texto_preprocesado = texto.replace(';', ' ;')
    palabras = texto_preprocesado.strip().split()
    
    for idx, palabra in enumerate(palabras, 1):
        match_encontrado = False
        for nombre_token, patron in PATRONES:
            if re.match(patron, palabra):
                tokens.append({
                    'id': idx,
                    'lexema': palabra,
                    'token': nombre_token,
                    'patron': patron,
                    'valido': True,
                    'detalle': f'Lexema válido para {nombre_token}'
                })
                match_encontrado = True
                break
        
        # Si NO hay match, igual pasamos un texto para que se muestre en la columna de RegEx
        if not match_encontrado:
            tokens.append({
                'id': idx,
                'lexema': palabra,
                'token': 'ERROR_LEXICO',
                'patron': '∅ (Sin coincidencia)', # <-- Se muestra incluso si no hay match
                'valido': False,
                'detalle': 'Lexema no pertenece al alfabeto ni reglas del lenguaje'
            })
            
    return tokens

def analizar_sintactico(tokens):
    if not tokens:
        return False, "No se ingresó ninguna cadena para analizar."

    si_tokens_validos = all(t['valido'] for t in tokens)
    if not si_tokens_validos:
        return False, "Error léxico detectado: Existen lexemas no reconocidos por el autómata."
    
    secuencia_esperada = ['ID_PRODUCTO', 'CANTIDAD', 'PRECIO', 'FIN_ORDEN']
    secuencia_obtenida = [t['token'] for t in tokens]
    
    if secuencia_obtenida == secuencia_esperada:
        return True, "¡Sintaxis Correcta! La orden cumple con la Gramática Libre de Contexto (CFG) y fue aprobada para el ERP."
    else:
        return False, f"Error Sintáctico: Estructura no válida. Se esperaba {secuencia_esperada} pero se recibió {secuencia_obtenida}."

@app.route('/', methods=['GET', 'POST'])
def index():
    codigo_entrada = EJEMPLO_CODIGO
    tokens_resultado = None
    es_sintaxis_valida = None
    mensaje_sintaxis = None

    if request.method == 'POST':
        if 'archivo' in request.files and request.files['archivo'].filename != '':
            archivo = request.files['archivo']
            codigo_entrada = archivo.read().decode('utf-8')
        else:
            codigo_entrada = request.form.get('codigo', '')

        if codigo_entrada.strip():
            tokens_resultado = analizar_lexico(codigo_entrada)
            es_sintaxis_valida, mensaje_sintaxis = analizar_sintactico(tokens_resultado)

    # Calcular estadísticas
    tot_lexemas = len(tokens_resultado) if tokens_resultado else 0
    tot_validos = sum(1 for t in tokens_resultado if t['valido']) if tokens_resultado else 0
    tot_errores = tot_lexemas - tot_validos

    return render_template(
        'index.html',
        enunciado=ENUNCIADO,
        ejemplo=EJEMPLO_CODIGO,
        codigo=codigo_entrada,
        tokens=tokens_resultado,
        sintaxis_valida=es_sintaxis_valida,
        mensaje_sintaxis=mensaje_sintaxis,
        tot_lexemas=tot_lexemas,
        tot_validos=tot_validos,
        tot_errores=tot_errores
    )

if __name__ == '__main__':
    app.run(debug=True)