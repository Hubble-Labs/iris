Iris
=====
Repository for running Iris nodes based on Chainlink's latest node client software.

Installing and Running an Iris node
-----

```
git clone --recurse-submodules -j8 https://github.com/Hubble-Labs/iris.git
cd iris/external-adapter
python3 -m venv env
source env/bin/activate
pip install -r req.txt
```

## Setup Chainlink
Follow these instructions to set up a chainlink docker node: https://docs.chain.link/docs/running-a-chainlink-node/
```
docker run -p 6688:6688 -v ~/YOUR_FOLDER_NAME:/chainlink -it --env-file=.env smartcontract/chainlink:<version> local n
```

It is technically possible to run a node from source but its not worth the trouble at this stage.
