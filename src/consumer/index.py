import asyncio
import json
import os
import secrets
from urllib.parse import urlparse

import aiohttp
from consumer_logger import logger
from redis import asyncio as aioredis

from supabase import Client, create_client

# 全局变量来存储 Redis 连接
redis = None
supabase: Client = None


async def create_redis_connection(redis_url):
    try:
        # 使用 aioredis 创建 Redis 连接
        return await aioredis.from_url(redis_url, db=0)
    except Exception as e:
        print(f"Redis连接失败: {e}")
        return None


async def initialize_supabase():
    try:
        global supabase
        supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
    except Exception as e:
        print(f"Supabase连接失败: {e}")
        return None


async def initialize_redis():
    global redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost')
    redis = await create_redis_connection(REDIS_URL)
    if redis is None:
        logger.error("无法创建 Redis 连接，请检查 Redis 服务是否可用和配置是否正确。")
        redis = await create_redis_connection(REDIS_URL)
        # 如果仍然连接不上，等待一段时间再尝试
        if redis is None:
            await asyncio.sleep(1)
        exit(1)  # 如果无法连接Redis，则退出程序


async def send_text_message(talkerId, text):
    """ Send a text message to the user."""
    # talkerId, text, type
    print(f'send_text_message: {talkerId}, {text}')
    message = {
        'talkerId': talkerId,
        'type': 'text',
        'text': text
    }
    redis_res = await redis.rpush('sendmsgs', json.dumps(message))
    print(f'send_text_message: {redis_res}')


def is_valid_http_url(url):
    try:
        result = urlparse(url)
        # Check if the URL has the required scheme and netloc, and scheme is either 'http' or 'https'
        return all([result.scheme in ['http', 'https'], result.netloc])
    except:
        return False


def parse_cmd(string):
    # Normalize spaces by replacing potential full-width spaces with half-width spaces
    normalized_string = string.replace('　', ' ')

    # Split the string into parts using spaces
    parts = normalized_string.split()

    # Extract the command from the first part and convert it to lowercase
    # Remove any leading punctuation such as '.', '。', etc.
    command = parts[0].lstrip('.。,，@/').lower()

    # Extract the argument if present; otherwise, set it to None
    argument = parts[1] if len(parts) > 1 else None

    return command, argument

    # Example usage (uncomment to test)
    # cmd, arg = get_cmd('。hook　http://finalurl.com/aaa')
    # print(f"Command: {cmd}, Argument: {arg}")


def generate_new_token(talkerId: str) -> str:
    print(f'generate_new_token: {talkerId}')
    new_token = secrets.token_hex(16)
    modify_user_profile(talkerId, {'token': new_token})
    return new_token


def init_user_profile(message: dict) -> dict:
    new_token = secrets.token_hex(16)
    talkerId = message['talkerId']
    talkerName = message['talkerName']
    data = supabase.table('user_profiles').insert({'talkerId': talkerId, 'talkerName': talkerName, 'token': new_token}).execute()
    return data.data[0] if data.data else None


def retrieve_user_profile(talkerId: str) -> dict:
    data = supabase.table('user_profiles').select('*').eq('talkerId', talkerId).execute()
    return data.data[0] if data.data else None


def modify_user_profile(talkerId: str, profile: dict) -> dict:
    data = supabase.table('user_profiles').update(profile).eq('talkerId', talkerId).execute()
    return data.data[0] if data.data else None


async def process_cmd(text, talkerId):
    command, argument = parse_cmd(text)
    print(f'Command: {command}, Argument: {argument}')
    if command == 'hook':
        # Set the hook URL for the user
        if is_valid_http_url(argument):
            # Save the hook URL to Redis
            modify_user_profile(talkerId, {'hook': argument})

            # Send a success message to the user
            await send_text_message(talkerId, f'Hook url 已经设置为： {argument}')
        else:
            await send_text_message(talkerId, 'Hook URL is invalid. Please provide a valid URL. Example:')
            await send_text_message(talkerId, '@hook http://example.com/api')
            await send_text_message(talkerId, '有不明白的地方，去看看 https://github.com/chaovinci/geeksio')
            # Send an error message to the user
    elif command == 'token':
        new_token = generate_new_token(talkerId)
        # await send_text_message(talkerId, 'New token generated. Please use this token to send messages and verification requests:')
        await send_text_message(talkerId, '新token已经生效，请使用此token发送消息及验证请求:')
        await send_text_message(talkerId, new_token)
        return

    elif command == 'help':
        # Send help messages to the user
        await send_text_message(talkerId, '去看看 https://github.com/chaovinci/geeksio')
    else:
        # Send an error message to the user
        pass


async def send_to_hook(message, user):
    """ Send the message to the hook URL."""
    # Reassembling the message
    msg_dict = {
        "id": message['id'],
        "timestamp": message['timestamp'],
        "type": message['type'],
        "text": message['text'],
        "filePath": message['filePath'],
        "content": message['content'],
        "token": user['token']
    }

    logger.debug(f"send to hook, url: {user['hook']}, message: {msg_dict}")
    async with aiohttp.ClientSession() as session:
        async with session.post(user['hook'], json=msg_dict) as response:
            # Assuming you want to check the status and possibly the response
            logger.info(f"Response status: {response.status}")
            # response_text = await response.text()
            # print(f"Response text: {response_text}")


async def process_msg(message):
    # Convert the message from string to dict
    logger.debug(message)

    # 检查用户是否存在
    user = retrieve_user_profile(message['talkerId'])
    if not user:
        # 如果不存在，init_user_profile
        user = init_user_profile(message)

    logger.debug(user)

    if not user['hook']:
        # If user hasn't set a hook, send help messages
        await send_text_message(message['talkerId'], '使用@hook https://yourhookurl.com 设置hook地址，用于接收消息')
        return

    if message['type'] == 7:
        # message is text, check if it's a command
        if message['text'] and message['text'][0] in ['/', '@']:
            # Check if the message is a command
            await process_cmd(message['text'], message['talkerId'])
            return

    FILE_TYPES = [1, 2, 5, 6, 15]
    # Attachment-1, Audio-2,  Emoticon-5, Image-6, Video-15

    if message['type'] in FILE_TYPES:
        print('FILE_TYPES: ')
        print(message['type'])

    await send_to_hook(message, user)
    return


def restructure_dict(data: dict) -> dict:
    msg_dict = {
        "id": data['id'],
        "timestamp": data['payload']['timestamp'],
        "type": data['payload']['type'],
        "talkerId": data['payload']['talkerId'],
        "talkerName": data['talkerName'],
        "text": data['payload']['text'],
        "filePath": data['filePath'],
        "content": data['content']
    }
    return msg_dict


async def consume():
    logger.debug('running consume...')
    global redis
    global supabase
    while True:
        # Use blpop to block until a message is available
        message = await redis.blpop('messages', timeout=0)

        if message is not None:
            _, message_data = message  # blpop returns a tuple (list_name, message)
            message_dict = restructure_dict(json.loads(message_data))

            logger.debug(message_dict)
            try:
                asyncio.create_task(process_msg(message_dict))
            except Exception as e:
                logger.error(f"error: {e}")


async def main():
    await initialize_redis()
    await initialize_supabase()

    await consume()

# Start consuming messages
if __name__ == "__main__":
    asyncio.run(main())
