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
    greetings = f'<div align="center"><h1>✨ {hello[randrange(45)]} 👋</h1>\n'

    links = '''
  <p>
    <a href="https://github.com/john-bampton">
      <img src="https://avatars.githubusercontent.com/u/23456618?s=200&v=4"
        alt="Dedicated, skilled, and community-oriented individual within the technology and local Brisbane communities" title="John Bampton">
    </a>
  </p>
  <h2><a href="https://github.com/john-bampton">John Bampton</a> is a dedicated, skilled, and community-oriented individual within the technology and local Brisbane communities</h2>
</div>

<div align="center">
  <a href="https://cloudstack.apache.org/who">
    <img src="./projects/apache-cloudstack.png" alt="Apache CloudStack Team Members">
  </a>
  <a href="https://sedona.apache.org/latest-snapshot/community/contributor/">
    <img src="./projects/apache-sedona.png" alt="Apache Sedona Team Members">
  </a>
  <a href="https://www.mail-archive.com/dev@cloudstack.apache.org/msg100220.html">
    <img src="./projects/apache.png" alt="Happy Days at The ASF">
  </a>
  <a href="https://curl.se/docs/thanks.html">
    <img src="./projects/curl.png" alt="Thanks for Your Contribution to the curl Project!">
  </a>
</div>

## 🥋 Ruby Warrior

- [Mukyu 無級](https://github.com/robygems)
- [Kukyu 九級](https://github.com/ruby/ruby/commit/97a114de44c71c688e8ba928da41bc396153ef5d)
- [Hachikyu 八級](https://github.com/sponsors/hsbt#sponsors)
- [Nanakyu 七級](https://github.com/whitesmith/rubycritic/graphs/contributors)
- [Rokkyu 六級](https://github.com/mruby/mruby.github.io/graphs/contributors)
- [Gokyu 五級](https://contributors.rubyonrails.org/)
- [Yonkyu 四級](https://github.com/mruby/mgem-list/graphs/contributors)
- [Sankyu 三級](https://github.com/mruby/mruby/graphs/contributors)
- [Nikyu 二級](https://www.codewars.com/users/Beast)

![I'm Ruby !??!!! 👺](images/ImRuby.gif)\n
'''

    perf_types = ['bullet', 'blitz', 'rapid'] # 'classical', 'correspondence', 'chess960', 'crazyhouse'
    lichess = '## ♟️ lichess\n\n'
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
                    date = d.strftime('%Y-%m-%d %A %#I:%M:%S %p')
                    results += f'| [{title}{name}](https://lichess.org/@/{name}) | __({rating})__ | {date} |\n'
                results += '\n'
            lichess += results
    
    codewars = '## 🧠 Codewars ⚔️\n\n'
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
    
    wikipedia = '## 🌐 Random Wikipedia 📘\n\n'
    with urllib.request.urlopen(f'https://en.wikipedia.org/api/rest_v1/page/random/summary') as url:
        data = json.load(url)
        extract = data['extract']
        page = data['content_urls']['mobile']['page']
        wikipedia += f'{extract}\n\n{page}\n\n'

    chessart = '''## 🎨 Chess is Art ♟️\n
![Chess Art 1](images/multi-color-chess-set.jpg)'''

    sections = f'\n{greetings}{links}{codewars}{lichess}{wikipedia}{chessart}\n'
    with open("README.md", 'r+', encoding='utf-8') as my_file:
        readme = my_file.read()
        readme = re.sub(pattern, r"\1"+sections, readme)
        my_file.truncate(0)
        my_file.seek(0)
        my_file.write(readme)

if __name__ == "__main__":
    build_readme()