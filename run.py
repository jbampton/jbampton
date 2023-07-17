import json
import re
import urllib.request
from datetime import datetime


pattern = re.compile(r"(<!-- lichess -->)(.*?)(<!-- lichess -->)", re.MULTILINE | re.DOTALL)
perfTypes = ['bullet', 'blitz', 'rapid'] # 'classical', 'correspondence', 'chess960', 'crazyhouse']
sections = ''
for perf in perfTypes:
    with urllib.request.urlopen(f'https://lichess.org/api/user/SexyMate/perf/{perf}') as url:
        data = json.load(url)
        results = f'## Best {perf} wins\n\n'
        for row in data['stat']['bestWins']['results']:
            title = row['opId']['title']
            if title == None:
                title = ''
            else:
                title += ' '
            name = row['opId']['name']
            rating = row['opRating']
            date = row['at']
            results += f'- {title}{name} ({rating}) {date}\n'
        results += '\n'
        sections += results
with open("README.md", 'r+') as my_file:
    readme = my_file.read()
    readme = re.sub(pattern, r"\1\n"+sections+r"\3", readme)
    my_file.seek(0)
    my_file.write(readme)
