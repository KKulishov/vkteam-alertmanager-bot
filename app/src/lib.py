from json.tool import main
from multiprocessing.dummy import Manager
import time
import os
import logging
import multiprocessing
from aiohttp import web
from bot.bot import Bot
from argparse import ArgumentParser
from pythonjsonlogger import jsonlogger
from traceback import format_exc
from src.redis_connect import write_to_redis, read_from_redis

parser = ArgumentParser()
parser.add_argument("--log-level", type=str, help='specify a log level')
parser.add_argument("--api-url-base", type=str, help="specify an api endpoint")
parser.add_argument("--api-token", type=str, help="specify an api token")
parser.add_argument("--bot-name", type=str, help="specify a bot name")
parser.add_argument("--parse-mode", type=str, help="specify a text format")
args = parser.parse_args()

envs = {
  "log_level": os.getenv('LOG_LEVEL', args.log_level),
  "api_url_base": os.getenv('API_URL_BASE', args.api_url_base),
  "api_token": os.getenv('API_TOKEN', args.api_token),
  "bot_name": os.getenv('BOT_NAME', args.bot_name),
  "default_chat_id": os.getenv('default_chat_id'),
  "ALERTMANAGER_NAME": os.getenv('ALERTMANAGER_NAME'),
  "parse_mode": args.parse_mode or "HTML"
}

redis_status=os.getenv('redis_status', "off").lower()
last_successful_alertmanager_request_time = multiprocessing.Value('i', 0)
time_interval_check_alert=int(os.getenv('time_interval_check_alert', 60))
time_how_long_not_to_send=int(os.getenv('time_how_long_not_to_send', 300))
bot = Bot(api_url_base=envs['api_url_base'], name=envs['bot_name'], token=envs['api_token'], is_myteam=True)

def set_log_level(level):
    if level == 'INFO' or level == 'info':
      log_level = logging.INFO
    elif level == 'DEBUG' or level == 'debug':
      log_level = logging.DEBUG
    elif level == 'ERROR' or level == 'error':
      log_level = logging.ERROR
    else:
      log_level = logging.INFO
    return log_level

log_level = set_log_level(envs['log_level'])
logger = logging.getLogger()
logger.setLevel(log_level)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(levelname)%(asctime)%(message)%(pathname)%(lineno))')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

async def heartbeat(request):
  if redis_status == "on":
    time_heartbeat = int(time.time())
    write_redis = write_to_redis("time_last_heartbeat", time_heartbeat)
    msg = f"heartbeat check is push time to redis {time_heartbeat}"
    logger.info(msg)
    return web.Response(text=msg)
  else:  
    global last_successful_alertmanager_request_time
    with last_successful_alertmanager_request_time.get_lock():
        last_successful_alertmanager_request_time.value = int(time.time())
    msg = f"heartbeat check is push time {last_successful_alertmanager_request_time.value}"
    logger.info(msg)
    return web.Response(text=msg)

def check_alertmanager_heartbeat():
  time.sleep(60)
  global last_successful_alertmanager_request_time
  while True:
    if redis_status == "on":
      ## логика проверик значений из redis
      current_time = time.time()
      last_successful_alertmanager_request_time_redis = int(read_from_redis("time_last_heartbeat"))
      time_since_last_request = current_time - last_successful_alertmanager_request_time_redis
      if time_since_last_request > time_how_long_not_to_send:
        chat_id = envs.get('default_chat_id')
        ALERTMANAGER_NAME =  envs.get('ALERTMANAGER_NAME')
        msg = f"ALerting AHTUNG, alertmanager {ALERTMANAGER_NAME} don't work in last_successful time: {last_successful_alertmanager_request_time_redis}, real time {current_time}"
        send_message = bot.send_text(chat_id=chat_id, parse_mode=envs['parse_mode'], text=msg)
        status = send_message.status_code
        try:
          if status == 200:
            msgs = 'Message successfully sent'
            logger.info(msgs)
          else:
            msgs = 'Error dont sent to meesage vkteeams'  
            logger.info(msgs)
        except web.HTTPException:
            logger.error(format_exc())    
      time.sleep(time_interval_check_alert)    
    else:  
      current_time = time.time()
      time_since_last_request = current_time - last_successful_alertmanager_request_time.value
      if time_since_last_request > time_how_long_not_to_send:
        chat_id = envs.get('default_chat_id')
        ALERTMANAGER_NAME =  envs.get('ALERTMANAGER_NAME')
        msg = f"ALerting AHTUNG, alertmanager {ALERTMANAGER_NAME} don't work in last_successful time: {last_successful_alertmanager_request_time.value}, real time {current_time}"
        send_message = bot.send_text(chat_id=chat_id, parse_mode=envs['parse_mode'], text=msg)
        status = send_message.status_code
        try:
          if status == 200:
            msgs = 'Message successfully sent'
            logger.info(msgs)
          else:
            msgs = 'Error dont sent to meesage vkteeams'  
            logger.info(msgs)
        except web.HTTPException:
            logger.error(format_exc())    
      time.sleep(time_interval_check_alert)