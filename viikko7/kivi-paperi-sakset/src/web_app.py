import uuid
from dataclasses import dataclass, field
from typing import Optional, Dict

from flask import Flask, redirect, render_template_string, request, url_for, make_response

from tuomari import Tuomari
from tekoaly import Tekoaly
from tekoaly_parannettu import TekoalyParannettu

app = Flask(__name__)


@dataclass
class GameState:
    mode: str  # a, b, c
    tuomari: Tuomari = field(default_factory=Tuomari)
    ai: Optional[Tekoaly] = None
    ai_parannettu: Optional[TekoalyParannettu] = None
    over: bool = False
    message: str = "Peli käynnissä"

    def kirjaa_siirto(self, eka: str, toka: str):
        self.tuomari.kirjaa_siirto(eka, toka)

    def tulos(self) -> str:
        return str(self.tuomari)


games: Dict[str, GameState] = {}
WIN_THRESHOLD = 3


def reset_state():
  """Clear server-side sessions (used in tests)."""
  games.clear()

INDEX_TEMPLATE = """
<!doctype html>
<html lang="fi">
<head>
  <meta charset="utf-8">
  <title>Kivi-Paperi-Sakset</title>
  <style>
    :root { color-scheme: light; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #f6f7fb; color: #0f172a; }
    body { max-width: 720px; margin: 48px auto; padding: 0 20px; }
    h1 { font-size: 28px; margin-bottom: 8px; letter-spacing: -0.03em; }
    p { margin: 0 0 16px; color: #334155; }
    form { display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0 24px; }
    button { padding: 10px 14px; border: 1px solid #cbd5e1; background: white; border-radius: 10px; cursor: pointer; font-size: 15px; transition: all 120ms ease; }
    button:hover { border-color: #0ea5e9; box-shadow: 0 6px 20px rgba(15,23,42,0.06); }
    .card { background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; box-shadow: 0 10px 35px rgba(15,23,42,0.06); }
    .muted { color: #64748b; font-size: 14px; }
    .grid { display: grid; gap: 12px; }
    .row { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
    input[type=text] { padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 10px; font-size: 15px; width: 120px; }
    input[type=text]:focus { outline: 2px solid #0ea5e9; border-color: #0ea5e9; }
    .status { font-weight: 600; }
    .pill { display: inline-block; padding: 4px 10px; border-radius: 999px; background: #e0f2fe; color: #0369a1; font-size: 13px; }
    .score { display: flex; gap: 10px; font-weight: 600; color: #0f172a; }
    .score span { background: #eef2ff; padding: 6px 10px; border-radius: 10px; border: 1px solid #e2e8f0; }
  </style>
</head>
<body>
  <h1>Kivi · Paperi · Sakset</h1>
  <p>Minimalistinen web-versio. Siirrot: k = kivi, p = paperi, s = sakset (myös sanat käyvät).</p>

  <div class="card grid">
    <div class="row">
      <form action="{{ url_for('start') }}" method="post">
        <input type="hidden" name="mode" value="a" />
        <button type="submit">Ihminen vs ihminen</button>
      </form>
      <form action="{{ url_for('start') }}" method="post">
        <input type="hidden" name="mode" value="b" />
        <button type="submit">Ihminen vs tekoäly</button>
      </form>
      <form action="{{ url_for('start') }}" method="post">
        <input type="hidden" name="mode" value="c" />
        <button type="submit">Ihminen vs parannettu tekoäly</button>
      </form>
      {% if current_game %}
      <form action="{{ url_for('reset') }}" method="post">
        <button type="submit">Aloita alusta</button>
      </form>
      {% endif %}
    </div>

    {% if current_game %}
      <div class="grid">
        <div class="row" aria-live="polite">
          <span class="pill">Pelitila</span>
          <span class="status">{{ current_game.message }}</span>
        </div>
        <div class="score" aria-live="polite">
          <span>1. pelaaja: {{ current_game.tuomari.ekan_pisteet }}</span>
          <span>2. pelaaja: {{ current_game.tuomari.tokan_pisteet }}</span>
          <span>Tasapelit: {{ current_game.tuomari.tasapelit }}</span>
        </div>

        {% if not current_game.over %}
          <form action="{{ url_for('play') }}" method="post" class="grid">
            {% if current_game.mode == 'a' %}
              <div class="row">
                <label>Ensimmäinen:</label>
                <input name="p1" autocomplete="off" maxlength="1" />
                <label>Toinen:</label>
                <input name="p2" autocomplete="off" maxlength="1" />
              </div>
            {% else %}
              <div class="row">
                <label>Sinun siirtosi:</label>
                <input name="p1" autocomplete="off" maxlength="1" />
              </div>
            {% endif %}
            <button type="submit">Tee siirto</button>
          </form>
        {% else %}
          <p class="muted">Peli päättyi virheelliseen siirtoon. Aloita uusi peli painamalla yllä.</p>
        {% endif %}
      </div>
    {% else %}
      <p class="muted">Valitse pelimuoto aloittaaksesi.</p>
    {% endif %}
  </div>
</body>
</html>
"""


