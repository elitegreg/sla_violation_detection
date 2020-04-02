"""Class to handle possible SLA violations.

SLA violations are handled by provider specific plugins.
"""
class SLAHandler:
    _per_provider_handlers = {}

    """Register a plugin.

    Args:
        provider (str): identifier, must match DeviceOrCircuit table
        handler (func(UnscheduledOutage): SLA handler
    """
    @staticmethod
    def register_handler(provider, handler):
        SLAHandler._per_provider_handlers[provider] = handler

    """Dispatches outage to plugin handler.
    
    Args:
        outage (UnscheduledOutage)

    Raises:
        SLAError: no plugin registered for provider
    """
    @staticmethod
    def handle_unscheduled_outage(outage):
        handler = SLAHandler._per_provider_handlers.get(outage.provider)

        if not handler:
            raise SLAError(f'No SLA handler for {outage.provider}')

        return handler(outage)


"""Decorator to register a handler with SLAHandler..

Args:
    provider (str): identifier, must match DeviceOrCircuit table
"""
class register_handler:
    def __init__(self, provider):
        self._provider = provider

    def __call__(self, func):
        SLAHandler.register_handler(self._provider, func)
        return func


class SLAError(RuntimeError):
    pass


# load plugins
import sla_handlers
