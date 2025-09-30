# plot_facturacion.py
import sqlite3
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = Path("analytics.db")
CSV_PATH = Path("ventas.csv")
OUTPUT_IMG = "grafico.png"

def cargar_facturacion_mensual() -> pd.DataFrame:
    if DB_PATH.exists():
        con = sqlite3.connect(DB_PATH)
        try:
            # Usamos la tabla creada por analisis_ventas.py
            df = pd.read_sql_query("SELECT mes, facturacion_total FROM facturacion_mensual", con)
            # Asegurar orden por mes
            df["mes"] = pd.PeriodIndex(df["mes"], freq="M").astype(str)
            return df.sort_values("mes")
        finally:
            con.close()

    if not CSV_PATH.exists():
        raise FileNotFoundError("No se encontró analytics.db ni ventas.csv")

    # Como contingencia cargamos CSV
    df = pd.read_csv(CSV_PATH)
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce", dayfirst=True)
    df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
    df["precio_unitario"] = pd.to_numeric(df["precio_unitario"], errors="coerce")
    df = df.dropna(subset=["fecha", "producto", "cantidad", "precio_unitario"])
    df = df[(df["cantidad"] > 0) & (df["precio_unitario"] > 0)]
    df["total"] = df["cantidad"] * df["precio_unitario"]
    df["mes"] = df["fecha"].dt.to_period("M").astype(str)
    facturacion_mensual = (
        df.groupby("mes", as_index=False)["total"].sum()
          .rename(columns={"total": "facturacion_total"})
          .sort_values("mes")
    )
    return facturacion_mensual

def main():
    facturacion_mensual = cargar_facturacion_mensual()

    # --- Gráfico: Facturación total por mes ---
    plt.figure()
    plt.bar(facturacion_mensual["mes"], facturacion_mensual["facturacion_total"])
    plt.title("Facturación total por mes")
    plt.xlabel("Mes (YYYY-MM)")
    plt.ylabel("Facturación")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(OUTPUT_IMG, dpi=120)
    print(f"✅ Gráfico guardado en {OUTPUT_IMG}")

if __name__ == "__main__":
    main()
