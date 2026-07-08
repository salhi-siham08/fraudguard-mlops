import dlt
import pandas as pd

CSV_PATH = "data/raw/creditcard.csv"


@dlt.resource(name="transactions", write_disposition="replace")
def transactions_source():
    """Lit le CSV brut et le renvoie ligne par ligne à dlt."""
    df = pd.read_csv(CSV_PATH)
    yield df.to_dict(orient="records")


def run_full_load():
    pipeline = dlt.pipeline(
        pipeline_name="fraud_ingestion",
        destination="duckdb",
        dataset_name="raw",
    )
    load_info = pipeline.run(transactions_source())
    print(load_info)


if __name__ == "__main__":
    run_full_load()