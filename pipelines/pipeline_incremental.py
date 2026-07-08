import dlt
import pandas as pd
import glob
import os
import time

@dlt.resource(
    name="transactions",
    write_disposition="append",
    primary_key="transaction_id"
)
def load_day(file_path):
    df = pd.read_csv(file_path)
    yield df.to_dict(orient="records")

def run_incremental_load():
    pipeline = dlt.pipeline(
        pipeline_name="fraud_ingestion",
        destination="duckdb",
        dataset_name="raw"
    )

    files = sorted(glob.glob("data/incoming/day_*.csv"))

    for file_path in files:
        print(f"Chargement de {file_path} ...")
        info = pipeline.run(load_day(file_path))
        print(info)
        time.sleep(0.5)  # petite pause pour simuler l'arrivée progressive

if __name__ == "__main__":
    run_incremental_load()