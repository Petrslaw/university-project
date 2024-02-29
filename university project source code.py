from random import shuffle


class Deck:
	def __init__(self, game):
		self.top_card = None
		self.bottom_card = None
		self.game = game

	def get_top(self):
		return self.top_card

	def get_bottom(self):
		return self.bottom_card

	def remove_top(self):
		if self.get_top() is not None:
			old_top = self.get_top()
			self.top_card = self.get_top().get_next()
			if self.top_card is None:
				self.bottom_card = None
			return old_top, False
		else:
			if self.game.discarded.get_top().get_next() is not None:
				self.game.discarded.restock_deck()
				return self.remove_top()
			else:
				return None, True

	def add_card(self, card):
		new_card = DeckPosition(card)
		if self.get_top() is None:
			self.top_card = new_card
			self.bottom_card = new_card
		else:
			new_bottom = new_card
			new_bottom.set_previous(self.get_bottom())
			self.get_bottom().set_next(new_bottom)
			self.bottom_card = new_bottom


class DeckPosition:
	def __init__(self, card):
		self.card = card
		self.previous_card = None
		self.next_card = None

	def get_card(self):
		return self.card

	def get_previous(self):
		return self.previous_card

	def get_next(self):
		return self.next_card

	def set_previous(self, card):
		self.previous_card = card

	def set_next(self, card):
		self.next_card = card


class Discarded:
	def __init__(self, game):
		self.top_card = None
		self.top_color = None
		self.game = game

	def get_top(self):
		return self.top_card

	def set_top(self, card):
		self.top_card = card
		if card is not None:
			self.top_color = card.card.get_color()
		else:
			self.top_color = None

	def get_color(self):
		return self.top_color

	def place_card(self, card):
		new_top = DiscardPosition(card)
		new_top.set_next(self.get_top())
		self.set_top(new_top)

	def restock_deck(self):
		last_played_card = self.get_top()
		self.set_top(last_played_card.get_next())
		to_shuffle = []

		while self.get_top() is not None:
			to_shuffle.append(self.get_top().get_card())
			self.set_top(self.get_top().get_next())

		shuffle(to_shuffle)
		for card in to_shuffle:
			self.game.deck.add_card(card)

		last_played_card.set_next(None)
		self.set_top(last_played_card)


class DiscardPosition:
	def __init__(self, card):
		self.card = card
		self.next_card = None

	def get_card(self):
		return self.card

	def get_next(self):
		return self.next_card

	def set_next(self, card):
		self.next_card = card


