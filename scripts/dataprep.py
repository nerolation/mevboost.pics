import pandas as pd
from datetime import datetime
import os
import time
from logger import log 

CHARTDATA_FOLDER = "./chart_data/"
FOLDER = "./data/"
ENRICHED_DATA_FOLER = "./enriched_data/"

names = ["flashbots",
        "bloxroute (ethical)",
        "bloxroute (max profit)",
        "bloxroute (regulated)",
        "manifold",
        "eden",
        "blocknative",
        "Other/None"]

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


color_mapping = {
    "flashbots": '#3D9140',
    'bloxroute (regulated)': "#FF5733",
    'bloxroute (max profit)': "#FF5733",
    'bloxroute (ethical)': "#FF5733",
    'manifold': "#F2B880",
    'blocknative': "#FFD447",
    'eden': "#966B9D"
}

known_pkeys = {
    "flashbots":["0xa1dead01e65f0a0eee7b5170223f20c8f0cbf122eac3324d61afbdb33a8885ff8cab2ef514ac2c7698ae0d6289ef27fc",
        "0x81beef03aafd3dd33ffd7deb337407142c80fea2690e5b3190cfc01bde5753f28982a7857c96172a75a234cb7bcb994f",
        "0x81babeec8c9f2bb9c329fd8a3b176032fe0ab5f3b92a3f44d4575a231c7bd9c31d10b6328ef68ed1e8c02a3dbc8e80f9",
        "0xa1defa73d675983a6972e8686360022c1ebc73395067dd1908f7ac76a526a19ac75e4f03ccab6788c54fdb81ff84fc1b"], 
    "eden":["0xa5eec32c40cc3737d643c24982c7f097354150aac1612d4089e2e8af44dbeefaec08a11c76bd57e7d58697ad8b2bbef5"],
    "bloxroute":["0x80c7311597316f871363f8395b6a8d056071d90d8eb27defd14759e8522786061b13728623452740ba05055f5ba9d3d5",
        "0x8b8edce58fafe098763e4fabdeb318d347f9238845f22c507e813186ea7d44adecd3028f9288048f9ad3bc7c7c735fba",
        "0x95701d3f0c49d7501b7494a7a4a08ce66aa9cc1f139dbd3eec409b9893ea213e01681e6b76f031122c6663b7d72a331b",
        "0xb086acdd8da6a11c973b4b26d8c955addbae4506c78defbeb5d4e00c1266b802ff86ec7457c4c3c7c573fa1e64f7e9e0",
        "0xaa1488eae4b06a1fff840a2b6db167afc520758dc2c8af0dfb57037954df3431b747e2f900fe8805f05d635e9a29717b",
        "0x94aa4ee318f39b56547a253700917982f4b737a49fc3f99ce08fa715e488e673d88a60f7d2cf9145a05127f17dcb7c67",
        "0xb9b50821ec5f01bb19ec75e0f22264fa9369436544b65c7cf653109dd26ef1f65c4fcaf1b1bcd2a7278afc34455d3da6"],
    "manifold":["0xa25f5d5bd4f1956971bbd6e5a19e59c9b1422ca253587bbbb644645bd2067cc08fb854a231061f8c91f110254664e943"],
    "blocknative":["0x9000009807ed12c1f08bf4e81c6da3ba8e3fc3d953898ce0102433094e5f22f21102ec057841fcb81978ed1ea0fa8246"]
}

# invert dict
_known_pkeys = {}
for i in known_pkeys.keys():
    for j in known_pkeys[i]:
        _known_pkeys[j] = i

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
    return "(Anon)"

def now():
    return datetime.strftime(datetime.now(), "%m-%d|%H:%M:%S")

def prepare_last_known_slot(df):
     with open(FOLDER + "last_known_slot.txt", "w") as f:
        f.write(str(max(df["slot"])))
        
def create_label(x):
    label = get_builder_label(x)
    y = x[:8] +"... " + str(len(df[df["builder_pubkey"] == x])) +" blocks " + label
    return y

def create_source(x):
    return x[0].upper() + x[1:].lower() + " Relay"

def hextorgba(h):
    return "rgba"+str(tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (0.20,))

