import pytest
import tempfile
import shutil


@pytest.fixture
def tmp_config_dir():
    tmp_dir = tempfile.mkdtemp()
    yield tmp_dir
    shutil.rmtree(tmp_dir)
