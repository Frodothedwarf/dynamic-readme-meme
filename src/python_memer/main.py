import importlib
import inspect
import logging
import pkgutil

from dotenv import load_dotenv
from .sources.base import MemeBase

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(format="%(message)s", level=logging.INFO)


def load_meme_source_classes() -> list[MemeBase]:
    meme_classes = []

    # Find all sources in the folder "sources"
    folder = importlib.import_module("python_memer.sources")
    folder_path = folder.__path__

    # Iterate over possible modules
    for _, module_name, is_pkg in pkgutil.iter_modules(folder_path):
        if is_pkg:
            continue
        module = importlib.import_module(f"python_memer.sources.{module_name}")

        # Check the module/source have `MemeBase` as a subclass
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, MemeBase) and obj is not MemeBase:
                meme_classes.append(obj)
    return meme_classes


def main(*args, **kwargs):
    """
    The main function that finds sources from the "sources" folder, and fetches memes.
    """

    meme_sources = load_meme_source_classes()
    for meme_source in meme_sources:
        meme_source = meme_source()
        logging.info(f"🔎 Fetching memes from {meme_source}")
        meme_source.fetch_and_download_memes()


if __name__ == "__main__":
    main()