def get_builder_color(a):
    if a in fb_b:
        return "#3D9140"
    elif a in ed_b:
        return "#966B9D"
    elif a in bx_b:
         return "#FF5733"
    elif a in ma_b:
         return "#F2B880"
    elif a in bn_b:
        return "#FFD447"
    elif a in bu_z:
        return "#324ea8"
    return "#000001"


def open_file():
    df = pd.DataFrame()
    for file in os.listdir(FOLDER):
        if not (file.startswith("mevboost_") and file.endswith(".csv")):
            continue
        _df = pd.read_csv(FOLDER + file)
        df = pd.concat([df, _df])
        print(now()+ f" reading {file}", end="\r")
    df["value"] = df["value"].apply(lambda x: int(x))
    df["slot"] = df["slot"].apply(lambda x: int(x))
    return df

def open_enriched():
    return pd.read_csv(ENRICHED_DATA_FOLER + "mevboost_er.csv", dtype={"value": float, 
                                                                       "reward": float, 
                                                                       "slot": int}).sort_values("block_number")

def filter_errors_of_reward_df(df):
    """
    Filter out wrongly reported slots.
    """
    mani = df[df["relay"]=="manifold"]
    mani = mani[mani["value"]>mani["reward"]+1e18]["slot"].values.tolist()

    eden = df[df["relay"]=="eden"]
    eden = eden[eden["value"]>eden["reward"]+5e18]["slot"].values.tolist()

    bad_slots = mani + eden
    return df[~df["slot"].isin(bad_slots)]

def split_data(df):
    fb = df[df["relay"] == "flashbots"]
    be = df[df["relay"] == "bloxroute (ethical)"]
    bm = df[df["relay"] == "bloxroute (max profit)"]
    br = df[df["relay"] == "bloxroute (regulated)"]
    ma = df[df["relay"] == "manifold"]
    ed = df[df["relay"] == "eden"]
    bn = df[df["relay"] == "blocknative"]
    no = df[df["relay"] == "Other/None"]
    return fb, be, bm, br, ma, ed, bn, no

def add_date(df):
    # Add date column
    get_date = lambda x: datetime.strftime(datetime.utcfromtimestamp(x), "%y/%m/%d;%H:00:00")
    df["timestamp"] = df["slot"].apply(lambda x: get_date(1663224179 + (int(x) - 4700013) * 12)) 
    return df

def add_non_mev_slots(df):
    print(now()+ " filling empty builders...", end="\r")
    slots_with_builders = set(df["slot"].astype(int))
    indexdf = pd.DataFrame(index=range(min(slots_with_builders), 
                                       max(slots_with_builders))
                          )
    # Slots as index for joining
    df = df.set_index("slot")
    df = indexdf.join(df)
    df.loc[df["relay"] != df["relay"],"relay"] = "Other/None"
    df = df.reset_index().rename(columns={"index":"slot"})
    return df

def group_data_by_timestamp(*args):
    fb, be, bm, br, ma, ed, bn, no = args
    _fb = fb[["timestamp","slot"]].groupby("timestamp").count().iloc[0:-2].reset_index()
    _be = be[["timestamp","slot"]].groupby("timestamp").count().iloc[0:-2].reset_index()
    _bm = bm[["timestamp","slot"]].groupby("timestamp").count().iloc[0:-2].reset_index()
    _br = br[["timestamp","slot"]].groupby("timestamp").count().iloc[0:-2].reset_index()
    _ma = ma[["timestamp","slot"]].groupby("timestamp").count().iloc[0:-2].reset_index()
    _ed = ed[["timestamp","slot"]].groupby("timestamp").count().iloc[0:-2].reset_index()
    _bn = bn[["timestamp","slot"]].groupby("timestamp").count().iloc[0:-2].reset_index()
    _no = no[["timestamp","slot"]].groupby("timestamp").count().iloc[0:-2].reset_index()
    return _fb, _be, _bm, _br, _ma, _ed, _bn, _no


