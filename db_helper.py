import sqlite3
import json


def __singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@__singleton
class DBHelper:

    def __init__(self, path: str) -> None:
        self.connect(path)

    def connect(self, path):
        self.__con = sqlite3.connect(path)
        self.__cur = self.__con.cursor()
        self.init_tables()
    
    def close(self):
        self.__con.close()
    
    def init_tables(self) -> None:
        whois_table = '''
CREATE TABLE IF NOT EXISTS whois (
    id INTEGER PRIMARY KEY,
    domain TEXT,
    value TEXT
)
'''
        self.__cur.execute(whois_table)
        
        fqdn_ip_table = '''
CREATE TABLE IF NOT EXISTS fqdn_ip (
    id INTEGER PRIMARY KEY,
    fqdn TEXT,
    ip TEXT
)
'''
        self.__cur.execute(fqdn_ip_table)
        self.__con.commit()
    
    # whois
    def get_whois(self, dmn: str) -> dict:
        res = self.__cur.execute(f'SELECT value FROM whois WHERE domain="{dmn}"')
        val = res.fetchone()

        if val:
            return json.loads(val[0])
        else:
            return None

    def save_whois(self, dmn: str, dct: dict) -> None:
        val = json.dumps(dct)
        self.__cur.execute(f'''
INSERT INTO whois (domain, value) VALUES ('{dmn}', '{val}')
''')
        self.__con.commit()

    def update_whois(self, dmn: str, dct: dict) -> None:
        val = json.dumps(dct)
        self.__cur.execute(f'UPDATE whois SET (value="{val}") \
                           WHERE domain="{dmn}"')
        self.__con.commit()

    # FQDN & ip
    def get_ip(self, fqdn) -> str:
        res = self.__cur.execute(f'SELECT ip FROM fqdn_ip WHERE fqdn="{fqdn}"')
        ans = res.fetchone()

        if ans:
            return ans[0]
        else:
            return None
    
    def save_ip(self, fqdn, ip) -> None:
        self.__cur.execute(f'INSERT INTO fqdn_ip (fqdn, ip) \
                           VALUES ("{fqdn}", "{ip}")')
        self.__con.commit()
    
    def update_ip(self, fqdn, ip) -> None:
        self.__cur.execute(f'UPDATE fqdn_ip SET ip="{ip}" WHERE fqdn="{fqdn}"')
        self.__con.commit()
