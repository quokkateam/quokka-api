import pytest


def test_prod_config(snapshot, mocker):
    """
    Use this command to update snapshot:
        $ pipenv run pytest --snapshot-update src/prod_config_snapshot_test.py
    """
    mocker.patch.dict('os.environ', {'ENV': 'prod'})

    with pytest.raises(AssertionError):
      mocker.patch.dict('os.environ', {'ENV': 'prod', 'DATABASE_URL': 'the-db-url'})

    import config
    snapshot.assert_match(config.get_pretty_config())