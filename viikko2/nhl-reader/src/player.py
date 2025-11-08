class Player:
    def __init__(self, player_dict):
        self.name = player_dict["name"]
        self.team = player_dict["team"]
        self.nationality = player_dict["nationality"]
        self.assists = player_dict["assists"]
        self.goals = player_dict["goals"]
        self.points = self.goals + self.assists

    def __str__(self):
        return f"{self.name:20}  {self.team:15}  {self.goals:2} + {self.assists:2} = {self.points:2}"
