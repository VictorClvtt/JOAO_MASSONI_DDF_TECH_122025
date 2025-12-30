import warnings
import pandas as pd
import great_expectations as ge

warnings.filterwarnings("ignore", category=UserWarning)

df = pd.read_csv(
    "data/raw/synthetic_data_full.csv",
    parse_dates=["order_date", "shipping_date"]
)

df["_shipping_after_order"] = (
    df["shipping_date"].notna() &
    (df["shipping_date"] > df["order_date"])
)

ge_df = ge.from_pandas(df)

VALID_STATUS = ["Entregue", "Em trânsito", "Cancelado"]
VALID_PAYMENT = ["Cartão de crédito", "Boleto", "Pix"]
VALID_STATES = ["SP", "RJ", "MG", "PR", "RS", "SC", "BA", "PE", "CE", "GO", "DF"]

CANCELLED_CONDITION = 'status == "Cancelado"'

# ------------------------------------------------------------------
# CUSTOMER
# ------------------------------------------------------------------

# Null checks
ge_df.expect_column_values_to_not_be_null("customer_id")
ge_df.expect_column_values_to_not_be_null("customer_name")
ge_df.expect_column_values_to_not_be_null("customer_email")

# String hygiene
ge_df.expect_column_values_to_not_match_regex(
    "customer_name",
    r"^\s|\s$"
)

# Email format
ge_df.expect_column_values_to_match_regex(
    "customer_email",
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    mostly=0.99
)

# Domain
ge_df.expect_column_values_to_be_in_set(
    "customer_state",
    VALID_STATES
)

# ------------------------------------------------------------------
# ORDER
# ------------------------------------------------------------------

# Duplicates and nulls
ge_df.expect_column_values_to_be_unique("order_id")
ge_df.expect_column_values_to_not_be_null("order_id")
ge_df.expect_column_values_to_not_be_null("order_date")

# Domain
ge_df.expect_column_values_to_be_in_set("status", VALID_STATUS)

# Relationship
ge_df.expect_column_values_to_not_be_null("customer_id")

# ------------------------------------------------------------------
# ORDER_ITEM
# ------------------------------------------------------------------

# Null checks
ge_df.expect_column_values_to_not_be_null("product_id")
ge_df.expect_column_values_to_not_be_null("order_id")
ge_df.expect_column_values_to_not_be_null("quantity")
ge_df.expect_column_values_to_not_be_null("unit_price")

# Logical ranges
ge_df.expect_column_values_to_be_between(
    "quantity",
    min_value=1
)

ge_df.expect_column_values_to_be_between(
    "unit_price",
    min_value=0.01,
    mostly=0.95
)

# ------------------------------------------------------------------
# PAYMENT
# ------------------------------------------------------------------

ge_df.expect_column_values_to_be_in_set(
    "payment_method",
    VALID_PAYMENT
)

ge_df.expect_column_values_to_not_be_null("order_id")

# ------------------------------------------------------------------
# SHIPPING
# ------------------------------------------------------------------

# Business rule
ge_df.expect_column_values_to_be_null(
    "shipping_date",
    row_condition=CANCELLED_CONDITION,
    condition_parser="pandas"
)

# Temporal consistency
ge_df.expect_column_values_to_be_in_set(
    "_shipping_after_order",
    [True],
    mostly=0.98
)

# ------------------------------------------------------------------
# REVIEW
# ------------------------------------------------------------------

ge_df.expect_column_values_to_be_null(
    "review",
    row_condition=CANCELLED_CONDITION,
    condition_parser="pandas"
)

# ------------------------------------------------------------------
# Validação
# ------------------------------------------------------------------
results = ge_df.validate()

# ------------------------------------------------------------------
# Relatório
# ------------------------------------------------------------------
print("Success:", results["success"])
print("Total expectations:", len(results["results"]))

failed = [r for r in results["results"] if not r["success"]]
print("Failed expectations:", len(failed))

for r in failed:
    exp_type = r["expectation_config"]["expectation_type"]
    kwargs = r["expectation_config"]["kwargs"]
    column = kwargs.get("column", kwargs.get("column_A", "N/A"))
    print(f"[FAIL] {exp_type} | column: {column}")

print("[INFO] Data Quality report generated successfully.")
