# coding=utf-8
import ccxt
import pprint

def printsep():
    print("==========================")

pp = pprint.PrettyPrinter(indent=4)

bittrex = ccxt.bittrex()
kraken = ccxt.kraken()

bittrex_markets = bittrex.load_markets()
kraken_markets = kraken.load_markets()

# pp.pprint(bittrex_markets['LTC/USD'])
# print("=========================")
# pp.pprint(kraken.load_markets()['LTC/USD'])

for pair in bittrex_markets:

    price1 = bittrex.fetch_ticker(pair)['last']
    if not pair in kraken_markets:
        # print("Not available in second exchange")
        continue
    price2 = kraken.fetch_ticker(pair)['last']
    arbitrage = 0
    if price1 < price2:
        arbitrage = (price2 - price1)/price1*100
        buy = "Buy on Bittrex transfer to Kraken and sell"
    else:
        arbitrage = (price1 - price2)/price2*100
        buy = "Buy on Kraken transfer to Bittrex and sell"
    if arbitrage < 5:
        continue
    printsep()
    print("Pair:", pair, buy)
    print("Bittrex:", price1, "Kraken:", price2)
    print("Arbitrage:", "{:.2f}".format(arbitrage), "%")
