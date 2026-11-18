import asyncio
import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import src.bot as bot


@pytest.fixture(autouse=True)
def isolate_files(tmp_path, monkeypatch):
    monkeypatch.setattr(bot, "USERS_FILE", str(tmp_path / "users.json"))
    monkeypatch.setattr(bot, "STATE_FILE", str(tmp_path / "channel_state.json"))
    bot.live_message_id = None
    bot.last_sent_text = ""
    yield


@pytest.mark.asyncio
async def test_concurrent_save_user_no_data_loss():
    users = [MagicMock(id=i, full_name=f"User{i}", username=f"u{i}") for i in range(20)]
    await asyncio.gather(*[bot.save_user(u) for u in users])
    data = bot.load_users()
    assert len(data) == 20
    with open(bot.USERS_FILE, encoding="utf-8") as f:
        json.load(f)


@pytest.mark.asyncio
async def test_concurrent_update_channel_board_sends_once():
    fake_data = {
        "usd": 1,
        "gold_18k": 2,
        "gold_ounce": 3,
        "coin_emami": 4,
        "updated_at": "x 1",
        "date_shamsi_full": "d",
    }
    with (
        patch("src.bot.fetch_prices", new=AsyncMock(return_value=fake_data)),
        patch("src.bot.build_channel_message", return_value="MSG"),
        patch.object(bot.bot, "send_message", new=AsyncMock(return_value=MagicMock(message_id=42))),
        patch.object(bot.bot, "pin_chat_message", new=AsyncMock()),
    ):
        await asyncio.gather(*[bot.update_channel_board() for _ in range(10)])
        assert bot.bot.send_message.await_count == 1
        assert bot.bot.pin_chat_message.await_count == 1
        assert bot.live_message_id == 42
    assert os.path.exists(bot.STATE_FILE)
    with open(bot.STATE_FILE, encoding="utf-8") as f:
        state = json.load(f)
    assert state["live_message_id"] == 42


@pytest.mark.asyncio
async def test_state_roundtrip():
    bot.live_message_id = 7
    bot.last_sent_text = "hello"
    bot._save_state()
    bot.live_message_id = None
    bot.last_sent_text = ""
    bot._load_state()
    assert bot.live_message_id == 7
    assert bot.last_sent_text == "hello"


@pytest.mark.asyncio
async def test_cmd_gold_calc_invalid_gold_rate():
    bot.save_user = AsyncMock()
    msg = MagicMock()
    msg.from_user.id = 1
    msg.text = "/gold 10 14"
    msg.answer = AsyncMock()
    with patch("src.bot.fetch_prices", new=AsyncMock(return_value={"gold_18k": "abc"})):
        await bot.cmd_gold_calc(msg)
    msg.answer.assert_awaited()
    assert "خطا" in msg.answer.await_args.args[0]


@pytest.mark.asyncio
async def test_cmd_abshodeh_invalid_gold_rate():
    bot.save_user = AsyncMock()
    msg = MagicMock()
    msg.from_user.id = 1
    msg.text = "/abshodeh 10"
    msg.answer = AsyncMock()
    with patch("src.bot.fetch_prices", new=AsyncMock(return_value={"gold_18k": "abc"})):
        await bot.cmd_abshodeh_calc(msg)
    msg.answer.assert_awaited()
    assert "خطا" in msg.answer.await_args.args[0]


@pytest.mark.asyncio
async def test_inline_invalid_rates_no_crash():
    query = MagicMock()
    query.query = "5"
    query.answer = AsyncMock()
    with patch("src.bot.get_cached_prices", new=AsyncMock(return_value={"usd": "abc", "gold_18k": 2})):
        await bot.inline_calculator(query)
    query.answer.assert_not_awaited()


@pytest.mark.asyncio
async def test_admin_view_escapes_html(monkeypatch):
    monkeypatch.setattr(bot, "load_users", lambda: {"1": {"name": "<script>", "username": "@a"}})
    monkeypatch.setattr(bot, "ADMIN_ID", 999)
    msg = MagicMock()
    msg.from_user.id = 999
    msg.answer = AsyncMock()
    await bot.handle_admin_users(msg)
    text = msg.answer.await_args.args[0]
    assert "<script>" not in text
    assert "&lt;script&gt;" in text