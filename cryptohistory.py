from binance import Client
import asyncio
from binance import AsyncClient, BinanceSocketManager
from binance.enums import *
import pymongo
import time
import datetime

api_key = 'YP4d181tEnrrwuYe8mvtUW8KDfJPHu4ff95aZ0uaPqcbA4zQXxozF9OphoeSxYce'
api_secret = 'MnlDoLWYGhguf7WVfUfgnptpVd6fcCgph2Sgvx3NWQmNjgKQDFvukjuph3OHupwS'

def main():
    client = Client(api_key, api_secret)

    res = client.get_historical_klines_generator('BTCUSDT', Client.KLINE_INTERVAL_1HOUR,1451624401,klines_type=HistoricalKlinesType.SPOT)
    print(res)
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["crypto"]
    mycol = mydb["crypto1hfor5"]
    for i in res:
        print(i)
        print()
        print()
        jsn = {}
        jsn["Open time"] = datetime.datetime.fromtimestamp((i[0])/1000)
        jsn["Open"] = float(i[1])
        jsn["High"] = float(i[2])
        jsn["Low"] = float(i[3])
        jsn["Close"] = float(i[4])
        jsn["Volume"] = i[5]
        jsn["Close time"] = datetime.datetime.fromtimestamp((i[6])/1000)
        jsn["Quote asset volume"] = i[7]
        jsn["Number of trades"] = i[8]
        jsn["Taker buy base asset volume"] = i[9]
        jsn["Taker buy quote asset volume"] = i[10]


        print(jsn)
        x = mycol.insert_one(jsn)

        print("\n")

if __name__ == "__main__":
    main()