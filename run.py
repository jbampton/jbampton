import json
import re
import urllib.request
from datetime import datetime
from random import choice

# --- Constants ---
HELLO_GREETINGS = [
    "Hi", "Hello", "Hey", "G'day", "Good morning", "Good afternoon", "Good evening",
    "Howdy", "What's up?", "How's it going?", "How are you?", "How's your day?",
    "Long time no see", "Nice to meet you", "It's good to see you", "Pleased to meet you",
    "Greetings", "Salutations", "Cheers", "Yo", "What's new?", "What's crackalackin?",
    "How's tricks?", "How's things?", "How's everything?", "How's life?", "What's the story?",
    "What's the buzz?", "What's happening?", "What's going on?", "How's it hanging?",
    "How's it all going?", "How's things going?", "How are things?", "How's it all?",
    "What's all good?", "What's been going on?", "What's been up?", "What's been happening?",
    "How's it been?", "How's it been going?", "How's everything been?", "How's everything been going?",
    "How's everything going?", "How's it all been?", "How's it all been going?"
]

PERFORMANCE_TYPES = ['bullet', 'blitz', 'rapid']
LICHESS_USERS = ['RubyFu', 'SexyMate']


# --- HTML Section Generators ---
def get_greeting_html() -> str:
    """Return a random greeting HTML snippet."""
    greeting = choice(HELLO_GREETINGS)
    return f'<div align="center"><h1>✨ {greeting} 👋</h1></div>\n\n'


def get_links_html() -> str:
    """Return the links and badge section as HTML."""
    return '''<div align="center">
  <table>
    <tr>
      <td align="center">
        <a href="https://github.com/fuchsia-agency">
          <img src="https://avatars.githubusercontent.com/u/32108161?s=200&v=4" width="150" alt="Bold ideas. Futuristic tech. Open source at heart." title="Bold ideas. Futuristic tech. Open source at heart.">
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/john-bampton">
          <img src="https://avatars.githubusercontent.com/u/23456618?s=200&v=4" width="150" alt="Winter Is Coming" title="Winter Is Coming">
        </a>
      </td>
    </tr>
  </table>
</div>

<div align="center">
  <h2>👨‍🔬 🏩 💾 🇦🇺</h2>
  <h2><a href="https://github.com/john-bampton">John Bampton</a> is a dedicated, skilled, and community-oriented individual within the technology and local Brisbane communities</h2>
</div>

<div align="center">
  <h2>Invite on "Star" 🌠</h2>
  <h3>Add a "Star" to this <a href="https://github.com/john-bampton/.github">repository</a> and you will be sent an email invitation to join the <a href="https://github.com/john-bampton">John Bampton</a> GitHub Organization ⏩ 🏦</h3>
</div>

<div align="center">
  <a href="https://cloudstack.apache.org/who">
    <img src="./projects/apache-cloudstack.png"
      alt="Apache CloudStack Team Members"
      title="Apache CloudStack Team Members">
  </a>
  <a href="https://people.apache.org/phonebook.html?unix=openoffice">
    <img src="./projects/apache-openoffice.png"
      alt="Apache OpenOffice Team Members"
      title="Apache OpenOffice Team Members">
  </a>
  <a href="https://sedona.apache.org/latest-snapshot/community/contributor/">
    <img src="./projects/apache-sedona.png"
      alt="Apache Sedona Team Members"
      title="Apache Sedona Team Members">
  </a>
  <a href="https://github.com/brisbanesocialchess">
    <img src="https://avatars.githubusercontent.com/u/61562340?s=200&v=4"
      alt="Management team member, event host and Meetup dot com co-organizer"
      title="Management team member, event host and Meetup dot com co-organizer">
  </a>
  <a href="https://www.mail-archive.com/dev@cloudstack.apache.org/msg100220.html">
    <img src="./projects/apache.png"
      alt="Happy Days at The ASF"
      title="Happy Days at The ASF">
  </a>
  <a href="https://github.com/KashanUniversity">
    <img src="https://avatars.githubusercontent.com/u/50067282?s=200&v=4"
      alt="Guest of honor at Kashan University"
      title="Guest of honor at Kashan University">
  </a>
  <a href="https://github.com/SalamLang">
    <img src="https://avatars.githubusercontent.com/u/161657044?s=200&v=4" 
      alt="Maker at Salam Programming Language"
      title="Maker at Salam Programming Language">
  </a>
  <a href="https://curl.se/docs/thanks.html">
    <img src="./projects/curl.png"
      alt="Thanks for Your Contribution to the curl Project!"
      title="Thanks for Your Contribution to the curl Project!">
  </a>
</div>

<div align="center">
  <h2><a href="https://en.wikipedia.org/wiki/Ky%C5%AB">🥋 Ruby Warrior</a></h2>
  <p>
    <a href="https://github.com/robygems">Mukyū 無級</a>
    <br>
    <a href="https://github.com/ruby/ruby/commit/97a114de44c71c688e8ba928da41bc396153ef5d">Jukkyū 十級</a>
    <br>
    <a href="https://github.com/sponsors/hsbt#sponsors">Kyūkyū 九級</a>
    <br>
    <a href="https://github.com/natalie-lang/natalie/graphs/contributors">Hachikyu 八級</a>
    <br> 
    <a href="https://github.com/whitesmith/rubycritic/graphs/contributors">Nanakyū 七級</a>
    <br> 
    <a href="https://github.com/mruby/mruby.github.io/graphs/contributors">Rokkyū 六級</a>
    <br>
    <a href="https://contributors.rubyonrails.org/">Gokyū 五級</a>
    <br> 
    <a href="https://github.com/mruby/mgem-list/graphs/contributors">Yonkyū 四級</a>
    <br>
    <a href="https://github.com/mruby/mruby/graphs/contributors">Sankyū 三級</a>
    <br>
    <a href="https://www.codewars.com/users/Beast">Nikyū 二級</a>
    <br>
    <a href="./images/pre-1st-kyu.png">Jun'ikkyū 準一級</a>
    <br>
    <br>
    <a href="https://www.codewars.com/users/Beast"><img src="images/pre-1st-kyu.png" alt="Jun'ikkyū 準一級" title="Jun'ikkyū 準一級"></a>
    <br>
  </p>
  <p>
    <img src="images/ImRuby.gif"
      alt="I'm Ruby !??!!! 👺"
      title="I'm Ruby !??!!! 👺">
  </p>
</div>

'''

