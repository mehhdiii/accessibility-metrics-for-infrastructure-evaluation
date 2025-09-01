from entities.Platform import Platform

class PlatformMapper:
    def __init__(self):
        pass

    @staticmethod
    def platformMapper(platformSpec):
        length = platformSpec.get("length")
        width = platformSpec.get("width")
        name = platformSpec.get("name")

        child = platformSpec.get("child", None)

        is_leaf = False
        if child is None:
            is_leaf = True

        if length is None:
            raise ValueError("Missing 'length' in platform item.")
        if width is None:
            raise ValueError("Missing 'width' in platform item.")

        return Platform(name, length, width, front_kerb= is_leaf, kerbed=True)