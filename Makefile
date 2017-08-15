.PHONY: test
test:
	pipenv run coverage run -m pytest src

.PHONY: run
run:
	pipenv run python src/app.py
