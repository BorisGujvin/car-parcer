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
        start = time.time()
        with lock:
            request = store.get_old_tasks()
        if not request:
            print('No active ads')
            time.sleep(10)
            store.connection.commit()
            continue
        updated = []
        for r in request:
            output = current_thread().name + ' : ' + r
            d = parser.update_info(r)
            updated.append(UpdateAdRequest(status=d.status, url=d.url))
            output += ' : ' + d.status
            print(output)
        store.update_lead(request=updated)
        finish = time.time()
        print (f"Time: {finish - start}")


if __name__ == '__main__':
    num_workers = 1

    for i in range(num_workers):
         t = Thread(target=worker)
         t.name = 'Closer No ' + str(i)
         t.start()
         time.sleep(1)