import json
import re
import urllib.request
from datetime import datetime
from random import randrange

def build_readme():
    pattern = re.compile(r"(<!-- start-data -->)(.*)", re.MULTILINE | re.DOTALL)

    hello = ["Hi",
     "Hello",
     "Hey",
     "G'day",
     "Good morning",
     "Good afternoon",
     "Good evening",
     "Howdy",
     "What's up?",
     "How's it going?",
     "How are you?",
     "How's your day?",
     "Long time no see",
     "Nice to meet you",
     "It's good to see you",
     "Pleased to meet you",
     "Greetings",
     "Salutations",
     "Cheers",
     "Yo",
     "What's new?",
     "What's crackalackin?",
     "How's tricks?",
     "How's things?",
     "How's everything?",
     "How's life?",
     "What's the story?",
     "What's the buzz?",
     "What's happening?",
     "What's going on?",
     "How's it hanging?",
     "How's it all going?",
     "How's things going?",
     "How are things?",
     "How's it all?",
     "What's all good?",
     "What's been going on?",
     "What's been up?",
     "What's been happening?",
     "How's it been?",
     "How's it been going?",
     "How's everything been?",
     "How's everything been going?",
     "How's everything going?",
     "How's it all been?",
     "How's it all been going?"]
    greetings = f'# {hello[randrange(45)]}\n\n'

    links = '''- [Apache CloudStack Project Members](https://cloudstack.apache.org/who)
- [Apache Sedona Project Members](https://sedona.apache.org/latest-snapshot/community/contributor/)
- [Rails Contributors - All time](https://contributors.rubyonrails.org/)
- [Ruby Warrior ??!!!? 👺](https://github.com/ruby/ruby/commit/97a114de44c71c688e8ba928da41bc396153ef5d)
- [Thanks for Your Contribution to the curl Project!](https://curl.se/docs/thanks.html)
- [Happy Days at The ASF](https://www.mail-archive.com/dev@cloudstack.apache.org/msg100220.html)\n
'''

    perf_types = ['bullet', 'blitz', 'rapid'] # 'classical', 'correspondence', 'chess960', 'crazyhouse'
    lichess = '## lichess\n\n'
    users = ['RubyFu', 'SexyMate']
    for user in users:
        lichess += f'### Username: {user}\n\n'
        for perf in perf_types:
            with urllib.request.urlopen(f'https://lichess.org/api/user/{user}/perf/{perf}') as url:
                data = json.load(url)
                results = f'#### Best *{perf}* wins\n\n| Name | Rating | Date |\n| - | - | - |\n'
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
        leaderboard_position = data['leaderboardPosition']
        skills = data['skills']
        ranks = data['ranks']
        overall = ranks['overall']['name']
        total_completed = data['codeChallenges']['totalCompleted']
        codewars += f'''- Username: __{username}__
- Name: __{name}__
- Clan: __[{clan}](https://en.wikipedia.org/wiki/Summerhill_School)__
- Skills: __{skills}__
- Honor: __{honor}__
- Leaderboard Position: __{leaderboard_position}__
- Overall Rank: __{overall}__
- Total Completed Kata: __{total_completed}__\n\n'''
    
    wikipedia = '## Random Wikipedia\n\n'
    with urllib.request.urlopen(f'https://en.wikipedia.org/api/rest_v1/page/random/summary') as url:
        data = json.load(url)
        extract = data['extract']
        page = data['content_urls']['mobile']['page']
        wikipedia += f'{extract}\n\n{page}\n\n'

    chessart = '''## Chess is Art\n
![Chess Art 1](images/multi-color-chess-set.jpg)'''

    sections = f'\n{greetings}{links}{codewars}{lichess}{wikipedia}{chessart}\n'
    with open("README.md", 'r+') as my_file:
        readme = my_file.read()
        readme = re.sub(pattern, r"\1"+sections, readme)
        my_file.truncate(0)
        my_file.seek(0)
        my_file.write(readme)

if __name__ == "__main__":
    build_readme()
