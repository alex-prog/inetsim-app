import re

LOG_FILE_PATH = '/var/log/inetsim/service.log'

def get_file_to_proc():
    logfile = open(LOG_FILE_PATH,"r")
    # logfile = follow(open("service.log","r"))

    return logfile


''' LOG, re, dict details
# LOG
[2023-07-17 14:20:49] [6041] [http_80_tcp 6349] [192.168.179.128:37020] stat: 1 method=GET url=/ sent=./data/inetsim/http/fakefiles/sample.html postdata=
[2023-07-17 14:20:49] [6041] [http_80_tcp 6349] [192.168.179.128:37020] disconnect

#  re
1-11	2023-07-17
12-20	14:20:49
23-27	6041
30-41	http_80_tcp
42-46	6349
49-64	192.168.179.128
65-70	37020
72-153	stat: 1 method=GET url=/ sent=./data/inetsim/http/fakefiles/sample.html postdata=

# after dict zip 
{
    'date': '2023-07-17',
    'time': '14:20:49',
    'session_id': '6041',
    'service': 'http_80_tcp',
    'service_id': '6349',
    'src_ip': '192.168.179.128',
    'src_port': '37020',
    'info': 'stat: 1 method=GET url=/ sent=./data/inetsim/http/fakefiles/sample.html postdata='
}
'''


logpats = r'\[([^\s]+) ([^\s]+)\] \[([^\s]+)\] \[([^\s]+) ([^\s]+)\] \[([^\s]+):([^\s]+)\] (.*)'
logpat = re.compile(logpats)

def inetsim_log(lines):
    groups = (logpat.match(line) for line in lines)
    tuples = (g.groups() for g in groups if g)
    colnames = ('date', 'time', 'session_id', 'service', 'service_id', 'src_ip', 'src_port', 'info')
    log = (dict(zip(colnames, t)) for t in tuples)

    return log

class My_Row:

    def __init__(self, ip, first_seen, last_seen, count_no):
        self.ip = ip
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.count_no = count_no

# ---------------------Print a list of ips in the log------------------------------------------------------------------------
def print_ips_tbl():
    from rich.console import Console
    from rich.table import Table

    ips = {r['src_ip'] for r in inetsim_log(get_file_to_proc())}
    ips = list(ips)

    table = Table(title="IPS in the log")

    table.add_column("IP", justify="right", style="cyan", no_wrap=True)
    table.add_column("First seen", style="magenta")
    table.add_column("Last seen", style="magenta")
    table.add_column("Count", justify="right", style="green")

    rows = []

    for ip in ips:
        # count_no = sum(1 for r in inetsim_log(get_file_to_proc()) if r['src_ip']==ip)
        entries = (r for r in inetsim_log(get_file_to_proc()) if r['src_ip']==ip)
        entries_list = list(entries)
        count_no = len(entries_list)
        first_seen = entries_list[0]
        last_seen = entries_list[-1]
        rows.append(My_Row(ip, f'{first_seen["date"]} {first_seen["time"]}', f'{last_seen["date"]} {last_seen["time"]}', count_no))
    
    rows_to_print = sorted(rows, key=lambda x: x.count_no)
    for r in rows_to_print:
        table.add_row(r.ip, r.first_seen, r.last_seen, str(r.count_no))

    console = Console()
    console.print(table)

# -------------------------------------------------------------------------------------------------------------



print_ips_tbl()
