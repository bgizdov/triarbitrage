### Python script for finding arbitrage opportunities on crypto exchanges

#### Installation

Requires **ccxt** and **ascimatics**

`pip install -r requirements.txt`

#### 1. Arbitrage between two exchanges

`python3 two_exchanges_arbitrage.py`

#### 2. A triangular arbitrage
It is using not the best price, but current bid/ask price if there is 
arbitrage opportunity to be filled very fast.

`python3 triangular_arbitrage.py`


#### Screenshots

![Two exchanges arbitrage](https://github.com/bgizdov/triarbitrage/blob/master/images/2arb.png?raw=true)

![Triangular arbitrage](https://github.com/bgizdov/triarbitrage/blob/master/images/3arb.png?raw=true)
