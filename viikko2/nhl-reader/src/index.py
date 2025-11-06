from player_reader import PlayerReader
from player_stats import PlayerStats
from rich.console import Console
from rich.table import Table

def main():
    console = Console()

    season = input("Season: ")
    nationality = input("Nationality: ")

    url = "https://studies.cs.helsinki.fi/nhlstats/2024-25/players"
    reader = PlayerReader(url)
    stats = PlayerStats(reader)
    players = stats.top_scorers_by_nationality(nationality)

    table = Table(title=f"Season {season} players from {nationality}")
    table.add_column("Name", style="cyan")
    table.add_column("Teams", style="magenta")
    table.add_column("Goals", justify="right", style="green")
    table.add_column("Assists", justify="right", style="green")
    table.add_column("Points", justify="right", style="green")
    
    for player in players:
        table.add_row(player.name, player.team, str(player.goals), str(player.assists), str(player.points))
    console.print(table)


if __name__ == "__main__":
    main()
