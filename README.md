# Iris
Repository for running Iris nodes based on Chainlink's latest node client software.

## Build Chainlink

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
