import paramiko
from sshtunnel import SSHTunnelForwarder
import pymysql


def get_connection():
    mypkey = paramiko.RSAKey.from_private_key_file('./.ssh/id_rsa', 'K0r0stel!')
    tunnel = SSHTunnelForwarder(('68.183.217.93', 22),
        ssh_username='forge',
        ssh_pkey=mypkey,
        remote_bind_address=('127.0.0.1', 3306)
    )
    tunnel.start()
    return pymysql.connect(
        host='127.0.0.1',
        user='forge',
        passwd='nSvGDEPZwsE625VhpPco', db='forge',
        port=tunnel.local_bind_port
    )
