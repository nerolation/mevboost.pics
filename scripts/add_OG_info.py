GITFOLDER = "./wu-tecon.github.io/"

with open("index.html", "r") as file:
    f = file.read()
OG_STUFF = ' <meta charset="UTF-8" />\n<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:site" content="@nero_ETH">\n<meta name="twitter:title" content="MEV-Boost Relay API Dashboard">\n<meta name="twitter:description" content="Selected comparative visualizations on MEV-Boost and Proposer Builder Separation on Ethereum.">\n<meta name="twitter:image" content="https://mevboost.toniwahrstaetter.com/pv.png">\n<meta property="og:title" content=MEV-Boost Relay API Dashboard>\n<meta property="og:site_name" content=toniwahrstaetter.com>\n<meta property="og:url" content=mevboost.toniwahrstaetter.com>\n<meta property="og:description" content="Selected comparative visualizations on MEV-Boost and Proposer Builder Separation on Ethereum." >\n<meta property="og:type" content=website>\n<link rel="shortcut icon" href="https://mevboost.toniwahrstaetter.com/logo.png" />\n<meta property="og:image" content=https://mevboost.toniwahrstaetter.com/pv.png>\n<meta property="og:image" content=https://mevboost.toniwahrstaetter.com/pv2.png>'
f = f.replace('<meta charset="UTF-8" />\n', OG_STUFF)
with open("index.html", "w") as file:
    file.write(f)
