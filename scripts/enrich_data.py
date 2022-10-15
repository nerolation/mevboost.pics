import time
import pandas as pd
from web3 import Web3
import os
from web3.exceptions import BlockNotFound
from logger import log 

with open("./key/infura.txt", "r") as f:
    RPC_ENDPOINT = f.read().strip()
    
FOLDER = "./enriched_data/"
DATASET = "./data/"

# Open mevboost_*.csv files and concat
def open_file(FOLDER):
    df = pd.DataFrame()
    for file in os.listdir(FOLDER):
        if not (file.startswith("mevboost_") and file.endswith(".csv")):
            continue
        _df = pd.read_csv(FOLDER + file)
        df = pd.concat([df, _df])
    df["value"] = df["value"].apply(lambda x: int(x))
    df["slot"] = df["slot"].apply(lambda x: int(x))
    return df

# Open mevboost_e*.csv files and concat
def open_enriched_file(FOLDER):
    FILENR = 0
    df = pd.DataFrame()
    for file in os.listdir(FOLDER):
        if not (file.startswith("mevboost_e") and file.endswith(".csv")):
            continue
        if "txs" om file:
            continue
        FILENR = max([FILENR, int(re.findall("[0-9]+", file)[0])])
        _df = pd.read_csv(FOLDER + file, dtype={"miner":str, "value":float})
        df = pd.concat([df, _df])
    df["value"] = df["value"].apply(lambda x: int(x))
    df["slot"] = df["slot"].apply(lambda x: int(x))
    return df, FILENR + 1

NEW_DF = open_file(DATASET)

if not os.path.isdir(FOLDER):
    os.makedirs(FOLDER)

counter_txs = 1
for i in os.listdir(FOLDER):
    if "mevboost_e_txs" in i:
        counter_txs += 1


def enrich_data(w3, df, df_txs, counter_txs):
    #
    # Adds block hashes, miner address info about
    # transactions to new file named mevboost_e.csv
    #
    try:
        c = df.keys()
        # create columns if not exist
        if "miner" not in c:
            df["miner"] = None
            df["block_number"] = None
            df["tx_count"] = None
            
        # Loop over all rows
        for ix, row in df.iterrows():
            print(f"           {ix}/{len(df)}", end="\r")
            # If miner is not NaN, then skip, NaN == float
            while len(df) > 10000:
                _df = df.iloc[0:10000]
                df = df[~df["slot"].isin(_df["slot"])]
                _df.to_csv(FOLDER + "mevboost_e_{}.csv".format(FILENR), index=None)
                FILENR += 1
            
            if not df.loc[ix, "miner"] == "none":
                print(f"skipped", end="\r")
                continue
            try:
                block = w3.eth.get_block(row["block_hash"])
            except BlockNotFound:
                #print(f"\nBlock not found: {row['block_hash']}")
                #print(str(row["slot"]))
                continue
            print(f"parsing", end="\r")
            builder, block_number = block["miner"], block["number"]
            txs = [tx.hex() for tx in block.transactions]
            df.loc[ix,("miner", "block_number", "tx_count")] = builder, block_number, len(txs)
            l = len(df_txs)
            for ixx, tx in enumerate(txs):
                df_txs.loc[l+ixx, ("miner", "block_number","txhash")] = builder, block_number, tx
            if str(df.loc[ix, "gas_used"]) == "NaN" or df.loc[ix, "gas_used"] != df.loc[ix, "gas_used"]:
                df.loc[ix, ("gas_used", "gas_limit")] =  block["gasUsed"], block["gasLimit"]
            
            # Store file with transations in chunks
            if len(df_txs) >= 10000:
                df_txs.to_csv(FOLDER + f"mevboost_e_txs_{counter_txs}.csv", index=None)
                df_txs = pd.DataFrame(columns=["miner", "block_number","txhash"])
                counter_txs += 1

    except Exception as e:
        print("\n"+str(e))
        print(row)
        print("\nstopping application")
        log("enriching data FAILED")
    
    finally:
        df.to_csv(FOLDER + "mevboost_e.csv", index=None)
        df_txs.to_csv(FOLDER + f"mevboost_e_txs_{counter_txs}.csv", index=None)
        print("Storing successful")
        


if __name__ == "__main__":
    w3 = Web3(Web3.HTTPProvider(RPC_ENDPOINT))
    assert w3.isConnected()
    try:
        df, FILENR = open_enriched_file(FOLDER)
    except:
        df = pd.DataFrame(columns=["relay", "slot", "block_hash", "builder_pubkey", "value", "gas_used", "gas_limit"])

    df2 = NEW_DF
    df = pd.concat([df,df2[~df2["slot"].isin(df["slot"])]], ignore_index=True)
    df = df.sort_values("slot")
    df_txs = pd.DataFrame(columns=["miner", "block_number", "txhash"])
    df = df.fillna("none")
    enrich_data(w3, df, df_txs, counter_txs)
    log("enriching data successful")
