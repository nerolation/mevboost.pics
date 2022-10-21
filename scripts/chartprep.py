#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import datapane as dp
from plotly.subplots import make_subplots
from datetime import datetime
from logger import log 

FOLDER = "./chart_data/"
GITFOLDER = "./wu-tecon.github.io/"

BLACK = "rgb(15, 20, 25)"
BLACK_ALPHA = "rgba(15, 20, 25, {})"


# In[ ]:


def get_last_known_slot():
    with open("./data/last_known_slot.txt", "r") as f:
        LAST_KNOWN_SLOT = int(f.read().strip())
    return LAST_KNOWN_SLOT

def get_timestamp_of_slot(slot):
    date = 1654824023 + (slot-int(4e6))*12
    date = datetime.strftime(datetime.utcfromtimestamp(date), "%Y-%m-%d, %I:%M %p") + " +UTC"
    return date

def create_total_share_chart():
    df = pd.read_csv(FOLDER + "share_all.csv", index_col = 0)
    df["relay"] = df["relay"].apply(lambda x: x[0].upper()+x[1:]) 
    time_axis = df["timestamp"].drop_duplicates()[::int(len(df["timestamp"].drop_duplicates())/10)]
    fig = px.area(x=df["timestamp"], 
                  y=df["slot"], 
                  color=df["relay"], 
                  line_group=df["relay"], 
                  groupnorm="percent",
                 )
    fig.update_layout(
        title='<span style="font-size: 32px;font-weight:bold;">Total Slot Share (cumulative)</span>',
        xaxis_title="",
        yaxis_title="% of total slots",
        legend_title="Relay Provider",
        margin={"l":100},
        xaxis = dict(
           tickmode = 'array',
           tickvals = time_axis,
           ticktext = [i.split(";")[0] for i in time_axis],
           gridcolor = "LightPink",
       ),
        font=dict(
            family="Courier New, monospace",
            size=18,  # Set the font size here
            color="RebeccaPurple"
        ),
        paper_bgcolor='#eee',
        yaxis=dict(fixedrange =True)
        
    )
    fig.update_traces( hoverinfo='skip', hovertemplate=None)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=BLACK_ALPHA.format(0.2))
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=BLACK_ALPHA.format(0.2))
    return fig
create_total_share_chart()


# In[ ]:


def create_mevboost_share_chart():
    df = pd.read_csv(FOLDER + "share_mevboost.csv", index_col = 0)
    df["relay"] = df["relay"].apply(lambda x: x[0].upper()+x[1:]) 
    time_axis = df["timestamp"].drop_duplicates()[::int(len(df["timestamp"].drop_duplicates())/10)]
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
        title='<span style="font-size: 32px;font-weight:bold;">MEV-Boosted Slot Share (cumulative)</span>',
        xaxis_title="",
        yaxis_title="% of MEV-boosted slots",
        legend_title="Relay Provider",
        margin={"l":100},
        
        #hovermode="x unified",
        
        xaxis = dict(
           tickmode = 'array',
           tickvals = time_axis,
           ticktext = [i.split(";")[0] for i in time_axis]
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
        paper_bgcolor='#eee',
        yaxis=dict(fixedrange =True)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=BLACK_ALPHA.format(0.2))
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=BLACK_ALPHA.format(0.2))
    fig.update_traces( hoverinfo='skip', hovertemplate=None)
    
    return fig
create_mevboost_share_chart()


# In[ ]:


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
        uniformtext_minsize=20, 
        uniformtext_mode='hide',
        title=dict(
            text='MEV-Boost <b>Builders</b> Market <span style="font-size:18px;">(last 14 days)</span><br> ',
            font=dict(
                family="Courier New, monospace",
                size=30,
                color='RebeccaPurple'
            )),
        font=dict(
                family="Courier New, monospace",
                size=18,  # Set the font size here
                color="RebeccaPurple"
            ),
    )
    fig.update_traces(hovertemplate="<b>%{label}:<br>%{value:,.0f} blocks</b>",hoverinfo='label+value',
                      textposition='inside',texttemplate = "<b>%{percent}<b>", 
                      textfont_size=24, hoverlabel=dict(font=dict(color="#ffffff", size=22)),
                      marker=dict(line=dict(color=BLACK, width=2)), 
                      textfont=dict(color=BLACK))
    
    fig.layout.annotations[1].update(y=1.05)
    fig.layout.annotations[0].update(y=1.05)
    fig.update_annotations(font_size=20)

    return fig