def get_chess_art_section() -> str:
    """Return a static Chess Art HTML section."""
    return (
        "## 🎨 Chess is Art ♟️\n\n"
        "![Chess Art 1](images/multi-color-chess-set.jpg)\n"
        """\n</div>"""
    )


# --- Data Fetchers ---
def fetch_json(url: str) -> dict:
    """Fetch JSON data from a given URL."""
    with urllib.request.urlopen(url) as response:
        return json.load(response)


def fetch_lichess_stats() -> str:
    """Fetch and format Lichess best win statistics for defined users."""
    lichess_section = """<div align="center">\n\n## ♟️ Lichess Stats\n\n"""

    for username in LICHESS_USERS:
        lichess_section += f'### Username: {username}\n\n'

        for perf_type in PERFORMANCE_TYPES:
            data = fetch_json(f'https://lichess.org/api/user/{username}/perf/{perf_type}')
            best_wins = data.get('stat', {}).get('bestWins', {}).get('results', [])

            if not best_wins:
                lichess_section += f'#### Best *{perf_type}* wins\n\n_No data available to display..._\n\n'
                continue

            stats_table = (
                f'#### Best *{perf_type}* wins\n\n'
                '| Name | Rating | Date |\n'
                '|------|--------|------|\n'
            )

            for win in best_wins:
                op_id = win.get('opId', {})
                title = f"__{op_id.get('title')}__ " if op_id.get('title') else ''
                name = op_id.get('name', 'Unknown')
                rating = win.get('opRating', 'N/A')
                try:
                    date_str = datetime.strptime(win['at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                except ValueError:
                    date_str = datetime.strptime(win['at'], '%Y-%m-%dT%H:%M:%SZ')
                formatted_date = date_str.strftime('%Y-%m-%d %A %I:%M:%S %p')
                stats_table += f'| [{title}{name}](https://lichess.org/@/{name}) | __({rating})__ | {formatted_date} |\n'

            lichess_section += stats_table + '\n'

    return lichess_section


def fetch_codewars_profile() -> str:
    """Fetch and return Codewars user stats as Markdown."""
    data = fetch_json('https://www.codewars.com/api/v1/users/Beast')

    return (
        """<div align="center">\n\n## 🧠 Codewars ⚔️\n\n</div>\n\n"""
        f"- Username: __{data['username']}__\n"
        f"- Name: __{data['name']}__\n"
        f"- Clan: __[{data['clan']}](https://en.wikipedia.org/wiki/Summerhill_School)__\n"
        f"- Skills: __{data['skills']}__\n"
        f"- Honor: __{data['honor']}__\n"
        f"- Leaderboard Position: __{data['leaderboardPosition']}__\n"
        f"- Overall Rank: __{data['ranks']['overall']['name']}__\n"
        f"- Total Completed Kata: __{data['codeChallenges']['totalCompleted']}__\n\n"
    )


def fetch_random_wikipedia() -> str:
    """Fetch and return a random Wikipedia article summary."""
    data = fetch_json('https://en.wikipedia.org/api/rest_v1/page/random/summary')
    return (
        "## 🌐 Random Wikipedia 📘\n\n"
        f"{data['extract']}\n\n"
        f"{data['content_urls']['mobile']['page']}\n\n"
    )


# --- README Builder ---
def build_readme():
    """Build the README.md file by injecting generated content between special markers."""
    sections = (
        get_greeting_html() +
        get_links_html() +
        fetch_codewars_profile() +
        fetch_lichess_stats() +
        fetch_random_wikipedia() +
        get_chess_art_section()
    )

    pattern = re.compile(r"(<!-- start-data -->)(.*)", re.MULTILINE | re.DOTALL)
    
    with open("README.md", "r+", encoding="utf-8") as file:
        content = file.read()
        updated_content = re.sub(pattern, r"\1\n" + sections, content)
        file.seek(0)
        file.write(updated_content)
        file.truncate()


# --- Entry Point ---
if __name__ == "__main__":
    build_readme()