class Card:
	def __init__(self, rank, color, game):
		self.rank = rank
		self.color = color
		self.game = game

		if rank == 12:
			self.universal = True
		else:
			self.universal = False

		if rank == 14:
			self.color_shift = True
		else:
			self.color_shift = False

	def get_rank(self):
		return self.rank

	def get_color(self):
		return self.color

	def is_universal(self):
		return self.universal

	def __str__(self):
		if self.get_rank() == 14:
			first_part = "A"
		elif self.get_rank() == 11:
			first_part = "J"
		elif self.get_rank() == 12:
			first_part = "Q"
		elif self.get_rank() == 13:
			first_part = "K"
		else:
			first_part = str(self.rank)

		kolory = {"c": "trefl", "d": "karo", "h": "kier", "s": "pik"}
		second_part = kolory[self.color]

		return " ".join([first_part, second_part])

	def direct_next_turn(self):
		if self.game.current_player == self.game.n_players - 1:
			self.game.current_player = 0
		else:
			self.game.current_player += 1

	def card_function(self):
		current_player = self.game.players[self.game.current_player]
		top_card = self.game.discarded.get_top().get_card()
		top_color = self.game.discarded.get_color()
		chosen_card = None
		continue_turn = False

		can_play = False
		for card in current_player.hand:
			if card.get_rank() == top_card.get_rank() or card.get_color() == top_color or card.universal or top_card.universal:
				can_play = True

		if can_play:
			response = None

			if not self.game.continue_turn:
				while response not in ["t", "n"]:
					response = input("\nCzy chcesz zagrać kartę (t/n)? ")

					if response == "makao":
						self.game.makao_said = True
						print("Przyjąłem.")
					if response == "po makale":
						self.game.po_makale_said = True
						print("Przyjąłem.")

			else:
				pass

			if response == "n" and not continue_turn:
				new_card, all_empty = current_player.draw_card()  #jeśli dobrowolnie oddajesz turę, to nie ma grania dobranej karty
				if not all_empty:
					input(f"Dobrano {new_card}.")

			else:
				done = False
				while not done:
					card_name_candidate = input("Jaką kartę zagrasz? (nazwa, która się wyświetla) ")

					if card_name_candidate == "makao":
						self.game.makao_said = True
						print("Przyjąłem.")
					if card_name_candidate == "po makale":
						self.game.po_makale_said = True
						print("Przyjąłem.")

					for card in current_player.hand:
						if card_name_candidate == str(card) and (card.get_rank() == top_card.get_rank() or (
								not self.game.continue_turn and (card.get_color() == top_color or card.universal or top_card.universal))):

							chosen_card = card
							current_player.play_card(chosen_card)
							done = True
				for card in current_player.hand:
					if card.get_rank() == chosen_card.get_rank() and card.get_rank() != 13:
						response = None
						while response not in ["t", "n"]:
							response = input("\nCzy chcesz mieć po tej turze następną i zagrać w niej kartę o tej samej wartości (t/n)? ")

							if response == "makao":
								self.game.makao_said = True
								print("Przyjąłem.")
							if response == "po makale":
								self.game.po_makale_said = True
								print("Przyjąłem.")

						if response == "t":
							continue_turn = True
						else:
							continue_turn = False

						break

		else:
			new_card, all_empty = current_player.draw_card()
			if not all_empty:
				input(f"Dobrano {new_card}.")
			if not all_empty and (new_card.get_rank() == top_card.get_rank() or new_card.get_color() == top_color) or new_card.universal:
				response = None
				while response not in ["t", "n"]:
					response = input("\nCzy chcesz zagrać dobraną kartę (t/n)? ")

					if response == "makao":
						self.game.makao_said = True
						print("Przyjąłem.")
					if response == "po makale":
						self.game.po_makale_said = True
						print("Przyjąłem.")

				if response == "t":
					chosen_card = new_card
					current_player.play_card(new_card)
					for card in current_player.hand:
						if card.get_rank() == chosen_card.get_rank() and card.get_rank() != 13:
							response = None
							while response not in ["t", "n"]:
								response = input("\nCzy chcesz mieć po tej turze następną i zagrać w niej kartę o tej samej wartości (t/n)? ")

								if response == "makao":
									self.game.makao_said = True
									print("Przyjąłem.")
								if response == "po makale":
									self.game.po_makale_said = True
									print("Przyjąłem.")

							if response == "t":
								continue_turn = True
							else:
								continue_turn = False

							break

		if isinstance(chosen_card, CardDraw):
			self.game.draw_queue += chosen_card.amount
		if isinstance(chosen_card, CardWait):
			self.game.wait_queue += 1

		if chosen_card is None:
			self.game.set_action(False)
			self.game.continue_turn = False
			Card(7, "h", self.game).direct_next_turn()

			self.game.makao_said = False
			self.game.po_makale_said = False

		else:
			response = None
			if isinstance(chosen_card, CardExchange):

				players = [player for player in self.game.players.values()]
				players.remove(current_player)
				player_parameters = [f"{player} - liczba kart: {len(player.hand)}" for player in players]
				print("\n", player_parameters)

				while response not in ["t", "n"]:
					response = input("Czy chcesz zainicjować wymianę kart (t/n)?")

					if response == "makao":
						self.game.makao_said = True
						print("Przyjąłem.")
					if response == "po makale":
						self.game.po_makale_said = True
						print("Przyjąłem.")

				if response == "t":
					victim_name = None
					while victim_name not in [str(player) for player in players]:
						victim_name = input("Wpisz imię gracza, z którym chcesz się zamienić kartami.")
					for n in self.game.players.keys():
						if victim_name == str(self.game.players[n]):
							self.game.exchange_victim = n
							break
					self.game.exchange_initiator = self.game.current_player
					self.game.makao_said = False
					self.game.po_makale_said = False

			if response != "t":
				if self.game.check_makao():
					for _ in range(5):
						new_card, all_empty = current_player.draw_card()
						if all_empty:
							break

			if continue_turn:
				self.game.set_action(False)
				self.game.continue_turn = True

			elif isinstance(chosen_card, CardExchange) and response == "n":
				self.game.set_action(False)
				self.game.continue_turn = False
				Card(7, "h", self.game).direct_next_turn()

			else:
				self.game.set_action(True)
				self.game.continue_turn = False
				chosen_card.direct_next_turn()

				if chosen_card.color_shift:
					chosen_color = None
					while chosen_color not in ["trefl", "karo", "kier", "pik"]:
						chosen_color = input("Wybierz kolor, nawet jeśli ma zostać oryginalny (trefl, karo, kier, pik).")
					kolory = {"trefl": "c", "karo": "d", "kier": "h", "pik": "s"}
					self.game.discarded.top_color = kolory[chosen_color]

				if isinstance(chosen_card, CardDemand):
					chosen_demand = None
					while chosen_demand not in ["5", "6", "7", "8", "9", "10", "brak"]:
						chosen_demand = input(
							"Wybierz żądanie (od 5 do 10, nie musisz mieć na ręce) lub brak żądania (brak).")

					if chosen_demand == "brak":
						self.game.set_action(False)
						for player in self.game.players.values():
							player.active_demand = None
					else:
						for player in self.game.players.values():
							player.active_demand = int(chosen_demand)