fig = create_pie_charts()
fig.show()


# In[ ]:


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
        uniformtext_minsize=20, 
        uniformtext_mode='hide',
        title=dict(
            text='MEV-Boost <b>Relays</b> Market <span style="font-size:18px;">(last 14 days)</span><br> ',
            font=dict(
                family="Courier New, monospace",
                size=30,
                color='RebeccaPurple'
            )),
        font=dict(
                family="Courier New, monospace",
                size=18,  
                color="RebeccaPurple"
            ),
        paper_bgcolor='rgba(255, 255, 255, 0.5)',
    )

    fig.update_traces(hovertemplate="<b>%{label}:<br>%{value:,.0f} blocks</b>",hoverinfo='label+value',
                      textposition='inside',texttemplate = "<b>%{percent}<b>",
                      textfont_size=24, hoverlabel=dict(font=dict(color="#ffffff", size=22)),
                      marker=dict(line=dict(color=BLACK, width=2)), textfont=dict(color=BLACK))
    fig.update_annotations(font_size=20)
    fig.layout.annotations[1].update(y=1.05)
    fig.layout.annotations[0].update(y=1.05)
    return fig

fig = create_pie_relay_charts()
fig.show()


# In[ ]:


def create_sankey():
    df = pd.read_csv(FOLDER + "sankey_source_target_value.csv")
    df2 = pd.read_csv(FOLDER + "sankey_colors.csv")
    df3 = pd.read_csv(FOLDER + "sankey_link_colors.csv")
    df4 = pd.read_csv(FOLDER + "builder_labels.csv")
    df5 = pd.read_csv(FOLDER + "relay_labels.csv")

    fig = go.Figure(data=[go.Sankey(
        textfont=go.sankey.Textfont(size=15, color="black", family="Courier New"),
        node = dict(
          pad = 40,
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

    fig.update_layout(title_text='<span style="font-size: 32px;font-weight:bold;">Builders --> Relays</span>',
                      paper_bgcolor='#eee',
                      font=dict(
                                family="Courier New, monospace",
                                size=24,  # Set the font size here
                                color="RebeccaPurple"
                               ), autosize=False, width=800, height=1000,)
    return fig
fig = create_sankey()
fig.show()


# In[ ]:


def create_avg_proposer_payment():
    fig = go.Figure()
    df = pd.read_csv(FOLDER + "avg_proposer_val_gas.csv")
    df["relay"] = df["relay"].apply(lambda x: x[0].upper()+x[1:]) 
    for relay in ["Flashbots", "Bloxroute (max profit)", "Bloxroute (ethical)", 
                  "Bloxroute (regulated)", "Manifold", "Eden", "Blocknative"]:
        if relay in ["Flashbots", "Bloxroute (max profit)"]:
            show = True
        else:
            show = "legendonly"
        _df = df[df["relay"] == relay]
        fig.add_scatter(mode="markers",
                        x=_df["timestamp"], 
                        y=_df["value"], 
                        name = relay,
                        marker=dict(
                            
                            size=_df["value"].apply(lambda x: 20+(x-min(df["value"]))/(max(df["value"])-min(df["value"]))*10),
                        ),
                     visible = show,
                     )

    fig.update_layout(
        title='<span style="font-size: 32;font-weight:bold;">Daily avg. Proposer Payments per block</span>',
        xaxis_title="",
        yaxis_title='<span style="font-size: 32;">ETH</span>',
        legend_title="Relay Provider",
        margin={"l":100},
        hovermode="closest",
        yaxis_tickformat = "0.1r",
        yaxis = dict(
            type="log",
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
    fig.update_traces(hovertemplate = '<b>Avg. payment: %{y:.2f} ETH</b>',hoverlabel=dict(font=dict(color='#ffffff')))
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=BLACK_ALPHA.format(0.2))
    return fig
    
create_avg_proposer_payment()


# In[ ]:


pd.read_csv(FOLDER + "potentialmev.csv")


# In[ ]:





# In[ ]:


def create_potential_mev_chart():
    df = pd.read_csv(FOLDER + "potentialmev.csv")
    fig = go.Figure()
    time_axis = df["timestamp"][::int(len(df["timestamp"])/10)]
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
        title='<span style="font-size: 32px;font-weight:bold;">Daily Proposer Payments ~ Block Rewards</span>',
        xaxis_title="",
        yaxis_title='<span style="font-size: 32;">ETH</span>',
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
            font_size=18,
            font_family="Rockwell"
        ),
        paper_bgcolor='#eee',
        yaxis=dict(fixedrange =True),
        xaxis = dict(
           tickmode = 'array',
           tickvals = time_axis,
           ticktext = time_axis,
           gridcolor = "LightPink",
       )


    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0, 0, 0, 0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0, 0, 0, 0.2)')
    return fig
create_potential_mev_chart()


# In[ ]:


def create_builder_bar_chart():
    df = pd.read_csv(FOLDER + "builderbar.csv")
    fig = px.histogram(df, x='builder', y='value', color="frame",  barmode='group')
    fig.update_layout(
            title='<span style="font-size: 32;font-weight:bold;">Avg. Proposer Payment per Builder <span style="font-size:18px;">(Top 10)</span></span>',
            xaxis_title="",
            yaxis_title='<span style="font-size: 32;">ETH</span>',
            margin={"l":100},
            legend_title="",
            legend=dict(
                yanchor="top",
                y=0.98,
                xanchor="right",
                x=0.99,
                font=dict(
                    family="Courier New, monospace",
                    size=22,  
                    color="RebeccaPurple"
                ),
            ),
            xaxis = dict(
               gridcolor = BLACK_ALPHA.format(0.5),
               categoryorder = "total descending"
           ),
            yaxis = dict(
                gridcolor = BLACK_ALPHA.format(0.5),     
                fixedrange =True
               ),
            font=dict(
                family="Courier New, monospace",
                size=16,  
                color="RebeccaPurple"
            ),
            #paper_bgcolor='#eee'
        )
    fig.update_traces(hovertemplate = '<b>Avg. payment: %{y:.3f} ETH</b>',textposition='inside', 
                          hoverlabel=dict(font=dict(color='#ffffff')),
                          marker=dict(line=dict(color="#ffffff", width=2)), 
                          textfont=dict(color="#ffffff"), opacity=0.95)
    return fig
create_builder_bar_chart()


# In[ ]:


LAST_SLOT = get_last_known_slot()
LAST_TS = get_timestamp_of_slot(LAST_SLOT)
app = dp.Report(
    '<h1 style="text-align:center;font-family:Georgia;font-variant:small-caps;font-size: 70px;color:#0F1419;">MEV-Boost Dashboard</h1>',
    "<div style ='font-family: Georgia;color:#0F1419;font-size:22px'>Lastest known slot: {:,.0f} ({})<br>All charts have an interactive component: you can filter by a certain time frame or hide and show specific relays and builders.</div>".format(LAST_SLOT, LAST_TS),
    create_pie_relay_charts(),
    create_total_share_chart(),
    create_pie_charts(),
    create_mevboost_share_chart(),
    create_builder_bar_chart(),
    create_potential_mev_chart(),
    create_avg_proposer_payment(),
    create_sankey(),
    '<div><div style ="float:left;font-family: Courier New, monospace;">built with 🖤 by '\
    + '<a href="https://github.com/Nerolation">Toni Wahrstätter</a></div>'\
    +'<div style ="float:right;font-family: Courier New, monospace;">View Source on <a href="https://github.com/Nerolation/mevboost.pics">Github</a></div></div>',   
)
app.save(path = GITFOLDER + "index.html",
        formatting=dp.ReportFormatting(
        bg_color="#EEE"
    ))
log("charts sucessfully created")


# In[ ]:




