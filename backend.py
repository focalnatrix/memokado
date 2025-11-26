import json
import uuid
import time
import os

class Flashcard:
    def __init__(self, front, back, card_id=None, created_at=None):
        self.id = card_id or str(uuid.uuid4()) 
        self.front = front
        self.back = back 
        self.last_score = 0

class Deck:
    def __init__(self, name):
        self.name = name
        self.score = 0

        # The list that gets sorted by score every session
        self.cards = []

        # Hash map to store initial sorting order
        self.card_map = {}

    def add_card(self, card: Flashcard):
        self.cards.append(card)
        self.card_map[card.id] = card

    def remove_card(self, card_id):
        card = self.card_map.pop(card_id, None)
        if card:
            self.cards.remove(card)
            return True
        return False

    def get_card(self, card_id):
        return self.card_map.get(card_id)

    def sort_by_score(self):
        def get_last_score(card):
            return card.last_score
    
        self.cards = self.quicksort(self.cards, score=get_last_score)

    def quicksort(self, cards, score):
        # Sorts cards by their score

        if cards is None:
            cards = self.cards

        if len(cards) <= 1:
            return cards
        
        pivot = score(cards[len(cards) // 2])
        left = [c for c in cards if score(c) < pivot]
        mid = [c for c in cards if score(c) == pivot]
        right = [c for c in cards if score(c) > pivot]
        return self.quicksort(left, score) + mid + self.quicksort(right, score)

    def rate_card(self, card: Flashcard, rating):
        card.last_score = rating
        self.score += rating

    def insert_card_sorted(self, card):
        # Uses binary search to find correct index to insert new card
        low, high = 0, len(self.cards)
        while low < high:
            mid = (low + high) // 2
            if self.cards[mid].last_score < card.last_score:
                low = mid + 1
            else:
                high = mid
        self.cards.insert(low, card)

    def max_score(self):
        '''
        Returns the highest possible score for this deck
        assuming all cards were rated 'Easy' (2 points each)
        '''

        return len(self.cards) * 2

    '''
    Code for saving/loading JSON files
    '''
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
                )
                card.last_score = card_data.get("last_score", 0)
                deck.cards.append(card)
                deck.card_map[card.id] = card
            return deck

    @staticmethod
    def _card_to_dict(card: Flashcard):
        return {
            "id": card.id,
            "front": card.front,
            "back": card.back,
            "last_score": getattr(card, "last_score", 0)
        }