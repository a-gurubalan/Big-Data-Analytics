
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, date_format, to_timestamp
)
from database.db import get_db_connection


def main():

    spark = (
        SparkSession.builder
        .appName("MonthlyWasteAnalysis")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    try:
        connection = get_db_connection()

        rows = connection.execute("""
            SELECT created_at, predicted_label
            FROM waste_records
            WHERE created_at IS NOT NULL
        """).fetchall()

        connection.close()

        data = [
            {
                "created_at": row["created_at"],
                "predicted_label": row["predicted_label"] or "Unclassified"
            }
            for row in rows
        ]

        if not data:
            print("No waste records available for monthly analysis.")
            return

        df = spark.createDataFrame(data)

        df = df.withColumn(
            "record_date",
            to_timestamp(col("created_at"))
        )

        monthly_summary = (
            df.filter(col("record_date").isNotNull())
            .withColumn(
                "month",
                date_format(col("record_date"), "yyyy-MM")
            )
            .groupBy("month")
            .agg(count("*").alias("total_uploads"))
            .orderBy("month")
        )

        print("\nMONTHLY WASTE GENERATION ANALYSIS")
        monthly_summary.show(truncate=False)

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
