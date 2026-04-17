"""
Maintenance Mode Module
Manages system maintenance state during model retraining
"""

import json
from pathlib import Path
from datetime import datetime


MAINTENANCE_FLAG = Path('data/.maintenance')
MAINTENANCE_STATUS = Path('data/.maintenance_status.json')


def is_maintenance_mode():
    """Check if system is in maintenance mode"""
    return MAINTENANCE_FLAG.exists()


def enable_maintenance(reason='Scheduled maintenance', estimated_minutes=30):
    """Enable maintenance mode"""
    # Ensure data directory exists
    MAINTENANCE_FLAG.parent.mkdir(parents=True, exist_ok=True)
    
    # Create flag file
    MAINTENANCE_FLAG.touch()
    
    # Save status
    status = {
        'enabled': True,
        'started_at': datetime.now().isoformat(),
        'reason': reason,
        'estimated_completion': f'{estimated_minutes} minutes',
        'estimated_minutes': estimated_minutes
    }
    
    with open(MAINTENANCE_STATUS, 'w') as f:
        json.dump(status, f, indent=2)
    
    print(f"🔧 Maintenance mode enabled: {reason}")
    return status


def disable_maintenance():
    """Disable maintenance mode"""
    if MAINTENANCE_FLAG.exists():
        MAINTENANCE_FLAG.unlink()
    
    if MAINTENANCE_STATUS.exists():
        status = json.load(open(MAINTENANCE_STATUS))
        status['enabled'] = False
        status['ended_at'] = datetime.now().isoformat()
        
        with open(MAINTENANCE_STATUS, 'w') as f:
            json.dump(status, f, indent=2)
    
    print("✅ Maintenance mode disabled")


def get_maintenance_status():
    """Get current maintenance status"""
    if not MAINTENANCE_STATUS.exists():
        return {
            'enabled': False,
            'started_at': None,
            'reason': None,
            'estimated_completion': None
        }
    
    with open(MAINTENANCE_STATUS, 'r') as f:
        return json.load(f)


def update_maintenance_progress(message, percent_complete=None):
    """Update maintenance progress"""
    if not MAINTENANCE_STATUS.exists():
        return
    
    with open(MAINTENANCE_STATUS, 'r') as f:
        status = json.load(f)
    
    status['last_message'] = message
    if percent_complete is not None:
        status['percent_complete'] = percent_complete
    
    with open(MAINTENANCE_STATUS, 'w') as f:
        json.dump(status, f, indent=2)
