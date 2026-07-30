import lvgl as lv

class RebuildableObj(lv.obj):
    """Base for all lv.obj subclasses that own a named list of children in a
    guaranteed order.

    _SUBELEMENTS is a list of (name, factory) tuples.  Children are created
    in list order — first tuple becomes child index 0 (top in flex column).
    """
    _SUBELEMENTS = []  # override: [("slot_name", WidgetClass), ...]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_self()
        self._init_grid()
        self.post_init()

    def setup_self(self):
        """Hook for subclasses to do things before subelements are built."""
        pass

    def post_init(self):
        """Hook for subclasses to do things after subelements are built."""
        pass

    def _init_grid(self):
        for name, factory in self._SUBELEMENTS:
            setattr(self, name, factory(self))

    def _delete_grid(self):
        for name, _ in self._SUBELEMENTS:
            getattr(self, name).delete()

    def _factory_for(self, name):
        for n, f in self._SUBELEMENTS:
            if n == name:
                return f
        print(f"could not find key '{name}' in _SUBELEMENTS")
        return None

    def rebuild_slot(self, name):
        old = getattr(self, name)
        idx = old.get_index()
        old.delete()
        new_factory = self._factory_for(name)
        if new_factory is not None:
            new = new_factory(self)
            new.move_to_index(idx)
            setattr(self, name, new)
            return new
        return None

    def rebuild_all(self):
        self._delete_grid()

        self.setup_self()
        self._init_grid()
        self.post_init()