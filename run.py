# analisis_ventas.py
import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = Path("analytics.db")
DATA_VENTAS = Path("data/ventas.csv")

def cargar_y_limpiar(csv_path: Path) -> pd.DataFrame:
    """Carga y limpia el archivo CSV de ventas."""
    df = pd.read_csv(csv_path)

    # Normalizar tipos
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", dayfirst=True)
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
    df["precio_unitario"] = pd.to_numeric(df["precio_unitario"], errors="coerce")

    # Limpiar nulos y valores inconsistentes
    df = df.dropna(subset=["fecha", "producto", "cantidad", "precio_unitario"])
    df = df[(df["cantidad"] > 0) & (df["precio_unitario"] > 0)]

    # Calcular columna total
    df["total"] = df["cantidad"] * df["precio_unitario"]
    return df

def calcular_agregados(df: pd.DataFrame):
    """Genera tablas resumen por producto y por mes."""
    # Resumen por producto
    resumen_producto = (
        df.groupby("producto", as_index=False)
          .agg(cantidad_total=("cantidad", "sum"),
               facturacion_total=("total", "sum"))
    )

    # Facturación mensual
    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    facturacion_mensual = (
        df.groupby("mes", as_index=False)
          .agg(facturacion_total=("total", "sum"))
          .sort_values("mes")
    )
    return resumen_producto, facturacion_mensual

def persistir_en_sqlite(df: pd.DataFrame,
                        resumen_producto: pd.DataFrame,
                        facturacion_mensual: pd.DataFrame,
                        db_path: Path):
    """Guarda los datos y agregados en SQLite y crea vistas útiles."""
    con = sqlite3.connect(db_path)
    try:
        # Tablas principales
        df.to_sql("ventas", con, if_exists="replace", index=False)
        resumen_producto.to_sql("resumen_producto", con, if_exists="replace", index=False)
        facturacion_mensual.to_sql("facturacion_mensual", con, if_exists="replace", index=False)

        # Índices
        cur = con.cursor()
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ventas_producto ON ventas(producto);")

        # Vistas
        cur.execute("""
            CREATE VIEW IF NOT EXISTS v_top3_productos_mas_vendidos AS
            SELECT producto, SUM(cantidad) AS cantidad_total
            FROM ventas
            GROUP BY producto
            ORDER BY cantidad_total DESC
            LIMIT 3;
        """)
        cur.execute("""
            CREATE VIEW IF NOT EXISTS v_producto_mayor_facturacion AS
            SELECT producto, SUM(total) AS facturacion_total
            FROM ventas
            GROUP BY producto
            ORDER BY facturacion_total DESC
            LIMIT 1;
        """)
        con.commit()
    finally:
        con.close()

def main():
    if not DATA_VENTAS.exists():
        raise FileNotFoundError(f"No se encontró {DATA_VENTAS.resolve()}")

    # 1. Cargar y limpiar
    df = cargar_y_limpiar(DATA_VENTAS)

    df.to_csv("data/ventas_limpias.csv")
    
    # 2. Calcular agregados
    resumen_producto, facturacion_mensual = calcular_agregados(df)

    # 3. Persistir en base de datos
    persistir_en_sqlite(df, resumen_producto, facturacion_mensual, DB_PATH)

    # 4. Mostrar resultados principales en consola
    prod_top = resumen_producto.sort_values("cantidad_total", ascending=False).head(1)
    fact_top = resumen_producto.sort_values("facturacion_total", ascending=False).head(1)

    print("✅ Persistencia completada en analytics.db")

    print("\n(a) Producto más vendido por cantidad:")
    print(prod_top.to_string(index=False))

    # print("\n(b) Producto con mayor facturación total:")
    # print(fact_top.to_string(index=False))

    # print("\n(c) Facturación total por mes:")
    # print(facturacion_mensual.to_string(index=False))

if __name__ == "__main__":
    main()
