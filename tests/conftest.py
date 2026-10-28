import pytest
from unittest.mock import MagicMock, patch
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture
def mock_llm():
    with patch("src.agents.llm") as mock:
        yield mock

@pytest.fixture
def mock_retriever():
    with patch("src.tools.get_retriever") as mock_get:
        mock_retriever_instance = MagicMock()
        mock_retriever_instance.invoke.return_value = []
        mock_get.return_value = mock_retriever_instance
        yield mock_retriever_instance

@pytest.fixture
def mock_zynd_agent():
    with patch("src.tools.get_zynd_agent") as mock_get:
        mock_agent = MagicMock()
        mock_agent.agent_config.identity_credential_path = "mock/path/cred.json"
        mock_agent.agent_config.secret_seed = "mock_seed"
        mock_get.return_value = mock_agent
        yield mock_agent
