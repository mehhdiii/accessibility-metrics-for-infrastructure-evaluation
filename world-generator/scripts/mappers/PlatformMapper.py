from entities.Platform import Platform

class PlatformMapper:
    def __init__(self):
        pass

    @staticmethod
    def platformMapper(platformSpec):
        length = platformSpec.get("length")
        width = platformSpec.get("width")
        name = platformSpec.get("name")

        if length is None:
            raise ValueError("Missing 'length' in platform item.")
        if width is None:
            raise ValueError("Missing 'width' in platform item.")

        return Platform(name, length, width)