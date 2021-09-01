from source.utils import errors
import typing
import discord
import datetime
from ..utils import constants
import aiohttp
import pathlib


def build_embed(
    user: typing.Optional[typing.Union[discord.Member, discord.User]] = None,
    title: typing.Optional[str] = discord.Embed.Empty,
    description: typing.Optional[str] = discord.Embed.Empty,
    colour: typing.Optional[discord.Colour] = constants.Colours.base_color,
    timestamp: typing.Optional[datetime.datetime] = discord.Embed.Empty,
    url: typing.Optional[str] = discord.Embed.Empty,
    type: typing.Optional[str] = "rich",
) -> discord.Embed:

    embed = discord.Embed(
        title=title,
        description=description,
        colour=colour,
        timestamp=timestamp,
        url=url,
        type=type,
    )
    if user:
        embed.set_author(name=user.name, icon_url=user.display_avatar.url)
    return embed


async def paste(session: aiohttp.ClientSession, text: str):

    data = bytes(text, encoding="utf-8")
    async with session.post(
        constants.URLs.paste_service_documents, data=data
    ) as response:

        if response.status != 200:
            raise errors.BadStatus(
                f"Returned status: {response.status}. Invalid to proceed."
            )

        json_response = await response.json(content_type=None, encoding="utf-8")
        key = json_response.get("key")
        return constants.URLs.paste_service.format(key=key)


def file(text: str, filename: typing.Optional[str] = "file.txt"):
    with open(filename, mode="w", encoding="utf-8") as file_object:
        file_object.write(text)
        return file_object


async def paste_or_file(
    text: str,
    session: aiohttp.ClientSession,
    filename: typing.Optional[str] = "file.txt",
):
    try:
        link = await paste(session=session, text=text)
        return link
    except errors.BadStatus:
        file_object = file(text=text, filename=filename)
        file_object = discord.File(file_object.name)
        return file_object


def get_relative_path(filename: str, *, with_extension: bool = False, sep: str = "/"):
    filename = f"{filename}" if filename.endswith(".py") else f"{filename}.py"

    iterable = pathlib.Path().glob(f"**/{filename}")
    pathlib_paths = [pathlib_path for pathlib_path in iterable]
    if not pathlib_paths:
        return None
    paths = [sep.join(path.parts) for path in pathlib_paths]
    paths = [path.replace(".py", "") for path in paths if not with_extension]
    return paths
