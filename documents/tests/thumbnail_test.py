from documents.thumbnail import get_thumbnail


def test_single_page():
    i, img = get_thumbnail("documents/tests/files/1page.pdf")
    assert i == 0
    assert img.size == (100, 150)


def test_single_page_bytes():
    with open("documents/tests/files/1page.pdf", "rb") as fp:
        i, _img = get_thumbnail(stream=fp)
    assert i == 0


def test_2page_first_almost_empty_takes_second():
    i, _img = get_thumbnail("documents/tests/files/2page_first_almost_empty.pdf")
    assert i == 1


def test_all_almost_empty_takes_first():
    i, _img = get_thumbnail("documents/tests/files/repaired.pdf")
    assert i == 0
