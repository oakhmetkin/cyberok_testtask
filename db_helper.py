import sqlite3
import json
import aiosqlite
from typing import List

import utils


class DBHelper:

    def __init__(self, path: str, logger=None) -> None:
        self.logger = logger
        self.path = path
    
    async def init_tables(self) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute('''
CREATE TABLE IF NOT EXISTS whois (
    id INTEGER PRIMARY KEY,
    domain TEXT,
    value TEXT
)
''')
            await db.commit()
        
        async with aiosqlite.connect(self.path) as db:
            await db.execute('''
CREATE TABLE IF NOT EXISTS fqdn_ip (
    id INTEGER PRIMARY KEY,
    fqdn TEXT,
    ip TEXT
)
''')
            await db.commit()

        self.logger.info('Tables are initialized (or already existed)')
    

    # /get_whois_info/
    async def get_whoises_by_domains(self, domains: List[str]) -> dict:
        async with aiosqlite.connect(self.path) as db:
            domains_in_quotes = list(map(lambda it: f'"{it}"', domains))
            domains_in_str = ','.join(domains_in_quotes)
            cur = await db.execute(f'''
SELECT domain, value
FROM whois 
WHERE
    domain IS NOT NULL AND
    domain IN ({domains_in_str})
''')
            res = await cur.fetchall()
            res = {k: json.loads(v) if v else None for k, v in res}
        
        return res

    async def save_domains_for_whoises(self, domains: List[str]) -> None:
        async with aiosqlite.connect(self.path) as db:
            domains_in_brackets = list(map(lambda it: f'("{it}")', domains))
            domains_in_str = ','.join(domains_in_brackets)
            await db.execute(f'''
INSERT INTO whois (domain) VALUES {domains_in_str}
''')
            await db.commit()

    async def update_whoises_by_domains(self, dct: dict) -> None:
        if len(dct) < 1:
            return
        
        async with aiosqlite.connect(self.path) as db:
            for dmn, whois in dct.items():
                whois_json = json.dumps(whois)
                await db.execute(f'''
UPDATE whois
SET value='{whois_json}'
WHERE domain="{dmn}"
''')
            await db.commit()


    # /get_ips_by_fqdns/
    async def get_ips_by_fqdns(self, fqdns: List[str]) -> dict:
        async with aiosqlite.connect(self.path) as db:
            fqdns_in_quotes = list(map(lambda it: f'"{it}"', fqdns))
            fqdns_in_str = ','.join(fqdns_in_quotes)
            cur = await db.execute(f'''
SELECT fqdn, ip
FROM fqdn_ip 
WHERE
    fqdn IS NOT NULL AND
    fqdn IN ({fqdns_in_str})
''')
            res = await cur.fetchall()
            res = {k: v for k, v in res}
        
        return res        
    
    async def save_fqdns_for_ips(self, fqdns: List[str]) -> None:
        async with aiosqlite.connect(self.path) as db:
            fqdns_in_brackets = list(map(lambda it: f'("{it}")', fqdns))
            fqdns_in_str = ','.join(fqdns_in_brackets)
            await db.execute(f'''
INSERT INTO fqdn_ip (fqdn) VALUES {fqdns_in_str}
''')
            await db.commit()
    
    async def update_ips_by_fqdns(self, dct: dict) -> None:
        if len(dct) < 1:
            return
        
        async with aiosqlite.connect(self.path) as db:
            for fqdn, ip in dct.items():
                await db.execute(f'''
UPDATE fqdn_ip
SET ip="{ip}"
WHERE fqdn="{fqdn}"
''')
            await db.commit()
    

    # /get_domains_by_ips/
    async def get_domains_by_ips(self, ips: List[str]) -> dict:
        async with aiosqlite.connect(self.path) as db:
            ips_in_quotes = list(map(lambda it: f'"{it}"', ips))
            ips_in_str = ','.join(ips_in_quotes)
            cur = await db.execute(f'''
SELECT ip, fqdn
FROM fqdn_ip 
WHERE
    ip IS NOT NULL AND
    ip IN ({ips_in_str})
''')
            res = await cur.fetchall()
            
            dct = {}
            for ip, dmn in res:
                if ip not in dct.keys():
                    dct[ip] = []
                dct[ip].append(dmn)
        
        return dct
    
    async def save_ips_for_domains(self, ips: List[str]) -> dict:
        async with aiosqlite.connect(self.path) as db:
            ips_in_brackets = list(map(lambda it: f'("{it}")', ips))
            ips_in_str = ','.join(ips_in_brackets)
            await db.execute(f'''
INSERT INTO fqdn_ip (ip) VALUES {ips_in_str}
''')
            await db.commit()
    
    async def update_domains_by_ips(self, dct: dict) -> dict:
        if len(dct) < 1:
            return
        
        async with aiosqlite.connect(self.path) as db:
            ips_in_brackets = list(map(lambda it: f'("{it}")', dct.keys()))
            ips_in_str = ','.join(ips_in_brackets)
            await db.execute(f'''
DELETE FROM fqdn_ip
WHERE
    ip IS NOT NULL AND
    fqdn IS NULL AND
    ip IN ({ips_in_str})
''')
            data = []
            for ip, domains in dct.items():
                if domains:
                    data.extend([(ip, dmn) for dmn in domains])
                
            await db.executemany(f'''
INSERT INTO fqdn_ip (ip, fqdn) VALUES (?, ?)
''', data)
            await db.commit()


    # database updating
    async def update_db(self):
        # updating ips by fqdns in 'fqdn_ip' table
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(f'''
SELECT fqdn
FROM fqdn_ip 
WHERE
    ip IS NULL AND
    fqdn IS NOT NULL 
''')
            unknown_ips = await cur.fetchall()
            
            dct = {}
            for (fqdn,) in unknown_ips:
                dct[fqdn] = utils.get_ip_by_fqdn(fqdn)
            
            await self.update_ips_by_fqdns(dct)
            await db.commit()
        
        # updating fqdns by ips in 'fqdn_ip' table
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(f'''
SELECT ip
FROM fqdn_ip 
WHERE
    fqdn IS NULL AND
    ip IS NOT NULL 
''')
            unknown_ips = list(map(lambda it: it[0], await cur.fetchall()))

            cur = await db.execute(f'''
SELECT DISTINCT ip
FROM fqdn_ip
WHERE
    fqdn IS NOT NULL AND
    ip IS NOT NULL
ORDER BY RANDOM()
LIMIT 10
''')
            rnd_ips_to_upd = list(map(lambda it: it[0], await cur.fetchall()))
            unknown_ips.extend(rnd_ips_to_upd)

            known_domains = await self.get_domains_by_ips(unknown_ips)

            dct = {}
            for ip in unknown_ips:
                new_domains = set(utils.get_domains_by_ip(ip))
                dct[ip] = list(new_domains - set(known_domains[ip]))
            
            await self.update_domains_by_ips(dct)
            await db.commit()
        
        # updating 'whois' table
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute(f'''
SELECT domain
FROM whois
WHERE
    value IS NULL AND
    domain IS NOT NULL 
''')
            unknown_ips = await cur.fetchall()
            
            dct = {}
            for (dmn,) in unknown_ips:
                dct[dmn] = utils.get_whois_info(dmn)
            
            await self.update_whoises_by_domains(dct)
            await db.commit()
        
        self.logger.info(f'Database successfully updated')
