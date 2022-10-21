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
    
fb_b = ["0xa1dead01e65f0a0eee7b5170223f20c8f0cbf122eac3324d61afbdb33a8885ff8cab2ef514ac2c7698ae0d6289ef27fc",
        "0x81beef03aafd3dd33ffd7deb337407142c80fea2690e5b3190cfc01bde5753f28982a7857c96172a75a234cb7bcb994f",
        "0x81babeec8c9f2bb9c329fd8a3b176032fe0ab5f3b92a3f44d4575a231c7bd9c31d10b6328ef68ed1e8c02a3dbc8e80f9",
        "0xa1defa73d675983a6972e8686360022c1ebc73395067dd1908f7ac76a526a19ac75e4f03ccab6788c54fdb81ff84fc1b"]

ed_b = ["0xa5eec32c40cc3737d643c24982c7f097354150aac1612d4089e2e8af44dbeefaec08a11c76bd57e7d58697ad8b2bbef5"]

bx_b = ["0x80c7311597316f871363f8395b6a8d056071d90d8eb27defd14759e8522786061b13728623452740ba05055f5ba9d3d5",
        "0x8b8edce58fafe098763e4fabdeb318d347f9238845f22c507e813186ea7d44adecd3028f9288048f9ad3bc7c7c735fba",
        "0x95701d3f0c49d7501b7494a7a4a08ce66aa9cc1f139dbd3eec409b9893ea213e01681e6b76f031122c6663b7d72a331b",
        "0xb086acdd8da6a11c973b4b26d8c955addbae4506c78defbeb5d4e00c1266b802ff86ec7457c4c3c7c573fa1e64f7e9e0",
        "0xaa1488eae4b06a1fff840a2b6db167afc520758dc2c8af0dfb57037954df3431b747e2f900fe8805f05d635e9a29717b",
        "0x94aa4ee318f39b56547a253700917982f4b737a49fc3f99ce08fa715e488e673d88a60f7d2cf9145a05127f17dcb7c67",
        "0xb9b50821ec5f01bb19ec75e0f22264fa9369436544b65c7cf653109dd26ef1f65c4fcaf1b1bcd2a7278afc34455d3da6"]

ma_b = ["0xa25f5d5bd4f1956971bbd6e5a19e59c9b1422ca253587bbbb644645bd2067cc08fb854a231061f8c91f110254664e943"]

bn_b = ["0x9000009807ed12c1f08bf4e81c6da3ba8e3fc3d953898ce0102433094e5f22f21102ec057841fcb81978ed1ea0fa8246"]

bu_z = ["0xb194b2b8ec91a71c18f8483825234679299d146495a08db3bf3fb955e1d85a5fca77e88de93a74f4e32320fc922d3027"]

def get_builder_label(a):
    if a in fb_b:
        return "(Flashbots)"
    elif a in ed_b:
        return "(Eden)"
    elif a in bx_b:
         return "(Bloxroute)"
    elif a in ma_b:
         return "(Manifold)"
    elif a in bn_b:
        return "(Blocknative)"
    elif a in bu_z:
        return "(Builder 0x69)"
    return "(anon)"

def get_twitter_handle(a):
    if a in fb_b or a == "flashbots":
        return "Flashbots"
    elif a in ed_b or a == "eden":
        return "@EdenNetwork"
    elif a in bx_b or "bloxroute" in a:
         return "@bloXrouteLabs"
    elif a in ma_b or a == "manifold":
         return "@foldfinance"
    elif a in bn_b or a == "blocknative":
        return "@blocknative"
    elif a in bu_z:
        return "@builder0x69"
    return a


    
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
TWEET = "High Proposer Payment Alert! 💸 \nValidator received {:,.3f} ETH\nBuilder: {}.\n" \
            + "Slot: {:,.0f}.\nReceived through the {} relay.\n"+URL

TWEET_2 = "High Proposer Payment Alert! 💸 \nValidator {} received {:,.2f} ETH\nBuilder: {} ({}).\n" \
            + "Slot: {:,.0f}.\nReceived through the {} relay.\n"+URL

TWEET_3 = "High Proposer Payment Alert! 💸 \nValidator {} received {:,.2f} ETH\nBlock built by a {} builder ({}) 👷‍.\n" \
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
    max_file = str(max(maxfilenr)+off)
    maxfilenr.remove(int(max_file))
    second_max = str(max(maxfilenr)+off)
    
    return LOCATION + "mevboost_" +  max_file + ".csv", LOCATION + "mevboost_" +  second_max + ".csv",

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
        handle_twitter = get_twitter_handle(row["builder_pubkey"])
        val = row["value"]/1e18
        short_pk = row["builder_pubkey"][0:8]+"..."
        slot_int = int(row["slot"])
        slot_str = row["slot"]
        if get_twitter_handle(row["builder_pubkey"]) == "anon":
            return TWEET_2.format(recipient,
                                  val, 
                                  short_pk, 
                                  handle_twitter,
                                  slot_int, 
                                  handle_twitter,
                                  slot_str
                                )
        else:
            return TWEET_3.format(recipient,
                                  val, 
                                  handle_twitter,
                                  short_pk, 
                                  slot_int, 
                                  handle_twitter,
                                  slot_str
                                )
            
        

    return TWEET.format(row["value"]/1e18, 
                         row["builder_pubkey"][0:8]+"...", 
                         int(row["slot"]), 
                         get_twitter_handle(row["relay"]),
                         row["slot"]
                        )

def now():
    return datetime.strftime(datetime.now(), "%m-%d|%H:%M:%S")

with open("./known_slots.txt", "r") as file:
    posted = set(file.read().split("\n"))

df = pd.DataFrame()
for file in get_last_file():
    print(f"opening {file}")
    _df = pd.read_csv(file).sort_values("slot")
    _df["value"] = _df["value"].apply(lambda x: int(x))
    _df = _df[_df["value"] >= int(5e18)]
    df = pd.concat([df,_df], ignore_index=True)


df["value"] = df["value"].apply(lambda x: int(x) if x==x and x!=None else None)
for ix, row in df[df["value"] >= int(5e18)].iterrows():
    if str(row["slot"]) not in posted:
        posted.add(str(row["slot"]))
        post = generate_post(row)
        success, resp = make_tweet(post)
        assert success
        print(colored("Tweet successfully sent", "green", attrs=["bold"]))
        if len(resp.errors) > 0:
            print(f"Response: {str(resp)}")
        else:
            print(f"https://twitter.com/user/status/{resp.data['id']}")
        with open("./known_slots.txt", "a") as file:
            file.write(str(row["slot"])+"\n")
