
import abc


class Base(abc.ABC):
    scale = []
    parent = None

    def get_attr(self, attr_: str, other):
        """ Get attribute from other, but if not there use self. """
        attr_self = getattr(self, attr_)
        if attr_self is None:
            raise ValueError(f"Unsupported attribute for this Font. {attr_}")
        attr_other = getattr(other, attr_)

        attr_out = attr_other if attr_other is not None else attr_self

        if attr_ in self.scale:
            attr_out = attr_out / self.parent._scaling

        return attr_out


class Font(Base):
    scale = ["size", "offset", "top_offset"]

    def __init__(self,
                 parent=None,
                 show: bool = None,
                 family: str = None,
                 size: int = None,
                 bold: bool = None,
                 color: str = None,
                 offset: float = None,
                 alignment: str = None,
                 top_offset: float = None,
                 ):
        self.show = show
        self.family = family
        self.bold = bold
        self.size = size
        self.color = color
        self.offset = offset
        self.alignment = alignment
        self.top_offset = top_offset
        self.parent = parent


class Line(Base):
    scale = ["width"]

    def __init__(self,
                 parent=None,
                 show: bool = None,
                 width: int = None,
                 color: str = None,
                 ):
        self.show = show
        self.width = width
        self.color = color
        self.parent = parent


class Highlight(Base):
    scale = ["size"]

    def __init__(self,
                 parent=None,
                 show: bool = None,
                 size: int = None,
                 color: str = None,
                 offset: float = None,
                 ):
        self.show = show
        self.size = size
        self.color = color
        self.offset = offset
        self.parent = parent