class CardDraw(Card):
	def __init__(self, rank, color, game):
		Card.__init__(self, rank, color, game)
		if self.rank in [2, 3]:
			self.amount = self.rank
		else:
			self.amount = 5

		if self.amount == 5 and self.color == "s":
			self.reverse = True
		else:
			self.reverse = False

	def direct_next_turn(self):
		if self.reverse:
			if self.game.current_player == 0:
				self.game.current_player = self.game.n_players - 1
			else:
				self.game.current_player -= 1
		else:
			Card(7, "h", self.game).direct_next_turn()

	def card_function(self):
		current_player = self.game.players[self.game.current_player]
		top_card = self.game.discarded.get_top().get_card()
		top_color = self.game.discarded.get_color()
		chosen_card = None
		continue_turn = False

		can_play = False
		for card in current_player.hand:
			if (card.get_rank() == top_card.get_rank() or card.get_color() == top_color) and isinstance(card, CardDraw):
				can_play = True

		if can_play:
			if self.game.draw_queue < 5:
				input(f"Jeśli się nie obronisz, dobierzesz {self.game.draw_queue} karty.")
			else:
				input(f"Jeśli się nie obronisz, dobierzesz {self.game.draw_queue} kart.")

			response = None
			while response not in ["t", "n"]:
				response = input("\nCzy chcesz zagrać kartę (t/n)? ")

				if response == "makao":
					self.game.makao_said = True
					print("Przyjąłem.")
				if response == "po makale":
					self.game.po_makale_said = True
					print("Przyjąłem.")

			if response == "t":
				while chosen_card is None:
					card_name_candidate = input("Jaką kartę zagrasz? (nazwa, która się wyświetla) ")

					if card_name_candidate == "makao":
						self.game.makao_said = True
						print("Przyjąłem.")
					if card_name_candidate == "po makale":
						self.game.po_makale_said = True
						print("Przyjąłem.")

					for card in current_player.hand:
						if card_name_candidate == str(card) and (card.get_rank() == top_card.get_rank() or card.get_color() == top_color):
							if isinstance(card, CardDraw):
								chosen_card = card
								current_player.play_card(chosen_card)
				for card in current_player.hand:
					if card.get_rank() == chosen_card.get_rank() and card.get_rank() != 13:
						response = None
						while response not in ["t", "n"]:
							response = input("\nCzy chcesz mieć po tej turze następną i zagrać w niej kartę o tej samej wartości (t/n)? ")

							if response == "makao":
								self.game.makao_said = True
								print("Przyjąłem.")
							if response == "po makale":
								self.game.po_makale_said = True
								print("Przyjąłem.")

						if response == "t":
							continue_turn = True
						else:
							continue_turn = False

						break

			else:
				for _ in range(self.game.draw_queue):
					new_card, all_empty = current_player.draw_card()
					if all_empty:
						break
				self.game.draw_queue = 0

		else:
			if self.game.draw_queue < 5:
				input(f"Dobierasz {self.game.draw_queue} karty")
			else:
				input(f"Dobierasz {self.game.draw_queue} kart")

			new_card, all_empty = current_player.draw_card()
			self.game.draw_queue -= 1

			if not all_empty and (new_card.get_rank() == top_card.get_rank() or new_card.get_color() == top_color):
				if isinstance(new_card, CardDraw):
					input(f"Dobrano {new_card}.")
					response = None
					while response not in ["t", "n"]:
						response = input(f"\nDobrano z góry {new_card}. Czy chcesz zagrać dobraną kartę (t/n)?")

						if response == "makao":
							self.game.makao_said = True
							print("Przyjąłem.")
						if response == "po makale":
							self.game.po_makale_said = True
							print("Przyjąłem.")

					if response == "t":
						chosen_card = new_card
						current_player.play_card(new_card)
						for card in current_player.hand:
							if card.get_rank() == chosen_card.get_rank() and card.get_rank() != 13:
								response = None
								while response not in ["t", "n"]:
									response = input("\nCzy chcesz mieć po tej turze następną i zagrać w niej kartę o tej samej wartości (t/n)? ")

									if response == "makao":
										self.game.makao_said = True
										print("Przyjąłem.")
									if response == "po makale":
										self.game.po_makale_said = True
										print("Przyjąłem.")

								if response == "t":
									continue_turn = True
								else:
									continue_turn = False

								break

					else:
						for _ in range(self.game.draw_queue - 1):
							new_card, all_empty = current_player.draw_card()
							if all_empty:
								break
						self.game.draw_queue = 0

			else:
				for _ in range(self.game.draw_queue):
					new_card, all_empty = current_player.draw_card()
					if all_empty:
						break
				self.game.draw_queue = 0

		if isinstance(chosen_card, CardDraw):
			self.game.draw_queue += chosen_card.amount

		if chosen_card is None:
			self.game.set_action(False)
			self.game.continue_turn = False
			Card(7, "h", self.game).direct_next_turn()

			self.game.makao_said = False
			self.game.po_makale_said = False

		else:
			if self.game.check_makao():
				for _ in range(5):
					new_card, all_empty = current_player.draw_card()
					if all_empty:
						break

			if continue_turn:
				self.game.set_action(False)
				self.game.continue_turn = True

			else:
				self.game.set_action(True)
				self.game.continue_turn = False
				chosen_card.direct_next_turn()


