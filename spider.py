from store import AdvertisementStore
from threading import Thread, current_thread, Lock
from parsers.mobile_de import MobileDeParser
import time
from model import UpdateAdRequest
from db_connection import get_connection

lock = Lock()

def worker():
    parser = MobileDeParser()
    connection = get_connection()
    store = AdvertisementStore(connection=connection)

    
    while True:
        start1 = time.time()
        with lock:
            request = store.get_tasks()
        get_task_time = time.time() - start1
        if not request:
            print('No jobb')
            time.sleep(10)
            store.connection.commit()
            continue
        scrap_time = 0
        store_time = 0
        updates = []
        for r in request:
            output = current_thread().name + ': ' + r + ' '
            start = time.time()
            request = parser.update_info(r)
            updates.append(request)
            output += ' : ' + request.status
            scrap_iter_time = time.time()
            store_iter_time = time.time()
            print(output)
            scrap_time += scrap_iter_time - start
            store_time += store_iter_time - scrap_iter_time
        store.update_lead(updates)
        finish = time.time()
        print (current_thread().name + ': ' + f"Time: {finish - start1}: get task: {get_task_time}, scrap:{scrap_time}, store: {store_time}")


if __name__ == '__main__':
    num_workers = 4

    for i in range(num_workers):
         t = Thread(target=worker)
         t.name = 'Spider No ' + str(i)
         t.start()
         time.sleep(1)