
import pytest
import os
from unittest.mock import patch, AsyncMock
from chimera.core.commerce import CommerceManager, BudgetExceededError

# Mark as async
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_commerce_manager():
    """Returns a CommerceManager with mocked providers."""
    with patch("chimera.core.commerce.AGENTKIT_AVAILABLE", True):
        with patch.dict(os.environ, {
            "CDP_API_KEY_NAME": "test-key", 
            "CDP_API_KEY_PRIVATE_KEY": "test-secret",
            "MAX_DAILY_USDC": "100.0"
        }):
            # Mock the internal providers
            with patch("chimera.core.commerce.CdpEvmWalletProvider") as MockWallet:
                with patch("chimera.core.commerce.Erc20ActionProvider") as MockErc20:
                    with patch("redis.Redis") as MockRedis:
                        
                        manager = CommerceManager()
                        
                        # Setup Wallet Mock
                        manager.wallet_provider.get_wallet_address.return_value = "0xAgentWallet"
                        manager.wallet_provider.get_balance = AsyncMock(return_value=1000000000000000000) # 1 ETH
                        
                        # Setup ERC20 Mock
                        manager.erc20_provider.get_balance = AsyncMock(return_value=50000000) # 50 USDC
                        manager.erc20_provider.transfer = AsyncMock(return_value="0xTransactionHash")
                        
                        # Setup Redis Mock
                        mock_redis_instance = manager.redis_client
                        mock_redis_instance.get.return_value = "0.0" # No spend yet
                        
                        yield manager

async def test_get_balance(mock_commerce_manager):
    """Test balance retrieval."""
    balance_usdc = await mock_commerce_manager.get_balance("USDC")
    assert balance_usdc == 50.0 # 50000000 / 1e6
    
    balance_eth = await mock_commerce_manager.get_balance("ETH")
    assert balance_eth == 1.0 # 1e18 / 1e18

async def test_send_payment_success(mock_commerce_manager):
    """Test successful payment."""
    result = await mock_commerce_manager.send_payment(
        to_address="0xRecipient",
        amount_usdc=20.0,
        agent_id="test_agent"
    )
    
    assert result["status"] == "success"
    assert result["amount"] == 20.0
    assert result["tx_hash"] == "0xTransactionHash"
    
    # Verify Redis increment was called
    mock_commerce_manager.redis_client.incrbyfloat.assert_called_with(
        "daily_spend:USDC:test_agent", 20.0
    )

async def test_send_payment_budget_exceeded(mock_commerce_manager):
    """Test budget enforcement."""
    # Mock existing spend
    mock_commerce_manager.redis_client.get.return_value = "90.0" # Limit is 100.0
    
    with pytest.raises(BudgetExceededError) as excinfo:
        await mock_commerce_manager.send_payment(
            to_address="0xRecipient",
            amount_usdc=15.0, # 90 + 15 = 105 > 100
            agent_id="test_agent"
        )
    
    assert "exceed daily limit" in str(excinfo.value)

async def test_deploy_token(mock_commerce_manager):
    """Test token deployment simulation."""
    result = await mock_commerce_manager.deploy_token(
        name="ChimeraCoin",
        symbol="CMC",
        total_supply=1000000
    )
    
    assert result["status"] == "success"
    assert result["contract_address"].startswith("0x")
    assert result["name"] == "ChimeraCoin"
