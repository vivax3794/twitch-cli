from enum import Enum
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import time

import requests


class Url(Enum):
    SearchChannel = "helix/search/channels"
    StreamInfo = "helix/streams"
    Game = "helix/games"


@dataclass
class Stream:
    channel: str
    title: str
    views: str
    game: str


class Api:
    """Inteface with the twitch Api"""

    def __init__(self, id_: str, secret: str) -> None:
        self.id_ = id_
        self.token = self.get_token(secret)
        self.ratelimit_reset = 0
        self.ratelimit_current = -1

    def get_token(self, secret: str):
        return requests.post(
                "https://id.twitch.tv/oauth2/token",
                params={
                    "client_id": self.id_,
                    "client_secret": secret,
                    "grant_type": "client_credentials",
                    }
                ).json()["access_token"]

    def get(
            self, url: Url, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> Dict[str, Any]:

        if self.ratelimit_current == 0:
            time.sleep(self.ratelimit_reset - time.time())

        heads = {"client-id": self.id_, "Authorization": f"Bearer {self.token}"}
        if headers is not None:
            heads.update(headers)
        data = requests.get(
                "https://api.twitch.tv/" + url.value, headers=heads, **kwargs
        )

        self.ratelimit_current = int(data.headers["Ratelimit-Remaining"])
        self.ratelimit_reset = int(data.headers["Ratelimit-Reset"])

        return data.json()

    def search(self, query: str, live: bool = True, amount: int = 20) -> List[str]:
        data = self.get(Url.SearchChannel, params={
            "query": query,
            "first": amount,
            "live_only": live
            })

        streamers = []
        for streamer in data["data"]:
            streamers.append(streamer["broadcaster_login"])

        return streamers

    def get_stream_info(self, stream: str) -> Stream:
        data = self.get(Url.StreamInfo, params={
            "user_login": stream
            })["data"][0]
        return Stream(
                channel=stream,
                title=data["title"],
                views=data["viewer_count"],
                game=self.get_game(data["game_id"])
                )

    def get_game(self, id_: int) -> str:
        return self.get(Url.Game, params={"id": id_})["data"][0]["name"]
