"""
Demonstrates a Rich "application" using the Layout and Live classes.

"""

from datetime import datetime

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table

import time
import os

LOG_FILE_PATH = '/var/log/inetsim/service.log'


def follow(thefile):
    thefile.seek(0, os.SEEK_END)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line


console = Console()


def make_layout() -> Layout:
    """Define the layout."""
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=7),
    )
    layout["main"].split_row(
        Layout(name="side"),
        Layout(name="body", ratio=2, minimum_size=60),
    )
    layout["body"].split(Layout(name="box1"), Layout(name="box2"))
    return layout






service_log_msg = Table.grid(padding=1)
service_log_msg.add_column(style="green", justify="right")
service_log_msg.add_row("logging..")

service_message = Table.grid(padding=1)
service_message.add_column()
service_message.add_column(no_wrap=True)
service_message.add_row(service_log_msg)

service_log_message_panel = Panel(
    Align.center(
        Group("\n", Align.center(service_log_msg)),
        vertical="middle",
    ),
    box=box.ROUNDED,
    padding=(1, 2),
    title="[b red]service.log",
    border_style="bright_blue",
)



class Header:
    """Display header with clock."""

    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            "[b]Cyber Academy[/b] iNetSim status",
            datetime.now().ctime().replace(":", "[blink]:[/]"),
        )
        return Panel(grid, style="white on blue")

''' #func ret Panel example
def make_ips_list() -> Panel:
    """Some example content."""
    sponsor_message = Table.grid(padding=1)
    sponsor_message.add_column(style="green", justify="right")
    sponsor_message.add_column(no_wrap=True)
    sponsor_message.add_row(
        "Twitter",
        "[u blue link=https://twitter.com/textualize]https://twitter.com/textualize",
    )
    sponsor_message.add_row(
        "CEO",
        "[u blue link=https://twitter.com/willmcgugan]https://twitter.com/willmcgugan",
    )
    sponsor_message.add_row(
        "Textualize", "[u blue link=https://www.textualize.io]https://www.textualize.io"
    )

    message = Table.grid(padding=1)
    message.add_column()
    message.add_column(no_wrap=True)
    message.add_row(sponsor_message)

    message_panel = Panel(
        Align.center(
            Group("\n", Align.center(sponsor_message)),
            vertical="middle",
        ),
        box=box.ROUNDED,
        padding=(1, 2),
        title="[b red]List of IPs in the log",
        border_style="bright_blue",
    )
    return message_panel
'''

def run_and_print(cmd) -> Syntax:
    import subprocess
    cmd_to_run = cmd.split()
    result = subprocess.run(['python3', 'inetsim-print_ips.py'], stdout=subprocess.PIPE)
    code = result.stdout.decode()

    syntax = Syntax(code, "no", line_numbers=False)
    return syntax


def make_ips_list() -> Syntax:
    import subprocess
    # python3 inetsim-print_ips.py
    result = subprocess.run(['python3', 'inetsim-print_ips.py'], stdout=subprocess.PIPE)
    code = result.stdout.decode()

    syntax = Syntax(code, "no", line_numbers=False)
    return syntax

def make_inet_status() -> Syntax:
    import subprocess
    result = subprocess.run(['service', 'inetsim', 'status'], stdout=subprocess.PIPE)
    code = result.stdout.decode()

    syntax = Syntax(code, "vim", line_numbers=False)
    return syntax

def make_service_log() -> Syntax:
    import subprocess
    result = subprocess.run(['sudo', 'tail', '-n', '20', LOG_FILE_PATH], stdout=subprocess.PIPE)
    code = result.stdout.decode()

    syntax = Syntax(code, "vim", line_numbers=False)
    return syntax



job_progress = Progress(
    "{task.description}",
    SpinnerColumn(),
    BarColumn(),
    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
)
job_progress.add_task("[green]Log processing")
job_progress.add_task("[magenta]Services", total=200)
job_progress.add_task("[cyan]IPs", total=400)

total = sum(task.total for task in job_progress.tasks)
overall_progress = Progress()
overall_task = overall_progress.add_task("All Jobs", total=int(total))

progress_table = Table.grid(expand=True)
progress_table.add_row(
    Panel(
        overall_progress,
        title="Overall Progress",
        border_style="green",
        padding=(2, 2),
    ),
    Panel(job_progress, title="[b]Jobs", border_style="red", padding=(1, 2)),
)

log_table = Panel(job_progress, title="[b]Jobs", border_style="red", padding=(1, 2))


layout = make_layout()
layout["header"].update(Header())
layout["box1"].update(Panel(make_service_log(), border_style="red", title="[b]service.log [blink]...[/]"))
layout["box2"].update(Panel(make_ips_list(), border_style="red", title="[b]List of IPs in the log [blink]...[/]"))
layout["side"].update(Panel(make_inet_status(), border_style="red", title="[b]iNetSim status [blink]...[/]"))
layout["footer"].update(progress_table)


from time import sleep

from rich.live import Live

# logfile = open("service.log","r")
# loglines = follow(logfile)

with Live(layout, refresh_per_second=10, screen=True):
    while True:
        try:
            sleep(0.1)
            for job in job_progress.tasks:
                if not job.finished:
                    job_progress.advance(job.id)

            completed = sum(task.completed for task in job_progress.tasks)
            overall_progress.update(overall_task, completed=completed)
            layout["side"].update(Panel(make_inet_status(), border_style="red", title="[b]iNetSim status [blink]...[/]"))
            layout["box1"].update(Panel(make_service_log(), border_style="red", title="[b]service.log [blink]...[/]"))
            layout["box2"].update(Panel(make_ips_list(), border_style="red", title="[b]List of IPs in the log [blink]...[/]"))
            # for line in loglines:
            #     service_log_msg.add_row(line)
        except KeyboardInterrupt:
            print('Bye!')
            exit()

