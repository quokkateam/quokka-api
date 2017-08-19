.PHONY: test
test:
	pipenv run coverage run -m pytest --doctest-modules src/ --ignore=src/prod_config_snapshot_test.py
	pipenv run coverage run -m pytest src/prod_config_snapshot_test.py

.PHONY: run
run:
	pipenv run python src/app.py
