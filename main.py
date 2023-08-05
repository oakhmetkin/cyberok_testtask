from fastapi import FastAPI
import uvicorn
import asyncio

from typing import List

import config
from db_helper import DBHelper
from logger import setup_logger
import utils


logger = setup_logger(__name__)
app = FastAPI()
db = DBHelper(config.DB_PATH, logger)


@app.get('/')
def root():
    return 'Service is running...'


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
        await asyncio.sleep(config.DB_UPDATE_INTERVAL)


@app.on_event('startup')
async def startup_event():
    asyncio.create_task(update_db())


if __name__ == "__main__":
    logger.info(f'HOST:PORT - {config.HOST}:{config.PORT}')
    logger.info(f'DB_PATH - {config.DB_PATH}')
    logger.info(f'DB_UPD_INTERVAL - {config.DB_UPDATE_INTERVAL} sec')
    uvicorn.run(app, host=config.HOST, port=config.PORT)
