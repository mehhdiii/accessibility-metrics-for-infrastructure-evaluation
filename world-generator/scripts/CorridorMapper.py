from Corridor import Corridor

class CorridorMapper:
    def __init__(self):
        pass

    @staticmethod
    def corridorMapper(corridorSpec):
        length = corridorSpec.get("length")
        width = corridorSpec.get("width")
        name = corridorSpec.get("name")

        if length is None:
            raise ValueError("Missing 'length' in corridor item.")
        if width is None:
            raise ValueError("Missing 'width' in corridor item.")

        return Corridor(name, length, width)