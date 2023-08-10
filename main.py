from fastapi import FastAPI
import uvicorn
import asyncio

from typing import List

import config
from db_helper import DBHelper
from logger import setup_logger
from data_handler import handle_data


logger = setup_logger(__name__)
app = FastAPI()
db = DBHelper(config.DB_PATH, logger)


@app.get('/')
def root():
    return 'Service is running...'


@app.post('/get_domains_by_ips/')
async def get_domains_by_ips(ips: List[str]):
    logger.info(f'request to /get_domains_by_ips/, len of ips: {len(ips)}')
    
    meta = {}
    answer = None

    data = await db.get_domains_by_ips(ips)
    answer, st, msg = await handle_data(
        ips, data, logger, db.save_ips_for_domains, 'fqdn_ip')

    return {
        'meta': { 'status': st, 'message': msg },
        'answer': answer
    }


@app.post('/get_ips_by_fqdns/')
async def get_ips_by_fqdns(fqdns: List[str]):
    logger.info(f'request to /get_ips_by_fqdns/, len of fqdns: {len(fqdns)}')

    data = await db.get_ips_by_fqdns(fqdns)
    answer, st, msg = await handle_data(
        fqdns, data, logger, db.save_fqdns_for_ips, 'fqdn_ip')

    return {
        'meta': { 'status': st, 'message': msg },
        'answer': answer
    }


@app.post('/get_whois_info/')
async def get_whois_info(domains: List[str]):
    logger.info(f'request to /get_whois_info/, len of domains: {len(domains)}')

    data = await db.get_whoises_by_domains(domains)
    answer, st, msg = await handle_data(
        domains, data, logger, db.save_domains_for_whoises, 'whois')

    return {
        'meta': { 'status': st, 'message': msg },
        'answer': answer
    }


# database updating
async def update_db():
    while True:
        await db.update_db()
        await asyncio.sleep(config.DB_UPDATE_INTERVAL)


@app.on_event('startup')
async def startup_event():
    asyncio.create_task(update_db())


if __name__ == "__main__":
    logger.info(f'HOST:PORT - {config.HOST}:{config.PORT}')
    logger.info(f'DB_PATH - {config.DB_PATH}')
    logger.info(f'DB_UPD_INTERVAL - {config.DB_UPDATE_INTERVAL} sec')

    asyncio.run(db.init_tables())
    uvicorn.run(app, host=config.HOST, port=config.PORT)
