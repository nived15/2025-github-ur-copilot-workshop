#!/usr/bin/env python3
"""
Simple test script to verify Pomodoro Timer functionality
"""
import requests
import json
import time

def test_logging_endpoint():
    """Test the /log endpoint"""
    print("Testing Flask app logging endpoint...")
    
    # Start the Flask app first (should be running)
    base_url = "http://127.0.0.1:5000"
    
    # Test data
    test_sessions = [
        {
            "session_type": "work",
            "action": "completed",
            "session_number": 1
        },
        {
            "session_type": "short_break", 
            "action": "completed",
            "session_number": 1
        },
        {
            "session_type": "work",
            "action": "skipped", 
            "session_number": 2
        }
    ]
    
    try:
        # Test each session log
        for session in test_sessions:
            response = requests.post(
                f"{base_url}/log",
                headers={"Content-Type": "application/json"},
                data=json.dumps(session)
            )
            
            if response.status_code == 200:
                print(f"✅ Logged: {session['session_type']} - {session['action']}")
            else:
                print(f"❌ Failed to log: {session} - Status: {response.status_code}")
        
        # Test history endpoint
        history_response = requests.get(f"{base_url}/history")
        if history_response.status_code == 200:
            history_data = history_response.json()
            print(f"✅ History endpoint works - Found {len(history_data.get('sessions', []))} sessions")
            
            # Print last few sessions
            sessions = history_data.get('sessions', [])
            if sessions:
                print("\n📋 Recent sessions:")
                for session in sessions[-5:]:  # Last 5 sessions
                    print(f"   {session['timestamp']} | {session['session_type']} | {session['action']}")
        else:
            print(f"❌ History endpoint failed - Status: {history_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask app. Make sure it's running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    
    return True

def check_log_file():
    """Check if the log file was created and has content"""
    try:
        with open('pomodoro_log.txt', 'r') as f:
            lines = f.readlines()
            print(f"\n📄 Log file contains {len(lines)} entries")
            if lines:
                print("   Last few entries:")
                for line in lines[-3:]:  # Show last 3 lines
                    print(f"   {line.strip()}")
        return True
    except FileNotFoundError:
        print("❌ Log file 'pomodoro_log.txt' not found")
        return False

if __name__ == "__main__":
    print("🍅 Pomodoro Timer Test Suite\n")
    
    print("Starting tests...")
    time.sleep(1)
    
    # Run tests
    api_test_passed = test_logging_endpoint()
    log_file_test_passed = check_log_file()
    
    print(f"\n{'='*50}")
    if api_test_passed and log_file_test_passed:
        print("🎉 All tests passed! The Pomodoro Timer is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    print(f"{'='*50}")