# %%
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import logging

# Logger configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M"
)

logger = logging.getLogger(__name__)

INPUT_PATH = "../../data/clean/clean_orders/"
OUTPUT_PATH = "../../data/analytics"

spark = SparkSession.builder.appName("Data Modeling").getOrCreate()

df = spark.read.csv(INPUT_PATH, header=True, inferSchema=True)

df.printSchema()
# %%
logger.info("Starting gold layer data modeling for analytics\n")
print("fact_order schema:")
fact_order = (
    df.select(
        "order_id",
        "order_date",
        "shipping_date",
        "customer_id",
        "product_id",
        "payment_method",
        "status",
        "quantity",
        "unit_price"
    )
    .withColumn(
        "order_date_sk",
        F.sha2(F.col("order_date").cast("date").cast("string"), 256)
    )
    .withColumn(
        "shipping_date_sk",
        F.sha2(F.col("shipping_date").cast("date").cast("string"), 256)
    )
    .withColumn(
        "customer_sk",
        F.sha2(F.col("customer_id").cast("string"), 256)
    )
    .withColumn(
        "product_sk",
        F.sha2(F.col("product_id").cast("string"), 256)
    )
    .withColumn(
        "payment_method_sk",
        F.sha2(F.col("payment_method").cast("string"), 256)
    )
    .withColumn(
        "order_status_sk",
        F.sha2(F.col("status").cast("string"), 256)
    )
    .withColumn(
        "total_amount",
        F.col("quantity") * F.col("unit_price")
    )
    .select(
        "order_id",                # degenerate dimension
        "order_date_sk",
        "shipping_date_sk",
        "customer_sk",
        "product_sk",
        "payment_method_sk",
        "order_status_sk",
        "quantity",
        "unit_price",
        "total_amount"
    )
)
fact_order.printSchema()

print("dim_date schema:")
dim_date = (
    df.select(F.col("order_date").cast("date").alias("full_date"))
    .union(
        df.select(F.col("shipping_date").cast("date").alias("full_date"))
    )
    .filter(F.col("full_date").isNotNull())
    .distinct()
    .withColumn("day", F.dayofmonth(F.col("full_date")))
    .withColumn("month", F.month(F.col("full_date")))
    .withColumn("month_name", F.date_format(F.col("full_date"), "MMMM"))
    .withColumn("quarter", F.quarter(F.col("full_date")))
    .withColumn("year", F.year(F.col("full_date")))
    .withColumn("day_of_week", F.date_format(F.col("full_date"), "EEEE"))
    .withColumn(
        "is_weekend",
        F.when(F.dayofweek(F.col("full_date")).isin(1, 7), F.lit(True))
        .otherwise(F.lit(False))
    )
    .withColumn(
        "date_sk",
        F.sha2(F.col("full_date").cast("string"), 256)
    )
)
dim_date.printSchema()

print("dim_order_status schema:")
dim_order_status = (
    df.select("status")
    .filter(F.col("status").isNotNull())
    .distinct()
    .withColumn(
        "order_status_sk",
        F.sha2(F.col("status").cast("string"), 256)
    )
)
dim_order_status.printSchema()

print("dim_payment_method schema:")
dim_payment_method = (
    df.select("payment_method")
    .filter(F.col("payment_method").isNotNull())
    .distinct()
    .withColumn(
        "payment_method_sk",
        F.sha2(F.col("payment_method").cast("string"), 256)
    )
)
dim_payment_method.printSchema()

print("dim_product schema:")
dim_product = (
    df.select("product_id", "product_name", "category", "supplier")
    .filter(F.col("product_id").isNotNull())
    .distinct()
    .withColumn(
        "product_sk",
        F.sha2(F.col("product_id").cast("string"), 256) # sk derivada do id original (Kimball)
    )
)
dim_product.printSchema()

print("dim_customer schema:")
dim_customer = (
    df.select(
        "customer_id",
        "customer_name",
        "customer_email",
        "customer_city",
        "customer_state"
    )
    .filter(F.col("customer_id").isNotNull())
    .distinct()
    .withColumn(
        "customer_sk",
        F.sha2(F.col("customer_id").cast("string"), 256)
    )
    .withColumn(
        "location_sk",
        F.sha2(
            F.concat_ws(
                "|",
                F.col("customer_city"),
                F.col("customer_state")
            ),
            256
        )
    )
    .drop("customer_city", "customer_state")
)
dim_customer.printSchema()

print("dim_location schema:")
dim_location = (
    df.select("customer_city", "customer_state")
    .filter(
        F.col("customer_city").isNotNull() &
        F.col("customer_state").isNotNull()
    )
    .distinct()
    .withColumn(
        "location_sk",
        F.sha2(
            F.concat_ws(
                "|",
                F.col("customer_city"),
                F.col("customer_state")
            ),
            256
        )
    )
    .withColumnRenamed("customer_city", "city")
    .withColumnRenamed("customer_state", "state")
)
dim_location.printSchema()

# %%
logger.info(f"Recording gold schema tables to {OUTPUT_PATH}\n")

fact_order.write.parquet(f"{OUTPUT_PATH}/fact_order", mode="overwrite")
dim_date.write.parquet(f"{OUTPUT_PATH}/dim_date", mode="overwrite")
dim_order_status.write.parquet(f"{OUTPUT_PATH}/dim_order_status", mode="overwrite")
dim_payment_method.write.parquet(f"{OUTPUT_PATH}/dim_payment_method", mode="overwrite")
dim_product.write.parquet(f"{OUTPUT_PATH}/dim_product", mode="overwrite")
dim_customer.write.parquet(f"{OUTPUT_PATH}/dim_customer", mode="overwrite")
dim_location.write.parquet(f"{OUTPUT_PATH}/dim_location", mode="overwrite")

logger.info("Gold layer data modeling finished successfully")