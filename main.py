import asyncio
import aiohttp
import json
import random
import uuid
import pyfiglet
from colorama import init, Fore
import time

init()

text = "Yay! Spammer"
font = "slant"

ascii_art = pyfiglet.figlet_format(text, font=font)

print(Fore.MAGENTA + ascii_art + Fore.RESET)

async def fetch_group_members(session, group_id, tokens):
    token = random.choice(tokens)  
    url = f"https://api.yay.space/v2/groups/{group_id}/members?number=500"
    headers = {"Authorization": f"Bearer {token}"}
    async with session.get(url, headers=headers) as response:
        assert response.status == 200
        data = await response.json()
        return [{"id": member["user"]["id"], "nickname": member["user"]["nickname"]} for member in data["group_users"]]

async def send_message(session, group_id, member, base_message, tokens):
    token = random.choice(tokens)  
    url = "https://yay.space/api/posts"
    headers = {"Authorization": f"Bearer {token}"}
    text = f"@{member['nickname']} {base_message}" if member else base_message
    message_tags = json.dumps([{"type": "user", "user_id": member['id'], "offset": 0, "length": len(member['nickname']) + 1}]) if member else "[]"
    
    post_data = {
        "post_type": "text",
        "text": text,
        "color": "0",
        "font_size": "0",
        "message_tags": message_tags,
        "group_id": group_id,
        "uuid": str(uuid.uuid4())
    }
    
    async with session.post(url, headers=headers, json=post_data) as response:
        response_text = await response.text()
        print(f"Status Code: {response.status}, Response: {response_text}")
        assert response.status == 201  

async def main():
    group_id = input("グループIDを入力してください: ")
    base_message = input("メッセージを入力してください: ")
    num_messages = int(input("送信するメッセージ数を入力してください: "))
    mention_random_member = input("ランダムにメンションしますか? (y/n): ").lower() == 'y'

    with open("token.txt", "r") as file:
        tokens = [line.strip() for line in file.readlines() if line.strip()]
    
    async with aiohttp.ClientSession() as session:
        members = await fetch_group_members(session, group_id, tokens)
        for _ in range(num_messages):
            member = random.choice(members) if mention_random_member and members else None
            await send_message(session, group_id, member, base_message, tokens)

asyncio.run(main())
