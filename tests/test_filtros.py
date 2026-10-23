"""Regresión del botón de restablecimiento con datos pequeños, sin leer Excel."""
import unittest
from pathlib import Path
from unittest.mock import patch
import pandas as pd
from streamlit.testing.v1 import AppTest


class Restablecimiento(unittest.TestCase):
    def test_recupera_filtros_despues_de_cambios_y_seleccion_vacia(self):
        filas = [(fecha, region, via, 10.)
                 for fecha in pd.date_range('2026-01-01', periods=3, freq='MS')
                 for region in ['Europa', 'Asia'] for via in ['Aérea', 'Terrestre']]
        df = pd.DataFrame(filas, columns=['Fecha', 'Región dos', 'Vía', 'Viajero'])
        with patch('src.datos.cargar_visitantes', return_value=df):
            at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=30).run()
            self.assertFalse(at.exception)
            periodo = at.select_slider[0].value
            at.multiselect(key='regiones').set_value(['Europa']).run()
            at.multiselect(key='vias').set_value(['Aérea']).run()
            at.radio(key='detalle').set_value('Año').run()
            at.select_slider[0].set_value((periodo[1], periodo[1])).run()
            at.button(key='restablecer_filtros').click().run()
            self.assertFalse(at.exception)
            self.assertEqual(at.multiselect(key='regiones').value, ['Asia', 'Europa'])
            self.assertEqual(at.multiselect(key='vias').value, ['Aérea', 'Terrestre'])
            self.assertEqual(at.select_slider[0].value, periodo)
            self.assertEqual(at.radio(key='detalle').value, 'Mes')
            at.multiselect(key='regiones').set_value([]).run()
            self.assertTrue(at.warning)
            at.button(key='restablecer_filtros').click().run()
            self.assertFalse(at.exception)
            self.assertEqual(len(at.get('plotly_chart')), 3)
            at.radio(key='seccion').set_value('Mercados y vías').run()
            at.radio(key='modo_composicion').set_value('Cantidad de visitantes').run()
            at.button(key='restablecer_filtros').click().run()
            self.assertFalse(at.exception)
            self.assertEqual(at.radio(key='modo_composicion').value, 'Porcentaje')
            self.assertEqual(len(at.get('plotly_chart')), 3)


if __name__ == '__main__':
    unittest.main()
