import json


# Todo: fix this

def test_prod_config(snapshot, mocker):
    """
    Use this command to update snapshot:
        $ pipenv run pytest --snapshot-update src/tests/prod_config_snapshot_test.py
    """
    mocker.patch.dict('os.environ', {
      'ENV': 'prod',
      'DATABASE_URL': 'the-db-url'
    })

    from src.configs.prod import *

    configs = json.dumps({k: v for k, v in globals().items() if k.isupper()},
                         sort_keys=True, indent=2)

    snapshot.assert_match(configs)
