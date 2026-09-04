# Weight checkpoints

This directory holds **JSON** weight checkpoints for Q-learning and SARSA.

## Layout

| Path | Purpose |
|------|---------|
| `q_learning_alpha0.3.json` | Default / latest Q-learning checkpoint (local) |
| `sarsa_alpha0.2.json` | Default / latest SARSA checkpoint (local) |
| `history/` | Optional timestamped copies written on each save |
| `.gitkeep` / this README | Tracked in git so the folder exists in a fresh clone |

`*.json` files and `history/` are listed in the repo `.gitignore` — train locally; do not commit large blobs unless you intentionally force-add them.

## Format

Produced by `ai_players/weight_io.py`:

- `format_version`: currently `1`
- `feature_dim`: **must be 26** (`FEATURE_DIM` in `feature_utils`)
- `algorithm`: `"q-learning"` or `"sarsa"`
- `alpha`, `gamma`, `epsilon`, `games_trained`
- `weights`: list of 26 floats
- `feature_names`: optional, from `FEATURE_NAMES`

Loaders reject mismatched `feature_dim` with a clear error.

## Obsolete logs (removed)

These old text append logs are **incompatible** with FEATURE_DIM=26 and were deleted from the repo:

- `q_weights_alpha03_0`, `q_weights_alpha05_0`
- `sarsa_weights_alpha02_0`, `sarsa_weights_alpha05_0`
- `weights_0`
- `alpha_vs_q_0`, `q_vs_alpha_0`, `sarsa_vs_q_alpha_02_0`

Do not try to parse them. Retrain with `training_q.py` / `training_sarsa.py`.

## Usage

```bash
cd Game_logic
python3 training_q.py --games 100 --save-every 50
python3 gomoku.py --player2 q-learning --weights-p2 weights/q_learning_alpha0.3.json
```

If `--weights-p*` is omitted, `gomoku.py` auto-loads a matching `weights/{algo}_*.json` when present.
