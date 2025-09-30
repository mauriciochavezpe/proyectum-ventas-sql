# test_ventas_utils.py
import pytest
from ventas_totales import calcular_total

def test_calcular_total_correcto():
    assert calcular_total(2, 5) == 10.0
    assert calcular_total("3", "4.5") == 13.5  # acepta strings numéricos

def test_calcular_total_valores_invalidos():
    with pytest.raises(ValueError):
        calcular_total(0, 10)
    with pytest.raises(ValueError):
        calcular_total(5, -2)

def test_calcular_total_tipo_invalido():
    with pytest.raises(TypeError):
        calcular_total("dos", 5)
