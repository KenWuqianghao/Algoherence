import pytest
from algoherence.tools import MeanReversionTool
import pandas as pd
import os

def test_mean_reversion_tool_init():
    tool = MeanReversionTool()
    assert tool.name == "mean_reversion"
    assert "ticker" in tool.args_schema.model_fields

@pytest.mark.skipif(not os.getenv("TAVILY_API_KEY"), reason="TAVILY_API_KEY not set")
def test_search_tool():
    from algoherence.search import SearchTool
    tool = SearchTool()
    assert tool.name == "web_search"
