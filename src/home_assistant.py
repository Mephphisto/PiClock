from typing import Dict

from homeassistant_api import Client

class HA_Client:
    def __init__(self, addr: str, api_key: str, entities: Dict[str, str]):
        self.entities = {}
        with Client(addr, api_key) as client:
            for entity_name, entity_id in entities.items():
                self.entities[entity_name] = client.get_entity(entity_id=entity_id)
    async def get_val(self, entity_name:str) -> str:
        res = self.entities[entity_name].get_state()
        return res.state+' '+res.attributes['unit_of_measurement']
