# Iris
Repository for running Iris nodes based on Chainlink's latest node client software.

## Installing and Running an Iris node

### Build Chainlink

1. [Install Go 1.18](https://golang.org/doc/install), and add your GOPATH's [bin directory to your PATH](https://golang.org/doc/code.html#GOPATH)
   - Example Path for macOS `export PATH=$GOPATH/bin:$PATH` & `export GOPATH=/Users/$USER/go`
2. Install [NodeJS](https://nodejs.org/en/download/package-manager/) & [Yarn](https://yarnpkg.com/lang/en/docs/install/). See the current version in `package.json` at the root of this repo under the `engines.node` key.
   - It might be easier long term to use [nvm](https://nodejs.org/en/download/package-manager/#nvm) to switch between node versions for different projects. For example, assuming $NODE_VERSION was set to a valid version of NodeJS, you could run: `nvm install $NODE_VERSION && nvm use $NODE_VERSION`
3. Install [Postgres (>= 11.x)](https://wiki.postgresql.org/wiki/Detailed_installation_guides).
   - You should [configure Postgres](https://www.postgresql.org/docs/12/ssl-tcp.html) to use SSL connection (or for testing you can set `?sslmode=disable` in your Postgres query string).
4. Ensure you have Python 3 installed (this is required by [solc-select](https://github.com/crytic/solc-select) which is needed to compile solidity contracts)
5. Download Chainlink: `git clone https://github.com/smartcontractkit/chainlink && cd chainlink`
6. Build and install Chainlink: `make install`
   - If you got any errors regarding locked yarn package, try running `yarn install` before this step
   - If `yarn install` throws a network connection error, try increasing the network timeout by running `yarn install --network-timeout 150000` before this step
7. Run the node: `chainlink help`

#### Common Issues:
1. If your shell/terminal doesn't recognize that you downloaded a new package or made a change to a file, make sure to reset your terminal for it to see the change. Alternavily you could use the `source FILE_NAME` command in your terminal on bash/zsh shells.


### Configure Chainlink

1. In your terminal create an enviroment file by entering `nano .env`.
2. Paste this into your new `.env` file:
   ```bash
   ROOT=/chainlink
   LOG_LEVEL=debug
   ETH_CHAIN_ID=4
   CHAINLINK_TLS_PORT=0
   SECURE_COOKIES=false
   ALLOW_ORIGINS=*
   ETH_URL=CHANGEME
   DATABASE_URL=postgresql://$USERNAME:$PASSWORD@$SERVER:$PORT/$DATABASE
   ```

NOTE: Special considerations must be made when configuring your node based on what Ethereum chain you're using, the URL to your Ethereum node, URL to your database, etc.
Detailed instructions can be found here: https://docs.chain.link/docs/running-a-chainlink-node

### Run Chainlink Node

1. Make sure your Chainlink `.env` file and all other components are configured correctly 
2. Start the node with `chainlink node start`.
