"""Track a best-of series using an explicit champion pool and draft rules."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Game:
    blue_picks: tuple[str, ...]
    red_picks: tuple[str, ...]


def draft_board(
    pool: tuple[str, ...],
    history: tuple[Game, ...],
    *,
    picks: tuple[str, ...] = (),
    bans: tuple[str, ...] = (),
    fearless: bool = True,
) -> dict[str, tuple[str, ...]]:
    """Return mutually exclusive lists for the current game.

    Hard Fearless removes both teams' prior picks. Prior bans never carry over.
    The input contains games in the current series only.
    """
    known = set(pool)
    if not known or len(known) != len(pool):
        raise ValueError("Supply a champion pool with unique entries.")

    locked: set[str] = set()
    for index, game in enumerate(history, start=1):
        played = game.blue_picks + game.red_picks
        if len(game.blue_picks) != 5 or len(game.red_picks) != 5:
            raise ValueError(f"Game {index} must have five picks per side.")
        if len(set(played)) != len(played) or not set(played) <= known:
            raise ValueError(f"Game {index} contains unknown or duplicate picks.")
        if fearless and locked.intersection(played):
            raise ValueError(f"Game {index} reuses a champion under Hard Fearless.")
        if fearless:
            locked.update(played)

    current = picks + bans
    if len(picks) > 10 or len(bans) > 10:
        raise ValueError("A current game supports up to ten picks and ten bans.")
    if len(set(current)) != len(current) or not set(current) <= known:
        raise ValueError("Current picks and bans must be known and distinct.")
    if locked.intersection(current):
        raise ValueError("A current pick or ban is already locked by Hard Fearless.")
    return {
        "fearless_locked": tuple(champion for champion in pool if champion in locked),
        "picked": picks,
        "banned": bans,
        "available": tuple(champion for champion in pool if champion not in locked and champion not in current),
    }