def create_share_data(df):
    print(now()+ " converting values to int...", end="\r")    

    # Split into different relays
    fb, be, bm, br, ma, ed, bn, no = split_data(df)
    # Group by timestamp and count
    _fb, _be, _bm, _br, _ma, _ed, _bn, _no = group_data_by_timestamp(fb, be, bm, br, ma, ed, bn, no)

    # Store files for charting
    shares = pd.DataFrame()
    for ix, file in enumerate([_fb, _be, _bm, _br, _ma, _ed, _bn, _no]):
        file["relay"]=names[ix]
        shares = pd.concat([shares,file], ignore_index=True)
    shares.to_csv(CHARTDATA_FOLDER + f"share_all.csv")
    
    shares = pd.DataFrame()
    for ix, file in enumerate([_fb, _be, _bm, _br, _ma, _ed, _bn]):
        file["relay"]=names[ix]
        shares = pd.concat([shares,file], ignore_index=True)
    shares.to_csv(CHARTDATA_FOLDER + f"share_mevboost.csv")
    log("share data successfully created")
    print(now()+ " share data successfully created", end="\r")
    
def create_builder_pie_chart(_df):
    df = _df.copy()
    df = df[df["slot"] >= max(df["slot"]) - 7200*14]
    
    # RELAY - note: when all entries have slot, but non-mev entries have no block hash
    # therefore we can group be them and separate between total vs mev-boosted
    _df = df[["relay", "slot"]].groupby(["relay"]).count().reset_index()
    _df["relay"] = _df["relay"].apply(lambda x: x[0].upper()+x[1:]) 
    _df.to_csv(CHARTDATA_FOLDER + f"pie_total_relay.csv", index=None)
    _df = df[["relay", "block_hash"]].groupby(["relay"]).count().reset_index()
    _df["relay"] = _df["relay"].apply(lambda x: x[0].upper()+x[1:]) 
    _df.to_csv(CHARTDATA_FOLDER + f"pie_mevboost_relay.csv", index=None)
    
    # BUILDER
    _shorten = lambda x: x[0:8] + "..." + get_builder_label(x) if x==x else "Others"
    df["builder_pubkey"] = df["builder_pubkey"].apply(_shorten)
    _df = df[["builder_pubkey", "block_hash"]].groupby(["builder_pubkey"]).count().reset_index()
    _df.to_csv(CHARTDATA_FOLDER + f"pie_mevboost.csv", index=None)
    df = df[["builder_pubkey", "slot"]].groupby(["builder_pubkey"]).count().reset_index()
    df.to_csv(CHARTDATA_FOLDER + f"pie_total.csv", index=None)
    log("pie chart data successfully created")
    print(now()+ " pie chart data successfully created", end="\r")
    
    
def create_sankey(df):
    all_builders = list(df.sort_values("relay").groupby("builder_pubkey").count().index)
    builder_labels = [create_label(i) for i in all_builders]
    all_relays = ['flashbots',
                  'bloxroute (ethical)',
                  'bloxroute (max profit)',
                  'bloxroute (regulated)',
                  'eden',
                  'blocknative',
                  'manifold'
                 ]

    relay_colors = [color_mapping[i] for i in all_relays]
    
    summarized = dict()
    for j in [fb_b, ed_b, bx_b, ma_b, bn_b]:
        _df = df[df["builder_pubkey"].isin(j)]
        builder = get_builder_label(list(_df["builder_pubkey"])[0])
        builder = builder.replace("(", "").replace(")", "")
        summarized[builder] = _df
        
    source = []
    target = []
    value = []
    colors = []
    colors_builder = []

    for ii, i in enumerate(all_builders):
        ll = get_builder_label(i)
        col = get_builder_color(i)
        colors_builder.append(col)
        for jj, j in enumerate(all_relays):
            if i in set(df[df["relay"] == j]["builder_pubkey"]):
                only_relay = df[df["relay"] == j]
                l = len(only_relay[only_relay["builder_pubkey"] == i])
                value.append(l)
                source.append(ii)
                target.append(len(all_builders)+jj)

                colors.append(hextorgba(col.replace("#", "")))
    all_relays = [i[0].upper() + i[1:].lower() for i in all_relays]
    
    pd.DataFrame(zip(source,target,value), 
                 columns=["source", "target", "value"]).to_csv(CHARTDATA_FOLDER + "sankey_source_target_value.csv", index=None)
    pd.DataFrame(colors_builder + relay_colors, columns=["colors"]).to_csv(CHARTDATA_FOLDER + "sankey_colors.csv", index=None)
    pd.DataFrame(colors, columns=["link_colors"]).to_csv(CHARTDATA_FOLDER + "sankey_link_colors.csv", index=None)    
    pd.DataFrame(builder_labels, columns=["labels"]).to_csv(CHARTDATA_FOLDER + "builder_labels.csv", index=None)
    pd.DataFrame(all_relays, columns=["labels"]).to_csv(CHARTDATA_FOLDER + "relay_labels.csv", index=None)
    log("sankey data successfully created")
    print(now()+ " sankey data successfully created", end="\r")

