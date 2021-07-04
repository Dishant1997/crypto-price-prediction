import asyncio
from binance import AsyncClient, BinanceSocketManager
from binance.enums import *
import pymongo
import time
import datetime
async def main():
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    # start any sockets here, i.e a trade socket
    ts = bm.kline_socket('BNBBTC', interval=KLINE_INTERVAL_1MINUTE)
    # then start receiving messages

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["crypto"]
    mycol = mydb["crypto1m"]
    async with ts as tscm:
        while True:
            res = await tscm.recv()
            print(res)
            print(datetime.datetime.now())
            x = mycol.insert_one(res)
            time.sleep(60)

    await client.close_connection()

if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())