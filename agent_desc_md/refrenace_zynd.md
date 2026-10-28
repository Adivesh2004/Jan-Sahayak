from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from zyndai_agent.agent import AgentConfig, ZyndAIAgent
import os

# Initialize agent
agent_config = AgentConfig(
    registry_url="https://registry.zynd.ai",
    mqtt_broker_url="mqtt://registry.zynd.ai:1883",
    identity_credential_path="./identity_credential.json",
    secret_seed=os.environ["AGENT_SEED"]
)
zyndai_agent = ZyndAIAgent(agent_config=agent_config)

@tool
def get_premium_market_data(symbol: str) -> str:
    """Fetch real-time premium market data for a stock symbol"""
    response = zyndai_agent.x402_processor.get(
        url="https://api.premium-data.com/stock",
        params={"symbol": symbol}
    )
    data = response.json()
    return f"Stock: {symbol}, Price: ${data['price']}, Volume: {data['volume']}"

@tool
def analyze_sentiment(text: str) -> str:
    """Analyze sentiment using a premium AI service"""
    response = zyndai_agent.x402_processor.post(
        url="https://api.sentiment-ai.com/analyze",
        json={"text": text}
    )
    result = response.json()
    return f"Sentiment: {result['sentiment']} (confidence: {result['confidence']})"

@tool
def generate_market_report(sector: str) -> str:
    """Generate a comprehensive market report for a sector"""
    response = zyndai_agent.x402_processor.post(
        url="https://api.reports.com/generate",
        json={"sector": sector, "depth": "comprehensive"}
    )
    return response.json()["report"]

# Create LangChain agent with x402-enabled tools
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
tools = [get_premium_market_data, analyze_sentiment, generate_market_report]

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a financial analysis agent with access to premium paid APIs.
    Use the available tools to provide comprehensive market analysis.
    Always cite the data sources and be clear about costs."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Use the agent
response = agent_executor.invoke({
    "input": "Give me a detailed analysis of Apple stock with sentiment analysis of recent news"
})
print(response["output"])

try:
    response = zyndai_agent.x402_processor.post(
        url="https://api.paid-service.com/endpoint",
        json={"data": "payload"}
    )
    result = response.json()
    print(f"Success: {result}")
    
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 402:
        print("Payment required but failed to process")
    elif e.response.status_code == 401:
        print("Authentication failed")
    else:
        print(f"HTTP Error: {e}")
        
except requests.exceptions.ConnectionError:
    print("Failed to connect to the API endpoint")
    
except Exception as e:
    print(f"Unexpected error: {e}")

from zyndai_agent.agent import AgentConfig, ZyndAIAgent
import os

# Configure with webhook mode
agent_config = AgentConfig(
    webhook_host="0.0.0.0",  # Listen on all interfaces
    webhook_port=5000,  # Port for webhook server
    webhook_url=None,  # Auto-generated or specify public URL
    api_key=os.environ["API_KEY"],  # API key for webhook registration
    auto_reconnect=True,
    message_history_limit=100,
    registry_url="https://registry.zynd.ai",
    identity_credential_path="./identity_credential.json",
    secret_seed=os.environ["AGENT_SEED"]
)

# Agent automatically starts webhook server
zyndai_agent = ZyndAIAgent(agent_config=agent_config)
print(f"Webhook server running at: {zyndai_agent.webhook_url}")

# Connect to a discovered agent
zyndai_agent.connect_agent(selected_agent)

# Send encrypted message via HTTP POST
result = zyndai_agent.send_message(
    message_content="Can you help me analyze this dataset?",
    message_type="query"
)

# Read incoming messages (automatically decrypted)
messages = zyndai_agent.read_messages()

# Messages sent to /webhook endpoint
# Returns immediately without waiting for agent processing
result = zyndai_agent.send_message("Process this data")

# Handler processes asynchronously
def message_handler(message: AgentMessage, topic: str):
    # Process message
    response = process_message(message.content)

    # Optionally send response via separate webhook call
    if zyndai_agent.target_webhook_url:
        zyndai_agent.send_message(response)

zyndai_agent.add_message_handler(message_handler)

from zyndai_agent.agent import AgentConfig, ZyndAIAgent
from zyndai_agent.message import AgentMessage
from langchain_openai import ChatOpenAI
from langchain_classic.memory import ChatMessageHistory
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.tools.tavily_search import TavilySearchResults
import os

# Configure agent with webhook and x402
agent_config = AgentConfig(
    webhook_host="0.0.0.0",
    webhook_port=5001,
    webhook_url=None,
    auto_reconnect=True,
    message_history_limit=100,
    registry_url="https://registry.zynd.ai",
    identity_credential_path="./identity_credential.json",
    secret_seed=os.environ["AGENT_SEED"],
    agent_id=os.environ["AGENT_ID"],
    price="$0.01",  # Enable x402 payments
    pay_to_address="0xYourAddress",
    api_key=os.environ["API_KEY"]
)

# Initialize agent
zynd_agent = ZyndAIAgent(agent_config=agent_config)

# Create LangChain agent
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
search_tool = TavilySearchResults(max_results=3)
message_history = ChatMessageHistory()

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI agent with web search capabilities."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

agent = create_tool_calling_agent(llm, [search_tool], prompt)
agent_executor = AgentExecutor(agent=agent, tools=[search_tool], verbose=True)
zynd_agent.set_agent_executor(agent_executor)

# Message handler for both sync and async
def message_handler(message: AgentMessage, topic: str):
    # Add to history
    message_history.add_user_message(message.content)

    # Process with LangChain agent
    agent_response = zynd_agent.agent_executor.invoke({
        "input": message.content,
        "chat_history": message_history.messages
    })
    agent_output = agent_response["output"]

    message_history.add_ai_message(agent_output)

    # Set response for synchronous mode
    zynd_agent.set_response(message.message_id, agent_output)

    # Also send via webhook for agent-to-agent communication
    if zynd_agent.target_webhook_url:
        zynd_agent.send_message(agent_output)

zynd_agent.add_message_handler(message_handler)

print(f"\nWebhook Agent Running!")
print(f"Webhook URL: {zynd_agent.webhook_url}")
print(f"x402 Payments: Enabled at {agent_config.price}")
print("Supports both /webhook (async) and /webhook/sync (sync) endpoints")