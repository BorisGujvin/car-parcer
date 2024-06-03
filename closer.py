from store import AdvertisementStore
from threading import Thread, current_thread, Lock, RLock
from parsers.mobile_de import MobileDeParser
import time
from datetime import datetime, timedelta
from model import UpdateAdRequest
from db_connection import get_connection
from env import Env


lock = Lock()
lock2 = Lock()


CLOSER_PERIOD = {
    1: (1, 14400),  # now - 4 hours
    2: (14400, 259200),
    3: (259200, 1814400)
}


def worker():
    parser = MobileDeParser()
    connection = get_connection()
    store = AdvertisementStore(connection=connection)
    branch = current_thread().name + ' : '
   
    while True:
        start = time.time()
        before_diff, after_diff = CLOSER_PERIOD.get(Env.CLOSER_INTERVAL)
        timedelta1 = timedelta(seconds=after_diff)
        timedelta2 = timedelta(seconds=before_diff)
        after = datetime.now() - timedelta1
        before = datetime.now() - timedelta2
        print('To close: ', store.count_old_ads(after_time=after, before_time=before),
              f'(from {after} till {before})')
        store.connection.commit()
        with lock:
            request = store.get_old_tasks(after_time=after, before_time=before, count=10)

        if not request:
            output = branch + 'No active ads'
            print(output)
            time.sleep(10)

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
        with lock2:
            store.update_lead(request=updated)
        finish = time.time()
        print(f"Time: {finish - start}")


if __name__ == '__main__':

    for i in range(Env.THREADS):
        t = Thread(target=worker)
        t.name = 'Closer No ' + str(i)
        t.start()
        time.sleep(1)
