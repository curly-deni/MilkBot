from .md import ModuleLoader

loader = ModuleLoader("./")
loader.load_all()

from .bot import *  # noqa
from .cog import *  # noqa