class CardWait(Card):
	def __init__(self, rank, color, game):
		Card.__init__(self, rank, color, game)

	def card_function(self):
		current_player = self.game.players[self.game.current_player]
		chosen_card = None
		continue_turn = False

		can_play = False
		for card in current_player.hand:
			if isinstance(card, CardWait):
				can_play = True

		if can_play:
			if self.game.wait_queue == 1:
				input(f"Jeśli się nie obronisz, czekasz jedną turę.")
			else:
				input(f"Jeśli się nie obronisz, czekasz {self.game.wait_queue} tury.")

			response = None
			while response not in ["t", "n"]:
				response = input("\nCzy chcesz zagrać kartę (t/n)? ")

				if response == "makao":
					self.game.makao_said = True
					print("Przyjąłem.")
				if response == "po makale":
					self.game.po_makale_said = True
					print("Przyjąłem.")

			if response == "t":
				while chosen_card is None:
					card_name_candidate = input("Jaką kartę zagrasz? (nazwa, która się wyświetla) ")

					if card_name_candidate == "makao":
						self.game.makao_said = True
						print("Przyjąłem.")
					if card_name_candidate == "po makale":
						self.game.po_makale_said = True
						print("Przyjąłem.")

					for card in current_player.hand:
						if card_name_candidate == str(card) and isinstance(card, CardWait):
							chosen_card = card
							current_player.play_card(chosen_card)
				for card in current_player.hand:
					if card.get_rank() == chosen_card.get_rank() and card.get_rank() != 13:
						response = None
						while response not in ["t", "n"]:
							response = input("\nCzy chcesz mieć po tej turze następną i zagrać w niej kartę o tej samej wartości (t/n)? ")

							if response == "makao":
								self.game.makao_said = True
								print("Przyjąłem.")
							if response == "po makale":
								self.game.po_makale_said = True
								print("Przyjąłem.")

						if response == "t":
							continue_turn = True
						else:
							continue_turn = False

						break

			else:
				current_player.n_wait += self.game.wait_queue - 1
				self.game.wait_queue = 0

		else:
			if self.game.wait_queue == 1:
				input(f"Czekasz jedną turę.")
			else:
				input(f"Czekasz {self.game.wait_queue} tury.")

			response = None
			while response not in ["t", "n"]:
				response = input("\nCzy chcesz dobrać kartę, żeby spróbować się obronić (t/n)? ")

				if response == "makao":
					self.game.makao_said = True
					print("Przyjąłem.")
				if response == "po makale":
					self.game.po_makale_said = True
					print("Przyjąłem.")

			if response == "t":
				new_card, all_empty = current_player.draw_card()
				if not all_empty and isinstance(new_card, CardWait):
					chosen_card = new_card
					current_player.play_card(new_card)
					input(f"Udało się, dobrano i zagrano {new_card}.")

					print(f"i'm in len(current_player.hand) == {len(current_player.hand)}")

					if len(current_player.hand) == 1:
						response2 = None
						while response2 not in ["t", "n"]:
							response2 = input("Tak w ogóle to jak się gra, w porządku wszystko (t/n)?")

							if response2 == "makao":
								self.game.makao_said = True
								print("Przyjąłem.")
							if response2 == "po makale":
								self.game.po_makale_said = True
								print("Przyjąłem.")

				else:
					if not all_empty:
						input(f"Czekanie i karta dla Ciebie, gratulacje. ({new_card})")
					current_player.n_wait += self.game.wait_queue - 1
					self.game.wait_queue = 0

			else:
				current_player.n_wait += self.game.wait_queue - 1
				self.game.wait_queue = 0

		if chosen_card is None:
			self.game.set_action(False)
			self.game.continue_turn = False
			Card(7, "h", self.game).direct_next_turn()

			self.game.makao_said = False
			self.game.po_makale_said = False

		else:
			self.game.wait_queue += 1

			if self.game.check_makao():
				for _ in range(5):
					new_card, all_empty = current_player.draw_card()
					if all_empty:
						break

			if continue_turn:
				self.game.set_action(False)
				self.game.continue_turn = True

			else:
				self.game.set_action(True)
				self.game.continue_turn = False
				chosen_card.direct_next_turn()


