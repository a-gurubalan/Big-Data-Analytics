
import json
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, lower, when

from database.db import get_db_connection


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_FILE = BASE_DIR / "analytics" / "dashboard_data.json"


def main():
    spark = (
        SparkSession.builder
        .appName("WasteDashboardExport")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    try:
        connection = get_db_connection()

        rows = connection.execute("""
            SELECT predicted_label, review_status, created_at
            FROM waste_records
        """).fetchall()

        connection.close()

        data = [dict(row) for row in rows]

        if not data:
            print("No waste records available.")
            return

        df = spark.createDataFrame(data)

        category_df = (
            df.withColumn(
                "category",
                when(lower(col("predicted_label")) == "e_waste", "E-Waste")
                .when(lower(col("predicted_label")) == "natural_waste", "Natural Waste")
                .otherwise("Other")
            )
            .groupBy("category")
            .agg(count("*").alias("total"))
        )

        status_df = (
            df.withColumn(
                "status",
                when(col("review_status").isNull(), "Pending")
                .otherwise(col("review_status"))
            )
            .groupBy("status")
            .agg(count("*").alias("total"))
        )

        category_data = [
            {"label": row["category"], "value": row["total"]}
            for row in category_df.collect()
        ]

        status_data = [
            {"label": row["status"], "value": row["total"]}
            for row in status_df.collect()
        ]

        result = {
            "total_records": df.count(),
            "categories": category_data,
            "statuses": status_data
        }

        OUTPUT_FILE.write_text(
            json.dumps(result, indent=4),
            encoding="utf-8"
        )

        print("Dashboard data exported successfully!")
        print("Output:", OUTPUT_FILE)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
