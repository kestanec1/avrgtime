import requests
import time
import re
import webbrowser
import os
from datetime import datetime
# --- RENDER UYUMASIN DIYE GEREKLI KUTUPHANELER ---
from flask import Flask
from threading import Thread

# Settings
POOL_LIMIT = 100               # Number of players to fetch from the leaderboard
FILE_INPUT = "mcsr_liderlik_ilk100.txt"
FILE_HTML = "index.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

# --- RENDER UYUMASIN DIYE SNEAKY WEB SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Canli!"

def run():
    # Render varsayılan olarak 8080 portunu dinler
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

def download_live_leaderboard_names():
    print(f"STEP 1: Fetching current top {POOL_LIMIT} players from the leaderboard...")
    players = []
    for page in range(1, 3):
        try:
            url = f"https://api.mcsrranked.com/leaderboard?page={page}"
            response = requests.get(url, headers=HEADERS, timeout=5)
            if response.status_code == 200:
                res_json = response.json()
                if isinstance(res_json, dict) and "data" in res_json:
                    users_list = res_json["data"].get("users", [])
                    for user in users_list:
                        name = user.get("nickname", user.get("username"))
                        if name and name not in players:
                            players.append(name)
            time.sleep(0.2)
        except Exception as e:
            print(f"Error: {e}")
            break
            
    if players:
        with open(FILE_INPUT, "w", encoding="utf-8") as f:
            for idx, name in enumerate(players[:POOL_LIMIT], 1):
                f.write(f"{idx}. {name}\n")
        print(f"[SUCCESS] Player names saved to '{FILE_INPUT}'.\n" + "-"*65)
        return True
    return False

