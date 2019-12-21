from typing import List, Set, Dict, Tuple, Optional, Any, Callable
from chainalytic.common import config
from chainalytic.provider.api_bundle import BaseApiBundle


class ApiBundle(BaseApiBundle):

    def __init__(self, working_dir: str, zone_id: str):
        super(ApiBundle, self).__init__(working_dir, zone_id)

    async def get_unstaking(self, api_params: dict) -> Optional[float]:
        if 'height' in api_params:
            return await self.collator.get_block(api_params['height'], 'unstaking')