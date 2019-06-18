import os

from yaml import dump, Dumper, load, Loader


def handle_exception(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except OSError as oe:
            print(f"Failed to open config file: {str(oe)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")

    return wrapper


class PyjjConfig:
    def __init__(self):
        self.path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config.yaml"
        )
        if not os.path.exists(self.path):
            with open(self.path, "w") as file:
                file.write("division: default")

    @handle_exception
    def parse(self) -> None:
        with open(self.path, "r") as file:
            try:
                yml_content = load(file, Loader=Loader)
                for key, val in yml_content.items():
                    setattr(self, key, val)
            except Exception as e:
                print(f"Falied to parse config file: {str(e)}")

    @handle_exception
    def update(self, **kwargs) -> None:
        try:
            dump(data=kwargs, stream=open(self.path, "w"), Dumper=Dumper)
            for key, val in kwargs.items():
                setattr(self, key, val)
        except Exception as e:
            print(f"Falied to serialize config file: {str(e)}")
