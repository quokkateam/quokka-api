.PHONY: test
test:
	pipenv run coverage run -m pytest --doctest-modules src/ --ignore=src/tests/prod_config_snapshot_test.py
	pipenv run coverage run -m pytest src/tests/prod_config_snapshot_test.py

.PHONY: run
run:
	pipenv run python app.py
