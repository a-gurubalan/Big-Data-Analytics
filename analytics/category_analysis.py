
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, lower, when

from database.db import get_db_connection


def main():
    spark = (
        SparkSession.builder
        .appName("WasteCategoryAnalysis")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    try:
        connection = get_db_connection()

        rows = connection.execute("""
            SELECT predicted_label
            FROM waste_records
            WHERE predicted_label IS NOT NULL
        """).fetchall()

        connection.close()

        data = [
            {"predicted_label": row["predicted_label"]}
            for row in rows
        ]

        if not data:
            print("No classified waste records available.")
            return

        df = spark.createDataFrame(data)

        df = df.withColumn(
            "waste_category",
            when(lower(col("predicted_label")) == "e_waste",
                 "E-Waste")
            .when(lower(col("predicted_label")) == "natural_waste",
                  "Natural Waste")
            .otherwise("Other")
        )

        summary = df.groupBy("waste_category").agg(
            count("*").alias("total_records")
        )

        print("\nWASTE CATEGORY ANALYSIS")
        summary.orderBy(col("total_records").desc()).show()

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
