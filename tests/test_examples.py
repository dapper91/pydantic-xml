import runpy
import sys
from pathlib import Path

import pytest
from helpers import is_lxml_native

MODULE_PATH = Path(__file__).parent
PROJECT_ROOT = MODULE_PATH.parent
EXAMPLES_PATH = PROJECT_ROOT / 'examples'


@pytest.mark.parametrize('snippet', list((EXAMPLES_PATH / 'snippets').glob('*.py')), ids=lambda p: p.name)
def test_snippets(snippet: Path):
    runpy.run_path(str(snippet), run_name='snippet')


@pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python 3.9 and above")
@pytest.mark.parametrize('snippet', list((EXAMPLES_PATH / 'snippets' / 'py3.9').glob('*.py')), ids=lambda p: p.name)
def test_snippets_py39(snippet: Path):
    runpy.run_path(str(snippet), run_name='snippet')


@pytest.mark.skipif(not is_lxml_native(), reason='not lxml used')
@pytest.mark.parametrize('snippet', list((EXAMPLES_PATH / 'snippets' / 'lxml').glob('*.py')), ids=lambda p: p.name)
def test_snippets_py39(snippet: Path):
    runpy.run_path(str(snippet), run_name='snippet')


@pytest.fixture(
    params=[
        'computed-entities',
        'custom-encoder',
        'generic-model',
        'quickstart',
        'self-ref-model',
        'xml-serialization-decorator',
        pytest.param(
            'xml-serialization-annotation',
            marks=pytest.mark.skipif(sys.version_info < (3, 9), reason="requires python 3.9 and above"),
        ),
    ],
)
def example_dir(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch):
    example_dir = request.param

    with monkeypatch.context() as mp:
        path = EXAMPLES_PATH / example_dir
        mp.chdir(path)
        yield path


def test_example(example_dir):
    runpy.run_path(str(example_dir / 'model.py'), run_name='example')
