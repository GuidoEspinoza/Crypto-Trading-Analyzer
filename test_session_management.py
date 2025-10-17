#!/usr/bin/env python3
"""
Test script for Capital.com session management improvements
"""

import sys
import os
import time
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.capital_client import create_capital_client_from_env
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_session_management():
    """Test the improved session management system"""
    
    print("🔧 TESTING CAPITAL.COM SESSION MANAGEMENT")
    print("=" * 50)
    
    try:
        # Create client
        print("1. Creating Capital.com client...")
        client = create_capital_client_from_env()
        
        # Test initial session status
        print("\n2. Initial session status:")
        status = client.get_session_status()
        print(json.dumps(status, indent=2))
        
        # Test ping functionality
        print("\n3. Testing ping functionality...")
        ping_result = client.ping()
        print(f"   Ping result: {ping_result}")
        
        # Test market data retrieval
        print("\n4. Testing market data retrieval...")
        symbols = ["GOLD", "SILVER"]
        market_data = client.get_market_data(symbols)
        print(f"   Retrieved data for {len(market_data)} symbols")
        for symbol, data in market_data.items():
            print(f"   {symbol}: bid={data.get('bid')}, offer={data.get('offer')}")
        
        # Test session status after operations
        print("\n5. Session status after operations:")
        status = client.get_session_status()
        print(json.dumps(status, indent=2))
        
        # Test session persistence
        print("\n6. Testing session persistence...")
        session_file = client.session_file
        if os.path.exists(session_file):
            print(f"   ✅ Session file exists: {session_file}")
            with open(session_file, 'r') as f:
                session_data = json.load(f)
            print(f"   Session data keys: {list(session_data.keys())}")
        else:
            print(f"   ❌ Session file not found: {session_file}")
        
        # Test health check
        print("\n7. Testing health check...")
        health_result = client._perform_health_check()
        print(f"   Health check result: {health_result}")
        
        # Test session validation
        print("\n8. Testing session validation...")
        validation_result = client._ensure_valid_session()
        print(f"   Session validation result: {validation_result}")
        
        print("\n✅ All session management tests completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Session management test failed: {str(e)}")
        logger.error(f"Session management test error: {str(e)}", exc_info=True)
        return False

def test_session_renewal_simulation():
    """Simulate session renewal scenarios"""
    
    print("\n🔄 TESTING SESSION RENEWAL SCENARIOS")
    print("=" * 50)
    
    try:
        client = create_capital_client_from_env()
        
        # Force session renewal by manipulating session age
        print("1. Simulating session expiry...")
        if client.session_created_at:
            # Simulate old session
            from datetime import timedelta
            client.session_created_at = datetime.now() - timedelta(seconds=client.renewal_threshold + 10)
            
            print(f"   Simulated session age: {(datetime.now() - client.session_created_at).total_seconds():.0f}s")
            print(f"   Renewal threshold: {client.renewal_threshold}s")
            
            # Test if renewal is triggered
            should_renew = client._should_renew_session()
            print(f"   Should renew session: {should_renew}")
            
            if should_renew:
                print("   Triggering session renewal...")
                validation_result = client._ensure_valid_session()
                print(f"   Renewal result: {validation_result}")
        
        print("\n✅ Session renewal simulation completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Session renewal simulation failed: {str(e)}")
        logger.error(f"Session renewal simulation error: {str(e)}", exc_info=True)
        return False

def test_session_monitoring():
    """Test session monitoring and alerting"""
    
    print("\n📊 TESTING SESSION MONITORING")
    print("=" * 50)
    
    try:
        client = create_capital_client_from_env()
        
        # Test monitoring data
        print("1. Session monitoring data:")
        status = client.get_session_status()
        monitoring_data = {
            "session_renewals": status["session_renewals"],
            "session_failures": status["session_failures"],
            "failed_requests": status["failed_requests"],
            "session_healthy": status["session_healthy"]
        }
        print(json.dumps(monitoring_data, indent=2))
        
        # Test alert logging
        print("\n2. Testing alert system...")
        client._log_session_alert("TEST_ALERT", "This is a test alert", "info")
        
        # Test failure tracking
        print("\n3. Testing failure tracking...")
        initial_failures = client.session_failures
        client._track_session_failure("Test failure for monitoring")
        print(f"   Failures before: {initial_failures}")
        print(f"   Failures after: {client.session_failures}")
        
        print("\n✅ Session monitoring tests completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Session monitoring test failed: {str(e)}")
        logger.error(f"Session monitoring test error: {str(e)}", exc_info=True)
        return False

def main():
    """Run all session management tests"""
    
    print("🚀 CAPITAL.COM SESSION MANAGEMENT TEST SUITE")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Basic Session Management", test_session_management),
        ("Session Renewal Simulation", test_session_renewal_simulation),
        ("Session Monitoring", test_session_monitoring)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All session management tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check logs for details.")
        return 1

if __name__ == "__main__":
    exit(main())