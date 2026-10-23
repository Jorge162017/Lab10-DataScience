import unittest
import pandas as pd
from src.datos import estacionalidad, evolucion_regional, composicion_regional


class AgregacionesExploratorias(unittest.TestCase):
    def setUp(self):
        self.df = pd.DataFrame([
            ('2026-01-01', 'Europa', 'Aérea', 30.),
            ('2026-01-01', 'Europa', 'Terrestre', 10.),
            ('2026-03-01', 'Europa', 'Aérea', 0.),
            ('2026-01-01', 'Asia', 'Aérea', 0.),
        ], columns=['Fecha', 'Región dos', 'Vía', 'Viajero'])
        self.df['Fecha'] = pd.to_datetime(self.df.Fecha)

    def test_mapa_distingue_ceros_y_meses_sin_datos(self):
        matriz = estacionalidad(self.df, '2026-01-01', '2026-06-01')
        self.assertEqual(matriz.loc[2026, 1], 40)
        self.assertTrue(pd.isna(matriz.loc[2026, 2]))
        self.assertEqual(matriz.loc[2026, 3], 0)
        self.assertTrue(pd.isna(matriz.loc[2026, 12]))

    def test_porcentajes_suman_cien_y_excluyen_denominador_cero(self):
        tabla = composicion_regional(self.df)
        europa = tabla.loc[tabla['Región dos'].eq('Europa')]
        self.assertAlmostEqual(europa['Participación'].sum(), 100)
        self.assertEqual(europa.loc[europa.Vía.eq('Aérea'), 'Participación'].iloc[0], 75)
        self.assertTrue(tabla.loc[tabla['Región dos'].eq('Asia'), 'Participación'].isna().all())
        solo_aerea = composicion_regional(self.df.loc[self.df.Vía.eq('Aérea')])
        self.assertEqual(solo_aerea.loc[solo_aerea['Región dos'].eq('Europa'), 'Participación'].iloc[0], 100)

    def test_evolucion_conserva_total_e_identifica_periodo_parcial(self):
        tabla = evolucion_regional(self.df, ['Europa', 'Asia'], 'Y')
        self.assertEqual(tabla.Visitantes.sum(), self.df.Viajero.sum())
        self.assertTrue(tabla.Cobertura.str.startswith('Parcial').all())


if __name__ == '__main__':
    unittest.main()
