#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import datapane as dp
from plotly.subplots import make_subplots
from datetime import datetime
from logger import log 

FOLDER = "./data/"
GITFOLDER = "./wu-tecon.github.io/"

BLACK = "rgb(15, 20, 25)"
BLACK_ALPHA = "rgba(15, 20, 25, {})"


# In[2]:


def get_last_known_slot():
    with open(FOLDER + "last_known_slot.txt", "r") as f:
        LAST_KNOWN_SLOT = int(f.read().strip())
    return LAST_KNOWN_SLOT

def get_timestamp_of_slot(slot):
    date = 1654824023 + (slot-int(4e6))*12
    date = datetime.strftime(datetime.utcfromtimestamp(date), "%Y-%m-%d, %I:%M %p") + " +UTC"
    return date

def create_total_share_chart():
    df = pd.read_csv(FOLDER + "share_all.csv", index_col = 0)
    fig = px.area(x=df["timestamp"], 
                  y=df["slot"], 
                  color=df["relay"], 
                  line_group=df["relay"], 
                  groupnorm="percent",
                 )
    fig.update_layout(
        title="Total Slot Share (cumulative)",
        xaxis_title="",
        yaxis_title="% of total slots",
        legend_title="Relay Provider",
        margin={"l":100},
        xaxis = dict(
           tickmode = 'array',
           tickvals = df["timestamp"].drop_duplicates()[::24],
           ticktext = [i.split(";")[0] for i in df["timestamp"].drop_duplicates()[::24]],
           gridcolor = "LightPink"
       ),
        font=dict(
            family="Courier New, monospace",
            size=18,  # Set the font size here
            color="RebeccaPurple"
        ),
        paper_bgcolor='#eee'
        
    )
    fig.update_traces( hoverinfo='skip', hovertemplate=None)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=BLACK_ALPHA.format(0.2))
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=BLACK_ALPHA.format(0.2))
    return fig
create_total_share_chart()


# In[3]:


def create_mevboost_share_chart():
    df = pd.read_csv(FOLDER + "share_mevboost.csv", index_col = 0)
    fig = px.area(df,x=df["timestamp"], 
                  y=df["slot"], 
                  color=df["relay"], 
                  line_group=df["relay"], 
                  groupnorm="percent",
                  hover_data={'timestamp':False, 
                             'relay': False,
                             'slot':False
                            }
                 )
    fig.update_layout(
        title="MEV-Boosted Slot Share (cumulative)",
        xaxis_title="",
        yaxis_title="% of MEV-boosted slots",
        legend_title="Relay Provider",
        margin={"l":100},
        
        #hovermode="x unified",
        
        xaxis = dict(
           tickmode = 'array',
           tickvals = df["timestamp"].drop_duplicates()[::24],
           ticktext = [i.split(";")[0] for i in df["timestamp"].drop_duplicates()[::24]]
        ),
        font=dict(
            family="Courier New, monospace",
            size=18,  # Set the font size here
            color="RebeccaPurple"
        ),
        # hoverlabel=dict(
        #    bgcolor="rgba(255, 255, 255, 0.1)",
        #    font_size=14,
        #    font_family="Rockwell"
        #)
        paper_bgcolor='#eee'

    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=BLACK_ALPHA.format(0.2))
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=BLACK_ALPHA.format(0.2))
    fig.update_traces( hoverinfo='skip', hovertemplate=None)
    
    return fig
create_mevboost_share_chart()


# In[4]:


