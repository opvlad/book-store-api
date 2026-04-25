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
            except Exception:
                raise


bus = EventBus()