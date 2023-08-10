import os


def get_int_envvar(name, defval):
    try:
        var = int(os.getenv(name, defval))
    except:
        var = defval
    
    return var


HOST = os.getenv('HOST', '127.0.0.1')
DB_PATH = os.getenv('DB_PATH', 'cyberok.sqlite')
PORT = get_int_envvar('PORT', 8000)
DB_UPDATE_INTERVAL = get_int_envvar('DB_UPDATE_INTERVAL', 60)
