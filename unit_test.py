# test_flashcards.py
import unittest
from backend import Flashcard, Deck

class TestFlashcardDeck(unittest.TestCase):

    def setUp(self):
        # Runs before each test
        self.deck = Deck("Test Deck")
        self.card1 = Flashcard("Front 1", "Back 1")
        self.card2 = Flashcard("Front 2", "Back 2")
        self.card3 = Flashcard("Front 3", "Back 3")

    def test_insert_card_sorted(self):
        # Insert cards with different scores
        self.card1.last_score = 2
        self.card2.last_score = 0
        self.card3.last_score = 1

        self.deck.insert_card_sorted(self.card1)
        self.deck.insert_card_sorted(self.card2)
        self.deck.insert_card_sorted(self.card3)

        scores = [c.last_score for c in self.deck.cards]
        self.assertEqual(scores, [0, 1, 2], "Cards should be sorted by last_score after insertion")

    def test_quicksort(self):
        # Add unsorted cards
        self.card1.last_score = 2
        self.card2.last_score = 0
        self.card3.last_score = 1
        self.deck.cards = [self.card1, self.card2, self.card3]

        # Sort using quicksort
        self.deck.sort_by_score()
        scores = [c.last_score for c in self.deck.cards]
        self.assertEqual(scores, [0, 1, 2], "Quicksort should sort cards by last_score")

    def test_rate_card_updates_score(self):
        self.deck.cards = [self.card1, self.card2]
        self.deck.rate_card(self.card1, 1)
        self.deck.rate_card(self.card2, 2)

        self.assertEqual(self.deck.score, 3, "Deck score should sum individual card ratings")
        self.assertEqual(self.deck.cards[-1].last_score, 2, "Highest scored card should be last after sort")

    def test_study_session_score_reset(self):
        # Mimic a deck with previous scores
        self.card1.last_score = 2
        self.card2.last_score = 1
        self.deck.cards = [self.card1, self.card2]

        # Simulate starting a new study session
        self.deck.score = 0
        for card in self.deck.cards:
            card.last_score = 0

        # Simulate rating during session
        ratings = [2, 1]  # simulate user ratings
        for card, rating in zip(self.deck.cards, ratings):
            self.deck.rate_card(card, rating)
            
        self.deck.sort_by_score()

        self.assertEqual(self.deck.score, sum(ratings), "Deck score should reflect new study session ratings")
        self.assertEqual([c.last_score for c in self.deck.cards], [1, 2], "Cards should be sorted by updated score")

if __name__ == "__main__":
    unittest.main()
