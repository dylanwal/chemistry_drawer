

class MoleParsingError(Exception):
    def __init__(self, text: str, optional: str = "", error=None):
        self.text = f"Invalid symbol: {text}  "
        if optional:
            self.text += "(" + optional + ")"
        if error:
            self.text += "/n/n" + error
        # logger.error(self.text)

    def __str__(self):
        return self.text


class RDKitError(Exception):
    def __init__(self, error):
        self.text = error

    def __str__(self):
        return self.text