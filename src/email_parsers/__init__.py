import importlib
import pkgutil


__all__ = []


discovered_plugins = {
    name: importlib.import_module(name)
    for finder, name, ispkg
    in pkgutil.iter_modules(__path__, __name__ + ".")
}


del discovered_plugins
