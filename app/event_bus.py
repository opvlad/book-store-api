import logging


logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self):
        self._handlers = {}

    def on_event(self, event: str):
        def decorator(handler):
            self._handlers.setdefault(event, []).append(handler)
            return handler

        return decorator

    async def emit(self, event: str, **kwargs):
        for handler in self._handlers.get(event, []):
            try:
                await handler(**kwargs)
            except Exception as e:
                logger.error(
                    f"EMIT_MESSAGE_ERROR | handler={handler.__name__} | event={event} | kwargs={kwargs} | error={e}",
                    exc_info=True,
                )


bus = EventBus()
