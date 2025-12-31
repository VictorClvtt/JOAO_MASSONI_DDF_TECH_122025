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
logger.info("fact_order schema:")
fact_order = df.select(
        "order_id",
        "quantity",
        "unit_price"
    ).withColumn(
        "total_amount",
        F.col("quantity") * F.col("unit_price")
    )
fact_order.printSchema()

logger.info("dim_date schema:")
dim_date = df.
# %%
