import unittest
from statistics_service import StatisticsService, SortBy
from player import Player

class PlayerReaderStub:
    def get_players(self):
        return [
            Player("Semenko", "EDM", 4, 12),  #  4+12 = 16
            Player("Lemieux", "PIT", 45, 54), # 45+54 = 99
            Player("Kurri",   "EDM", 37, 53), # 37+53 = 90
            Player("Yzerman", "DET", 42, 56), # 42+56 = 98
            Player("Gretzky", "EDM", 35, 89)  # 35+89 = 124
        ]

class TestStatisticsService(unittest.TestCase):
    def setUp(self):
        # annetaan StatisticsService-luokan oliolle "stub"-luokan olio
        self.stats = StatisticsService(
            PlayerReaderStub()
        )
    
    def test_search_found(self):
        player = self.stats.search("Semenko")
        self.assertEqual(player.name, "Semenko")
    
    def test_search_none(self):
        player = self.stats.search("None")
        self.assertEqual(player, None)
    
    def test_team_found(self):
        edm_team = self.stats.team("EDM")
        self.assertEqual(len(edm_team), 3)
        names = []
        for player in edm_team:
            names.append(player.name)
        self.assertEqual(names, ["Semenko", "Kurri", "Gretzky"])
    
    def test_team_not_found(self):
        team = self.stats.team("Nothing")
        self.assertEqual(len(team), 0)
    
    def test_top_points(self):
        top_players = self.stats.top(1, SortBy.POINTS)
        self.assertEqual(len(top_players), 2)
        self.assertEqual(top_players[0].name, "Gretzky")
        self.assertEqual(top_players[1].name, "Lemieux")
    
    def test_top_goals(self):
        top_players = self.stats.top(1, SortBy.GOALS)
        self.assertEqual(len(top_players), 2)
        self.assertEqual(top_players[0].name, "Lemieux")
        self.assertEqual(top_players[1].name, "Yzerman")
    
    def test_top_assists(self):
        top_players = self.stats.top(1, SortBy.ASSISTS)
        self.assertEqual(len(top_players), 2)
        self.assertEqual(top_players[0].name, "Gretzky")
        self.assertEqual(top_players[1].name, "Yzerman")
    
    def test_top_none(self):
        top_players = self.stats.top(1, "nothing")
        self.assertEqual(len(top_players), 2)
        self.assertEqual(top_players[0].name, "Gretzky")
        self.assertEqual(top_players[1].name, "Lemieux")