def _new_game(mode: str) -> GameState:
    if mode == "b":
        return GameState(mode=mode, ai=Tekoaly())
    if mode == "c":
        return GameState(mode=mode, ai_parannettu=TekoalyParannettu(10))
    return GameState(mode=mode)


def _ok_siirto(siirto: Optional[str]) -> bool:
  return normalize_siirto(siirto) is not None


def normalize_siirto(siirto: Optional[str]) -> Optional[str]:
  if not siirto:
    return None
  s = siirto.strip().lower()
  mapping = {
    "k": "k",
    "kivi": "k",
    "p": "p",
    "paperi": "p",
    "s": "s",
    "sakset": "s",
  }
  return mapping.get(s)


def _check_game_end(game: GameState):
  if game.tuomari.ekan_pisteet >= WIN_THRESHOLD:
    game.over = True
    game.message = "Ensimmäinen pelaaja voitti (5 voittoa)"
  elif game.tuomari.tokan_pisteet >= WIN_THRESHOLD:
    game.over = True
    if game.mode == "a":
      game.message = "Toinen pelaaja voitti (5 voittoa)"
    else:
      game.message = "Tietokone voitti (5 voittoa)"


def _current_game() -> Optional[GameState]:
    session_id = request.cookies.get("session_id")
    if session_id and session_id in games:
        return games[session_id]
    return None


@app.route("/", methods=["GET"])
def index():
    return render_template_string(INDEX_TEMPLATE, current_game=_current_game())


@app.route("/start", methods=["POST"])
def start():
    mode = request.form.get("mode", "")
    if mode not in {"a", "b", "c"}:
        return redirect(url_for("index"))

    game = _new_game(mode)
    session_id = uuid.uuid4().hex
    games[session_id] = game

    resp = make_response(redirect(url_for("index")))
    resp.set_cookie("session_id", session_id, httponly=True, samesite="Lax")
    return resp


@app.route("/play", methods=["POST"])
def play():
    game = _current_game()
    if not game or game.over:
        return redirect(url_for("index"))

    p1_raw = request.form.get("p1", "")
    p2_raw = request.form.get("p2", "")
    p1 = normalize_siirto(p1_raw)
    p2 = normalize_siirto(p2_raw)

    if game.mode == "a":
      if not (_ok_siirto(p1) and _ok_siirto(p2)):
        game.message = "Virheellinen siirto, käytä k/p/s"
        return redirect(url_for("index"))
      game.kirjaa_siirto(p1, p2)
      game.message = "Siirto kirjattu"
    elif game.mode == "b":
      if not _ok_siirto(p1):
        game.message = "Virheellinen siirto, käytä k/p/s"
        return redirect(url_for("index"))
      ai_move = game.ai.anna_siirto() if game.ai else "k"
      game.kirjaa_siirto(p1, ai_move)
      game.message = f"Tietokone valitsi: {ai_move}"
    else:  # mode c
      if not _ok_siirto(p1):
        game.message = "Virheellinen siirto, käytä k/p/s"
        return redirect(url_for("index"))
      ai_move = game.ai_parannettu.anna_siirto() if game.ai_parannettu else "k"
      game.kirjaa_siirto(p1, ai_move)
      game.ai_parannettu.aseta_siirto(p1)
      game.message = f"Tietokone valitsi: {ai_move}"

    _check_game_end(game)

    return redirect(url_for("index"))


@app.route("/reset", methods=["POST"])
def reset():
    session_id = request.cookies.get("session_id")
    if session_id and session_id in games:
        del games[session_id]
    resp = make_response(redirect(url_for("index")))
    resp.delete_cookie("session_id")
    return resp


def main():
    app.run(debug=True)


if __name__ == "__main__":
    main()
