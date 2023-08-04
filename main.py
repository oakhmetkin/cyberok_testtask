from fastapi import FastAPI
import uvicorn
import asyncio

from typing import List
import signal

from db_helper import DBHelper
from logger import setup_logger
import utils


DB_UPDATE_INTERVAL = 5

logger = setup_logger(__name__)
app = FastAPI()
db = DBHelper('cyberok.sqlite', logger)


@app.post('/get_domains_by_ips/')
async def get_domains_by_ips(ips: List[str]):
    logger.info(f'request to /get_domains_by_ips/, len of ips: {len(ips)}')

    domains = []
    
    for ip in ips:
        dmn = utils.get_domain_by_ip(ip)
        domains.append(dmn)
    
    return domains


@app.post('/get_ips_by_fqdns/')
async def get_ips_by_fqdns(fqdns: List[str]):
    logger.info(f'request to /get_ips_by_fqdns/, len of fqdns: {len(fqdns)}')

    ips = []

    for fqdn in fqdns:
        ip = db.get_ip(fqdn)

        if not ip:
            ip = utils.get_ip_by_fqdn(fqdn)
            db.save_ip(fqdn, ip)

        ips.append(ip)

    return ips


@app.post('/get_whois_info/')
async def get_whois_info(domains: List[str]):
    logger.info(f'request to /get_whois_info/, len of domains: {len(domains)}')

    ans = []

    for dmn in domains:
        dct = db.get_whois(dmn)

        if not dct:
            dct = utils.get_whois_info(dmn)
            db.save_whois(dmn, dct)

        ans.append(dct)
    
    return ans


# database updating
async def update_db():
    while True:
        db.update_db()
        await asyncio.sleep(DB_UPDATE_INTERVAL)


@app.on_event('startup')
async def startup_event():
    asyncio.create_task(update_db())


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
