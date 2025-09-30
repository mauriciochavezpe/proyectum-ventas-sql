# ventas_utils.py

def calcular_total(cantidad, precio_unitario):
    """
    Calcula el total = cantidad * precio_unitario.
    Lanza ValueError si alguno es <= 0.
    """
    try:
        c = float(cantidad)
        p = float(precio_unitario)
    except Exception as e:
        raise TypeError("Los valores deben ser numéricos") from e

    if c <= 0 or p <= 0:
        raise ValueError("Cantidad y precio_unitario deben ser mayores a 0")

    return c * p