class CardDemand(Card):
	def __init__(self, rank, color, game):
		Card.__init__(self, rank, color, game)

	def card_function(self):
		current_player = self.game.players[self.game.current_player]
		top_card = self.game.discarded.get_top().get_card()
		chosen_card = None
		continue_turn = False

		if isinstance(top_card, CardDemand):
			input(f"Aktywne żądanie: {current_player.active_demand} (można przebić).")
		else:
			input(f"Aktywne żądanie: {current_player.active_demand} (nie można przebić).")

		can_play = False
		for card in current_player.hand:
			if card.get_rank() in [top_card.get_rank(), current_player.active_demand]:
				can_play = True

		if can_play:
			response = None
			while response not in ["t", "n"]:
				response = input("\nCzy chcesz zagrać kartę (t/n)? ")

				if response == "makao":
					self.game.makao_said = True
					print("Przyjąłem.")
				if response == "po makale":
					self.game.po_makale_said = True
					print("Przyjąłem.")

			if response == "n":
				new_card, all_empty = current_player.draw_card()  # jeśli dobrowolnie oddajesz turę, to nie ma grania dobranej karty
				if not all_empty:
					input(f"Dobrano {new_card}.")

			else:
				done = False
				while not done:
					card_name_candidate = input("Jaką kartę zagrasz? (nazwa, która się wyświetla) ")

					if card_name_candidate == "makao":
						self.game.makao_said = True
						print("Przyjąłem.")
					if card_name_candidate == "po makale":
						self.game.po_makale_said = True
						print("Przyjąłem.")

					for card in current_player.hand:
						if card_name_candidate == str(card) and card.get_rank() in [top_card.get_rank(), current_player.active_demand]:
							chosen_card = card
							current_player.play_card(chosen_card)
							done = True
				for card in current_player.hand:
					if card.get_rank() == chosen_card.get_rank():
						response = None
						while response not in ["t", "n"]:
							response = input("\nCzy chcesz mieć po tej turze następną i zagrać w niej kartę o tej samej wartości (t/n)? ")

							if response == "makao":
								self.game.makao_said = True
								print("Przyjąłem.")
							if response == "po makale":
								self.game.po_makale_said = True
								print("Przyjąłem.")

						if response == "t":
							continue_turn = True
						else:
							continue_turn = False

						break

		else:
			new_card, all_empty = current_player.draw_card()
			if not all_empty:
				input(f"Dobrano {new_card}.")
			if not all_empty and new_card.get_rank() in [top_card.get_rank(), current_player.active_demand]:
				response = None
				while response not in ["t", "n"]:
					response = input("\nCzy chcesz zagrać dobraną kartę (t/n)? ")

					if response == "makao":
						self.game.makao_said = True
						print("Przyjąłem.")
					if response == "po makale":
						self.game.po_makale_said = True
						print("Przyjąłem.")

				if response == "t":
					chosen_card = new_card
					current_player.play_card(new_card)

		current_player.active_demand = None

		if chosen_card is None:
			self.game.set_action(False)
			self.game.continue_turn = False
			Card(7, "h", self.game).direct_next_turn()

			self.game.makao_said = False
			self.game.po_makale_said = False

		else:
			if self.game.check_makao():
				for _ in range(5):
					new_card, all_empty = current_player.draw_card()
					if all_empty:
						break

			if continue_turn:
				self.game.set_action(False)
				self.game.continue_turn = True

			else:
				self.game.set_action(True)
				self.game.continue_turn = False
				chosen_card.direct_next_turn()

				if isinstance(chosen_card, CardDemand):
					chosen_demand = None
					while chosen_demand not in ["5", "6", "7", "8", "9", "10", "brak"]:
						chosen_demand = input("Wybierz żądanie (od 5 do 10, nie musisz mieć na ręce) lub brak żądania (brak). ")

					if chosen_demand == "brak":
						self.game.set_action(False)
						for player in self.game.players.values():
							player.active_demand = None
					else:
						for player in self.game.players.values():
							player.active_demand = int(chosen_demand)


