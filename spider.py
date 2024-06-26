from store import AdvertisementStore
from threading import Thread, current_thread, Lock
from parsers.mobile_de import MobileDeParser
import time
from db_connection import get_connection
from env import Env


lock = Lock()
lock2 = Lock()

def worker():
    parser = MobileDeParser()
    connection = get_connection()
    store = AdvertisementStore(connection=connection)
    branch = current_thread().name + ' : '
    
    while True:
        start1 = time.time()
        with lock:
            request = store.get_tasks()
        get_task_time = time.time() - start1
        if not request:
            output = branch + 'No jobb'
            print(output)
            time.sleep(10)
            store.connection.commit()
            continue
        scrap_time = 0
        updates = []
        for r in request:
            output = branch + r + ' '
            start = time.time()
            request = parser.update_info(r)
            if not request:
                continue
            updates.append(request)
            output += ' : ' + request.status
            scrap_iter_time = time.time()
            print(output)
            scrap_time += scrap_iter_time - start
        finish1 = time.time()
        with lock2:
            store.update_lead(updates)
        finish = time.time()
        store_time = finish - finish1
        print (current_thread().name + ': ' + f"Time: {finish - start1}: get task: {get_task_time}, scrap:{scrap_time}, store: {store_time}")


if __name__ == '__main__':

    for i in range(Env.THREADS):
         t = Thread(target=worker)
         t.name = 'Spider No ' + str(i)
         t.start()
         time.sleep(1)