from app.event_bus import EventBus



async def test_unhandled_exception_handled(client, mocker, admin_token, test_user):
    mocker.patch("app.routers.v1.users.service_get_user", side_effect=Exception("test-unexpected"))
    response = await client.get(f"/api/v1/users/{test_user.id}", headers={"Authorization": f"Bearer {admin_token}"})

    print(response.status_code, response.json())

    assert response.status_code == 500
    assert response.json()["detail"] == "Internal server error"


async def test_emit_logs_error_and_continue():
    calls = []
    bus = EventBus()

    @bus.on_event("test")
    async def failed_handler():
        calls.append("failed")
        raise Exception("test-error")

    @bus.on_event("test")
    async def second_handler():
        calls.append("done")

    await bus.emit("test")
    assert calls == ["failed", "done"]