class CardExchange(Card):
	def __init__(self, rank, color, game):
		Card.__init__(self, rank, color, game)

	def direct_next_turn(self):
		if self.game.exchange_initiator is not None:
			self.game.current_player = self.game.exchange_victim
		else:
			Card(7, "h", self.game).direct_next_turn()

	def card_function(self):
		current_player = self.game.players[self.game.current_player]
		exchanger = self.game.players[self.game.exchange_initiator]

		can_play = False
		for card in current_player.hand:
			if isinstance(card, CardNoExchange):
				can_play = True

		response = None

		if can_play:
			input(f"Jeśli nie zagrasz króla karo, gracz {str(exchanger)} zamieni się z Tobą kartami na ręce. (liczba kart: {len(exchanger.hand)})")
			while response not in ["t", "n"]:
				response = input("\nCzy chcesz zagrać króla karo? Inicjator wymiany dobierze 5 kart. (t/n) ")

				if response == "makao":
					self.game.makao_said = True
					print("Przyjąłem.")
				if response == "po makale":
					self.game.po_makale_said = True
					print("Przyjąłem.")

		if response == "t":
			for card in current_player.hand:
				if isinstance(card, CardNoExchange):
					current_player.play_card(card)
			for _ in range(5):
				new_card, all_empty = exchanger.draw_card()
				if all_empty:
					break

		else:
			input(f"Gracz {str(exchanger)} (liczba kart: {len(exchanger.hand)}) zamienia się z Tobą kartami.")

			response = None
			while response not in ["t", "n"]:
				response = input("\nCzy wiesz, co to oznacza (t/n)?")

				if response == "makao":
					self.game.makao_said = True
					print("Przyjąłem.")
				if response == "po makale":
					self.game.po_makale_said = True
					print("Przyjąłem.")

				if response == "n":
					input("Było uważać, jak tłumaczyłem zasady.")

			current_player.hand, exchanger.hand = exchanger.hand, current_player.hand

		if self.game.check_makao():
			for _ in range(5):
				new_card, all_empty = current_player.draw_card()
				if all_empty:
					break

		self.game.current_player = self.game.exchange_initiator
		self.game.set_action(False)
		Card(7, "h", self.game).direct_next_turn()

		self.game.exchange_initiator = None
		self.game.exchange_victim = None


class CardNoExchange(Card):
	def __init__(self, rank, color, game):
		Card.__init__(self, rank, color, game)
	# klasa istniejąca ze względów estetycznych do pary dla klasy CardExchange


class Player:
	def __init__(self, game, player_name):
		self.game = game
		self.player_name = player_name
		self.n_wait = 0
		self.active_demand = None
		self.hand = []

	def __str__(self):
		return self.player_name

	def draw_card(self):
		new_card, all_empty = self.game.deck.remove_top()
		if not all_empty:
			new_card = new_card.card
			if len(self.hand) == 0:
				self.hand.append(new_card)
			else:
				color_order = {"c": 0, "d": 1, "h": 2, "s": 3}
				was_card_added = False
				if color_order[new_card.get_color()] < color_order[self.hand[0].get_color()] or (
						color_order[new_card.get_color()] == color_order[self.hand[0].get_color()] and new_card.rank <= self.hand[0].rank):
					self.hand.insert(0, new_card)
					was_card_added = True
				if not was_card_added and len(self.hand) > 1:
					current_card = self.hand[0]
					for count in range(len(self.hand)):
						previous_card = current_card
						current_card = self.hand[count]

						if color_order[previous_card.get_color()] < color_order[new_card.get_color()] < color_order[current_card.get_color()] or (
							color_order[previous_card.get_color()] == color_order[new_card.get_color()] < color_order[current_card.get_color()] and previous_card.get_rank() < new_card.get_rank()) or (
							color_order[previous_card.get_color()] < color_order[new_card.get_color()] == color_order[current_card.get_color()] and new_card.get_rank() <= current_card.get_rank()) or (
							color_order[previous_card.get_color()] == color_order[new_card.get_color()] == color_order[current_card.get_color()] and (
								previous_card.get_rank() <= new_card.get_rank() <= current_card.get_rank())): # ten moloch układa karty na ręce w kolejności

							self.hand.insert(count, new_card)
							was_card_added = True
							break
				if not was_card_added:
					self.hand.append(new_card)
		else:
			input("Koniec kart w talii i pod ostatnio zagraną kartą.")
		return new_card, all_empty

	def play_card(self, card):
		self.hand.remove(card)
		self.game.discarded.place_card(card)


