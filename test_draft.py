import unittest

from draft import Game, draft_board
from run import board_for


POOL = tuple(f"C{i:02d}" for i in range(1, 26))
FIRST_GAME = Game(POOL[:5], POOL[5:10])


class DraftBoardTests(unittest.TestCase):
    def test_game_two_excludes_prior_picks_from_both_teams(self):
        board = draft_board(POOL, (FIRST_GAME,), picks=(POOL[10],), bans=(POOL[11],))
        self.assertEqual(board["fearless_locked"], POOL[:10])
        self.assertEqual(board["picked"], (POOL[10],))
        self.assertEqual(board["banned"], (POOL[11],))
        self.assertEqual(board["available"], POOL[12:])

    def test_standard_mode_releases_previous_picks(self):
        board = draft_board(POOL, (FIRST_GAME,), fearless=False, picks=(POOL[0],))
        self.assertEqual(board["fearless_locked"], ())
        self.assertEqual(board["available"], POOL[1:])

    def test_rejects_locked_and_duplicate_current_choices(self):
        with self.assertRaisesRegex(ValueError, "already locked"):
            draft_board(POOL, (FIRST_GAME,), picks=(POOL[0],))
        with self.assertRaisesRegex(ValueError, "known and distinct"):
            draft_board(POOL, (), picks=(POOL[0],), bans=(POOL[0],))

    def test_rejects_history_that_could_not_happen_under_selected_rule(self):
        with self.assertRaisesRegex(ValueError, "Game 2 reuses"):
            draft_board(POOL, (FIRST_GAME, FIRST_GAME))

    def test_imported_sides_stay_separate_and_the_fifth_game_closes_the_board(self):
        pool = [f"C{i:02d}" for i in range(1, 71)]
        history = [
            {"blue": pool[offset:offset + 5], "red": pool[offset + 5:offset + 10]}
            for offset in range(0, 40, 10)
        ]
        state = {"pool": pool, "mode": "fearless", "history": history,
                 "blue": pool[40:45], "red": pool[45:50], "bans": pool[50:60]}
        active = board_for(state)
        self.assertFalse(active["complete"])
        self.assertEqual(active["red"], tuple(pool[45:50]))
        self.assertEqual(len(active["available"]), 10)
        history.append({"blue": state["blue"], "red": state["red"]})
        finished = board_for({**state, "blue": [], "red": [], "bans": []})
        self.assertTrue(finished["complete"])
        self.assertEqual(finished["game"], 5)
        self.assertEqual(len(finished["fearless_locked"]), 50)
        with self.assertRaisesRegex(ValueError, "series is complete"):
            board_for(state)


if __name__ == "__main__":
    unittest.main()
