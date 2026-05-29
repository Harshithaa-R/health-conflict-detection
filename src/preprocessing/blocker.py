import pandas as pd
import os


def create_blocks():

    print("Loading standardized records...")

    df = pd.read_csv(
        "data/processed/standardized_records.csv"
    )

    df["name_prefix"] = (
        df["name"]
        .astype(str)
        .str.upper()
        .str[:2]
    )

    df["dob"] = df["dob"].astype(str)

    blocks = []

    grouped = df.groupby(
        ["district", "name_prefix"]
    )

    for block_id, (_, group) in enumerate(grouped):

        temp = group.copy()

        temp["block_id"] = block_id

        blocks.append(temp)

    blocked_df = pd.concat(
        blocks,
        ignore_index=True
    )

    os.makedirs(
        "data/processed",
        exist_ok=True
    )

    blocked_df.to_csv(
        "data/processed/blocked_records.csv",
        index=False
    )

    print("\nBlocking Complete")
    print("=" * 50)

    print(
        f"Total Records : {len(blocked_df):,}"
    )

    print(
        f"Unique Blocks : "
        f"{blocked_df['block_id'].nunique():,}"
    )

    print(
        "\nAverage Records Per Block : "
        f"{round(blocked_df.groupby('block_id').size().mean(), 2)}"
    )

    print(
        "\nSaved: "
        "data/processed/blocked_records.csv"
    )

    return blocked_df


if __name__ == "__main__":

    create_blocks()