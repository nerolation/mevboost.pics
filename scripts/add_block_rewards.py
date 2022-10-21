import pandas as pd
import json
import os
import time
import requests
from logger import log 

# Load Etherscan API key
with open("./key/key.txt", "r") as file:
    KEY = file.read()

FOLDER = "./enriched_data/"

PAYLOAD = "https://api.etherscan.io/api" \
             + "?module=block" \
             + "&action=getblockreward" \
             + "&blockno={}" \
             + "&apikey={}".format(KEY)

def build_payload(block):
    return PAYLOAD.format(block)

def send_payload(payload):
    try:
        _res = requests.get(payload)
        res = json.loads(_res.content)    
        res["result"]
    except:
        print("Waiting for 10 seconds")
        time.sleep(10)
        return send_payload(payload)
        
    return res["result"]

def get_block_reward(blocknr):
    pl = build_payload(blocknr)
    return send_payload(pl)["blockReward"]
    
    
try:
    df = pd.read_csv(FOLDER + "mevboost_er.csv", dtype={"miner":str, "value":float, "slot":int})
    print("mevboost_er.csv loaded")
except:
    df = pd.DataFrame(columns=["slot"])

# Concat existing file with new entries
df2 = pd.read_csv(FOLDER + "mevboost_e.csv", dtype={"miner":str, "value":float, "slot":int})
df = pd.concat([df,df2[~df2["slot"].isin(df["slot"])]], ignore_index=True)
df = df[~df["block_number"].isna()]

if "reward" not in df.columns:
    df["reward"] = None
max_block = str(int(max(df.sort_values("block_number")["block_number"])))
df = df.sort_values("block_number").fillna("none")

nonnones = df[df["reward"] != "none"].reset_index(drop=True)
df = df[df["reward"] == "none"].reset_index(drop=True)
l = len(df)
try:
    for ix, i in df.iterrows():
        print(str(ix) +"/"+ str(l), end="\r")
        # Add reward
        df.loc[ix, "reward"] = get_block_reward(int(i["block_number"]))
    log("adding block rewards successful")
except:
    log("enriching data FAILED")
    
df = pd.concat([nonnones, df], ignore_index=True)
df.to_csv(FOLDER + "mevboost_er.csv", index=None)
