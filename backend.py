import json
import uuid
import os


# ======================================================
# FLASHCARD CLASS
# ======================================================
class Flashcard:
    """
    Represents a single flashcard.
    Stores:
      - front/back text
      - SM-2 values (interval, ease_factor, repetitions)
    """

    def __init__(self, front, back, card_id=None):
        self.id = card_id or str(uuid.uuid4())  # unique ID
        self.front = front
        self.back = back
        self.repetitions = 0      # number of consecutive successful reviews
        self.interval = 1         # review interval (logical, not date-based)
        self.ease_factor = 2.5    # SM-2 ease factor

    def apply_rating(self, rating):
        """
        Update this card using simplified SM-2 algorithm.
        Ratings:
            0 = Again
            1 = Hard
            2 = Easy
        """

        if rating == 0:  # Forgot
            self.repetitions = 0
            self.interval = 1
            self.ease_factor = max(1.3, self.ease_factor - 0.2)
        elif rating == 1:  # Hard
            self.repetitions += 1
            self.interval = max(1, int(self.interval * 1.2))
            self.ease_factor = max(1.3, self.ease_factor - 0.05)
        elif rating == 2:  # Easy
            self.repetitions += 1
            if self.repetitions == 1:
                self.interval = 1
            elif self.repetitions == 2:
                self.interval = 3
            else:
                self.interval = int(self.interval * self.ease_factor)
            self.ease_factor = min(2.5, self.ease_factor + 0.1)


# ======================================================
# DECK CLASS
# ======================================================
class Deck:
    """
    Represents a collection of flashcards.
    Provides methods to:
      - add/remove/search cards
      - sort cards (QuickSort)
      - JSON save/load
      - track score
    """

    def __init__(self, name):
        self.name = name
        self.cards = []      # list of Flashcard objects
        self.score = 0       # total score from user ratings

    # --------------------------------------------------
    # ADD A FLASHCARD
    # QuickSort is applied here to maintain sorted order
    # --------------------------------------------------
    def add_card(self, card: Flashcard):
        self.cards.append(card)
        self.sort_by_id()  # maintain sorted order for binary search

    # --------------------------------------------------
    # REMOVE A FLASHCARD BY ID
    # --------------------------------------------------
    def remove_card(self, card_id):
        card = self.get_card(card_id)
        if card:
            self.cards.remove(card)
            return True
        return False

    # --------------------------------------------------
    # FIND A CARD BY ID USING BINARY SEARCH
    # Precondition: self.cards is sorted by id
    # --------------------------------------------------
    def get_card(self, card_id):
        # Binary search implementation
        low = 0
        high = len(self.cards) - 1

        while low <= high:
            mid = (low + high) // 2
            mid_id = self.cards[mid].id

            if mid_id == card_id:
                return self.cards[mid]
            elif mid_id < card_id:
                low = mid + 1
            else:
                high = mid - 1
        return None

    # --------------------------------------------------
    # SORT CARDS BY ID (for binary search)
    # QuickSort applied here
    # --------------------------------------------------
    def sort_by_id(self):
        self.cards = self._quicksort(self.cards, key=lambda c: c.id)

    # --------------------------------------------------
    # QUICK SORT IMPLEMENTATION
    # --------------------------------------------------
    @staticmethod
    def _quicksort(cards, key):
        if len(cards) <= 1:
            return cards
        pivot = key(cards[len(cards) // 2])
        left = [c for c in cards if key(c) < pivot]
        mid = [c for c in cards if key(c) == pivot]
        right = [c for c in cards if key(c) > pivot]
        return Deck._quicksort(left, key) + mid + Deck._quicksort(right, key)

    # --------------------------------------------------
    # RATE CARD (apply rating & update score)
    # --------------------------------------------------
    def rate_card(self, card: Flashcard, rating):
        """
        Applies a rating to a card and updates the deck score.
        Easy = 2 points, Hard = 1 point, Again = 0 points
        """
        card.apply_rating(rating)

        if rating == 2:
            self.score += 2
        elif rating == 1:
            self.score += 1
        # Again (0) adds 0 points

    # --------------------------------------------------
    # HIGHEST POSSIBLE SCORE
    # --------------------------------------------------
    def max_score(self):
        """
        Returns the highest possible score for this deck,
        assuming all cards were rated 'Easy' (2 points each).
        """
        return len(self.cards) * 2

    # --------------------------------------------------
    # SAVE DECK TO JSON
    # --------------------------------------------------
    def save_to_file(self, filename):
        data = {
            "name": self.name,
            "score": self.score,
            "cards": [self._card_to_dict(c) for c in self.cards]
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # --------------------------------------------------
    # LOAD DECK FROM JSON
    # --------------------------------------------------
    @classmethod
    def load_from_file(cls, filename):
        if not os.path.exists(filename):
            return None
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            deck = cls(data["name"])
            deck.score = data.get("score", 0)
            for card_data in data["cards"]:
                card = Flashcard(
                    front=card_data["front"],
                    back=card_data["back"],
                    card_id=card_data["id"]
                )
                card.repetitions = card_data["repetitions"]
                card.interval = card_data["interval"]
                card.ease_factor = card_data["ease_factor"]
                deck.cards.append(card)
            return deck

    # --------------------------------------------------
    # HELPER TO CONVERT CARD TO DICT FOR JSON
    # --------------------------------------------------
    @staticmethod
    def _card_to_dict(card: Flashcard):
        return {
            "id": card.id,
            "front": card.front,
            "back": card.back,
            "repetitions": card.repetitions,
            "interval": card.interval,
            "ease_factor": card.ease_factor
        }


# ======================================================
# HELPER FUNCTION TO CREATE A NEW CARD
# ======================================================
def create_card(front, back):
    """
    Helper to create a new Flashcard object
    with default SM-2 values.
    """
    return Flashcard(front, back)