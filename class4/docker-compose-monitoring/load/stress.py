import requests
import time
import os
import threading
import random
from datetime import datetime

TARGET_URL = os.getenv('TARGET_URL', 'http://webapp:8000')
STRESS_LEVEL = os.getenv('STRESS_LEVEL', 'low').lower()

# Stress level configurations
STRESS_CONFIG = {
    'low': {'threads': 2, 'requests_per_second': 5, 'delay': 0.2},
    'medium': {'threads': 5, 'requests_per_second': 20, 'delay': 0.05},
    'high': {'threads': 10, 'requests_per_second': 50, 'delay': 0.02},
    'extreme': {'threads': 20, 'requests_per_second': 100, 'delay': 0.01}
}

# Endpoints to test
ENDPOINTS = [
    '/',
    '/health',
    '/cpu-test',
    '/memory-test',
    '/db-test'
]

def make_request(endpoint):
    """Make a single HTTP request"""
    url = f"{TARGET_URL}{endpoint}"
    try:
        response = requests.get(url, timeout=5)
        return {
            'endpoint': endpoint,
            'status': response.status_code,
            'time': response.elapsed.total_seconds(),
            'success': True
        }
    except Exception as e:
        return {
            'endpoint': endpoint,
            'status': 0,
            'time': 0,
            'success': False,
            'error': str(e)
        }

def worker_thread(thread_id, config):
    """Worker thread that generates load"""
    delay = config['delay']
    
    print(f"[Thread-{thread_id}] Started with delay {delay}s")
    
    while True:
        endpoint = random.choice(ENDPOINTS)
        result = make_request(endpoint)
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if result['success']:
            print(f"[{timestamp}] Thread-{thread_id} | {endpoint} | "
                  f"Status: {result['status']} | Time: {result['time']:.3f}s")
        else:
            print(f"[{timestamp}] Thread-{thread_id} | {endpoint} | "
                  f"FAILED | Error: {result.get('error', 'Unknown')}")
        
        time.sleep(delay)

def main():
    """Main load generator"""
    config = STRESS_CONFIG.get(STRESS_LEVEL, STRESS_CONFIG['low'])
    
    print("=" * 60)
    print(f"🔥 Load Generator Started")
    print(f"Target: {TARGET_URL}")
    print(f"Stress Level: {STRESS_LEVEL.upper()}")
    print(f"Threads: {config['threads']}")
    print(f"Requests/sec: ~{config['requests_per_second']}")
    print("=" * 60)
    
    # Wait for target to be ready
    print("Waiting for target application to be ready...")
    time.sleep(10)
    
    # Start worker threads
    threads = []
    for i in range(config['threads']):
        t = threading.Thread(target=worker_thread, args=(i+1, config), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(0.5)  # Stagger thread starts
    
    print(f"\n✅ All {config['threads']} threads started!\n")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(60)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Load generator running...")
    except KeyboardInterrupt:
        print("\n🛑 Load generator stopped")

if __name__ == '__main__':
    main()
