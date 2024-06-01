from store import AdvertisementStore
from threading import Thread, current_thread, Lock
from parsers.mobile_de import MobileDeParser
import time
from model import UpdateAdRequest
from db_connection import get_connection
from env import Env


lock = Lock()

def worker():
    parser = MobileDeParser()
    connection = get_connection()
    store = AdvertisementStore(connection=connection)
    branch = current_thread().name + ' : '
   
    while True:
        start = time.time()
        with lock:
            request = store.get_old_tasks()
        if not request:
            output = branch + 'No active ads'
            print(output)
            time.sleep(10)
            store.connection.commit()
            continue
        updated = []
        for r in request:
            output = branch + r
            d = parser.update_info(r)
            if not d:
                continue
            updated.append(UpdateAdRequest(status=d.status, url=d.url))
            output += ' : ' + d.status
            print(output)
        store.update_lead(request=updated)
        finish = time.time()
        print (f"Time: {finish - start}")


if __name__ == '__main__':

    for i in range(Env.THREADS):
         t = Thread(target=worker)
         t.name = 'Closer No ' + str(i)
         t.start()
         time.sleep(1)