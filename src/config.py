import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

from src.logger import setup_logger

logger = setup_logger("Config")

# Zynd Config
try:
    from zyndai_agent.agent import AgentConfig, ZyndAIAgent
except ImportError:
    logger.warning("zyndai_agent not found. Mocking for development if needed, but this should be installed.")
    ZyndAIAgent = None
    AgentConfig = None

_zynd_agents = {}

def get_zynd_agent(agent_name="default"):
    global _zynd_agents
    
    if agent_name in _zynd_agents:
        return _zynd_agents[agent_name]

    if ZyndAIAgent is None:
        raise ImportError("zyndai_agent package is missing.")
        
    logger.info(f"Initializing Zynd Agent: {agent_name}...")
    
    # Determine seed based on agent_name
    seed_env_var = "AGENT_SEED"
    if agent_name == "ORCHESTRATOR":
        seed_env_var = "ORCHESTRATOR_SEED"
    elif agent_name == "POLICY":
        seed_env_var = "POLICY_SEED"
    elif agent_name == "ELIGIBILITY":
        seed_env_var = "ELIGIBILITY_SEED"
    elif agent_name == "BENEFIT":
        seed_env_var = "BENEFIT_SEED"
    elif agent_name == "ADVOCACY":
        seed_env_var = "ADVOCACY_SEED"
        
    seed = os.getenv(seed_env_var)
    if not seed:
        logger.warning(f"No seed found for {agent_name} (checked {seed_env_var}). Using mock/default.")
        seed = "mock_seed_123"

    # Determine credential path (optional, if we want separate cred files)
    # logic to use specific json files in zynd_agents_cred/ if they exist
    cred_file = "identity_credential.json" 
    if agent_name == "ORCHESTRATOR":
        cred_file = "zynd_agents_cred/orchestration.json"
    elif agent_name == "POLICY":
        cred_file = "zynd_agents_cred/policy.json"
    elif agent_name == "ELIGIBILITY":
        cred_file = "zynd_agents_cred/eligibility.json"
    elif agent_name == "BENEFIT":
        cred_file = "zynd_agents_cred/benefits.json"
    elif agent_name == "ADVOCACY":
        cred_file = "zynd_agents_cred/advocacy.json"
        
    cred_path = os.path.abspath(cred_file)
    if not os.path.exists(cred_path):
        logger.warning(f"Credential file not found at {cred_path}. Falling back to identity_credential.json")
        cred_path = os.path.abspath("identity_credential.json")

    # Load generated ID from credential
    import json
    try:
        with open(cred_path, 'r') as f:
            cred_data = json.load(f)
            # The credential ID (DID) is usually the "issuer" or logic found in reference
            # Reference uses os.environ["AGENT_ID"]. We can derive it or use a default.
            # Using the issuer DID as agent_id for identity purposes
            agent_did = cred_data.get("issuer", f"did:zynd:{agent_name.lower()}")
    except Exception:
         agent_did = f"did:zynd:{agent_name.lower()}"

    # Assign distinct local ports to avoid collision if run concurrently (though they run in one process here)
    # Orchestrator: 5001, Policy: 5002, etc.
    port_map = {
        "ORCHESTRATOR": 5001,
        "POLICY": 5002,
        "ELIGIBILITY": 5003,
        "BENEFIT": 5004,
        "ADVOCACY": 5005,
        "default": 5000
    }
    
    agent_config = AgentConfig(
        webhook_host="0.0.0.0",
        webhook_port=port_map.get(agent_name, 5000),
        webhook_url=None,
        auto_reconnect=True,
        message_history_limit=100,
        registry_url=os.getenv("ZYND_REGISTRY_URL", "https://registry.zynd.ai"),
        identity_credential_path=cred_path,
        secret_seed=seed,
        agent_id=agent_did,
        price="$0.01", # Placeholder price as requested
        pay_to_address=os.getenv("PAY_TO_ADDRESS", "0x0000000000000000000000000000000000000000"),
        api_key=os.getenv("ZYND_API_KEY", "mock_key") # Added API key from env
    )
    logger.debug(f"Loaded API Key: {agent_config.api_key[:10]}...")
    
    try:
        agent = ZyndAIAgent(agent_config=agent_config)
        _zynd_agents[agent_name] = agent
        return agent
    except Exception as e:
        logger.warning(f"Failed to initialize Zynd Agent '{agent_name}'. Error: {e}")
        return None
