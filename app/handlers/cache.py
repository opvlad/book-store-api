from fastapi_cache import FastAPICache

from app.event_bus import bus


@bus.on_event("book.created")
@bus.on_event("book.updated")
@bus.on_event("book.deleted")
async def invalidate_books_list_cache(**kwargs):
    await FastAPICache.clear(namespace="books-list")


@bus.on_event("author.created")
@bus.on_event("author.updated")
@bus.on_event("author.deleted")
async def invalidate_authors_list_cache(**kwargs):
    await FastAPICache.clear(namespace="authors-list")
