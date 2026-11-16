
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when
from database.db import get_db_connection


def main():

    spark = (
        SparkSession.builder
        .appName("RecyclingPerformanceAnalysis")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("ERROR")

    try:
        connection = get_db_connection()

        rows = connection.execute("""
            SELECT predicted_label, review_status
            FROM waste_records
        """).fetchall()

        connection.close()

        data = [
            {
                "predicted_label": row["predicted_label"] or "Unclassified",
                "review_status": row["review_status"] or "Pending"
            }
            for row in rows
        ]

        if not data:
            print("No waste records available for analysis.")
            return

        df = spark.createDataFrame(data)

        total = df.count()

        print("\nTOTAL WASTE RECORDS:", total)

        print("\nRECYCLING REVIEW STATUS ANALYSIS")

        status_summary = (
            df.groupBy("review_status")
            .agg(count("*").alias("total_records"))
            .orderBy(col("total_records").desc())
        )

        status_summary.show(truncate=False)

        print("\nCLASSIFICATION PERFORMANCE")

        classification_summary = (
            df.groupBy("predicted_label")
            .agg(count("*").alias("total_records"))
            .orderBy(col("total_records").desc())
        )

        classification_summary.show(truncate=False)

        reviewed = df.filter(
            col("review_status") == "Reviewed"
        ).count()

        pending = total - reviewed

        print("\nREVIEW SUMMARY")
        print("Reviewed Records:", reviewed)
        print("Pending Records:", pending)

        review_percentage = (reviewed / total) * 100

        print(
            "Review Completion Percentage:",
            round(review_percentage, 2), "%"
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
