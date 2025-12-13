import pytest

from src.web_app import WIN_THRESHOLD, app, games, reset_state


@pytest.fixture(autouse=True)
def clear_games():
    reset_state()
    app.config["TESTING"] = True
    yield
    reset_state()


def test_index_renders():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Minimalistinen web-versio" in resp.get_data(as_text=True)


def test_start_game_and_scoreboard_shows_zeroes():
    client = app.test_client()
    resp = client.post("/start", data={"mode": "b"}, follow_redirects=False)
    assert resp.status_code == 302
    # Session must be stored on redirect response
    assert "session_id" in resp.headers.get("Set-Cookie", "")

    landing = client.get("/", follow_redirects=True)
    body = landing.get_data(as_text=True)
    assert landing.status_code == 200
    assert "Pelitila" in body
    assert "1. pelaaja: 0" in body
    assert "2. pelaaja: 0" in body
    assert "Tasapelit: 0" in body


def test_play_against_ai_updates_score():
    client = app.test_client()
    start_resp = client.post("/start", data={"mode": "b"}, follow_redirects=True)
    assert start_resp.status_code == 200

    play_resp = client.post("/play", data={"p1": "k"}, follow_redirects=True)
    body = play_resp.get_data(as_text=True)
    # AI first move is paper, so player loses: tokan_pisteet should be 1
    assert "Tietokone valitsi" in body
    assert "2. pelaaja: 1" in body
    assert games  # ensure server-side state exists


class FixedAI:
    def __init__(self, move: str):
        self.move = move

    def anna_siirto(self):
        return self.move

    def aseta_siirto(self, siirto):
        pass


def test_game_runs_until_three_wins_and_stops():
    client = app.test_client()
    resp = client.post("/start", data={"mode": "b"}, follow_redirects=False)
    assert resp.status_code == 302

    cookie = resp.headers.get("Set-Cookie", "")
    session_id = cookie.split("session_id=")[1].split(";")[0]

    # Make AI always pick kivi, player plays paper -> player wins every round
    games[session_id].ai = FixedAI("k")

    for _ in range(WIN_THRESHOLD):
        client.post("/play", data={"p1": "p"}, follow_redirects=True)

    landing = client.get("/", follow_redirects=True)
    body = landing.get_data(as_text=True)
    assert "Ensimmäinen pelaaja voitti" in body
    assert f"1. pelaaja: {WIN_THRESHOLD}" in body
    assert "2. pelaaja: 0" in body

    # Further play requests do not change the finished game
    client.post("/play", data={"p1": "p"}, follow_redirects=True)
    landing2 = client.get("/", follow_redirects=True).get_data(as_text=True)
    assert f"1. pelaaja: {WIN_THRESHOLD}" in landing2


def test_full_word_input_is_accepted():
    client = app.test_client()
    resp = client.post("/start", data={"mode": "b"}, follow_redirects=False)
    cookie = resp.headers.get("Set-Cookie", "")
    session_id = cookie.split("session_id=")[1].split(";")[0]

    # AI fixed to kivi; player plays "paperi" -> player wins
    games[session_id].ai = FixedAI("k")

    play_resp = client.post("/play", data={"p1": "paperi"}, follow_redirects=True)
    body = play_resp.get_data(as_text=True)

    assert "Tietokone valitsi" in body
    assert "1. pelaaja: 1" in body
    assert "2. pelaaja: 0" in body
