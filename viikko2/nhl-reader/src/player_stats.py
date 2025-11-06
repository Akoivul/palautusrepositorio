class PlayerStats:
    def __init__(self, reader):
        self.reader = reader
        self.players = reader.get_players()
    
    def top_scorers_by_nationality(self, nationality):
        self.players.sort(key=lambda player: player.points, reverse=True)
        players_of_nationality = []
        for player in self.players:
            if player.nationality == nationality:
                players_of_nationality.append(player)
        return players_of_nationality