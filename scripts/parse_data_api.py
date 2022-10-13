import os
import re
import time
import requests
import argparse
import pandas as pd
from web3 import Web3
from datetime import datetime
from termcolor import colored
from requests.exceptions import ConnectionError


# Handle parameters
parser = argparse.ArgumentParser(formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=60))

# Set True if starting from scratch
parser.add_argument('-s', '--scratch', help="start from scratch - default: False",  action='store_true')
parser.add_argument('-slot', '--slot', help="latest slot", default="4750000")
parser.add_argument('-l', '--location', help="Storage location", default="data/")
_args = parser.parse_args()

# Start timestamp
startTS = datetime.now()

# Location to store mevboost.csv files
LOCATION = vars(_args)["location"]
if not os.path.isdir(LOCATION):
    os.mkdir(LOCATION)
    

# Ignore and overwrite old dataframe and start from scratch (first time usage, always from scratch)
IGNORE_OLD_DF = vars(_args)["scratch"]

# Parsing will start at the latest slot and then loop backwards
START_SLOT = int(vars(_args)["slot"])

# Slot of the Merge
POS_SWITCH_SLOT = 4700013 

# API Limit
LIMIT = 100

# Start timestamp 
startTS = datetime.now()

# column names
c = ["relay", 
     "slot", 
     "block_hash", 
     "builder_pubkey", 
     "value", 
     "gas_used", 
     "gas_limit"]

# API endpoints
path = "/relay/v1/data/bidtraces/proposer_payload_delivered?limit={}&cursor={}"
fb = "https://boost-relay.flashbots.net" + path
et = "https://bloxroute.ethical.blxrbdn.com" + path
mp = "https://bloxroute.max-profit.blxrbdn.com" + path
mr = "https://bloxroute.regulated.blxrbdn.com" + path
mf = "https://mainnet-relay.securerpc.com" + path
ed = "https://relay.edennetwork.io/" + path
bn = "https://builder-relay-mainnet.blocknative.com" + path

# Endpoint class
class Endpoint():
    def __init__(self, endpoint, relay):
        self.endpoint = endpoint
        self.relay = relay
        self.slotFrom = START_SLOT
        self.LIMIT = LIMIT
        self.knownMaxSlot = POS_SWITCH_SLOT
        self.endslot = POS_SWITCH_SLOT
        
eps = [Endpoint(fb, "flashbots"), 
       Endpoint(bn, "blocknative"),
       Endpoint(et, "bloxroute (ethical)"), 
       Endpoint(mp, "bloxroute (max profit)"),
       Endpoint(mr, "bloxroute (regulated)"), 
       Endpoint(mf, "manifold"), 
       Endpoint(ed, "eden")
      ]

# Returns the current file or with off=1 the next one
def get_last_file(off=0):
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
    if len(maxfilenr) > 0:
        return LOCATION + "mevboost_" +  str(max(maxfilenr)+off) + ".csv"
    else:
        return LOCATION + "mevboost_0.csv"

# Set endslot to last known slot of relay
def set_end_slot(df, eps):
    for ep in eps:
        print(f"{len(df[df['relay'] == ep.relay])} blocks found for {ep.relay}")
        entries_per_ep = df[df['relay'] == ep.relay]["slot"].astype(int)
        if len(entries_per_ep) == 0:
            continue
        max_slot_ep = max(entries_per_ep)
        if max_slot_ep > ep.endslot:
            ep.endslot = max_slot_ep
            ep.knownMaxSlot = max_slot_ep
        print(f"{colored(ep.relay, 'green', attrs=['bold'])} last slot set to {ep.endslot}")
        
            
# Current file to proceed
FILENAME = get_last_file()
LEN_CURRENT_FILE = 0
KNOWN_SLOTS = set()
KNOWN_SLOTS_int = set()
if not IGNORE_OLD_DF:
    for file in sorted(os.listdir(LOCATION)):
        if file.startswith("mevboost_") and file.endswith(".csv"):
            OLD_DF = pd.read_csv(LOCATION + file)[["relay", "slot"]]
            print(f"Existing file found: {file}")
            
            set_end_slot(OLD_DF, eps)
            
            if LOCATION + file == FILENAME:
                LEN_CURRENT_FILE = len(OLD_DF)
            for ix, row in OLD_DF.iterrows():
                r = OLD_DF.loc[ix, "relay"]
                s = OLD_DF.loc[ix, "slot"]
                KNOWN_SLOTS.add(r + str(s))
    # Update loaded blocks
    

    OLD_DF = None  
        
