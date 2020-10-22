# coding=utf-8
import ccxt
import time
import json
import os.path
from asciimatics.screen import Screen

COLOUR_BLACK = 0
COLOUR_RED = 1
COLOUR_GREEN = 2
COLOUR_YELLOW = 3
COLOUR_BLUE = 4
COLOUR_MAGENTA = 5
COLOUR_CYAN = 6
COLOUR_WHITE = 7

exchange = ccxt.kraken() # Can be changed to bittrex, kraken, or something else
exchange_markets = exchange.load_markets()
start_balance = 1000
maker_fee = 0.26 / 100  # TODO use real fee maker fee, market order
CACHE_PAIRS = False
USE_LAST_PRICE_FOR_CALC = False # if True using last price in the exchange, else if False using bid/ask prices

class Arbitrage():
    percent = 0
    text = "No info"
    key = ""
    color = COLOUR_WHITE

    def __init__(self, percent, text, key):
        self.percent = percent
        self.text = text
        self.key = key
        if percent < 0:
            self.color = COLOUR_RED
        elif percent <= 1:
            self.color = COLOUR_YELLOW
        elif percent > 1:
            self.color = COLOUR_GREEN

def save_obj(name, data):
    # Serialize data into file:
    json.dump(data, open(name + ".json", 'w'))

def read_obj(name):
    # Read data from file:
    data = json.load(open(name + ".json"))
    return data

def calculate_triangular_arbitrage(tri_pairs):
    price1, price1_original, buy1_text = get_pair_price(tri_pairs['pair1']['buy'], tri_pairs['pair1']['name'])

    price2, price2_original, buy2_text = get_pair_price(tri_pairs['pair2']['buy'], tri_pairs['pair2']['name'])

    price3, price3_original, buy3_text = get_pair_price(tri_pairs['pair3']['buy'], tri_pairs['pair3']['name'])

    balance, fee, profit_percent = calc_balance(price1, price2, price3)

    key, line = format_line(balance, buy1_text, buy2_text, buy3_text, fee, price1_original, price2_original, price3_original, profit_percent, tri_pairs)
    return Arbitrage(profit_percent, line, key)

def get_pair_price(is_buy, pair_name):
    buy = "Sell"
    if is_buy:
        buy = "Buy"
        if USE_LAST_PRICE_FOR_CALC:
            price = exchange.fetch_ticker(pair_name)['last'] #ask
        else:
            price = exchange.fetch_ticker(pair_name)['ask'] #ask
        price_original = price
        if price == 0:
            return
        price = 1 / price
    else:
        if USE_LAST_PRICE_FOR_CALC:
            price = exchange.fetch_ticker(pair_name)['last'] #ask
        else:
            price = exchange.fetch_ticker(pair_name)['bid'] #ask
        price_original = price
    return price, price_original, buy

def calc_balance(price1, price2, price3):
    balance_no_fee = start_balance * price1 * price2 * price3
    balance = start_balance * price1
    fee = balance * maker_fee
    balance = balance - fee
    balance = balance * price2
    fee = balance * maker_fee
    balance = balance - fee
    balance = balance * price3
    fee = balance * maker_fee
    balance = balance - fee
    profit = (balance - start_balance) / start_balance * 100
    fee = balance_no_fee - balance
    return balance, fee, profit


def format_line(balance, buy1, buy2, buy3, fee, price1org, price2org, price3org, profit, tri_pairs):
    key = tri_pairs['pair1']['name'] + tri_pairs['pair2']['name'] + tri_pairs['pair3']['name']
    line = '{} {} {:011.6f}\t{} {} {:011.6f}\t{} {} {:011.8f}\t{:011.6f}\t\t{:011.6f}\t\t{:011.6f}\t\t{:.2f}%' \
        .format(buy1, tri_pairs['pair1']['name'].rjust(12), price1org,
                buy2, tri_pairs['pair2']['name'].rjust(12), price2org,
                buy3, tri_pairs['pair3']['name'].rjust(12), price3org,
                start_balance, balance, fee, profit)
    return key, line


def find_all_pairs(filter_pair1=[], filter_pair2 = []):
    all_pairs = []
    for pair1 in exchange_markets:
        if "/" not in pair1:
            continue
        if not pair1 in filter_pair1 and len(filter_pair1) > 0:
            continue
        step1cur1 = pair1.split('/')[0]
        step1cur2 = pair1.split('/')[1]
        step1exit = step1cur2
        step1begin = step1cur1
        buy1 = False
        for pair2 in exchange_markets:
            # print(pair2)
            if pair1 == pair2:
                continue
            if not pair2 in filter_pair2 and len(filter_pair2) > 0:
                continue
            if "/" not in pair2:
                continue
            step2cur1 = pair2.split('/')[0]
            step2cur2 = pair2.split('/')[1]
            buy2 = True
            step2exit = step2cur1
            if step1exit == step2cur1:
                buy2 = False
                step2exit = step2cur2
            elif step1exit == step2cur2:
                buy2 = True
                step2exit = step2cur1

            if step1exit != step2cur1 and step1exit != step2cur2:
                continue
            for pair3 in exchange_markets:
                # print(pair3)
                if "/" not in pair3:
                    continue
                if pair2 == pair3:
                    continue
                step3cur1 = pair3.split('/')[0]
                step3cur2 = pair3.split('/')[1]
                buy3 = True
                step3exit = step3cur2
                # BTC/BCH
                if step2exit == step3cur1:
                    buy3 = False
                    step3exit = step3cur2
                elif step2exit == step3cur2:
                    buy3 = True
                    step3exit = step3cur1
                if step2exit != step3cur1 and step2exit != step3cur2:
                    continue
                if step1begin != step3exit:
                    continue

                tri_pairs = {'pair1': {'name': pair1, 'buy': buy1}, 'pair2': {'name': pair2, 'buy': buy2},
                             'pair3': {'name': pair3, 'buy': buy3}}
                all_pairs.append(tri_pairs)
    save_obj('cache', all_pairs)
    return all_pairs

def demo(screen, all_arbitrages):
    if not os.path.exists("cache.json") or not CACHE_PAIRS:
        pairs = find_all_pairs()
    else:
        pairs = read_obj('cache')
    for tri_pairs in pairs:
        new_arb = calculate_triangular_arbitrage(tri_pairs)
        time.sleep(0.1)
        if new_arb == None:
            continue
        all_arbitrages = list(filter(lambda x: x.key != new_arb.key, all_arbitrages))
        all_arbitrages.append(new_arb)
        all_arbitrages.sort(key=lambda x: x.percent, reverse=True)
        row = 1
        screen.clear()
        screen.print_at('PAIR1\t\t\t\tPAIR2\t\t\t\tPAIR3\t\t\t\tSTART\t\t\tPROFIT\t\t\tFEE\t\t\tPERCENT',
                        0, 0,
                        COLOUR_WHITE)
        for cur_arb in all_arbitrages:
            screen.print_at(cur_arb.text,
                0, row,
                cur_arb.color)
            screen.refresh()
            row += 1
            ev = screen.get_key()
            if ev in (ord('Q'), ord('q')):
                print("Quit")
                return None
        time.sleep(0.5)
    return all_arbitrages


def loop(screen):
    all_arbitrages = []
    while True:
        all_arbitrages = demo(screen, all_arbitrages)
        if all_arbitrages == None:
            return
        else:
            print(len(all_arbitrages))
            time.sleep(1)

if __name__ == "__main__":
    Screen.wrapper(loop)
