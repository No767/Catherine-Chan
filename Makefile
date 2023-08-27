all: run

run:
	poetry run python bot/catherinebot.py

prod-run:
	./venv/bin/python3 bot/catherinebot.py