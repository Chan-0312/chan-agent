import os
from typing import Literal


DEFAULT_LLM_TRACKER: Literal['db_tracker', 'json_tracker'] = os.environ.get('CHAN_AGENT_DEFAULT_LLM_TRACKER', 'db_tracker')