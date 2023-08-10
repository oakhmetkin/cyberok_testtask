async def handle_data(request_data: dict, db_data: dict, logger, save_func,
                      db_table_name) -> (dict, str, str):
    answer = None
    status = None
    message = None

    new_data = list(set(request_data) - set(db_data.keys()))
    answer = { k: v for k, v in db_data.items() if v }
    null_count = len(list(set(request_data) - set(answer.keys()) \
                          - set(new_data)))

    if new_data:
        await save_func(new_data)
        logger.info(f'inserted {len(new_data)} rows into {db_table_name}. \
It\'ll update ASAP')
        
        status = 'fine'
        message = f'Not found {len(new_data)} notes. Database will update \
ASAP. Repeat in a few minutes.'
    else:
        status = 'good'
        message = f'The request has been fully processed.'
    
    if null_count:
        status = 'fine'
        message = f'{message + " " if message else ""}{null_count} \
notes have not yet been updated. Repeat in a few minutes.'
    
    return answer, status, message