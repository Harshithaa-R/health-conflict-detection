import pandas as pd
import os


def create_blocks():

    print("Loading standardized records...")

    df = pd.read_csv(
        "data/processed/standardized_records.csv",
        low_memory=False
    )

    # Ensure domain column exists
    if "domain" not in df.columns:
        df["domain"] = "maternal"

    df["name_prefix"] = (
        df["name"]
        .astype(str)
        .str.upper()
        .str[:2]
    )

    df["dob"] = df["dob"].astype(str)

    blocks = []

    # ---------------------------------------------------
    # GROUP BY domain + district + name_prefix
    # Domain ensures children are never blocked
    # with maternal or chronic patients
    # ---------------------------------------------------

    grouped = df.groupby(
        ["domain", "district", "name_prefix"]
    )

    for block_id, (_, group) in enumerate(grouped):

        temp = group.copy()
        temp["block_id"] = block_id
        blocks.append(temp)

    blocked_df = pd.concat(
        blocks,
        ignore_index=True
    )

    os.makedirs("data/processed", exist_ok=True)

    blocked_df.to_csv(
        "data/processed/blocked_records.csv",
        index=False
    )

    print("\nBlocking Complete")
    print("=" * 50)
    print(f"Total Records  : {len(blocked_df):,}")
    print(f"Unique Blocks  : {blocked_df['block_id'].nunique():,}")
    print(
        f"Avg Records/Block : "
        f"{round(blocked_df.groupby('block_id').size().mean(), 2)}"
    )

    if "domain" in blocked_df.columns:
        print("\nBlocks by Domain:")
        domain_blocks = blocked_df.groupby("domain")["block_id"].nunique()
        print(domain_blocks.to_string())

    print("\nSaved: data/processed/blocked_records.csv")

    return blocked_df


if __name__ == "__main__":

    create_blocks()