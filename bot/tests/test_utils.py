from libs.utils import is_docker


def test_is_docker():
    if is_docker() is False:
        assert is_docker() is False
        return
    assert is_docker() is True
