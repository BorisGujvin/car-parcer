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
        start = time.time()
        with lock:
            request = store.get_tasks()
        if not request:
            print('No jobb')
            time.sleep(10)
            continue
        for r in request:
            output = current_thread().name + ': ' + r + ' '
            status, images = parser.update_info(r)
            output += ' : ' + status
            store.update_lead(r, status, images)
            print(output)
        finish = time.time()
        print (f"Time: {finish - start}")


if __name__ == '__main__':
    num_workers = 4

    for i in range(num_workers):
         t = Thread(target=worker)
         t.name = 'Spider No ' + str(i)
         t.start()
         time.sleep(1)