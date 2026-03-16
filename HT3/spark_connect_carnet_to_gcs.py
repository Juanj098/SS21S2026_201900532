import os
from datetime import datetime, timezone

from pyspark.sql import SparkSession

# =========================
# CONFIGURACION (editar)
# =========================
CARNET = "201900532"  # Reemplazar con el carnet real
BUCKET_NAME = "ht3-carnet-40094c05"
SPARK_CONNECT_URL = "sc://136.114.236.151:15002"
GCS_PREFIX = "carnets"


def main() -> None:
    carnet_value = os.getenv("HT3_201900532", CARNET)

    spark = (
        SparkSession.builder.remote(SPARK_CONNECT_URL)
        .appName("HT3-201900532-Parquet-GCS")
        .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
        .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS")
        .getOrCreate()
    )

    # 1) Crear DataFrame con el carnet
    created_at_utc = datetime.now(timezone.utc).isoformat()
    df = spark.createDataFrame([(carnet_value, created_at_utc)], ["carnet", "created_at_utc"])

    # 2) Guardar Parquet directo en GCS desde el servidor Spark
    timestamp_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    gcs_output_path = (
        f"gs://{BUCKET_NAME}/{GCS_PREFIX}/carnet={carnet_value}/run={timestamp_id}"
    )
    df.coalesce(1).write.mode("overwrite").parquet(gcs_output_path)

    print(f"Parquet escrito en: {gcs_output_path}")

    spark.stop()


if __name__ == "__main__":
    main()
