"""Home Assistant REST API client wrapper."""

from typing import Dict

from homeassistant_api import Client
from homeassistant_api.errors import UnauthorizedError


class HaClient:  # pylint: disable=too-few-public-methods
    """Thin wrapper around homeassistant_api that caches entity handles."""

    def __init__(self, addr: str, api_key: str, entities: Dict[str, str]):
        try:
            self.entities = {}
            with Client(addr, api_key) as client:
                for entity_name, entity_id in entities.items():
                    self.entities[entity_name] = client.get_entity(entity_id=entity_id)
        except UnauthorizedError as e:
            print(f"Error initializing HaClient: {e}")

    async def get_val(self, entity_name: str) -> str:
        """Return the state and unit of measurement for a named entity."""
        try:
            res = self.entities[entity_name].get_state()
            return res.state + " " + res.attributes["unit_of_measurement"]
        except (KeyError, UnauthorizedError) as e:
            print(f"Error fetching value for {entity_name}: {e}")
            return "Error"
