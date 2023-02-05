import importlib.machinery
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).parent
PROJECT_ROOT = MODULE_PATH.parent
EXAMPLES_PATH = PROJECT_ROOT / 'examples'


@pytest.mark.parametrize('snippet', list((EXAMPLES_PATH / 'snippets').glob('*.py')), ids=lambda p: p.name)
def test_snippets(snippet: Path):
    loader = importlib.machinery.SourceFileLoader('snippet', str(snippet))
    loader.load_module('snippet')


@pytest.fixture(
    params=[
        'custom-encoder',
        'generic-model',
        'quickstart',
        'self-ref-model',
    ],
)
def example_dir(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch):
    example_dir = request.param

    with monkeypatch.context() as mp:
        path = EXAMPLES_PATH / example_dir
        mp.chdir(path)
        yield path


def test_example(example_dir):
    loader = importlib.machinery.SourceFileLoader('example', str(example_dir / 'model.py'))
    loader.load_module('example')
