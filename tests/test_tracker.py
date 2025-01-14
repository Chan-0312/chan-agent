import sys
sys.path.append("/home/chan/work/chan-agent")
from chan_agent.llm_track.db_tracker import LLMTracker


def test_db_tracker():
    LLMTracker.log({"test": "test"})