# If starting from scratch -> empty df, else load ./mevboost.csv    
else:
    OLD_DF = pd.DataFrame(columns=c)
    if os.path.isfile(FILENAME):
        input("There exists already a file named mevboost.csv. Press any key to continue.\n" \
              + "Press Crtl+C to stop\n")
    for i in os.listdir(LOCATION):
        if file.startswith("mevboost_") and file.endswith(".csv"):
            os.remove(LOCATION + i)
    OLD_DF.to_csv(FILENAME, index=None)    

    
        
def get_with_cursor(ep, s, counter=0):
    res = None
    while res == None:
        try:
            res = requests.get(ep.endpoint.format(ep.LIMIT,s), timeout=20)
        except Exception as e:
            time.sleep(2)
            print(f"something failed: ({counter+1}/3) " + str(e))
            counter += 1
            if counter >= 3:
                print(colored(f"{ep.relay} failed", "red", attrs=["bold"]))
                print(ep.endpoint.format(ep.LIMIT,s))
                res = "fail"
            else:
                res = None
    time.sleep(0.8)
    if res == "fail":
        return res
    if not res.status_code == 200:
        return None
    print(colored(ep.endpoint.format(ep.LIMIT,s), "green"))
    return eval(res.content.decode("utf-8"))

# Keep track of parsed slots to start new file if too many entries
slots_parsed = 0
def query(eps):
    global slots_parsed, LEN_CURRENT_FILE, FILENAME
    # Loop over all endpoints
    for ep in eps:
        
        # If more than 10k entries -> new file
        if LEN_CURRENT_FILE + slots_parsed > 10000:
            FILENAME = get_last_file(off=1)
            slots_parsed = 0
            LEN_CURRENT_FILE = 0
            pd.DataFrame(columns=c).to_csv(FILENAME, index=None)    
            print(f"Start writing into new file: {FILENAME}")
        
        print(f"parsing {ep.relay}")
        # Loop from ep.slotFrom to endslot, endslot is always lower than the slotFrom
        while ep.slotFrom > ep.endslot:
            results = None
            while results == None:
                results = get_with_cursor(ep, ep.slotFrom)
            min_slot = set()
            
            if results == "fail":
                print(colored(f"{ep.relay} limit set to 100", "red", attrs=["bold"]))
                ep.LIMIT = 100
                break
            
            for i, r in enumerate(results):
                if str(ep.relay+r["slot"]) in KNOWN_SLOTS:
                    continue
                # If api endpoint has no info on gas, set None manually
                if "gas_used" not in r.keys():
                    r["gas_used"] = "NaN"
                    r["gas_limit"] = "NaN"
                # Update dataframe
                content = ",".join([ep.relay, 
                                    r["slot"],
                                    r["block_hash"],
                                    r["builder_pubkey"],
                                    r["value"],
                                    r["gas_used"],
                                    r["gas_limit"]]
                                  ) + "\n"
                with open(FILENAME, 'a') as f:
                    f.write(content)
                
                KNOWN_SLOTS.add(str(ep.relay+r["slot"]))
                KNOWN_SLOTS_int.add(int(r["slot"]))
                # Keep track of max known slot per ep
                ep.knownMaxSlot = max([ep.knownMaxSlot, int(r["slot"])])
                slots_parsed += 1
                # Keep track of known slots
                min_slot.add(int(r["slot"]))
                
                if ep.LIMIT < 100:
                    print(f"Block found for slot {r['slot']} with relay {ep.relay}")
                
            # LIMIT can only be smaller than 100 after the first round
            if ep.LIMIT < 100:
                break
            # If nothing found, decrease parse-window by LIMIT, 
            # else take min slot -1 and start there
            if len(min_slot) == 0 and ep.LIMIT == 100:
                ep.slotFrom -= ep.LIMIT
            else:
                min_slot = min(min_slot)
                ep.slotFrom = min_slot -1
            
    return eps


# Run
while True:
    try:
        # Get timestamp at start of iteration
        roundStartTS = datetime.now()
        # Query relay data api
        eps = query(eps)
        # Measure the slots passed since the start of the app
        slots_passed = round((datetime.now()-startTS).total_seconds()/12)
        # When iteration takes too long there is the risk of missing slots
        # Therefore set limit to 100 which activates endless looping until endslot
        if (datetime.now()-roundStartTS).total_seconds() > 12*50:
            for ep in eps:
                ep.LIMIT = 100  
                ep.endslot = ep.knownMaxSlot
        else:
             for ep in eps:
                ep.endslot = ep.knownMaxSlot
                ep.LIMIT = 50 # 50 just to be safe (known slots will be skipped anyway)
            
        # Set slotFrom to the current slot
        for ep in eps:
            ep.slotFrom = START_SLOT + slots_passed

        print("waiting for 9 seconds")
        time.sleep(9)

    except KeyboardInterrupt:
        print("\nstopping application...")
        break