class Game:
	def __init__(self):
		self.players = {}
		self.n_players = 0
		self.current_player = None
		self.draw_queue = 0
		self.wait_queue = 0
		self.action = True
		self.continue_turn = False
		self.makao_said = False
		self.po_makale_said = False
		self.exchange_initiator = None
		self.exchange_victim = None
		self.over = False

		input("\nW każdej sytuacji, jeśli wygląda jakby program się zamroził - naciśnij enter.")
		input("Dokładnie.\n")

		print("Będziemy grać w makao. To znaczy nie 'my', bo nie ma tu żadnej sztucznej inteligencji.")
		input("Nazwijmy to trybem 'hot-seat'.\n")

		print("Jakie makao jest każdy widzi, ale bywają drobne różnice między zasadami według różnych graczy.")
		input("Przejdziemy teraz do konkretów:\n")

		input("1. 'makao' lub 'po makale' można powiedzieć zawsze, gdy gra zadaje pytanie. Faktyczne pytanie ze znakiem zapytania. (Dam znać, że przyjąłem.)")
		input("2. Nie ma schodków. W dowolnej sytuacji można położyć wiele kart tego samego nominału (oprócz 2b.)")
		print("\t2a. Kładzenie kilku kart działa w ten sposób, że gra pyta, czy chcesz nową turę.")
		input("\tW szczególności jeśli w tej *następnej turze* pozbędziesz się przedostatniej karty - nie mów jeszcze 'makao'.")
		input("\t2b. Nie można kłaść kilku królów. Rozwinięte w 5.")
		input("3. Obrona do koloru albo tego samego nominału. Bez wyjątków.")
		input("4. Dama nie broni przed niczym i nie działa na żądaniach (ale rzecz jasna ona na wszystko i wszystko na nią).\n")

		input("\n5. To już spora różnica. Opcjonalna. Króle trefl i karo dostają nowe funkcje. ")
		input("\t5a. Król trefl może zainicjować zamianę wszystkimi kartami z dowolnie wybranym graczem. ")
		input("\t5b. Król karo blokuje zamianę. Tylko król karo. ")
		input("\t5c. 'makao' lub 'po makale' inicjującego zamianę nie ma żadnego efektu. Nie ma żadnych kar.")
		input("\t5d. Ofiara zamiany musi powiedzieć co trzeba zarówno gdy blokuje zamianę, jak i gdy do zamiany dochodzi.")
		input("\t5e. Zablokowanie zamiany powoduje, że jej inicjator dobiera 5 kart.")

		response = None
		while response not in ["t", "n"]:
			response = input("\nNie wszystkim podoba się nowa funkcja króli. Czy zgadzasz się na nią (t/n)? ")

			if response in ["makao", "po makale"]:
				print("Tak, teraz też można.")

		if response == "t":
			self.with_a_twist = True
		else:
			self.with_a_twist = False

		playable_cards = []
		for color in ["c", "d", "h", "s"]:
			playable_cards.append(CardDemand(11, color, self))
			playable_cards.append(CardWait(4, color, self))
			for rank in [2, 3]:
				playable_cards.append(CardDraw(rank, color, self))
			for rank in [5, 6, 7, 8, 9, 10, 12, 14]:
				playable_cards.append(Card(rank, color, self))
		for color in ["h", "s"]:
			playable_cards.append(CardDraw(13, color, self))
		if self.with_a_twist:
			playable_cards.append(CardExchange(13, "c", self))
			playable_cards.append(CardNoExchange(13, "d", self))
		else:
			playable_cards.append(Card(13, "c", self))
			playable_cards.append(Card(13, "d", self))

		shuffle(playable_cards)

		self.discarded = Discarded(self)

		for card in playable_cards:
			if card.get_rank() in range(5, 11) and not (str(card) == "6 trefl" or str(card) == "10 karo"):
				starting_card = card
				self.discarded.place_card(starting_card)
				playable_cards.remove(starting_card)
				break

		deck = Deck(self)
		for card in playable_cards:
			deck.add_card(card)
		self.deck = deck

	def set_action(self, logic):
		self.action = logic

	def get_n_players(self):
		return self.n_players

	def add_player(self, player_name):
		self.players[self.n_players] = Player(self, player_name)
		self.n_players += 1

	def set_players(self):
		done = False
		while not done:
			response = input("\nPodaj imię nowego gracza. (od 2 do 4 graczy, wpisz 'koniec', gdy wszyscy gracze są wpisani) ")

			player_names = [str(player) for player in self.players.values()]

			if response in ["makao", "po makale"]:
				print("Tak, teraz też można.")
			if response in player_names:
				print("Ten gracz jest już wpisany.")
			if response == "":
				print("Musisz wpisać cokolwiek, żeby to zadziałało.")
			if response == "koniec" and self.get_n_players() < 2:
				print("Za mało graczy.")
			if response not in ["koniec", "makao", "po makale", ""] and response not in player_names:
				self.add_player(response)
			if (response == "koniec" and self.get_n_players() in [2, 3]) or self.get_n_players() == 4:
				done = True

		print("Imiona graczy to:")
		for n in range(self.get_n_players()):
			print(self.players[n])
		response = None
		while response not in ["t", "n"]:
			response = input("Czy wpisać graczy na nowo? (t/n) ")

			if response in ["makao", "po makale"]:
				print("Tak, teraz też można.")
			if response == "t":
				self.players = {}
				self.n_players = 0
				self.set_players()

	def start_game(self):
		self.current_player = 0
		for player in self.players.values():
			for _ in range(5):
				player.draw_card()

	def start_turn(self):
		current_player = self.players[self.current_player]
		top_card = self.discarded.get_top().get_card()
		top_color = self.discarded.get_color()

		if not self.continue_turn:
			print(f"\nTURA GRACZA {current_player.player_name}\n")
			if top_card.color_shift:
				kolory = {"c": "trefl", "d": "karo", "h": "kier", "s": "pik"}
				print(f"Karta na wierzchu stosu: {self.discarded.get_top().get_card()} ({kolory[top_color]})\n")
			else:
				print(f"Karta na wierzchu stosu: {self.discarded.get_top().get_card()}\n")
			print(f"Karty na ręce:")
			for card in current_player.hand:
				print(card)

		if current_player.n_wait > 0:
			input(f"Pozostało {current_player.n_wait} tur do przeczekania.")
			current_player.n_wait -= 1
			current_player.active_demand = None
			top_card.direct_next_turn()

		elif current_player.active_demand is not None:
			CardDemand(11, "h", self).card_function()

		elif self.action:
			top_card.card_function()

		else:
			Card(7, "h", self).card_function()

	def check_makao(self):
		current_player = self.players[self.current_player]
		nagroda = False

		if len(current_player.hand) == 1 and not self.makao_said:
			input("A gdzie makao? 5 kart.")
			nagroda = True
		if len(current_player.hand) == 0 and not self.po_makale_said:
			input("Gratulacje, 5 kart.")
			nagroda = True
		if (len(current_player.hand) == 1 and self.po_makale_said) or (len(current_player.hand) == 0 and self.makao_said):
			input("Nie ta formułka, 5 kart.")
			nagroda = True
		if not len(current_player.hand) in [0, 1] and (self.po_makale_said or self.makao_said):
			input("Mówienie makao na zaś to cwaniakowanie. 5 kart.")
			nagroda = True

		self.makao_said = False
		self.po_makale_said = False
		return nagroda

	def check_win(self):
		winner = None
		for player in self.players.values():
			if len(player.hand) == 0:
				winner = player
		return winner

	def meta_turn(self):
		player = self.check_win()
		if player is not None:
			print(f"\nGracz {str(player)} wygrywa. Bystrzak skubany.")
			self.over = True
		else:
			self.start_turn()


if __name__ == "__main__":
	game = Game()
	game.set_players()
	game.start_game()
	while not game.over:
		game.meta_turn()
