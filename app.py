import re
from flask import Flask, render_template, request

app = Flask(__name__)

# 1. CENTRALIZACIÓN DE REGLAS
REGLAS_LENGUAJE = [
    {"token": "ID_PRODUCTO", "patron": r"^[A-Z]{4}-[0-9]{3}$", "ejemplo": "PROD-100", "desc": "4 letras mayúsculas, guion y 3 números"},
    {"token": "CANTIDAD", "patron": r"^[1-9][0-9]*$", "ejemplo": "50", "desc": "Número entero positivo sin ceros a la izquierda"},
    {"token": "PRECIO", "patron": r"^[0-9]+\.[0-9]+$", "ejemplo": "12.50", "desc": "Número decimal obligatorio con punto"},
    {"token": "FIN_ORDEN", "patron": r"^;$", "ejemplo": ";", "desc": "Delimitador punto y coma de cierre de orden"}
]

PATRONES = [(regla["token"], regla["patron"]) for regla in REGLAS_LENGUAJE]

GRAMATICA = {
    "Orden": [
        ("ID_PRODUCTO", "CANTIDAD", "PRECIO", "FIN_ORDEN")
    ]
}

# 2. BASE DE DATOS TEÓRICA (QUÍNTUPLAS, TABLAS Y CÓDIGO DE GRAFOS)
TEORIA_AUTOMATAS = {
    "ID_PRODUCTO": {
        "quintupla": "Q = {q0, q1, q2, q3, q4, q5, q6, q7, q8}\nΣ = {[A-Z], -, [0-9]}\nq0 = q0\nF = {q8}\nδ = Función de transición (ver tabla)",
        "tabla": {
            "cabeceras": ["Estado (Q)", "Entrada [A-Z]", "Entrada '-'", "Entrada [0-9]"],
            "filas": [
                ["-> q0", "q1", "∅", "∅"], ["q1", "q2", "∅", "∅"], ["q2", "q3", "∅", "∅"],
                ["q3", "q4", "∅", "∅"], ["q4", "∅", "q5", "∅"], ["q5", "∅", "∅", "q6"],
                ["q6", "∅", "∅", "q7"], ["q7", "∅", "∅", "*q8"], ["*q8", "∅", "∅", "∅"]
            ]
        },
        "afnd": "graph LR\n q0((q0))--\"[A-Z]\"-->q1((q1))\n q1--\"[A-Z]\"-->q2((q2))\n q2--\"[A-Z]\"-->q3((q3))\n q3--\"[A-Z]\"-->q4((q4))\n q4--\"-\"-->q5((q5))\n q5--\"[0-9]\"-->q6((q6))\n q6--\"[0-9]\"-->q7((q7))\n q7--\"[0-9]\"-->q8(((q8)))",
        "afd": "graph LR\n q0((q0))--\"[A-Z]\"-->q1((q1))\n q1--\"[A-Z]\"-->q2((q2))\n q2--\"[A-Z]\"-->q3((q3))\n q3--\"[A-Z]\"-->q4((q4))\n q4--\"-\"-->q5((q5))\n q5--\"[0-9]\"-->q6((q6))\n q6--\"[0-9]\"-->q7((q7))\n q7--\"[0-9]\"-->q8(((q8)))"
    },
    "CANTIDAD": {
        "quintupla": "Q = {q0, q1}\nΣ = {[1-9], [0-9]}\nq0 = q0\nF = {q1}\nδ = Función de transición (ver tabla)",
        "tabla": {
            "cabeceras": ["Estado (Q)", "Entrada [1-9]", "Entrada [0-9]"],
            "filas": [
                ["-> q0", "q1", "∅"],
                ["*q1", "∅", "q1"]
            ]
        },
        "afnd": "graph LR\n q0((q0))--\"[1-9]\"-->q1((q1))\n q1--\"ε\"-->q2((q2))\n q2--\"[0-9]\"-->q3((q3))\n q3--\"ε\"-->q2\n q1--\"ε\"-->q4(((q4)))\n q3--\"ε\"-->q4(((q4)))",
        "afd": "graph LR\n q0((q0))--\"[1-9]\"-->q1(((q1)))\n q1--\"[0-9]\"-->q1"
    },
    "PRECIO": {
        "quintupla": "Q = {q0, q1, q2, q3}\nΣ = {[0-9], .}\nq0 = q0\nF = {q3}\nδ = Función de transición (ver tabla)",
        "tabla": {
            "cabeceras": ["Estado (Q)", "Entrada [0-9]", "Entrada '.'"],
            "filas": [
                ["-> q0", "q1", "∅"],
                ["q1", "q1", "q2"],   # Ya no es estado de aceptación final
                ["q2", "q3", "∅"],
                ["*q3", "q3", "∅"]    # Solo es válido si pasamos por el punto decimal
            ]
        },
        "afnd": "graph LR\n q0((q0))--\"[0-9]\"-->q1((q1))\n q1--\"[0-9]\"-->q1\n q1--\".\"-->q2((q2))\n q2--\"[0-9]\"-->q3(((q3)))\n q3--\"[0-9]\"-->q3",
        "afd": "graph LR\n q0((q0))--\"[0-9]\"-->q1((q1))\n q1--\"[0-9]\"-->q1\n q1--\".\"-->q2((q2))\n q2--\"[0-9]\"-->q3(((q3)))\n q3--\"[0-9]\"-->q3"
    },
    "FIN_ORDEN": {
        "quintupla": "Q = {q0, q1}\nΣ = {;}\nq0 = q0\nF = {q1}\nδ = Función de transición (ver tabla)",
        "tabla": {
            "cabeceras": ["Estado (Q)", "Entrada ';'"],
            "filas": [
                ["-> q0", "q1"],
                ["*q1", "∅"]
            ]
        },
        "afnd": "graph LR\n q0((q0))--\";\"-->q1(((q1)))",
        "afd": "graph LR\n q0((q0))--\";\"-->q1(((q1)))"
    }
}

