import json
import re
import urllib.request
from datetime import datetime


pattern = re.compile(r"(<!-- start-data -->)(.*)", re.MULTILINE | re.DOTALL)
perfTypes = ['bullet', 'blitz', 'rapid'] # 'classical', 'correspondence', 'chess960', 'crazyhouse'
lichess = '## lichess\n\n'
for perf in perfTypes:
    with urllib.request.urlopen(f'https://lichess.org/api/user/SexyMate/perf/{perf}') as url:
        data = json.load(url)
        results = f'### Best *{perf}* wins\n\n| Name | Rating | Date |\n| - | - | - |\n'
        for row in data['stat']['bestWins']['results']:
            title = row['opId']['title']
            if title is None:
                title = ''
            else:
                title = f'__{title}__ '
            name = row['opId']['name']
            rating = row['opRating']
            d = datetime.strptime(row['at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            date = d.strftime('%Y-%m-%d %A %-I:%M:%S %p')
            results += f'| [{title}{name}](https://lichess.org/@/{name}) | __({rating})__ | {date} |\n'
        results += '\n'
        lichess += results

codewars = '## Codewars\n\n'
with urllib.request.urlopen(f'https://www.codewars.com/api/v1/users/Beast') as url:
    data = json.load(url)
    username = data['username']
    name = data['name']
    honor = data['honor']
    clan = data['clan']
    leaderboardPosition = data['leaderboardPosition']
    skills = data['skills']
    ranks = data['ranks']
    overall = ranks['overall']['name']
    totalCompleted = data['codeChallenges']['totalCompleted']
    codewars += f'''- Username: __{username}__
- Name: __{name}__
- Clan: __{clan}__
- Skills: __{skills}__
- Honor: __{honor}__
- Leaderboard Position: __{leaderboardPosition}__
- Overalll Rank: __{overall}__
- Total Completed Kata: __{totalCompleted}__\n
'''

wikipedia = '## Random Wikipedia\n\n'
with urllib.request.urlopen(f'https://en.wikipedia.org/api/rest_v1/page/random/summary') as url:
    data = json.load(url)
    extract = data['extract']
    page = data['content_urls']['mobile']['page']
    wikipedia += f'{extract}\n\n{page}'

sections = f'\n{codewars}{lichess}{wikipedia}\n'
with open("README.md", 'r+') as my_file:
    readme = my_file.read()
    readme = re.sub(pattern, r"\1"+sections, readme)
    my_file.truncate(0)
    my_file.seek(0)
    my_file.write(readme)
