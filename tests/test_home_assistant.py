"""Tests for the Home Assistant REST API client wrapper."""
from unittest.mock import MagicMock, patch

import pytest

from home_assistant import HaClient


def _make_client(entities, state_value='21.3', unit='°C'):
    """Return an HaClient backed by a fully mocked homeassistant_api.Client."""
    mock_state = MagicMock()
    mock_state.state = state_value
    mock_state.attributes = {'unit_of_measurement': unit}

    mock_entity = MagicMock()
    mock_entity.get_state.return_value = mock_state

    mock_ha = MagicMock()
    mock_ha.__enter__ = MagicMock(return_value=mock_ha)
    mock_ha.__exit__ = MagicMock(return_value=False)
    mock_ha.get_entity.return_value = mock_entity

    with patch('home_assistant.Client', return_value=mock_ha):
        return HaClient('http://localhost:8123', 'test_key', entities)


class TestHaClientConstructor:
    def test_caches_all_requested_entities(self):
        client = _make_client({'temp': 'sensor.temp', 'humid': 'sensor.humid'})
        assert 'temp' in client.entities
        assert 'humid' in client.entities

    def test_empty_entities_dict_produces_empty_cache(self):
        client = _make_client({})
        assert client.entities == {}


class TestGetVal:
    async def test_returns_state_and_unit_concatenated(self):
        client = _make_client({'temp': 'sensor.temperature'})
        result = await client.get_val('temp')
        assert result == '21.3 °C'

    async def test_raises_key_error_for_unknown_entity(self):
        client = _make_client({'temp': 'sensor.temperature'})
        with pytest.raises(KeyError):
            await client.get_val('nonexistent')

    async def test_formats_different_state_and_unit(self):
        client = _make_client({'baro': 'sensor.baro'}, state_value='1013', unit='hPa')
        result = await client.get_val('baro')
        assert result == '1013 hPa'
