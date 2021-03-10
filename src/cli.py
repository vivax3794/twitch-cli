import os

import click
from rich import console
from rich.align import Align
from rich.table import Table
from rich.live import Live

from .twitch_api import Api

CLIENT_ID = os.getenv("CLIENT_ID")
SECRET = os.getenv("SECRET")
API = Api(CLIENT_ID, SECRET)

Console = console.Console()


@click.command()
@click.option("--query", help="what to search for", required=True)
@click.option("--amount", default=20, help="amount of channels to show")
@click.option("--ignore-errors", default=False, help="hide errors", is_flag=True)
@click.option("--max-views", type=int, help="filter views")
@click.option("--min-views", type=int, help="filter views")
@click.option("--game", type=str, help="filter for spefic games, type")
def search(query: str, amount: int, ignore_errors: bool, min_views, max_views, game) -> None:
    channels = API.search(query, live=True, amount=amount)
    table = Table()
    table_centerd = Align.center(table)

    table.add_column("channel")
    table.add_column("views")
    table.add_column("game")
    table.add_column("title")
    table.title = f"search results for [bold]{query}[/bold]"

    with Live(table_centerd, console=Console, refresh_per_second=20):
        for channel in channels:
            try:
                stream = API.get_stream_info(channel)
            except Exception as e:
                if not ignore_errors:
                    table.add_row(f"www.twitch.tv/{channel}", "[bold red]E[/bold red]", "[bold red]Error[/bold red]", f"[bold red]{e}[/bold red]")
            else:
                if max_views is not None and stream.views > max_views:
                    continue
                if min_views is not None and stream.views < min_views:
                    continue
                if game is not None and stream.game != game:
                    continue
                table.add_row(f"www.twitch.tv/{stream.channel}", str(stream.views), str(stream.game), str(stream.title))
