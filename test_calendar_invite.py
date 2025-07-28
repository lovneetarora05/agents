#!/usr/bin/env python3
"""
Test Calendar Invite Functionality

This script tests the calendar integration to ensure:
1. Calendar API connection works
2. Events can be created with invites
3. Meeting invites are sent properly
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

from smart_email_responder import SmartEmailResponder

def test_calendar_functionality():
    """Test calendar invite creation"""
    
    print("🧪 Testing Calendar Invite Functionality...")
    
    try:
        responder = SmartEmailResponder()
        
        # Test 1: List recent calendar events
        print("\n1. Listing recent calendar events:")
        
        # Get events from the last 7 days
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        events_result = responder.calendar_service.events().list(
            calendarId='primary',
            timeMin=week_ago.isoformat() + 'Z',
            timeMax=now.isoformat() + 'Z',
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        print("📅 Recent calendar events:")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            attendees = event.get('attendees', [])
            attendee_emails = [att.get('email', 'No email') for att in attendees]
            print(f"  • {event['summary']} - {start}")
            print(f"    Attendees: {', '.join(attendee_emails)}")
        
        # Test 2: Create a test calendar event with invite
        print("\n2. Creating test calendar event with invite:")
        
        # Create event for tomorrow at 2 PM
        tomorrow = datetime.now() + timedelta(days=1)
        start_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(hours=1)
        
        event = {
            'summary': 'Test Meeting - Smart Email Responder',
            'location': 'Virtual Meeting',
            'description': 'This is a test meeting created by the Smart Email Responder to verify calendar invite functionality.',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
            'attendees': [
                {'email': 'test@example.com'},
            ],
            'reminders': {
                'useDefault': True
            },
            'visibility': 'default',
            'status': 'confirmed'
        }
        
        created_event = responder.calendar_service.events().insert(
            calendarId='primary', 
            body=event,
            sendNotifications=True
        ).execute()
        
        print("✅ Test calendar event created successfully!")
        print(f"📅 Event ID: {created_event.get('id')}")
        print(f"🔗 Event Link: {created_event.get('htmlLink')}")
        print(f"⏰ Meeting Time: {start_time.strftime('%B %d, %Y at %I:%M %p')}")
        print(f"📧 Invite sent to: test@example.com")
        
        print("\n🎉 Calendar invite functionality is working!")
        
    except Exception as e:
        print(f"❌ Error testing calendar functionality: {e}")
        print("Make sure you have:")
        print("1. Valid credentials.json file")
        print("2. Completed OAuth flow for Calendar API")
        print("3. Calendar API enabled in Google Cloud Console")

if __name__ == "__main__":
    test_calendar_functionality()