def create_avg_val_gas_chart(_df):
    df = _df.copy()
    df = filter_errors_of_reward_df(df)
    get_date = lambda x: datetime.strftime(datetime.utcfromtimestamp(x), "%y/%m/%d")
    df["timestamp"] = df["slot"].apply(lambda x: get_date(1663224179 + (int(x) - 4700013) * 12))
    df["value"] = df["value"].apply(lambda x: float(x)/1e18)
    df["gas_used"] = df["gas_used"].apply(lambda x: float(x))
    df = df.loc[:,("relay","value", "timestamp", "gas_used")].groupby(["relay","timestamp"], as_index=False).mean()
    df = df.sort_values("timestamp")
    df.to_csv(CHARTDATA_FOLDER + "avg_proposer_val_gas.csv", index=None)
    log("avg gas and proposer value chart successfully created")
    print(now()+ " avg gas and proposer value chart successfully created", end="\r")
    
    
def create_potential_mev_chart(_df):
    df = _df.copy()
    df = filter_errors_of_reward_df(df)
    df["value"] = df["value"].apply(lambda x: int(x)/1e18)
    df["reward"] = df["reward"].apply(lambda x: int(x)/1e18)
    get_date = lambda x: datetime.strftime(datetime.utcfromtimestamp(x), "%y/%m/%d")
    df["timestamp"] = df["slot"].apply(lambda x: get_date(1663224179 + (int(x) - 4700013) * 12))
    df = df.loc[:,("value", "timestamp", "reward")].groupby("timestamp", as_index=False).sum()
    #a = df.tail(2)["reward"].tolist()
    # if last entry is too small because day still ongoing, skip it
    #if a[0]-a[1] > a[0]/2:
    #    df = df.loc[df.index[:-1], :]
    df.to_csv(CHARTDATA_FOLDER + "potentialmev.csv")
    log("potential mev chart successfully created")
    print(now()+ " potential mev chart successfully created", end="\r")
    
def create_builder_bar_chart(_df):
    _df = filter_errors_of_reward_df(_df)
    
    # last 7 days
    df2 = _df.copy()
    
    df2 = df2[df2["slot"] >= max(df2["slot"])-(86400*7/12)]
    df2["value"] = df2["value"].apply(lambda x: int(x)/1e18)
    df2 = df2[["builder_pubkey", "value"]]
    largest_builders = df2.groupby("builder_pubkey").count().sort_values("value")[::-1].index[0:10].tolist()
    df2 = df2[df2["builder_pubkey"].isin(largest_builders)].groupby("builder_pubkey").mean().reset_index()
    func = lambda x: x[0:8]+"...<br>("+_known_pkeys[x]+")" if x in _known_pkeys.keys() else x[0:8]+"...<br>(anon)"
    df2["builder"] = df2["builder_pubkey"].apply(func)
    df2["frame"] = "Last 7 days"

    # total
    df1 = _df.copy()
    df1["value"] = df1["value"].apply(lambda x: int(x)/1e18)
    df1 = df1[["builder_pubkey", "value"]]
    df1 = df1[df1["builder_pubkey"].isin(largest_builders)].groupby("builder_pubkey").mean().reset_index()
    df1["builder"] = df1["builder_pubkey"].apply(func)
    df1["frame"] = "Total"
    
    df = pd.concat([df1, df2])
    df.to_csv(CHARTDATA_FOLDER + "builderbar.csv", index=None)
    print(now()+ "builder bar chart successfully created", end="\r")


df = open_file()
df_e = open_enriched()
# Fill non-mev slots
df = add_non_mev_slots(df)
df = add_date(df)
prepare_last_known_slot(df)
create_share_data(df)
create_builder_pie_chart(df)
create_sankey(df[~df["block_hash"].isna()])
create_avg_val_gas_chart(df_e)
create_potential_mev_chart(df_e)
create_builder_bar_chart(df_e)
print("                                                                                    ", end="\r")
print("Success")