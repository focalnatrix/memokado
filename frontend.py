import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import uuid
import backend

class FlashcardApp:
    def __init__(self):
        self.decks = []
        self.current_deck = None
        self.deck_rows_frame = None

        self.main_window = tk.Tk()
        self.main_window.title("Flashcards")

        self.main_window.withdraw()
        self.center_window(self.main_window, 700, 500)
        self.main_window.deiconify()
    
        self.main_menu()
        self.main_window.mainloop()

    def main_menu(self):
        self.main_frame = ttk.Frame(self.main_window, padding="50")
        self.main_frame.pack(fill="both", expand=True)

        # Text here should be some welcoming text or whatever
        ttk.Label(self.main_frame, text="Welcome to our app!!!!!", 
                  font=("Arial", 16, "bold")).pack(padx=10, pady=10)

        self.decks_container = ttk.Frame(self.main_frame)
        self.decks_container.pack(fill="both", expand=True)

        self.show_decks(self.decks_container)

        ttk.Button(self.main_frame, text="Create New Deck", 
                   command=self.create_deck_menu).pack(pady=2)
        ttk.Button(self.main_frame, text="Add New Card", 
                   command=self.create_card_menu).pack(pady=2)

    def create_deck_menu(self):
        self.create_deck_window = tk.Toplevel(self.main_window)
        self.create_deck_window.title("Create Deck")

        self.create_deck_window.withdraw()
        self.center_window(self.create_deck_window, 300, 200)
        self.create_deck_window.deiconify()
        
        main_frame = ttk.Frame(self.create_deck_window, padding="50")
        main_frame.pack(anchor="center", expand=True)

        main_frame.columnconfigure(0, weight=1)

        '''
        Allows user to input deck name
        '''
        ttk.Label(main_frame, text="Deck Name", font=("Arial", 14, "bold")).grid(
            row=0, column=0, sticky=tk.W ,padx=(0,5), pady=(0,5))

        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=1, column=0, sticky=tk.W, pady=(0,15))
        self.name_entry.focus_set()

        '''
        Create deck
        '''
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2)

        ttk.Button(button_frame, text="Create This Deck", command=self.create_deck).grid(row=0, column=0)     

    def create_deck(self):
        deck_name = self.name_entry.get()

        if not deck_name:
            messagebox.showerror("Error", "A deck needs a name!")
            return
        
        try:
            new_deck = backend.Deck(deck_name)
            self.decks.append(new_deck)

            self.create_deck_window.destroy()

            if self.no_decks_label:
                self.no_decks_label.destroy()
                self.no_decks_label = None

            if len(self.decks) >= 1:
                ttk.Label(self.deck_rows_frame, text="Deck Name", font=("Arial", 13, "bold")).grid(
                    row=0, column=0, padx=5, pady=3, sticky="w")
                ttk.Label(self.deck_rows_frame, text="Cards", font=("Arial", 13, "bold")).grid(
                    row=0, column=1, padx=5, pady=3)
                ttk.Label(self.deck_rows_frame, text="Last Score", font=("Arial", 13, "bold")).grid(
                    row=0, column=2, padx=5, pady=3)
                ttk.Label(self.deck_rows_frame, text="Actions", font=("Arial", 13, "bold")).grid(
                    row=0, column=3, padx=5, pady=3)
            
            row_index = len(self.decks)
            self._add_deck_to_table(new_deck, row_index)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create deck: {str(e)}") 

    def show_decks(self, parent_frame):
        wrapper = ttk.Frame(parent_frame)
        wrapper.pack(pady=2)
        wrapper.pack(anchor="center")

        self.deck_rows_frame = ttk.Frame(wrapper)
        self.deck_rows_frame.pack(anchor="w")

        self.no_decks_label = None

        if not self.decks:
            self.no_decks_label = ttk.Label(
                self.deck_rows_frame, 
                text="No decks available. Create a new deck to get started!", 
                foreground="gray", anchor="center"
                )
            self.no_decks_label.grid(row=1, column=0, columnspan=2, pady=10)
            return
                
        for i, deck in enumerate(self.decks):
            self._add_deck_to_table(deck, i + 1)

    def _add_deck_to_table(self, deck, row_index):
        '''
        Loads each deck into the main menu table
        '''
        ttk.Label(self.deck_rows_frame, text=deck.name).grid(
                row=row_index, column=0, padx=5, pady=2, sticky="w")
        
        '''
        Shows number of cards in the deck
        '''
        card_count = ttk.Label(self.deck_rows_frame, text=len(deck.cards))
        card_count.grid(row=row_index, column=1, padx=5, pady=2)
        deck._card_count = card_count

        '''
        Shows the deck's previous score
        '''
        prev_score = ttk.Label(self.deck_rows_frame, text=deck.score)
        prev_score.grid(row=row_index, column=2, padx=5, pady=2)
    
        '''
        Action buttons
        '''
        button_frame = ttk.Frame(self.deck_rows_frame)
        button_frame.grid(row=row_index, column=3, padx=10, pady=2)
        
        ttk.Button(button_frame, text="Study", command=lambda d=deck: self.study_deck(d)).pack(
            side="left", padx=2)
        ttk.Button(button_frame, text="Edit", command=lambda d=deck: self.edit_deck(d)).pack(
            side="left", padx=2)
        ttk.Button(button_frame, text="Delete", command=lambda d=deck: self.delete_deck(d)).pack(
            side="left", padx=2)

    def create_card_menu(self):
        if not self.decks:
            messagebox.showerror("Error", "You need to create a deck before adding cards!")
            return
        
        '''
        General window setup
        '''
        self.create_card_window = tk.Toplevel(self.main_window)
        self.create_card_window.title("Create Card")

        self.create_card_window.withdraw()
        self.center_window(self.create_card_window, 600, 400)
        self.create_card_window.deiconify()

        main_frame = ttk.Frame(self.create_card_window, padding="20")
        main_frame.pack(anchor="center", expand=True)

        '''
        Allows user to pick a deck to add the card to
        '''
        option_frame = ttk.Frame(main_frame)
        option_frame.grid(row=0, column=0, sticky="w", pady=(0,15))

        options = [deck.name for deck in self.decks]
        self.deck_entry = tk.StringVar()
        self.deck_entry.set(options[0])

        ttk.Label(option_frame, text="Select Deck", font=("Arial", 14, "bold")).grid(
            row=0, column=0, padx=(0,10), sticky="w")
        deck_menu = ttk.OptionMenu(option_frame, self.deck_entry, options[0], *options)
        deck_menu.grid(row=0, column=1, padx=(0,10))

        '''
        Allows user to customize front and back parts of card
        '''
        ttk.Label(main_frame, text="Front", font=("Arial", 14, "bold")).grid(
            row=1, column=0, sticky="w", padx=(0,5), pady=(0,5))

        self.front_entry = tk.Text(main_frame, height=5, width=50)
        self.front_entry.grid(row=2, column=0, pady=(0,15))
        self.front_entry.focus_set()

        ttk.Label(main_frame, text="Back", font=("Arial", 14, "bold")).grid(
            row=3, column=0, sticky="w", padx=(0,5), pady=(0,5))

        self.back_entry = tk.Text(main_frame, height=5, width=50)
        self.back_entry.grid(row=4, column=0, pady=(0,15))

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0)

        ttk.Button(button_frame, text="Create Card", command=self.create_card).grid(row=0, column=0)

    def create_card(self):
        front = self.front_entry.get("1.0", "end")
        back = self.back_entry.get("1.0", "end")
        deck = self.deck_entry.get()

        if not front or not back:
            messagebox.showerror("Error", "Both front and back parts must be filled!")
            return
        
        selected_deck = next((d for d in self.decks if d.name == deck), None)
        
        try:
            new_card = backend.Flashcard(front, back)
            selected_deck.add_card(new_card)

            if hasattr(selected_deck, "_card_count"):
                selected_deck._card_count.config(text=str(len(selected_deck.cards)))

            messagebox.showinfo("Success", "Card added successfully!")

            self.create_card_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create card: {str(e)}")

    def study_deck(self, deck):
        if not deck.cards:
            messagebox.showerror("Error", "This deck has no cards to study!")
            return
        
        self.study_cards = list(deck.cards)
        self.study_cards_index = 0
        self.current_deck = deck
        self.showing_front = True
        
        self.study_deck_window = tk.Toplevel(self.main_window)
        self.study_deck_window.title(f"{deck.name}")
        
        self.study_deck_window.withdraw()
        self.center_window(self.study_deck_window, 500, 400)
        self.study_deck_window.deiconify()

        # Frame for card front 
        self.card_text = ttk.Label(self.study_deck_window, 
                                   text="", font=("Arial", 16), wraplength=450)
        self.card_text.pack(pady=30)

        # Frame for card back
        self.card_answer = ttk.Label(self.study_deck_window, 
                                   text="", font=("Arial", 16), wraplength=450)

        # Frame for rating buttons
        self.rating_frame = ttk.Frame(self.study_deck_window)
        for i, text in enumerate(["Again", "Okay", "Good"]):
            ttk.Button(self.rating_frame, text=text, 
                    command=lambda rating=i: self.rate_card(rating)).pack(side="left", padx=5)

        # Show first card front in deck
        self.show_card_front()

        # When clicking space, it reveals the answer
        self.study_deck_window.unbind("<space>")
        self.study_deck_window.bind("<space>", self.on_space)

    def on_space(self, event):
        if self.study_cards_index >= len(self.study_cards):
            return
        
        if self.showing_front:
            self.show_card_back()
        else:
            return

    def show_card_front(self):
        if not (0 <= self.study_cards_index < len(self.study_cards)):
            return
    
        card = self.study_cards[self.study_cards_index]
        self.card_text.config(text=card.front)

        self.card_answer.pack_forget()
        self.rating_frame.pack_forget()

        self.card_answer.config(text="")
        
        self.showing_front = True

    def show_card_back(self):
        if not (0 <= self.study_cards_index < len(self.study_cards)):
            return
    
        card = self.study_cards[self.study_cards_index]
        self.card_answer.config(text=card.back)
        self.card_answer.pack(pady=30)
        self.rating_frame.pack(pady=30)

        self.showing_front = False

    def rate_card(self, rating):
        if not (0 <= self.study_cards_index < len(self.study_cards)):
            return
    
        card = self.study_cards[self.study_cards_index]

        if hasattr(self.current_deck, "rate_card"):
            self.current_deck.rate_card(card, rating)
        else:
            card.rating = rating
            self.current_deck.score += (1 if rating >= 2 else 0)

        self.study_cards_index += 1

        if self.study_cards_index < len(self.study_cards):
            self.show_card_front()
        else:
            self.finish_study()

    def finish_study(self):
        self.card_answer.pack_forget()
        self.rating_frame.pack_forget()

        self.study_deck_window.unbind("<space>")

        self.card_text.config(text="Congratulations!")
        self.card_answer.config(text=f"Score: {getattr(self.current_deck, 'score', 0)}")
        self.card_answer.pack(pady=10)

        self.showing_front = False

        try:
            self.study_deck_window.unbind("<space>")
        except Exception:
            pass

    def close_study_window(self):
        self.study_deck_window.unbind("<space>")
        self.study_deck_window.destroy()

    def edit_deck(self, deck):
        # TODO
        '''
        Two sections
        1. Edit deck details (name, speed)
        2. View/Add/Edit/Delete cards in the deck
        '''
        pass

    def delete_deck(self, deck):
        # TODO
        pass  

    def center_window(self, window, width=None, height=None):
        window.update_idletasks()
        w = width if width else window.winfo_width()
        h = height if height else window.winfo_height()
        ws = window.winfo_screenwidth()
        hs = window.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        window.geometry(f'{w}x{h}+{x}+{y}')

FlashcardApp()