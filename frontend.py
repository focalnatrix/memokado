import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import backend

class FlashcardApp:
    def __init__(self):
        self.decks = []
        self.current_deck = None
        self.deck_rows_frame = None
        self.no_decks_label = None

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
        ttk.Label(self.main_frame, text="Welcome to Memokado!", 
                  font=("Arial", 20, "bold")).pack(padx=10, pady=10)

        self.decks_container = ttk.Frame(self.main_frame)
        self.decks_container.pack(fill="both", expand=True)

        self.show_decks(self.decks_container)

        ttk.Button(self.main_frame, text="Create New Deck", 
                   command=self.create_deck_menu).pack(pady=2)
        ttk.Button(self.main_frame, text="Add New Card", 
                   command=self.create_card_menu).pack(pady=2)
        ttk.Button(self.main_frame, text="Load Deck from File", 
                   command=self.load_deck).pack(pady=2)

    def create_deck_menu(self):
        self.create_deck_window = tk.Toplevel(self.main_window)
        self.create_deck_window.title("Create Deck")

        self.create_deck_window.withdraw()
        self.center_window(self.create_deck_window, 300, 200)
        self.create_deck_window.deiconify()
        
        main_frame = ttk.Frame(self.create_deck_window, padding="50")
        main_frame.pack(anchor="center", expand=True)

        main_frame.columnconfigure(0, weight=1)

        # Allows user to input deck name
        ttk.Label(main_frame, text="Deck Name", font=("Arial", 14, "bold")).grid(
            row=0, column=0, sticky=tk.W ,padx=(0,5), pady=(0,5))

        self.name_entry = ttk.Entry(main_frame, width=30)
        self.name_entry.grid(row=1, column=0, sticky=tk.W, pady=(0,15))
        self.name_entry.focus_set()

        # Create deck
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

            self.show_decks(self.decks_container)

            if self.no_decks_label:
                self.no_decks_label.destroy()
                self.no_decks_label = None
            
            row_index = len(self.decks)
            self._add_deck_to_table(new_deck, row_index)

            self.create_deck_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create deck: {str(e)}") 

    def show_decks(self, parent_frame):
        for widget in parent_frame.winfo_children():
            widget.destroy()

        self.deck_rows_frame = ttk.Frame(parent_frame)
        self.deck_rows_frame.pack(anchor="center")

        if not self.decks:
            self.no_decks_label = ttk.Label(
                self.deck_rows_frame, 
                text="No decks yet. Create a new one to get started!", 
                foreground="gray", anchor="center"
            )
            self.no_decks_label.grid(row=0, column=0, columnspan=4, pady=10)
            return
        
        self.no_decks_label = None

        headings = ["Deck Name", "Cards", "Last Score", "Actions"]
        for col, text in enumerate(headings):
            ttk.Label(self.deck_rows_frame, text=text, font=("Arial", 13, "bold")).grid(
                row=0, column=col, padx=5, pady=3
            )

        for i, deck in enumerate(self.decks):
            self._add_deck_to_table(deck, i + 1)

    def _add_deck_to_table(self, deck, row_index):
        # Loads each deck into the main menu table
        ttk.Label(self.deck_rows_frame, text=deck.name).grid(
                row=row_index, column=0, padx=5, pady=2, sticky="w")
        
        # Shows number of cards in the deck
        cards_label = ttk.Label(self.deck_rows_frame, text=len(deck.cards))
        cards_label.grid(row=row_index, column=1, padx=5, pady=2)
        deck._card_count = cards_label

        # Shows the deck's previous score
        score_label = ttk.Label(self.deck_rows_frame, text=f"{deck.score} / {deck.max_score()}")
        score_label.grid(row=row_index, column=2, padx=5, pady=2)
        deck._score_label = score_label
    
        # Shows action buttons
        button_frame = ttk.Frame(self.deck_rows_frame)
        button_frame.grid(row=row_index, column=3, padx=10, pady=2)
        
        ttk.Button(button_frame, text="Study", command=lambda d=deck: self.study_deck(d)).pack(
            side="left", padx=2)
        ttk.Button(button_frame, text="Edit", command=lambda d=deck: self.edit_deck(d)).pack(
            side="left", padx=2)
        ttk.Button(button_frame, text="Save", command=lambda d=deck: self.save_deck(d)).pack(
            side="left", padx=2)

    def create_card_menu(self):
        if not self.decks:
            messagebox.showerror("Error", "You need to create a deck before adding cards!")
            return
        
        # General window setup
        self.create_card_window = tk.Toplevel(self.main_window)
        self.create_card_window.title("Create Card")

        self.create_card_window.withdraw()
        self.center_window(self.create_card_window, 600, 400)
        self.create_card_window.deiconify()

        main_frame = ttk.Frame(self.create_card_window, padding="20")
        main_frame.pack(anchor="center", expand=True)

        # Dropdown to select deck
        option_frame = ttk.Frame(main_frame)
        option_frame.grid(row=0, column=0, sticky="w", pady=(0,15))

        options = [deck.name for deck in self.decks]
        self.deck_entry = tk.StringVar()
        self.deck_entry.set(options[0])

        ttk.Label(option_frame, text="Select Deck", font=("Arial", 14, "bold")).grid(
            row=0, column=0, padx=(0,10), sticky="w")
        deck_menu = ttk.OptionMenu(option_frame, self.deck_entry, options[0], *options)
        deck_menu.grid(row=0, column=1, padx=(0,10))

        # Allows user to customize front and back parts of card
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
        front = self.front_entry.get("1.0", "end").strip()
        back = self.back_entry.get("1.0", "end").strip()
        deck = self.deck_entry.get()

        if not front or not back:
            messagebox.showerror("Error", "Both front and back parts must be filled!")
            return
        
        try:
            selected_deck = next((d for d in self.decks if d.name == deck), None)
            new_card = backend.Flashcard(front, back)
            selected_deck.insert_card_sorted(new_card)

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
        self.current_deck.sort_by_score()
        self.current_deck.score = 0

        self.showing_front = True

        self.study_deck_window = tk.Toplevel(self.main_window)
        self.study_deck_window.title(f"{deck.name}")
        self.study_deck_window.withdraw()
        self.center_window(self.study_deck_window, 500, 400)
        self.study_deck_window.deiconify()

        self.card_text = ttk.Label(
            self.study_deck_window, text="", font=("Arial", 16), wraplength=450
        )
        self.card_text.pack(pady=30)

        self.card_answer = ttk.Label(
            self.study_deck_window, text="", font=("Arial", 16), wraplength=450
        )

        self.show_answer_button = ttk.Button(
            self.study_deck_window, text="Show Answer", command=self.show_card_back
        )
        self.show_answer_button.pack(pady=10)

        self.rating_frame = ttk.Frame(self.study_deck_window)
        for score_value, text in enumerate(["Again", "Okay", "Good"]):
            ttk.Button(
                self.rating_frame,
                text=text,
                command=lambda r=score_value: self.rate_card(r)
            ).pack(side="left", padx=5)

        self.show_card_front()

    def show_card_front(self):
        if self.study_cards_index >= len(self.study_cards):
            return

        card = self.study_cards[self.study_cards_index]
        self.card_text.config(text=card.front)

        self.card_answer.pack_forget()
        self.rating_frame.pack_forget()

        self.show_answer_button.pack(pady=5)

        self.card_answer.config(text="")
        self.showing_front = True

    def show_card_back(self):
        if self.study_cards_index >= len(self.study_cards):
            return

        card = self.study_cards[self.study_cards_index]
        self.card_answer.config(text=card.back)

        self.card_answer.pack(pady=30)
        self.rating_frame.pack(pady=30)

        self.show_answer_button.pack_forget()

        self.showing_front = False

    def rate_card(self, rating):
        if self.study_cards_index >= len(self.study_cards):
            return

        card = self.study_cards[self.study_cards_index]
        
        self.current_deck.rate_card(card, rating)

        self.study_cards_index += 1

        if self.study_cards_index < len(self.study_cards):
            self.show_card_front()
        else:
            self.finish_study()

    def finish_study(self):
        self.card_answer.pack_forget()
        self.rating_frame.pack_forget()

        self.card_text.config(text="Congratulations!", font=("Arial", 16, "bold"))
        self.card_answer.config(text=f"Your score for this deck is {self.current_deck.score} out of {self.current_deck.max_score()}!")
        self.card_answer.pack(pady=10)

        self.current_deck.sort_by_score()

        if hasattr(self.current_deck, "_score_label"):
            self.current_deck._score_label.config(
                text=f"{self.current_deck.score} / {self.current_deck.max_score()}"
            )

        ttk.Button(self.card_answer.master, text="Go Back", command=self.study_deck_window.destroy).pack(
            pady=10
        )

        self.showing_front = False

    def edit_deck(self, deck):
        self.edit_deck_window = tk.Toplevel(self.main_window)
        self.edit_deck_window.title(f"Editing {deck.name}")
        self.edit_deck_window.withdraw()
        self.center_window(self.edit_deck_window, 650, 550)
        self.edit_deck_window.deiconify()

        main_frame = ttk.Frame(self.edit_deck_window, padding=20)
        main_frame.pack(anchor="center")
        self.edit_deck_window.grid_rowconfigure(0, weight=1)
        self.edit_deck_window.grid_columnconfigure(0, weight=1)

        deck_frame = ttk.Frame(main_frame, padding=15)
        deck_frame.grid(row=0, column=0, pady=(0, 20))
        deck_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(deck_frame, text="Deck Details", font=("Arial", 16, "bold")).grid(
            row=0, column=0, pady=10, sticky="n")

        ttk.Label(deck_frame, text="Deck Name", font=("Arial", 14, "bold")).grid(
            row=1, column=0, pady=5, sticky="w")
        name_entry = ttk.Entry(deck_frame, width=40)
        name_entry.insert(0, deck.name)
        name_entry.grid(row=2, column=0, pady=5, sticky="w")

        def save_deck_name():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showerror("Error", "Deck name cannot be empty!")
                return
            deck.name = new_name
            messagebox.showinfo("Success", f"Deck renamed to '{deck.name}'")
            self.edit_deck_window.destroy()

            for widget in self.deck_rows_frame.winfo_children():
                widget.destroy()

            self.show_decks(self.decks_container)

        btn_frame = ttk.Frame(deck_frame, padding=15)
        btn_frame.grid(row=3, column=0, padx=10)

        ttk.Button(btn_frame, text="Save Deck Name", command=save_deck_name).grid(
            row=0, column=0, padx=10, pady=3, sticky="w")
        ttk.Button(btn_frame, text="Delete Deck", command=lambda d=deck: self.delete_deck(d)).grid(
            row=0, column=1, pady=3, sticky="w")

        cards_frame = ttk.Frame(main_frame, padding=10)
        cards_frame.grid(row=1, column=0, sticky="nsew")
        cards_frame.grid_columnconfigure(0, weight=3)
        cards_frame.grid_columnconfigure(1, weight=3)
        cards_frame.grid_columnconfigure(2, weight=1)

        ttk.Label(cards_frame, text="Card Front", font=("Arial", 13, "bold")).grid(
            row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Label(cards_frame, text="Card Back", font=("Arial", 13, "bold")).grid(
            row=0, column=1, padx=5, pady=5, sticky="w")

        for i, card in enumerate(deck.cards):
            ttk.Label(cards_frame, text=f"{card.front}", anchor="w", 
                      wraplength=250, justify="left").grid(
                row=i+1, column=0, padx=5, pady=1, sticky="w")
            
            ttk.Label(cards_frame, text=f"{card.back}", anchor="w", 
                      wraplength=250, justify="left").grid(
                row=i+1, column=1, padx=5, pady=1, sticky="w")
            
            btn_frame = ttk.Frame(cards_frame)
            btn_frame.grid(row=i+1, column=2, padx=5, pady=5, sticky="w")
            ttk.Button(btn_frame, text="Delete", command=lambda c=card: self.delete_card(deck, c, cards_frame)).pack(side="left", padx=2)

        ttk.Button(main_frame, text="Go Back", command=self.edit_deck_window.destroy).grid(
            row=3, column=0, padx=5, pady=5, sticky="we")

    def delete_deck(self, deck):
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the deck '{deck.name}'?")
        if not confirm:
            return
        
        self.edit_deck_window.destroy()
        messagebox.showinfo("Success", f"Deck '{deck.name}' was deleted.")
        
        if deck in self.decks:
            self.decks.remove(deck)

        for widget in self.deck_rows_frame.winfo_children():
            widget.destroy()
        self.show_decks(self.decks_container)

    def delete_card(self, deck, card, parent_frame):
        confirm = messagebox.askyesno("Confirm Delete", "Delete this card?")
        if not confirm:
            return

        '''
        need to redo
        '''

    def save_deck(self, deck):
        filename = filedialog.asksaveasfilename(
            title=f"Save deck '{deck.name}'",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")]
        )
        if not filename:
            return 

        try:
            deck.save_to_file(filename)
            messagebox.showinfo("Success", f"Deck '{deck.name}' saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save deck: {str(e)}")

    def load_deck(self):
        filename = filedialog.askopenfilename(
            title="Select deck file",
            filetypes=[("JSON Files", "*.json")]
        )

        if not filename:
            return
        
        deck = backend.Deck.load_from_file(filename)
        if not deck:
            messagebox.showerror("Error", "Failed to load deck from file!")
            return
        
        self.decks.append(deck)

        for widget in self.deck_rows_frame.winfo_children():
            widget.destroy()
        self.show_decks(self.decks_container)

        messagebox.showinfo("Success", f"Loaded deck '{deck.name}' successfully!")
    
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