import os
import re
import tweepy
import pandas as pd
import time
from datetime import datetime
from termcolor import colored
from web3 import Web3

LOCATION = "data/"

# Load infura rpc endpoint url
with open("key/infura.txt", "r") as f:
    RPC_ENDPOINT = f.read().strip()
    
w3 = Web3(Web3.HTTPProvider(RPC_ENDPOINT))
assert w3.isConnected()

# Twitter API KEY
with open("key/twitterkey.txt", "r") as f:
    consumer_key, consumer_secret, bearer, access_token, access_token_secret = f.read().strip().split(",")
    
client = tweepy.Client(
    consumer_key=consumer_key, consumer_secret=consumer_secret,
    access_token=access_token, access_token_secret=access_token_secret
)

# Use either beaconscan or beaconcha.in
URL = "https://beaconscan.com/slot/{}"
URL2 = "https://beaconcha.in/slot/{}"

# Tweet
TWEET = "High Proposer Payment Alert! 💸 \nValidator received {:,.3f} ETH from builder @ {}.\n" \
            + "Slot: {:,.0f}.\nReceived through the {} relay.\n"+URL

TWEET_2 = "High Proposer Payment Alert! 💸 \nValidator {} received {:,.3f} ETH from builder {}.\n" \
            + "Slot: {:,.0f}.\nReceived through the {} relay.\n"+URL

def get_last_file(off=0):
    # Get latest mevboost.csv file
    maxfilenr = []
    for file in os.listdir(LOCATION):
        if file.startswith("mevboost_") and file.endswith(".csv"):
            nr = re.findall("[0-9]+", file)
            nr = [int(n) for n in nr]
            if len(nr) == 0:
                nr = 0
            else:
                nr = max(nr)
            maxfilenr.append(nr)        
    return LOCATION + "mevboost_" +  str(max(maxfilenr)+off) + ".csv"

def make_tweet(tweet):
    # Send tweet
    try:
        print(colored(now() + f"\nsending tweet:\n{tweet}", "green"))
        return True, client.create_tweet(text=tweet)
    except Exception as e:
        print(str(e))
        return None, None

def generate_post(row):
    block = None
    loop_count = 0
    while block == None and loop_count < 5:
        try:
            block = w3.eth.get_block(row["block_hash"])
        except:
            block = None
        time.sleep(loop_count)
        loop_count += 1
        
    recipient = None
    if row.relay in ["manifold", "blocknative"]:
        recipient = block.miner
    else:
        tx = block.transactions[-1]
        try:
            tx = w3.eth.get_transaction(tx)
            recipient = tx.to
        except:
            recipient = None
    
    if recipient:
        recipient = recipient.lower()[:6]+"..."
        return TWEET_2.format(recipient,
                              row["value"]/1e18, 
                              row["builder_pubkey"][0:8]+"...", 
                              int(row["slot"]), 
                              row["relay"],
                              row["slot"]
                            )
        

    return TWEET.format(row["value"]/1e18, 
                         row["builder_pubkey"][0:8]+"...", 
                         int(row["slot"]), 
                         row["relay"],
                         row["slot"]
                        )

def now():
    return datetime.strftime(datetime.now(), "%m-%d|%H:%M:%S")

with open("./known_slots.txt", "r") as file:
    posted = set(file.read().split("\n"))

wait = 30
while True:
    FILE = get_last_file()
    df = pd.read_csv(FILE).sort_values("slot").tail(5000)
    if len(df) == 0:
        try:
            df = pd.read_csv(get_last_file(-1))
        except: 
            time.sleep(100)
            continue
        
    df["value"] = df["value"].apply(lambda x: int(x) if x==x and x!=None else None)
    for ix, row in df[df["value"] >= int(4e18)].iterrows():
        if str(row["slot"]) not in posted:
            posted.add(str(row["slot"]))
            post = generate_post(row)
            success = None
            while success == None:
                success, resp = make_tweet(post)
                time.sleep(10)
            print(colored("Tweet successfully sent", "green", attrs=["bold"]))
            if len(resp.errors) > 0:
                print(f"Response: {str(resp)}")
            else:
                print(f"https://twitter.com/user/status/{resp.data['id']}")
            with open("./known_slots.txt", "a") as file:
                file.write(str(row["slot"])+"\n")
    maxslot = max(df["slot"])
    print(now() + f" | sleeping for {wait} seconds; last slot {maxslot}; file {FILE}", end="\r")
    df = None
    time.sleep(wait)
