

from Widening import Widening

class WideningMapper:
    def __init__(self):
        pass

    @staticmethod
    def wideningMapper(wideningSpec):
        length = wideningSpec.get("length")
        width = wideningSpec.get("width")
        name = wideningSpec.get("name")
        front_close = wideningSpec.get("front_close", False)

        if length is None:
            raise ValueError("Missing 'length' in widening item.")
        if width is None:
            raise ValueError("Missing 'width' in widening item.")
        print(front_close)
        return Widening(name, length, width, front_close)