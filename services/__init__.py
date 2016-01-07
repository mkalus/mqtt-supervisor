# Services Package - import all classes
from .ServiceClass import ServiceClass
from .CommandReturnService import CommandReturnService
from .LinuxNetstatService import LinuxNetstatService
from .CommandContentService import CommandContentService

# Service factory
def service_factory(service_name, name, config, settings):
    for cls in ServiceClass.__subclasses__():
        if cls.is_service_name_for(service_name):
            return cls(name, config, settings)
    raise ValueError("No service with name \"" + service_name + "\" exists.")
