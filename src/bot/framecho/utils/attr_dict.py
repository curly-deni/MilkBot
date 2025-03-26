__all__ = ["AttrDict"]


class AttrDict(dict):
    def __getattr__(self, item):
        return self.get(item, None)
