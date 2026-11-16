
import sys
from pathlib import Path

import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    avg,
    when,
    coalesce,
    lit
)

from database.db import get_db_connection


def create_spark_session():

    return (
        SparkSession.builder
        .appName("SmartWasteAnalytics")
        .master("local[*]")
        .config("spark.driver.host", "127.0.0.1")
        .getOrCreate()
    )


def load_waste_records(spark):

    connection = get_db_connection()

    try:
        rows = connection.execute("""
            SELECT
                waste_id,
                user_id,
                predicted_label,
                confidence_score,
                review_status,
                created_at
            FROM waste_records
        """).fetchall()

        data = [dict(row) for row in rows]

    finally:
        connection.close()

    columns = [
        "waste_id",
        "user_id",
        "predicted_label",
        "confidence_score",
        "review_status",
        "created_at"
    ]

    if not data:
        return None

    return spark.createDataFrame(data, schema=columns)


def process_waste_data(df):

    df = df.withColumn(
        "waste_group",
        coalesce(col("predicted_label"), lit("Unclassified"))
    )

    group_summary = (
        df.groupBy("waste_group")
        .agg(count("*").alias("total_records"))
    )

    status_summary = (
        df.groupBy("review_status")
        .agg(count("*").alias("total_records"))
    )

    confidence_summary = (
        df.agg(
            avg("confidence_score").alias("average_confidence")
        )
    )

    return group_summary, status_summary, confidence_summary


def main():

    spark = create_spark_session()
    spark.sparkContext.setLogLevel("ERROR")

    try:

        df = load_waste_records(spark)

        if df is None:
            print("No waste records found. Upload images first.")
            return

        print("\nALL WASTE RECORDS")
        df.show(truncate=False)

        groups, statuses, confidence = process_waste_data(df)

        print("\nWASTE CATEGORY ANALYSIS")
        groups.show()

        print("\nREVIEW STATUS ANALYSIS")
        statuses.show()

        print("\nAVERAGE MODEL CONFIDENCE")
        confidence.show()

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
