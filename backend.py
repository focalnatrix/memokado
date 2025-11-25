import json
import uuid
import time
import os

class Flashcard:
    def __init__(self, front, back, card_id=None, created_at=None):
        self.id = card_id or str(uuid.uuid4()) 
        self.front = front
        self.back = back 
        self.created_at = int(time.time())
        self.last_score = 0

class Deck:
    def __init__(self, name):
        self.name = name
        self.cards = []
        self.score = 0

    def add_card(self, card: Flashcard):
        self.cards.append(card)

    def remove_card(self, card_id):
        card = self.get_card(card_id)
        if card:
            self.cards.remove(card)
            return True
        return False

    def get_card(self, card_id):
        # Binary search 
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

    def sort_by_score(self):
        self.cards = self.quicksort(self.cards, key=lambda c: c.last_score)

    def quicksort(self, cards, key):
        if cards is None:
            cards = self.cards

        if len(cards) <= 1:
            return cards
        
        pivot = key(cards[len(cards) // 2])
        left = [c for c in cards if key(c) < pivot]
        mid = [c for c in cards if key(c) == pivot]
        right = [c for c in cards if key(c) > pivot]
        return self.quicksort(left, key) + mid + self.quicksort(right, key)

    def rate_card(self, card: Flashcard, rating):
        card.last_score = rating
        self.score += rating

    def insert_card_sorted(self, card):
        # Uses binary search to find correct index
        low, high = 0, len(self.cards)
        while low < high:
            mid = (low + high) // 2
            if self.cards[mid].last_score < card.last_score:
                low = mid + 1
            else:
                high = mid
        self.cards.insert(low, card)

    def max_score(self):
        """
        Returns the highest possible score for this deck,
        assuming all cards were rated 'Easy' (2 points each).
        """
        return len(self.cards) * 2

    def save_to_file(self, filename):
        data = {
            "name": self.name,
            "score": self.score,
            "cards": [self._card_to_dict(c) for c in self.cards]
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

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
                    card_id=card_data["id"],
                    created_at=card_data.get("created_at")
                )
                card.last_score = card_data.get("last_score", 0)
                deck.cards.append(card)
            return deck

    @staticmethod
    def _card_to_dict(card: Flashcard):
        return {
            "id": card.id,
            "front": card.front,
            "back": card.back,
            "created_at": card.created_at,
            "last_score": getattr(card, "last_score", 0)
        }


def create_card(front, back):
    return Flashcard(front, back)