"""Home Assistant REST API client wrapper."""

from homeassistant_api import Client
from homeassistant_api.errors import UnauthorizedError


class HaClient:
    """Thin wrapper around homeassistant_api that caches entity handles."""

    def __init__(self, addr: str, api_key: str, entities: dict[str, str]):
        try:
            self.entities = {}
            with Client(addr, api_key) as client:
                for entity_name, entity_id in entities.items():
                    try:
                        self.entities[entity_name] = client.get_entity(entity_id=entity_id)
                    except UnauthorizedError as e:
                        print(f"Error fetching entity {entity_id}: {e}")
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
        except TypeError as e:
            print(f"TypeError fetching value for {entity_name}: {e}")
            return "Error"
    async def get_data(self) -> tuple[str, str, str, str]:
        """Return the state and unit of measurement for a named entity."""
        res = []
        for entity in self.entities:
            try:
                res.append(await self.get_val(entity))
            except (KeyError, UnauthorizedError) as e:
                print(f"Error fetching value for {entity}: {e}")
                res.append("Error")
        return tuple(res)
