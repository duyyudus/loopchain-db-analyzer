import json
import time
from typing import Dict, List, Optional, Set, Tuple, Union

import plyvel
from iconservice.icon_config import default_icon_config
from iconservice.icon_constant import ConfigKey
from iconservice.iiss.engine import Engine

from chainalytic.aggregator.transform import BaseTransform
from chainalytic.common import rpc_client, trie


class Transform(BaseTransform):
    LAST_STATE_HEIGHT_KEY = b'last_state_height'

    def __init__(self, working_dir: str, zone_id: str, transform_id: str):
        super(Transform, self).__init__(working_dir, zone_id, transform_id)

    async def execute(self, height: int, input_data: dict) -> Optional[Dict]:
        start_time = time.time()

        # Load transform cache to retrive previous staking state
        cache_db = self.transform_cache_db
        cache_db_batch = self.transform_cache_db.write_batch()

        # Make sure input block data represents for the next block of previous state cache
        prev_state_height = cache_db.get(Transform.LAST_STATE_HEIGHT_KEY)
        if prev_state_height:
            prev_state_height = int(prev_state_height)
            if prev_state_height != height - 1:
                await rpc_client.call_async(
                    self.warehouse_endpoint,
                    call_id='api_call',
                    api_id='set_last_block_height',
                    api_params={'height': prev_state_height, 'transform_id': self.transform_id},
                )
                return None

        # #################################################

        set_stake_wallets = input_data['data']

        if set_stake_wallets:
            recent_stake_wallets = cache_db.get(b'recent_stake_wallets')
            if recent_stake_wallets:
                recent_stake_wallets = json.loads(recent_stake_wallets)
            else:
                recent_stake_wallets = {}

            cache_db_batch.put(b'recent_stake_wallets', json.dumps(recent_stake_wallets).encode())
        else:
            recent_stake_wallets = None

        cache_db_batch.put(Transform.LAST_STATE_HEIGHT_KEY, str(height).encode())
        cache_db_batch.write()

        # execution_time = f'{round(time.time()-start_time, 4)}s'

        return {
            'height': height,
            'data': {},
            'misc': {'recent_stake_wallets': {'wallets': recent_stake_wallets, 'height': height}},
        }