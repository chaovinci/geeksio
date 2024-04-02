
import json
import secrets
import os
import redis


from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI()

auth_key = os.getenv('auth_key')  # 用于验证请求是否合法

# Set up the Redis connection
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


class Item(BaseModel):
    type: int
    text: str
    token: str


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/")
async def create_item(item: Item, x_api_key: str = Header(None)):
    if x_api_key is None or x_api_key != auth_key:
        raise HTTPException(status_code=400, detail="Bad request")

    print(f'Received item: {item}')
    talkerId = r.get(f'token:{item.token}')

    if talkerId:

        msg_id = secrets.token_hex(16)
        msg = {"type": item.type, "text": item.text, "talkerId": talkerId, "msg_id": msg_id}
        json_msg = json.dumps(msg)
        r.lpush('sendmsgs', json_msg)
        return {"message_id": msg_id}
    else:
        return item

# Run the server on 0.0.0.0 with port 539
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=539)
