.PHONY: test
test:
	pipenv run coverage run -m pytest

.PHONY: run
run:
	pipenv run python src/app.py
