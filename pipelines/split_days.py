import pandas as pd
import os

df = pd.read_csv("data/raw/creditcard.csv")

N_DAYS = 10  # on simule 10 journées d'arrivée de données

df = df.sort_values("Time").reset_index(drop=True)
df["transaction_id"] = df.index          # identifiant unique et stable pour chaque ligne
df["day_id"] = pd.qcut(df.index, N_DAYS, labels=False)  # découpe en 10 groupes égaux

os.makedirs("data/incoming", exist_ok=True)

for day in sorted(df["day_id"].unique()):
    day_df = df[df["day_id"] == day].drop(columns=["day_id"])
    file_path = f"data/incoming/day_{day+1:02d}.csv"
    day_df.to_csv(file_path, index=False)
    print(f"{file_path} -> {len(day_df)} lignes")