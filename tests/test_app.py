import unittest

from app import GRAMATICA, analizar_lexico, analizar_sintactico, app, reconocer_gramatica


class GramaticaEarleyTests(unittest.TestCase):
    def test_reconoce_la_gramatica_de_orden(self):
        tokens = ["ID_PRODUCTO", "CANTIDAD", "PRECIO", "FIN_ORDEN"]

        self.assertTrue(reconocer_gramatica(tokens, GRAMATICA, "Orden"))

    def test_rechaza_orden_incorrecto_y_tokens_adicionales(self):
        self.assertFalse(
            reconocer_gramatica(
                ["CANTIDAD", "ID_PRODUCTO", "PRECIO", "FIN_ORDEN"],
                GRAMATICA,
                "Orden",
            )
        )
        self.assertFalse(
            reconocer_gramatica(
                ["ID_PRODUCTO", "CANTIDAD", "PRECIO", "FIN_ORDEN", "CANTIDAD"],
                GRAMATICA,
                "Orden",
            )
        )

    def test_soporta_recursion_por_la_izquierda(self):
        gramatica = {
            "Expresion": [("Expresion", "+", "Numero"), ("Numero",)],
            "Numero": [("n",)],
        }

        self.assertTrue(
            reconocer_gramatica(["n", "+", "n", "+", "n"], gramatica, "Expresion")
        )
        self.assertFalse(
            reconocer_gramatica(["n", "+", "+", "n"], gramatica, "Expresion")
        )

    def test_soporta_producciones_vacias(self):
        gramatica = {"Opcional": [(), ("x",)]}

        self.assertTrue(reconocer_gramatica([], gramatica, "Opcional"))
        self.assertTrue(reconocer_gramatica(["x"], gramatica, "Opcional"))
        self.assertFalse(reconocer_gramatica(["x", "x"], gramatica, "Opcional"))

    def test_el_analizador_sintactico_usa_la_gramatica(self):
        tokens_validos = analizar_lexico("PROD-100 50 12.50;")
        tokens_reordenados = analizar_lexico("50 PROD-100 12.50;")

        self.assertTrue(analizar_sintactico(tokens_validos)[0])
        self.assertFalse(analizar_sintactico(tokens_reordenados)[0])

    def test_endpoint_web_muestra_el_resultado_del_parseo(self):
        cliente = app.test_client()
        respuesta = cliente.post("/", data={"codigo": "PROD-100 50 12.50;"})

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn(b"SINTAXIS EXITOSA", respuesta.data)


if __name__ == "__main__":
    unittest.main()
