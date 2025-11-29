class TennisGame:
    def __init__(self, player1_name, player2_name):
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.player1_score = 0
        self.player2_score = 0

    def won_point(self, player_name):
        if player_name == "player1":
            self.player1_score += 1
        else:
            self.player2_score += 1

    def get_score(self):
        if self.player1_score == self.player2_score:
            return self.equal_score()

        if self.player1_score >= 4 or self.player2_score >= 4:
            return self.endgame_score()

        return self.normal_score()

    def equal_score(self):
        if self.player1_score == 0:
            return "Love-All"
        elif self.player1_score == 1:
            return "Fifteen-All"
        elif self.player1_score == 2:
            return "Thirty-All"
        else:
            return "Deuce"
    
    def endgame_score(self):
        minus_result = self.player1_score - self.player2_score

        if minus_result == 1:
            return "Advantage player1"
        elif minus_result == -1:
            return "Advantage player2"
        elif minus_result >= 2:
            return "Win for player1"
        else:
            return "Win for player2"
    
    def normal_score(self):
        score_names = {0: "Love", 1: "Fifteen", 2: "Thirty", 3: "Forty"}
        player1_score_name = score_names[self.player1_score]
        player2_score_name = score_names[self.player2_score]

        return f"{player1_score_name}-{player2_score_name}"
