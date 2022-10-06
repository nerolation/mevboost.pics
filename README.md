# mevboost.pics
[mevboost.pics](https://mevboost.pics) provides visualizations on MEV-Boost.

[mev-boost twitter bot ](https://twitter.com/mevproposerbot) throws alerts for high proposer payment.

---





This repo contains the following scripts:
* **parse_data_api.py** is used to collect data (the [mev-boost relays](https://flashbots.notion.site/Relay-API-Spec-5fb0819366954962bc02e81cb33840f5) is used to collect the data).
* **enrich_data.py** is used to add additional information (block_nr, fee_recipient and transaction data) to the parsed data.
* **add_block_rewards.py** is used to add the reward/block to the data set.
* **dataprep.py** is used to prepare the data for plotting.
* **chartprep.py** is used to create the final html file with the charts.
* **twitterbot.py** continously scans the collected data for high proposer payments and tweets about it.