def create_pie_charts():
    df = pd.read_csv(FOLDER + "pie_total.csv")
    df2 = pd.read_csv(FOLDER + "pie_mevboost.csv")
    fig = make_subplots(rows=1, cols=2,  subplot_titles=("Total block market\n", "MEV-Boosted block market\n"), specs=[[{"type": "pie"}, {"type": "pie"}]])

    figure1 = px.pie(df, values='slot', names='builder_pubkey', hole=.3,
                 hover_data=['slot'])
    figure2 = px.pie(df2, values='block_hash', names='builder_pubkey', hole=.3,
                 hover_data=['block_hash'])
    
    

    for i, figure in enumerate([figure1,figure2]):
        for trace in range(len(figure["data"])):
            fig.append_trace(figure["data"][trace], row=1, col=i+1)

    fig.update_layout(
        uniformtext_minsize=18, 
        uniformtext_mode='hide',
        title="MEV-Boost <b>Builders</b> Market\n",
        font=dict(
                family="Courier New, monospace",
                size=18,  # Set the font size here
                color="RebeccaPurple"
            ),
    )
    fig.update_annotations(font_size=18)
    fig.update_traces(hovertemplate=None,hoverinfo='label+value',textposition='inside',textinfo='percent', 
                      textfont_size=12, hoverlabel=dict(font=dict(color='rgb(15, 20, 25)')),
                      marker=dict(line=dict(color=BLACK, width=2)), 
                      textfont=dict(color=BLACK))
    
    fig.layout.annotations[1].update(y=1.05)
    fig.layout.annotations[0].update(y=1.05)
    return fig

fig = create_pie_charts()
fig.show()


# In[5]:


def create_pie_relay_charts():
    df = pd.read_csv(FOLDER + "pie_total_relay.csv")
    df2 = pd.read_csv(FOLDER + "pie_mevboost_relay.csv")
    fig = make_subplots(rows=1, cols=2,  subplot_titles=("Total block market\n", "MEV-Boosted block market\n"), specs=[[{"type": "pie"}, {"type": "pie"}]])

    figure1 = px.pie(df, values='slot', names='relay', hole=.3,
                 hover_data=['slot'])
    figure2 = px.pie(df2, values='block_hash', names='relay', hole=.3,
                 hover_data=['block_hash'])
    
    for i, figure in enumerate([figure1,figure2]):
        for trace in range(len(figure["data"])):
            fig.append_trace(figure["data"][trace], row=1, col=i+1)

    fig.update_layout(
        uniformtext_minsize=18, 
        uniformtext_mode='hide',
        title="MEV-Boost <b>Relays</b> Market\n",
        font=dict(
                family="Courier New, monospace",
                size=18,  
                color="RebeccaPurple"
            ),
        paper_bgcolor='rgba(255, 255, 255, 0.5)',
    )

    fig.update_traces(hovertemplate=None,hoverinfo='label+value',textposition='inside',textinfo='percent', 
                      textfont_size=25, hoverlabel=dict(font=dict(color=BLACK)),
                      marker=dict(line=dict(color=BLACK, width=2)), textfont=dict(color=BLACK))
    fig.update_annotations(font_size=18)
    fig.layout.annotations[1].update(y=1.05)
    fig.layout.annotations[0].update(y=1.05)
    return fig

fig = create_pie_relay_charts()
fig.show()


# In[6]:


def create_sankey():
    df = pd.read_csv(FOLDER + "sankey_source_target_value.csv")
    df2 = pd.read_csv(FOLDER + "sankey_colors.csv")
    df3 = pd.read_csv(FOLDER + "sankey_link_colors.csv")
    df4 = pd.read_csv(FOLDER + "builder_labels.csv")
    df5 = pd.read_csv(FOLDER + "relay_labels.csv")

    fig = go.Figure(data=[go.Sankey(
        textfont=go.sankey.Textfont(size=15, color="black", family="Courier New"),
        node = dict(
          pad = 20,
          thickness = 20,
          line = dict(color = BLACK, width = 0.5),
          label = df4["labels"].tolist() + df5["labels"].tolist(),
          color = df2["colors"]
        ),
        link = dict(
          source = df["source"],
          target = df["target"],
          value = df["value"],
        color = df3["link_colors"])
    )])

    fig.update_layout(title_text="Builders --> Relays",
                      #paper_bgcolor='#eee',
                      font=dict(
                                family="Courier New, monospace",
                                size=18,  # Set the font size here
                                color="RebeccaPurple"
                               ), autosize=False, width=800, height=800,)
    return fig
fig = create_sankey()
fig.show()


