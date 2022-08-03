
class Font:
    def __init__(self,
                 show: bool = None,
                 family: str = None,
                 size: int = None,
                 bold: bool = None,
                 color: str = None,
                 offset: float = None,
                 ):
        self.show = show
        self.family = family
        self.bold = bold
        self.size = size
        self.color = color
        self.offset = offset

    def get_attr(self, attr_: str, other):
        """ Get attribute from other, but if not there use self. """
        attr_self = getattr(self, attr_)
        if attr_self is None:
            raise ValueError(f"Unsupported attribute for this Font. {attr_}")
        attr_other = getattr(other, attr_)
        return attr_other if attr_other is not None else attr_self


class Line:
    def __init__(self,
                 show: bool = None,
                 width: int = None,
                 color: str = None,
                 highlight: bool = None,
                 highlight_color: str = None,
                 highlight_width: float = None,
                 ):
        self.show = show
        self.width = width
        self.color = color
        self.highlight = highlight
        self.highlight_color = highlight_color
        self.highlight_width = highlight_width

    def get_attr(self, attr_: str, other):
        """ Get attribute from other, but if not there use self. """
        attr_self = getattr(self, attr_)
        if attr_self is None:
            raise ValueError(f"Unsupported attribute for this Font. {attr_}")
        attr_other = getattr(other, attr_)
        return attr_other if attr_other is not None else attr_self
