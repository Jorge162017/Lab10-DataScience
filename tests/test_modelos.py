import unittest
import numpy as np
import pandas as pd
from src.modelos import cargar_resultados, evaluar


class ResultadosModelos(unittest.TestCase):
    def test_metricas_en_escala_original(self):
        tabla = pd.DataFrame({'Modelo': ['A', 'A'], 'Observado': [10., 20.], 'Predicho': [7., 24.]})
        fila = evaluar(tabla).iloc[0]
        self.assertEqual(fila.MAE, 3.5)
        self.assertAlmostEqual(fila.RMSE, np.sqrt(12.5))

    def test_exportacion_completa_sin_fuga_temporal(self):
        pred, metricas, observados, meta = cargar_resultados()
        self.assertEqual(len(pred), 7 * 3 * 63)
        self.assertEqual(len(metricas), 21)
        self.assertFalse(pred.duplicated(['Serie', 'Modelo', 'Fecha']).any())
        self.assertTrue(np.isfinite(pred[['Observado', 'Predicho']].to_numpy()).all())
        self.assertTrue(pred.Predicho.ge(0).all())
        self.assertEqual(str(pred.Fecha.min().date()), meta['prueba_inicio'])
        self.assertEqual(str(pred.Fecha.max().date()), meta['prueba_fin'])
        self.assertTrue((observados.loc[observados.Conjunto.eq('Entrenamiento'), 'Fecha'] < pred.Fecha.min()).all())
        for serie, tabla in pred.groupby('Serie'):
            self.assertTrue(tabla.groupby('Fecha').Observado.nunique().eq(1).all())
            self.assertTrue(tabla.groupby('Modelo').Fecha.nunique().eq(63).all())
            calculadas = evaluar(tabla).set_index('Modelo')
            guardadas = metricas.loc[metricas.Serie.eq(serie)].set_index('Modelo').loc[calculadas.index]
            np.testing.assert_allclose(calculadas[['MAE', 'RMSE']], guardadas[['MAE', 'RMSE']], rtol=1e-12)

    def test_intervalo_parcial_evalua_solo_meses_seleccionados(self):
        pred, *_ = cargar_resultados()
        tabla = pred.loc[pred.Serie.eq('Total visitantes') & pred.Fecha.between('2026-01-01', '2026-06-01')]
        resultado = evaluar(tabla)
        self.assertEqual(len(resultado), 3)
        self.assertTrue(resultado.Meses.eq(6).all())


if __name__ == '__main__':
    unittest.main()
