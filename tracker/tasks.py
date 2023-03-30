from celery import shared_task
from yahoo_fin.stock_info import *
from threading import Thread
import queue
from channels.layers import get_channel_layer
import asyncio
import simplejson as json

@shared_task(bind=True)
def update_stocks(self, selected_stocks):
    data = {}
    all_stocks = tickers_nifty50()
    for i in selected_stocks:
        if i in all_stocks:
            pass
        else:
            selected_stocks.remove(i)
        
    n_threads = len(selected_stocks)
    thread_list = []
    que = queue.Queue()
    for i in range(n_threads):
        thread = Thread(target=lambda q, arg1:q.put({selected_stocks[i]: json.loads(json.dumps(get_quote_table(arg1), ignore_nan=True))}) , args=(que, selected_stocks[i]))
        thread_list.append(thread)
        thread_list[i].start()

    for thread in thread_list:
        thread.join()

    while not que.empty():
        result = que.get()
        data.update(result)

    # Send data to group
    channel_layer = get_channel_layer()
    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)
    loop.run_until_complete(channel_layer.group_send("stock_track", {#type:ignore 
        'type': 'send_update',
        'message': data,
    }))


    return 'Done'