def read_players_from_input_txt():
    players = []
    try:
        with open(FILE_INPUT, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    clean_name = re.sub(r'^\d+\.\s*', '', line)
                    if clean_name and clean_name not in players:
                        players.append(clean_name)
    except FileNotFoundError:
        print(f"[ERROR] '{FILE_INPUT}' not found!")
    return players

def generate_html_site(valid_players):
    """Converts the calculated data into a beautiful HTML webpage."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCSR Ranked - Live Average Leaderboard</title>
    <meta http-equiv="refresh" content="20">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #121214;
            color: #e1e1e6;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .container {{
            max-width: 1000px;
            width: 100%;
            background: #1d1d22;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            border: 1px solid #29292e;
        }}
        h1 {{
            text-align: center;
            color: #00e676;
            margin-bottom: 5px;
            font-size: 28px;
            letter-spacing: 0.5px;
        }}
        p.subtitle {{
            text-align: center;
            color: #8d8d99;
            margin-bottom: 25px;
            font-size: 14px;
        }}
        
        /* Search Box & Reset Button Grid Layout */
        .search-container {{
            width: 100%;
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
        }}
        .search-box {{
            flex: 1;
            padding: 12px 16px;
            background-color: #121214;
            border: 1px solid #29292e;
            border-radius: 8px;
            color: #ffffff;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
            box-sizing: border-box;
        }}
        .search-box:focus {{
            border-color: #00e676;
            box-shadow: 0 0 8px rgba(0, 230, 118, 0.2);
        }}
        
        /* Modern Reset Button */
        .reset-btn {{
            padding: 0 24px;
            background-color: #29292e;
            border: 1px solid #3e3e44;
            border-radius: 8px;
            color: #00e676;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s, border-color 0.2s, transform 0.1s;
        }}
        .reset-btn:hover {{
            background-color: #323239;
            border-color: #00e676;
        }}
        .reset-btn:active {{
            transform: scale(0.97);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            padding: 14px 16px;
            text-align: left;
        }}
        th {{
            background-color: #29292e;
            color: #ffffff;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 1px;
            border-bottom: 2px solid #121214;
            user-select: none;
        }}
        
        /* Sortable Columns Style */
        .sortable {{
            color: #00e676;
            cursor: pointer;
            transition: background-color 0.2s;
        }}
        .sortable:hover {{
            background-color: #323239;
        }}
        .sortable::after {{
            content: ' ↕';
            font-size: 10px;
            color: #666;
            margin-left: 5px;
        }}
        
        tr {{
            border-bottom: 1px solid #29292e;
            transition: background-color 0.2s;
        }}
        /* Zebra Striping */
        tr:nth-child(even) {{
            background-color: #1f1f26;
        }}
        tr:hover {{
            background-color: #26262f !important;
        }}
        
        .rank {{
            font-weight: bold;
            color: #8d8d99;
            width: 60px;
        }}
        /* Podium Highlights */
        .rank-1 {{ color: #ffd700; font-size: 18px; font-weight: 800; }}
        .rank-2 {{ color: #c0c0c0; font-size: 17px; font-weight: 800; }}
        .rank-3 {{ color: #cd7f32; font-size: 16px; font-weight: 800; }}
        
        .player-link {{
            color: #ffffff;
            font-weight: 500;
            text-decoration: none;
            transition: color 0.2s, border-bottom 0.2s;
            border-bottom: 1px solid transparent;
            padding-bottom: 2px;
            display: inline-block;
        }}
        .player-link:hover {{
            color: #00e676;
            border-bottom: 1px solid #00e676;
        }}
        
        .time-badge {{
            background: #00e676;
            color: #0a0a0c;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: bold;
            font-family: monospace;
            font-size: 14px;
            display: inline-block;
        }}
        .stats-count {{
            color: #ffffff;
            font-family: monospace;
            font-size: 14px;
            font-weight: 500;
        }}
        .elo-text {{
            color: #2196f3;
            font-family: monospace;
            font-size: 14px;
            font-weight: bold;
        }}
        .points-text {{
            color: #ffb74d; /* Warm orange/gold highlight for playoff points */
            font-family: monospace;
            font-size: 14px;
            font-weight: bold;
        }}
        .forfeit-text {{
            color: #ef5350;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 25px;
            color: #626269;
            font-size: 11px;
            letter-spacing: 0.5px;
        }}
    </style>
</head>
<body>

<div class="container">
    <h1>MCSR RANKED COMPREHENSIVE DASHBOARD</h1>
    <p class="subtitle">Real-time speed, ELO, points, and play-off performance analysis of the top 100 players</p>
    
    <div class="search-container">
        <input type="text" id="searchInput" class="search-box" placeholder="Search player by name...">
        <button class="reset-btn" onclick="resetTable()">Reset</button>
    </div>
    
    <table id="leaderboardTable">
        <thead>
            <tr>
                <th>Rank</th>
                <th>Player Name</th>
                <th class="sortable" onclick="sortTable(2, true)">Average Time</th>
                <th class="sortable" onclick="sortTable(3, true)">Won Matches</th>
                <th class="sortable" onclick="sortTable(4, true)">Forfeits (Rate)</th>
                <th class="sortable" onclick="sortTable(5, true)">ELO</th>
                <th class="sortable" onclick="sortTable(6, true)">Playoff Points</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for rank, p in enumerate(valid_players, 1):
        rank_class = f"rank-{rank}" if rank <= 3 else ""
        html_template += f"""
            <tr data-orig-index="{rank}">
                <td class="rank {rank_class}" data-val="{rank}">#{rank}</td>
                <td>
                    <a href="https://mcsrranked.com/stats/{p['name']}" target="_blank" class="player-link">{p['name']}</a>
                </td>
                <td data-val="{p['avg_seconds']}"><span class="time-badge">{p['time_str']}</span></td>
                <td class="stats-count" data-val="{p['wins']}">{p['wins']}</td>
                <td class="stats-count" data-val="{p['forfeits']}">
                    {p['forfeits']} <span class="forfeit-text">({p['forfeit_rate']:.1f}%)</span>
                </td>
                <td class="elo-text" data-val="{p['elo']}">{p['elo']}</td>
                <td class="points-text" data-val="{p['points']}">{p['points']}</td>
            </tr>
        """
        
    html_template += f"""
        </tbody>
    </table>
    
    <div class="footer">
        Last Updated: {current_time} | Developed by kestaneci
    </div>
</div>

<script>
// 1. Instant Search Feature
document.getElementById('searchInput').addEventListener('keyup', function() {{
    let filter = this.value.toLowerCase();
    let rows = document.querySelectorAll('#leaderboardTable tbody tr');
    
    rows.forEach(row => {{
        let playerName = row.querySelector('.player-link').innerText.toLowerCase();
        if (playerName.includes(filter)) {{
            row.style.display = '';
        }} else {{
            row.style.display = 'none';
        }}
    }});
}});

// 2. Dynamic Table Sorting Feature (For colIndex 2, 3, 4, 5 and 6)
let sortDirections = [true, true, true, true, true, true, true]; 

function sortTable(colIndex, isNumeric) {{
    let table = document.getElementById("leaderboardTable");
    let tbody = table.querySelector("tbody");
    let rows = Array.from(tbody.querySelectorAll("tr"));
    
    let ascending = sortDirections[colIndex];
    sortDirections[colIndex] = !ascending; 
    
    rows.sort((rowA, rowB) => {{
        let cellA = rowA.children[colIndex];
        let cellB = rowB.children[colIndex];
        
        let valA = cellA.getAttribute("data-val") || cellA.innerText.trim();
        let valB = cellB.getAttribute("data-val") || cellB.innerText.trim();
        
        if (isNumeric) {{
            return ascending ? parseFloat(valA) - parseFloat(valB) : parseFloat(valB) - parseFloat(valA);
        }} else {{
            return ascending ? valA.localeCompare(valB) : valB.localeCompare(valA);
        }}
    }});
    
    rows.forEach(row => tbody.appendChild(row));
}}

// 3. Reset Button Feature
function resetTable() {{
    document.getElementById('searchInput').value = '';
    
    let table = document.getElementById("leaderboardTable");
    let tbody = table.querySelector("tbody");
    let rows = Array.from(tbody.querySelectorAll("tr"));
    
    rows.sort((rowA, rowB) => {{
        let indexA = parseInt(rowA.getAttribute("data-orig-index"));
        let indexB = parseInt(rowB.getAttribute("data-orig-index"));
        return indexA - indexB;
    }});
    
    sortDirections = [true, true, true, true, true, true, true];
    
    rows.forEach(row => {{
        row.style.display = '';
        tbody.appendChild(row);
    }});
}}
</script>

</body>
</html>
    """
    
    with open(FILE_HTML, "w", encoding="utf-8") as f:
        f.write(html_template)

def main():
    # --- WEB SERVERI WHLE TRUE DONGUSUNDEN ONCE TETIKLIYORUZ ---
    keep_alive()

    # Burası artık sonsuz döngüde kalarak Render'da 7/24 çalışacak
    while True:
        if download_live_leaderboard_names():
            PLAYERS = read_players_from_input_txt()
            if PLAYERS:
                print(f"STEP 2: Calculating statistics for {len(PLAYERS)} players...")
                valid_players = []
                total_players = len(PLAYERS)
                
                for index, username in enumerate(PLAYERS, 1):
                    print(f"[{index}/{total_players}] Querying {username}...")
                    url = f"https://api.mcsrranked.com/users/{username}"
                    
                    try:
                        response = requests.get(url, headers=HEADERS, timeout=5)
                        if response.status_code == 200:
                            user_json = response.json()
                            user_data = user_json.get("data", {})
                            
                            elo = user_data.get("eloRate", 0)
                            if elo is None: elo = 0
                                
                            points = user_data.get("points", 0)
                            if points is None: points = 0
                            
                            statistics = user_data.get("statistics", {})
                            season_data = statistics.get("season", {})
                            
                            completions = season_data.get("completions", {}).get("ranked", 0)
                            completion_time_ms = season_data.get("completionTime", {}).get("ranked", 0)
                            
                            wins = season_data.get("wins", {}).get("ranked", 0)
                            forfeits = season_data.get("forfeits", {}).get("ranked", 0)
                            played_matches = season_data.get("playedMatches", {}).get("ranked", 0)
                            
                            forfeit_rate = (forfeits / played_matches * 100) if played_matches > 0 else 0.0
                            
                            if completions > 0 and completion_time_ms > 0:
                                avg_seconds = round((completion_time_ms / completions) / 1000)
                                
                                minutes = avg_seconds // 60
                                seconds = avg_seconds % 60
                                time_str = f"{minutes}:{seconds:02d}"
                                
                                valid_players.append({
                                    "name": username,
                                    "avg_seconds": avg_seconds,
                                    "time_str": time_str,
                                    "wins": wins,
                                    "forfeits": forfeits,
                                    "forfeit_rate": forfeit_rate,
                                    "elo": elo,
                                    "points": points
                                })
                        
                    except Exception:
                        pass
                        
                    time.sleep(0.15)

                valid_players.sort(key=lambda x: x["avg_seconds"])
                generate_html_site(valid_players)
                print(f"\n[EXCELLENT] Dashboard successfully updated! Last: {datetime.now().strftime('%H:%M:%S')}")
        
        # Her tur bittikten sonra 5 dakika (300 saniye) mola verip baştan başlayacak
        print("Waiting 5 minutes for the next update cycle...")
        time.sleep(300)

if __name__ == "__main__":
    main()