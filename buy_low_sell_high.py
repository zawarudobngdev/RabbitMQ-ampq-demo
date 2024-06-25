import pickle
import random
import uuid


class Buyer(object):
    def __init__(self, client, qname, trend=5):
        self.holdings = {}
        self.cash = 10000.0
        self.history = {}
        self.qname = qname
        self.client = client
        self.qname = uuid.uuid4().hex
        self.trend = trend

    def decide_whether_to_buy_or_sell(self, quote):
        symbol, price, date, counter = quote
        print(f"Thinking about whether to buy or sell {symbol} at ${price:.2f}")

        if symbol not in self.history:
            self.history[symbol] = [price]
        else:
            self.history[symbol].append(price)

        if len(self.history[symbol]) >= self.trend:
            price_low = min(self.history[symbol][-self.trend:])
            price_max = max(self.history[symbol][-self.trend:])
            price_avg = sum(self.history[symbol][-self.trend:]) / self.trend
        else:
            price_low, price_max, price_avg = (-1, -1, -1)
            print(
                f"{self.trend - len(self.history[symbol])} quotes until we start deciding whether to buy or sell {symbol}"
            )

        if price_low == -1: return

        value = sum([self.holdings[symbol][0] * self.history[symbol][-1] for symbol in self.holdings.keys()])
        print(f"Net worth is ${self.cash:.2f} + ${value:.2f} = ${self.cash + value:.2f}")

        if symbol not in self.holdings:
            if price < 1.01 * price_low:
                shares_to_buy = random.choice([10, 15, 20, 25, 30])
                print(
                    f"I don't own any {symbol} yet, and the price is below the trending minimum of ${price_low:.2f} "
                    f"so I'm buying {shares_to_buy} shares."
                )
                cost = shares_to_buy * price
                print(f"Cost is ${cost:.2f}, cash is ${self.cash:.2f}")

                if cost < self.cash:
                    self.holdings[symbol] = (shares_to_buy, price, cost)
                    self.cash -= cost
                    print(f"Cash is now ${self.cash:.2f}")
                else:
                    print("Unfortunately, I don't have enough cash at this time.")
        else:
            if price > self.holdings[symbol][1] and price > 0.99 * price_max:
                print(f"+++++++ Price of {symbol} is higher than my holdings, so I'm going to sell!")
                sale_value = self.holdings[symbol][0] * price
                print(f"Sale value is ${sale_value:.2f}")
                print(f"Holdings value is ${self.holdings[symbol][2]:.2f}")
                print(f"Total net is ${sale_value - self.holdings[symbol][2]:.2f}")
                self.cash += sale_value
                print(f"Cash is now ${self.cash:.2f}")
                del self.holdings[symbol]

    def handle_pyamqplib_delivery(self, msg):
        self.handle(msg.channel, msg.delivery_info["delivery_tag"], msg.body)

    # def handle_pika_delivery(self, ch, method, header, body):
    #     self.handle(ch, delivery_tag, body)

    def handle(self, ch, delivery_tag, body):
        quote = pickle.loads(body)
        # print("New price for %s => %s at %s" % quote)
        ch.basic_ack(delivery_tag=delivery_tag)
        print(f"\nReceived message {quote[3]}")
        self.decide_whether_to_buy_or_sell(quote)

    def monitor(self):
        self.client.monitor(self.qname, self.handle_pyamqplib_delivery)
