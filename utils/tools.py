import random
import string


def generate_random_string(length: int = 15, characters: str = None):
    if characters is None:
        characters = string.ascii_lowercase + "123456789"

    random_string = "".join(random.choice(characters) for _ in range(length))

    return random_string
