# Final Project for CS322 Artificial Intelligence

This project was created as a final project for my CS322 course during my senior-year spring semester.

Required implementation:

- Open-information game with no dice or chance elements (Gomoku / five-in-a-row)
- Human vs human play
- Two AI players:
  - Alpha–beta pruning
  - Reinforcement-learning players (linear function approximation) that can be trained: **Q-learning** and **SARSA**

A GUI was not required, but the main game uses **pygame**. AI player classes enforce types where helpful; `gomoku.py` itself is more loosely typed.

---

## Overview

| Piece | Role |
|-------|------|
| `Game_logic/gomoku.py` | Pygame GUI — play human / AI combinations |
| `Game_logic/training_q.py` | Self-play Q-learning trainer → JSON checkpoints |
| `Game_logic/training_sarsa.py` | Self-play SARSA trainer → JSON checkpoints |
| `ai_players/` | Agents + `feature_utils` (FEATURE_DIM=26) + `weight_io` |
| `Game_logic/weights/` | Local JSON checkpoints (gitignored blobs; README kept) |

---

## Setup

Run these from the **repository root**:

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Important:** start the game and trainers from `Game_logic/` so pygame can find `./sources/pics/...` assets:

```bash
cd Game_logic
```

---

## Play

From `Game_logic/`:

```bash
# Human vs Q-learning (default p2)
python3 gomoku.py --player1 human --player2 q-learning

# Human vs human
python3 gomoku.py --player1 human --player2 human

# SARSA vs Q-learning
python3 gomoku.py --player1 sarsa --player2 q-learning

# Explicit checkpoints
python3 gomoku.py --player1 human --player2 q-learning \
  --weights-p2 weights/q_learning_alpha0.3.json
```

### Weight loading (`gomoku.py`)

| Flag | Meaning |
|------|---------|
| `--weights-p1 PATH` | JSON checkpoint for player 1 (q-learning / sarsa) |
| `--weights-p2 PATH` | JSON checkpoint for player 2 |

If a flag is omitted and a matching file exists under `weights/` (`q_learning_*.json` or `sarsa_*.json`), that file is **auto-loaded**. Otherwise the agent uses `DEFAULT_WEIGHTS` from `feature_utils`.

Use `python3 gomoku.py --help` for the full flag list.

---

## Train Q-learning

From `Game_logic/` (board display off by default for speed):

```bash
# Smoke test
python3 training_q.py --games 50 --save-every 10 --update-every 10

# Longer run (default --games is large; checkpoints overwrite the latest file)
python3 training_q.py --games 10000 --save-every 100 --update-every 100

# Resume / custom output
python3 training_q.py --resume weights/q_learning_alpha0.3.json --games 5000
python3 training_q.py --out weights/q_learning_alpha0.3.json --games 1000
```

Defaults write to `weights/q_learning_alpha0.3.json` and optionally snapshot under `weights/history/`.

On start the trainer prints `feature_dim` and the output path.

---

## Train SARSA

Same CLI as Q-learning; default checkpoint is `weights/sarsa_alpha0.2.json`:

```bash
python3 training_sarsa.py --games 50 --save-every 10 --update-every 10
python3 training_sarsa.py --games 10000 --save-every 100
python3 training_sarsa.py --resume weights/sarsa_alpha0.2.json --games 5000
```

Shared flags: `--games`, `--save-every`, `--update-every`, `--show-board`, `--resume PATH`, `--out PATH`, `--no-visualize`.

---

## Weight files

Checkpoints are **JSON** (see `ai_players/weight_io.py`), not free-form text logs.

```json
{
  "format_version": 1,
  "feature_dim": 26,
  "algorithm": "q-learning",
  "alpha": 0.3,
  "gamma": 1.0,
  "epsilon": 0.2,
  "games_trained": 1000,
  "weights": [ "... length FEATURE_DIM floats ..." ],
  "feature_names": ["bias", "player_five", "..."]
}
```

- **`feature_dim` must equal `FEATURE_DIM` (26)** from `feature_utils`. A mismatch raises a clear `ValueError`.
- Latest checkpoints live under `Game_logic/weights/` (paths relative to `Game_logic` when that is the cwd).
- `*.json` checkpoints and `weights/history/` are **gitignored** so trained blobs stay local. The directory’s `README.md` and `.gitkeep` are committed.
- **Obsolete / deleted:** old append-only text logs such as `q_weights_alpha03_0`, `q_weights_alpha05_0`, `sarsa_weights_alpha02_0`, `sarsa_weights_alpha05_0`, `weights_0`, `alpha_vs_q_0`, `q_vs_alpha_0`, `sarsa_vs_q_alpha_02_0`. Those pre-FEATURE_DIM=26 dumps are **not loadable** and must not be used. Retrain to produce JSON checkpoints.

More detail: [`Game_logic/weights/README.md`](Game_logic/weights/README.md).

---

## Features

Linear RL agents score afterstates with a **26-dimensional** feature vector (fives, open/sleep/broken fours and threes, forks, center bias, immediate wins, …). See `ai_players/feature_utils.py` (`FEATURE_NAMES`, `FEATURE_DIM`, `DEFAULT_WEIGHTS`, `compute_features`).

Unit checks: `python3 test_features.py` from the repo root (with `ai_players` / `Game_logic` on `PYTHONPATH` as needed).

---

## Project layout

```
A.I-final-project/
├── README.MD
├── requirements.txt
├── test_features.py
├── ai_players/
│   ├── alpha_beta_pruning.py
│   ├── feature_utils.py
│   ├── q_learning.py
│   ├── sarsa_agent.py
│   └── weight_io.py          # save/load JSON checkpoints
├── Game_logic/
│   ├── gomoku.py             # pygame UI
│   ├── game_board.py
│   ├── training_q.py
│   ├── training_sarsa.py
│   ├── alpha_vs_q.py / q_vs_alpha.py / sarsa_vs_q.py
│   ├── sources/pics/         # board & stone images
│   └── weights/              # local JSON checkpoints (+ README)
├── utility/                  # e.g. Node for alpha–beta trees
└── .gitignore
```

### Utility folder

Contains helpers for modular code (e.g. `node.py` for alpha–beta search trees: children + game state).

### AI players folder

- **Alpha–beta** — adversarial search
- **Q-learning / SARSA** — linear TD learners over `feature_utils` features
- **weight_io** — versioned JSON checkpoints with `feature_dim` validation
