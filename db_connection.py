import paramiko
from sshtunnel import SSHTunnelForwarder
import pymysql
from env import Env


def get_connection():
    if Env.DB_LOCAL:
        return pymysql.connect(
            host='127.0.0.1',
            user=Env.DB_USER,
            passwd=Env.DB_PASS, 
            db=Env.DB_NAME
        )
    
    mypkey = paramiko.RSAKey.from_private_key_file(Env.KEY_FILE, Env.KEY_PASS)
    tunnel = SSHTunnelForwarder((Env.TUNNEL_ADDRESS, Env.TUNNEL_PORT),
        ssh_username=Env.TUNNEL_USERNAME,
        ssh_pkey=mypkey,
        remote_bind_address=('127.0.0.1', 3306)
    )
    tunnel.start()
    return pymysql.connect(
        host='127.0.0.1',
        user=Env.DB_USER,
        passwd=Env.DB_PASS, db=Env.DB_NAME,
        port=tunnel.local_bind_port
    )
