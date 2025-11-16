

class StyleFont:
    __slots__ = ['show', 'family', 'bold', 'size', 'color', 'offset', 'alignment', 'top_offset', 'parent']
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


class StyleLine:
    __slots__ = ['show', 'width', 'color', 'parent']
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


class StyleHighlight:
    __slots__ = ['show', 'size', 'color', 'offset', 'parent']
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