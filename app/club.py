import logging
from dataclasses import dataclass, fields

import aiohttp
import requests

from config import JWT_TOKEN

logger = logging.getLogger(__name__)
VAS3K_ENDPOINT = "https://vas3k.club"
BY_TELEGRAM_ID = "/by_telegram_id"
USER = "/user"


@dataclass(init=False)
class ClubUser:
    full_name: str
    slug: str
    moderation_status: str
    is_active_member: bool

    def __init__(self, **kwargs):
        names = set([f.name for f in fields(self)])
        for k, v in kwargs.items():
            if k in names:
                setattr(self, k, v)

    @property
    def user_link(self):
        return f"{VAS3K_ENDPOINT}{USER}/{self.slug}"

    @property
    def approved(self):
        return self.moderation_status == "approved"


async def get_member_by_username(username):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{VAS3K_ENDPOINT}{USER}/{username}.json?service_token={JWT_TOKEN}",
                params={"service_token": JWT_TOKEN}
            ) as response:
                return await response.json()
    except Exception as e:
        logger.exception(e)
        return None


async def get_member_by_telegram_id(telegram_id):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{VAS3K_ENDPOINT}{USER}{BY_TELEGRAM_ID}/{telegram_id}.json",
                params={"service_token": JWT_TOKEN}
            ) as response:
                return await response.json()
    except Exception as e:
        logger.exception(e)
        return


def sync_get_member_by_telegram_id(telegram_id):
    """To prevent API overload"""
    try:
        response = requests.get(
            f"{VAS3K_ENDPOINT}{USER}{BY_TELEGRAM_ID}/{telegram_id}.json",
            params={"service_token": JWT_TOKEN}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.exception(e)
        return


def user_by_telegram_id(telegram_id):
    club_profile = sync_get_member_by_telegram_id(telegram_id)
    if not club_profile:
        return

    user_profile: dict = club_profile.get('user')

    if not user_profile:
        return

    return ClubUser(**user_profile)
