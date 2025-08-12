from python_memer.main import load_meme_source_classes
from python_memer.sources.base import MemeBase

def test_load_meme_source_classes():
    expected_meme_classes = ["Reddit", "ProgrammerHumor.io"]

    meme_classes = load_meme_source_classes()

    for meme_class in meme_classes:
        assert issubclass(meme_class, MemeBase) is True

    meme_classes_str = [meme_class().__str__() for meme_class in meme_classes]

    meme_classes_str.sort()
    expected_meme_classes.sort()
    assert meme_classes_str == expected_meme_classes