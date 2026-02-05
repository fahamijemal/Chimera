#!/usr/bin/env python3
"""
Environment Variables Validation Script

Validates that all required environment variables are set and services are accessible.
"""
import os
import sys
from pathlib import Path
from typing import List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(project_root / ".env")


class ValidationResult:
    """Represents a validation check result."""
    def __init__(self, name: str, status: bool, message: str = "", warning: bool = False):
        self.name = name
        self.status = status
        self.message = message
        self.warning = warning
    
    def __str__(self):
        icon = "✅" if self.status else ("⚠️" if self.warning else "❌")
        return f"{icon} {self.name}: {self.message}"


def check_redis() -> ValidationResult:
    """Checks Redis connection."""
    try:
        import redis
        
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))
        
        # Try to connect
        client = redis.Redis(host=redis_host, port=redis_port, socket_connect_timeout=2)
        client.ping()
        
        return ValidationResult(
            "Redis",
            True,
            f"Connected to {redis_host}:{redis_port}"
        )
    except ImportError:
        return ValidationResult(
            "Redis",
            False,
            "redis package not installed. Install with: pip install redis"
        )
    except Exception as e:
        return ValidationResult(
            "Redis",
            False,
            f"Connection failed: {str(e)}"
        )


def check_weaviate() -> ValidationResult:
    """Checks Weaviate connection."""
    try:
        import requests
        
        weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
        
        # Try to connect
        headers = {}
        if weaviate_api_key:
            headers["Authorization"] = f"Bearer {weaviate_api_key}"
        
        response = requests.get(f"{weaviate_url}/v1/meta", headers=headers, timeout=2)
        response.raise_for_status()
        
        return ValidationResult(
            "Weaviate",
            True,
            f"Connected to {weaviate_url}"
        )
    except ImportError:
        return ValidationResult(
            "Weaviate",
            False,
            "requests package not installed. Install with: pip install requests"
        )
    except Exception as e:
        return ValidationResult(
            "Weaviate",
            False,
            f"Connection failed: {str(e)}"
        )


def check_coinbase() -> ValidationResult:
    """Checks Coinbase CDP credentials."""
    api_key_name = os.getenv("CDP_API_KEY_NAME")
    api_key_private_key = os.getenv("CDP_API_KEY_PRIVATE_KEY")
    
    if not api_key_name or api_key_name == "your-cdp-api-key-name":
        return ValidationResult(
            "Coinbase CDP",
            False,
            "CDP_API_KEY_NAME not set or using placeholder value"
        )
    
    if not api_key_private_key or api_key_private_key == "your-cdp-api-key-private-key":
        return ValidationResult(
            "Coinbase CDP",
            False,
            "CDP_API_KEY_PRIVATE_KEY not set or using placeholder value"
        )
    
    # Check if private key format looks correct
    if "BEGIN EC PRIVATE KEY" not in api_key_private_key:
        return ValidationResult(
            "Coinbase CDP",
            False,
            "CDP_API_KEY_PRIVATE_KEY format appears invalid (should include BEGIN/END markers)"
        )
    
    # Try to initialize CommerceManager (this will validate the keys)
    try:
        from chimera.core.commerce import CommerceManager
        
        manager = CommerceManager(
            api_key_name=api_key_name,
            api_key_private_key=api_key_private_key
        )
        
        # If initialization succeeds, credentials are valid
        wallet_address = manager.get_wallet_address()
        
        return ValidationResult(
            "Coinbase CDP",
            True,
            f"Credentials valid. Wallet: {wallet_address[:10]}..."
        )
    except ImportError:
        return ValidationResult(
            "Coinbase CDP",
            False,
            "coinbase-agentkit not installed. Install with: pip install coinbase-agentkit"
        )
    except Exception as e:
        return ValidationResult(
            "Coinbase CDP",
            False,
            f"Credential validation failed: {str(e)}"
        )


def check_required_vars() -> List[ValidationResult]:
    """Checks that all required environment variables are set."""
    required_vars = {
        "REDIS_URL": "Redis connection URL",
        "WEAVIATE_URL": "Weaviate instance URL",
    }
    
    results = []
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if not value:
            results.append(ValidationResult(
                f"Required: {var_name}",
                False,
                f"{description} not set"
            ))
        else:
            results.append(ValidationResult(
                f"Required: {var_name}",
                True,
                f"{description} is set"
            ))
    
    return results


def check_optional_vars() -> List[ValidationResult]:
    """Checks optional environment variables."""
    optional_vars = {
        "CDP_API_KEY_NAME": "Coinbase CDP API key name (required for commerce)",
        "CDP_API_KEY_PRIVATE_KEY": "Coinbase CDP private key (required for commerce)",
        "GEMINI_API_KEY": "Gemini API key (for LLM reasoning)",
        "ANTHROPIC_API_KEY": "Anthropic API key (for Claude)",
        "OPENAI_API_KEY": "OpenAI API key (for GPT-4o Vision)",
        "POSTGRES_URL": "PostgreSQL connection URL (optional)",
    }
    
    results = []
    for var_name, description in optional_vars.items():
        value = os.getenv(var_name)
        if not value or value.startswith("your-"):
            results.append(ValidationResult(
                f"Optional: {var_name}",
                False,
                f"{description} not set",
                warning=True
            ))
        else:
            results.append(ValidationResult(
                f"Optional: {var_name}",
                True,
                f"{description} is set"
            ))
    
    return results


def main():
    """Main validation function."""
    print("🔍 Validating Project Chimera Environment Setup\n")
    print("=" * 60)
    
    all_results: List[ValidationResult] = []
    
    # Check required variables
    print("\n📋 Required Environment Variables:")
    print("-" * 60)
    all_results.extend(check_required_vars())
    
    # Check optional variables
    print("\n📋 Optional Environment Variables:")
    print("-" * 60)
    all_results.extend(check_optional_vars())
    
    # Check service connections
    print("\n🔌 Service Connections:")
    print("-" * 60)
    all_results.append(check_redis())
    all_results.append(check_weaviate())
    all_results.append(check_coinbase())
    
    # Print all results
    print("\n📊 Validation Results:")
    print("=" * 60)
    for result in all_results:
        print(result)
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(1 for r in all_results if r.status)
    warnings = sum(1 for r in all_results if r.warning and not r.status)
    failed = sum(1 for r in all_results if not r.status and not r.warning)
    total = len(all_results)
    
    print(f"\nSummary: {passed}/{total} checks passed")
    if warnings > 0:
        print(f"⚠️  {warnings} optional items not configured")
    if failed > 0:
        print(f"❌ {failed} required items failed")
    
    # Exit code
    if failed > 0:
        print("\n❌ Validation failed. Please fix the errors above.")
        sys.exit(1)
    elif warnings > 0:
        print("\n⚠️  Validation passed with warnings. Optional features may not work.")
        sys.exit(0)
    else:
        print("\n✅ All validations passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