ENUNCIADO = {
    "titulo": "Analizador Léxico y Sintáctico: Validación Documental",
    "empresa": "TechLogis - Lima 2026",
    "descripcion": "Análisis determinista basado en AFND/AFD y Gramáticas Libres de Contexto (CFG).",
    "reglas": REGLAS_LENGUAJE,
    "cfg": " | ".join(
        f"Orden -> {' '.join(produccion)}"
        for produccion in GRAMATICA["Orden"]
    )
}

EJEMPLO_CODIGO = "PROD-100 50 12.50;"


def reconocer_gramatica(secuencia, gramatica, simbolo_inicial):
    if simbolo_inicial not in gramatica:
        raise ValueError(f"El símbolo inicial '{simbolo_inicial}' no existe en la gramática.")

    chart = [set() for _ in range(len(secuencia) + 1)]
    for produccion in gramatica[simbolo_inicial]:
        chart[0].add((simbolo_inicial, produccion, 0, 0))

    for posicion in range(len(secuencia) + 1):
        hubo_cambios = True
        while hubo_cambios:
            hubo_cambios = False
            for no_terminal, produccion, punto, origen in tuple(chart[posicion]):
                if punto < len(produccion):
                    siguiente = produccion[punto]
                    if siguiente in gramatica:
                        for regla in gramatica[siguiente]:
                            estado = (siguiente, regla, 0, posicion)
                            if estado not in chart[posicion]:
                                chart[posicion].add(estado)
                                hubo_cambios = True
                    elif posicion < len(secuencia) and secuencia[posicion] == siguiente:
                        chart[posicion + 1].add(
                            (no_terminal, produccion, punto + 1, origen)
                        )
                else:
                    for estado_padre in tuple(chart[origen]):
                        padre, regla_padre, punto_padre, origen_padre = estado_padre
                        if (
                            punto_padre < len(regla_padre)
                            and regla_padre[punto_padre] == no_terminal
                        ):
                            estado = (
                                padre,
                                regla_padre,
                                punto_padre + 1,
                                origen_padre,
                            )
                            if estado not in chart[posicion]:
                                chart[posicion].add(estado)
                                hubo_cambios = True

    return any(
        no_terminal == simbolo_inicial
        and origen == 0
        and punto == len(produccion)
        for no_terminal, produccion, punto, origen in chart[len(secuencia)]
    )


def analizar_lexico(texto):
    tokens = []
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
        
        if not match_encontrado:
            tokens.append({
                'id': idx,
                'lexema': palabra,
                'token': 'ERROR_LEXICO',
                'patron': '∅ (Sin coincidencia)',
                'valido': False,
                'detalle': 'Lexema no pertenece al alfabeto ni reglas del lenguaje'
            })
            
    return tokens

def analizar_sintactico(tokens):
    if not tokens:
        return False, "No se ingresó ninguna cadena para analizar."
    si_tokens_validos = all(t['valido'] for t in tokens)
    if not si_tokens_validos:
        return False, "Error léxico detectado: Existen lexemas no reconocidos."
    
    secuencia_obtenida = [t['token'] for t in tokens]
    
    if reconocer_gramatica(secuencia_obtenida, GRAMATICA, "Orden"):
        return True, "¡Sintaxis Correcta! Orden válida."
    else:
        return False, (
            "Error Sintáctico: la secuencia de tokens "
            f"{secuencia_obtenida} no puede derivarse desde el símbolo inicial "
            "'Orden' de la gramática."
        )

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
        tot_errores=tot_errores,
        teoria=TEORIA_AUTOMATAS
    )

if __name__ == '__main__':
    app.run(debug=True)