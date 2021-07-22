from binance import Client
import asyncio
from binance import AsyncClient, BinanceSocketManager
from binance.enums import *
import pymongo
import datetime


api_key = 'YP4d181tEnrrwuYe8mvtUW8KDfJPHu4ff95aZ0uaPqcbA4zQXxozF9OphoeSxYce'
api_secret = 'MnlDoLWYGhguf7WVfUfgnptpVd6fcCgph2Sgvx3NWQmNjgKQDFvukjuph3OHupwS'

def mainhistory():
    client = Client(api_key, api_secret)

    res = client.get_historical_klines_generator('BTCUSDT', Client.KLINE_INTERVAL_1HOUR,1451624401,klines_type=HistoricalKlinesType.SPOT)
    print(res)
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["crypto"]
    mycol = mydb["cryptodataBTC"]
    for i in res:
        print(i)

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

        mydoc = mycol.find({"Open time" : datetime.datetime.fromtimestamp((i[0])/1000)})
        count = 0
        for x in mydoc:
            count = count + 1

        if count == 0:
            x = mycol.insert_one(jsn)

        print("\n")


async def main():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    ts = bm.kline_socket('BTCUSDT', interval=KLINE_INTERVAL_1MINUTE)
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["crypto"]
    mycol = mydb["cryptodataBTC"]
    async with ts as tscm:
        while True:
            res = await tscm.recv()
            print(res["k"]["t"])
            print(datetime.datetime.now())
            print(datetime.datetime.fromtimestamp((res["k"]["t"])/1000))
            # x = mycol.insert_one(res)

            jsn = {}
            jsn["Open time"] = datetime.datetime.fromtimestamp((res["k"]["t"])/1000)
            jsn["Open"] = res["k"]["o"]
            jsn["High"] = res["k"]["h"]
            jsn["Low"] = res["k"]["l"]
            jsn["Close"] = res["k"]["c"]
            jsn["Volume"] = res["k"]["v"]
            jsn["Close time"] = datetime.datetime.fromtimestamp((res["k"]["T"])/1000)
            jsn["Quote asset volume"] = res["k"]["q"]
            jsn["Number of trades"] = res["k"]["v"]
            jsn["Taker buy base asset volume"] = res["k"]["V"]
            jsn["Taker buy quote asset volume"] = res["k"]["Q"]

            print(jsn)

            mydoc = mycol.find({"Open time": datetime.datetime.fromtimestamp((res["k"]["t"])/1000)})

            count = 0
            for x in mydoc:
                count = count + 1

            if count == 0:
                x = mycol.insert_one(jsn)



    await client.close_connection()

if __name__ == "__main__":

    # mainhistory()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())