from pathlib import Path
from api.smite import GODS_DICT, ensure_dicts
import requests


def save_god_images(path, file=None, clear=False) -> int:
    """ Download and saves all god images into specific directory

        Args:
            path (str): Path to save images 
            file (file): A reference to file to store logs
                        if is set to None then logs will be printed
                        on stdout (Default: None)
            clear (bool): A flag to clear directory before downloading
        Returns:
            Number of new images downloaded
    """
    # Create directory if not exist
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)

    # Clear directory
    if clear:
        for file in directory.glob('*'):
            try:
                file.unlink()
            except OSError as err:
                print(f'Error: {file} {err}')

    # Get list of all existing files
    image_files = [file.name for file in directory.glob('*.jpg')]

    ensure_dicts()
    GODS = {i[1][0]: i[1][1] for i in GODS_DICT.items()}

    counter = 0

    for god, url in GODS.items():
        if (god + '.jpg') not in image_files:
            r = requests.get(url)
            open(directory.joinpath(god + '.jpg'), 'wb').write(r.content)
            if file is None:
                print(f'{god}.jpg saved.')
            else:
                print(f'{god}.jpg saved.', file=file)
            counter += 1    
    
    return counter
