from store import AdvertisementStore
from threading import Thread, current_thread, Lock
from parsers.mobile_de import MobileDeParser
import time
import paramiko
from sshtunnel import SSHTunnelForwarder
import pymysql

lock = Lock()

def worker():
    parser = MobileDeParser()
    mypkey = paramiko.RSAKey.from_private_key_file('C:/Users/think/.ssh/id_rsa', 'K0r0stel!')
    tunnel = SSHTunnelForwarder(('68.183.217.93', 22),
        ssh_username='forge',
        ssh_pkey=mypkey,
        remote_bind_address=('127.0.0.1', 3306)
    )
    tunnel.start()
    connection = pymysql.connect(
        host='127.0.0.1',
        user='forge',
        passwd='nSvGDEPZwsE625VhpPco', db='forge',
        port=tunnel.local_bind_port
    )
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
        for r in request:
            output = current_thread().name + ': ' + r + ' '
            start = time.time()
            status, images, is_dealer = parser.update_info(r)
            output += ' : ' + status
            scrap_iter_time = time.time()
            store.update_lead(r, status, images, is_dealer)
            store_iter_time = time.time()
            print(output)
            scrap_time += scrap_iter_time - start
            store_time += store_iter_time - scrap_iter_time

        finish = time.time()
        print (current_thread().name + ': ' + f"Time: {finish - start1}: get task: {get_task_time}, scrap:{scrap_time}, store: {store_time}")


if __name__ == '__main__':
    num_workers = 2

    for i in range(num_workers):
         t = Thread(target=worker)
         t.name = 'Spider No ' + str(i)
         t.start()
         time.sleep(1)