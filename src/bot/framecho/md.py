import importlib
import importlib.util
import sys
from pathlib import Path

from framecho.utils.attr_dict import AttrDict
from framecho.utils.storage_builder import build_storage

__all__ = ["ModuleLoader"]


class ModuleLoader:
    _instance = None
    _loaded = False

    def __new__(cls, base_path: str):
        if cls._instance is None:
            cls._instance = super(ModuleLoader, cls).__new__(cls)
            cls._instance._init(base_path)
        return cls._instance

    def _init(self, base_path: str):
        self._base_path = Path(base_path).resolve()
        self._modules = AttrDict()

    @property
    def base_path(self):
        return self._base_path

    @property
    def modules(self):
        return self._modules

    def load_module(self, module_name: str, module_path: str):
        module_path = Path(module_path).resolve()
        init_file = module_path / "__init__.py"

        if not init_file.exists():
            print(f"Error: {module_name} does not contain an __init__.py file.")
            return

        module_spec = importlib.util.spec_from_file_location(
            module_name, str(init_file)
        )

        if module_spec is None:
            print(f"Error: Could not create modules spec for {module_name}")
            return

        module = importlib.util.module_from_spec(module_spec)

        # sys.modules[module_name] = modules

        original_sys_path = sys.path[:]
        sys.path.insert(0, str(module_path))

        try:
            module_spec.loader.exec_module(module)
            self.modules[module_name] = ModuleWrapper(module)
            return self.modules[module_name]
        except Exception as e:
            print(f"Error loading modules {module_name}: {e}")
        finally:
            sys.path = original_sys_path

    def load_standard_modules(self):
        app_path = self.base_path / "app"
        framecho_path = self.base_path / "framecho" / "module"

        if not app_path.exists():
            print(f"Warning: {app_path} does not exist, skipping 'app' module.")
        else:
            self.load_module("app", app_path)  # noqa

        if not framecho_path.exists():
            print(
                f"Warning: {framecho_path} does not exist, skipping 'framecho' module."
            )
        else:
            self.load_module("framecho", framecho_path)  # noqa

    def load_other_modules(self):
        modules_dir = self.base_path / "modules"

        if not modules_dir.exists():
            print(
                f"Warning: {modules_dir} does not exist, skipping additional modules."
            )
            return

        for module in modules_dir.iterdir():
            if module.is_dir() and (module / "__init__.py").exists():
                self.load_module(module.name, module)

    def load_all(self):
        if self._loaded:
            return
        self._loaded = True
        self.load_standard_modules()
        self.load_other_modules()

    def load_by_name(self, module_name: str):
        if module_name in self.modules:
            return self.modules[module_name]
        if module_name == "app":
            return self.load_module("app", self.base_path / "app")  # noqa
        elif module_name == "framecho":
            return self.load_module(
                "framecho", self.base_path / "framecho" / "module"
            )  # noqa
        return self.load_module(
            module_name, self.base_path / "modules" / module_name
        )  # noqa


class ModuleWrapper:
    def __init__(self, module):
        self._module = module
        self._name = module.__name__
        self._path = Path(module.__file__).parent
        self._cogs = self._load_cogs()
        self._models = self._load_models()
        self._migrations_conf = self._get_migration_conf()
        self._ext = self._load_ext()

    @property
    def module(self):
        return self._module

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return self._path

    @property
    def cogs(self):
        return self._cogs

    @property
    def models(self):
        return self._models

    @property
    def migrations_conf(self):
        return self._migrations_conf

    @property
    def ext(self):
        return self._ext

    @property
    def import_name(self):
        if self.name == "app":
            return "app"
        elif self.name == "framecho":
            return "framecho.module"
        else:
            return f"modules.{self.name}"

    def load_on_startup_script(self):
        ext_dir = self.path / "ext"
        startup_script_dir = ext_dir / "on_startup_script"
        if startup_script_dir.exists():
            for script in startup_script_dir.glob("*.py"):
                if script.stem != "__init__":
                    importlib.import_module(
                        f"{self.import_name}.ext.startup_script.{script.stem}"
                    )

    def load_on_connect_script(self):
        ext_dir = self.path / "ext"
        connect_script_dir = ext_dir / "on_connect_script"
        if connect_script_dir.exists():
            for script in connect_script_dir.glob("*.py"):
                if script.stem != "__init__":
                    importlib.import_module(
                        f"{self.import_name}.ext.on_connect_script.{script.stem}"
                    )

    def _load_cogs(self):
        cogs_dir = self.path / "cogs"
        if not cogs_dir.exists():
            return []
        cogs = []
        for item in cogs_dir.iterdir():
            if item.is_file() and item.suffix == ".py" and item.stem != "__init__":
                cogs.append(f"{self.import_name}.cogs.{item.stem}")
            elif item.is_dir() and (item / "__init__.py").exists():
                cogs.append(f"{self.import_name}.cogs.{item.name}")
        return cogs

    def _load_models(self):
        models_dir = self.path / "models"
        models = AttrDict()
        if models_dir.exists():
            for model_file in models_dir.glob("*.py"):
                if model_file.stem != "__init__":
                    model_module = f"{self.import_name}.models.{model_file.stem}"

                    try:
                        models[model_file.stem] = importlib.import_module(model_module)
                    except ImportError as e:
                        print(
                            f"Error loading model {model_file.stem} for {self.name}: {e}"
                        )
        return models

    def _get_migration_conf(self):
        alembic_ini = self.path / "alembic.ini"
        migrations_dir = self.path / "migrations"
        if alembic_ini.exists() and migrations_dir.exists():
            sub_migrations_dir = migrations_dir / "migrations"
            env_file = migrations_dir / "env.py"
            script_file = migrations_dir / "script.py.mako"
            if (
                sub_migrations_dir.exists()
                and env_file.exists()
                and script_file.exists()
            ):
                return AttrDict(
                    {
                        "alembic_ini": str(alembic_ini),
                        "migrations_dir": str(sub_migrations_dir),
                        "env_file": str(env_file),
                        "script_file": str(script_file),
                    }
                )
        return None

    def _get_localization_path(self):
        messages_dir = self.path / "messages"
        return str(messages_dir) if messages_dir.exists() else None

    def _build_localization(self):
        return build_storage(
            self._get_localization_path(), f"./runtime/messages/{self.name}"
        )

    def _load_ext(self):
        ext_dir = self.path / "ext"
        bot_parts_dir = ext_dir / "bot"
        loaded_ext = AttrDict()
        if bot_parts_dir.exists():
            for part in bot_parts_dir.glob("*.py"):
                module = importlib.import_module(
                    f"{self.import_name}.ext.bot.{part.stem}"
                )

                if hasattr(module, "__all__"):
                    loaded_ext.update(
                        {name: getattr(module, name) for name in module.__all__}
                    )
        return loaded_ext
