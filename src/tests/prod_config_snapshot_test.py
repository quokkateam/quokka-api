def test_prod_config(snapshot, mocker):
    """
    Use this command to update snapshot:
        $ pipenv run pytest --snapshot-update src/tests/prod_config_snapshot_test.py
    """
    mocker.patch.dict('os.environ', {
      'ENV': 'prod',
      'DATABASE_URL': 'the-db-url'
    })

    from src.config import ProdConfig
    snapshot.assert_match(ProdConfig().as_json_string())