# In[7]:


def create_avg_proposer_payment():
    df = pd.read_csv(FOLDER + "avg_proposer_val_gas.csv")
    fig = px.scatter(x=df["timestamp"], 
                      y=df["value"], 
                      color=df["relay"], 
                      size=df["value"].apply(lambda x: 80+(x-min(df["value"]))/(max(df["value"])-min(df["value"]))*100), 
                      range_y=[0.02,1],
                      log_y=True,
                     )
    fig.update_layout(
        title="Daily avg. Proposer Payments per block",
        xaxis_title="",
        yaxis_title="ETH",
        legend_title="Relay Provider",
        margin={"l":100},
        hovermode="closest",
        yaxis_tickformat = "0.1r",
        yaxis = dict(
            tickmode = 'array',
            tickvals = [0.02, 0.06, 0.1, 0.2, 0.3, 0.4, 0.6, 0.8, 1],
        ),
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
        ),
        #paper_bgcolor='#eee'
    )
    fig.update_traces(hovertemplate = '<b>Avg. payment: %{y:.2f} ETH</b>',)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=BLACK_ALPHA.format(0.2))
    return fig
    
create_avg_proposer_payment()


# In[8]:


def create_potential_mev_chart():
    df = pd.read_csv(FOLDER + "potentialmev.csv")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp"], 
                             y=df["reward"], 
                             fill='tozeroy',
                             name='Block reward (eth_1)',
                             fillpattern={"shape":"/"},
                             hoverinfo = "none"
                            )  
                 )

    fig.add_trace(go.Scatter(x=df["timestamp"], 
                             y=df["value"], 
                             fill='tonexty', 
                             name='Potential MEV',
                             fillpattern={"shape":"+", "fgcolor":"#000"},
                             hovertemplate =
                                '<b>%{text} ETH</b>',
                                text = [str(round(i,2)) for i in df["value"]-df["reward"]],
                                 showlegend=True
                             )) 

    fig.add_trace(go.Scatter(x=df["timestamp"], 
                             y=df["value"], 
                             fill='tonexty', 
                             line = {"color":"rgba(14, 116, 0, 1)"},
                             name='Proposer Payment',
                             fillpattern={"shape":"+", "fgcolor":"#000"},
                             hoverinfo = "none"
                            )) 

    fig.update_layout(
        title="Daily Proposer Payments ~ Block Rewards",
        xaxis_title="",
        yaxis_title="ETH",
        #legend_title="Relay Provider",
        margin={"l":100},

        hovermode="x unified",

        font=dict(
            family="Courier New, monospace",
            size=18,  # Set the font size here
            color="RebeccaPurple"
        ),
         hoverlabel=dict(
           # bgcolor="rgba(255, 255, 255, 0.1)",
            font_size=14,
            font_family="Rockwell"
        ),
        paper_bgcolor='#eee'

    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0, 0, 0, 0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0, 0, 0, 0.2)')
    return fig
create_potential_mev_chart()


# In[9]:


LAST_SLOT = get_last_known_slot()
LAST_TS = get_timestamp_of_slot(LAST_SLOT)
app = dp.Report(
    '<h1 style="text-align:center;font-family:Georgia;font-variant:small-caps;font-size: 60px;color:#0F1419;">MEV-Boost Dashboard</h1>',
    "<div style ='font-family: Georgia;color:#0F1419;'>Lastest known slot: {:,.0f} ({})</div>".format(LAST_SLOT, LAST_TS),
    create_pie_relay_charts(),
    create_total_share_chart(),
    create_pie_charts(),
    create_mevboost_share_chart(),
    create_avg_proposer_payment(),
    create_potential_mev_chart(),
    create_sankey(),
    '<div style ="font-family: Courier New, monospace;">built with 🖤 by <a href="https://github.com/Nerolation">Toni Wahrstätter</a></div>',   
)
app.save(path = GITFOLDER + "index.html",
        formatting=dp.ReportFormatting(
        bg_color="#EEE"
    ))
log("charts sucessfully created")

