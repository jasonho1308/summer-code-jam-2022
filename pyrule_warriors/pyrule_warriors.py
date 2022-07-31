import asyncio
import json

import websockets

WS_URI = 'ws://summer-code-jam-2022.herokuapp.com/ws/123a'


def _ws_connect():
    return websockets.connect(WS_URI)


async def _send_action(payload: dict):
    async with _ws_connect() as websocket:
        await websocket.send(json.dumps(payload))
        print(await websocket.recv())


def login(username: str, password: str):
    payload = {
        "action": "login",
        "name": username,
        "password": password
    }
    asyncio.run(_send_action(payload))


def new_account(username: str, password: str):
    payload = {
        "action": "new_account",
        "name": username,
        "password": password
    }
    asyncio.run(_send_action(payload))


def query_online_users():
    payload = {
        "action": "query_online_users"
    }
    asyncio.run(_send_action(payload))


def go_hunting():
    payload = {
        "action": "go_hunting"
    }
    asyncio.run(_send_action(payload))


def challenge_player(username: str):
    payload = {
        "action": "challenge_player",
        "player": username
    }
    asyncio.run(_send_action(payload))


def accept_challenge(lobby_id: str):
    payload = {
        "action": "accept_challenge",
        "lobby": lobby_id
    }
    asyncio.run(_send_action(payload))


def attack(attack: str):
    payload = {
        "action": "attack",
        "attack": attack
    }
    asyncio.run(_send_action(payload))


def view_shop():
    payload = {
        "action": "view_shop"
    }
    asyncio.run(_send_action(payload))


def buy(item: str):
    payload = {
        "action": "buy",
        "item": item
    }
    asyncio.run(_send_action(payload))


def sell(item):
    payload = {
        "action": "buy",
        "item": item
    }
    asyncio.run(_send_action(payload))


def seek_quest():
    payload = {
        "action": "seed_quest"
    }
    asyncio.run(_send_action(payload))


def accept_quest(quest: str):
    payload = {
        "action": "accept_quest",
        "quest": quest
    }
    asyncio.run(_send_action(payload))


def fulfil_quest(quest: str):
    payload = {
        "action": "fulfil_quest",
        "quest": quest
    }
    asyncio.run(_send_action(payload))


def inventory():
    payload = {
        "action": "inventory"
    }
    asyncio.run(_send_action(payload))


def equip(item: str):
    payload = {
        "action": "equip",
        "item": item
    }
    asyncio.run(_send_action(payload))


def use_item():
    payload = {
        "action": "use_item",
        "item": "xxx"
    }
    asyncio.run(_send_action(payload))


def status():
    payload = {
        "action": "status"
    }
    asyncio.run(_send_action(payload))


def send_trade_offer(user: str):
    payload = {
        "action": "send_trade_offer",
        "user": user
    }
    asyncio.run(_send_action(payload))


def put_trade(items: list = None, gold: int = None):
    payload = {
        "action": "put_trade",
        "items": items,
        "gold": gold
    }
    asyncio.run(_send_action(payload))


def accept_trade():
    payload = {
        "action": "accept_trade"
    }
    asyncio.run(_send_action(payload))


def chat(message: str):
    payload = {
        "action": "chat",
        "message": message
    }
    asyncio.run(_send_action(payload))


def direct_message(user: str, message: str):
    payload = {
        "action": "direct_message",
        "message": message,
        "user": user
    }
    asyncio.run(_send_action(payload))
