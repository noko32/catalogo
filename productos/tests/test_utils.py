import unittest
from decimal import Decimal

from productos.utils import filtrar_y_ordenar_productos


class FiltrarYOrdenarProductosTests(unittest.TestCase):
    def test_filtro_y_ordenamiento_caso_ejemplo(self):
        entrada = [
            {"nombre": "A", "precio": 100, "stock": 0},
            {"nombre": "B", "precio": 50, "stock": 4},
            {"nombre": "C", "precio": 80, "stock": 2},
        ]
        resultado = filtrar_y_ordenar_productos(entrada)
        esperado = [
            {"nombre": "B", "precio": 50, "stock": 4},
            {"nombre": "C", "precio": 80, "stock": 2},
        ]
        self.assertEqual(resultado, esperado)

    def test_todos_con_stock_cero(self):
        entrada = [
            {"nombre": "X", "precio": 10, "stock": 0},
            {"nombre": "Y", "precio": 20, "stock": 0},
        ]
        self.assertEqual(filtrar_y_ordenar_productos(entrada), [])

    def test_lista_vacia(self):
        self.assertEqual(filtrar_y_ordenar_productos([]), [])

    def test_inmutabilidad_de_lista_original(self):
        original = [
            {"nombre": "B", "precio": 50, "stock": 4},
            {"nombre": "C", "precio": 80, "stock": 2},
        ]
        copia_referencia = list(original)
        _ = filtrar_y_ordenar_productos(original)
        self.assertEqual(original, copia_referencia)

    def test_argumento_invalido_lanza_type_error(self):
        with self.assertRaises(TypeError):
            filtrar_y_ordenar_productos("no es una lista")

    def test_precios_con_tipos_mixtos_ordenan_correctamente(self):
        entrada = [
            {"nombre": "A", "precio": "120.50", "stock": 2},
            {"nombre": "B", "precio": 45, "stock": 1},
            {"nombre": "C", "precio": Decimal("15.99"), "stock": 5},
            {"nombre": "D", "precio": 99.99, "stock": 3},
        ]
        resultado = filtrar_y_ordenar_productos(entrada)
        nombres_ordenados = [item["nombre"] for item in resultado]
        self.assertEqual(nombres_ordenados, ["C", "B", "D", "A"])

    def test_stock_nulo_o_invalido_se_descarta_sin_error(self):
        entrada = [
            {"nombre": "Valido", "precio": 50, "stock": 3},
            {"nombre": "Stock None", "precio": 20, "stock": None},
            {"nombre": "Stock String Invalido", "precio": 30, "stock": "no_aplica"},
        ]
        resultado = filtrar_y_ordenar_productos(entrada)
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["nombre"], "Valido")
