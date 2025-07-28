#!/usr/bin/env python3
"""
Smart Email Response Agent

An AI agent that:
1. Reads unread emails from Gmail
2. Uses reasoning to detect which emails need responses
3. Filters out spam, junk, and marketing emails
4. Creates draft responses for important emails
5. Handles meeting requests with calendar availability

Usage: python smart_email_responder.py
"""

import os
import json
import base64
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Optional, Dict

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Google APIs
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# OpenAI
from openai import OpenAI

# Date parsing
from dateutil import parser as date_parser


@dataclass
class EmailAnalysis:
    needs_response: bool
    response_priority: str  # high, medium, low
    email_type: str  # business, personal, spam, marketing, automated
    reasoning: str
    suggested_response: str
    meeting_request: Optional[Dict] = None


@dataclass
class MeetingRequest:
    purpose: str
    preferred_date: Optional[str]
    preferred_time: Optional[str]
    duration_minutes: int
    attendees: List[str]


class SmartEmailResponder:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.gmail_service = self._setup_gmail()
        self.calendar_service = self._setup_calendar()
        
        # Working hours and availability settings
        self.working_hours = {
            'start': 9,  # 9 AM
            'end': 17,   # 5 PM
            'days': [0, 1, 2, 3, 4]  # Monday to Friday (0=Monday)
        }
    
    def _setup_gmail(self):
        """Setup Gmail API with read/write permissions"""
        scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.compose'
        ]
        creds = None
        
        if os.path.exists('gmail_token.json'):
            creds = Credentials.from_authorized_user_file('gmail_token.json', scopes)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
                creds = flow.run_local_server(port=0)
            
            with open('gmail_token.json', 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    def _setup_calendar(self):
        """Setup Calendar API connection"""
        scopes = ['https://www.googleapis.com/auth/calendar']
        creds = None
        
        if os.path.exists('calendar_token.json'):
            creds = Credentials.from_authorized_user_file('calendar_token.json', scopes)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
                creds = flow.run_local_server(port=0)
            
            with open('calendar_token.json', 'w') as token:
                token.write(creds.to_json())
        
        return build('calendar', 'v3', credentials=creds)
    
    def get_unread_emails(self, max_count=20):
        """Get unread emails from Gmail"""
        try:
            results = self.gmail_service.users().messages().list(
                userId='me', 
                maxResults=max_count, 
                q='is:unread in:inbox'
            ).execute()
            
            emails = []
            for message in results.get('messages', []):
                email_data = self.gmail_service.users().messages().get(
                    userId='me', id=message['id']
                ).execute()
                
                # Extract email details
                headers = email_data['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                body = self._extract_body(email_data['payload'])
                
                emails.append({
                    'id': message['id'],
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'body': body,
                    'thread_id': email_data.get('threadId')
                })
            
            return emails
        except Exception as e:
            print(f"Error getting emails: {e}")
            return []
    
    def _extract_body(self, payload):
        """Extract text from email payload"""
        body = ''
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
        elif payload['mimeType'] == 'text/plain':
            data = payload['body']['data']
            body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def analyze_email_with_reasoning(self, email):
        """Use AI with reasoning techniques to analyze if email needs response"""
        
        reasoning_prompt = f"""
        Analyze this email and determine if it needs a response. Return ONLY valid JSON.

        EMAIL:
        Subject: {email['subject']}
        From: {email['sender']}
        Body: {email['body'][:800]}

        ANALYSIS RULES:
        - Marketing/promotional emails = NO response
        - Newsletters/automated notifications = NO response  
        - Direct questions/requests = RESPONSE needed
        - Meeting invitations = RESPONSE needed
        - Personal messages from real people = RESPONSE needed

        Return this exact JSON structure:
        {{
            "needs_response": false,
            "response_priority": "low",
            "email_type": "marketing",
            "reasoning": "This appears to be a promotional/marketing email",
            "suggested_response": "",
            "meeting_request": {{
                "has_meeting_request": false,
                "purpose": "",
                "preferred_date": null,
                "preferred_time": null,
                "duration_minutes": 30,
                "attendees": []
            }}
        }}

        For most promotional emails, use the above template with needs_response: false.
        Only set needs_response: true for genuine personal/business communications.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert email assistant. Always respond with valid JSON only. No additional text or explanations."},
                    {"role": "user", "content": reasoning_prompt}
                ],
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON if it's wrapped in markdown
            if response_text.startswith('```json'):
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif response_text.startswith('```'):
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(response_text)
            
            meeting_request = None
            if result.get('meeting_request', {}).get('has_meeting_request'):
                meeting_data = result['meeting_request']
                meeting_request = MeetingRequest(
                    purpose=meeting_data.get('purpose', ''),
                    preferred_date=meeting_data.get('preferred_date'),
                    preferred_time=meeting_data.get('preferred_time'),
                    duration_minutes=meeting_data.get('duration_minutes', 30),
                    attendees=meeting_data.get('attendees', [])
                )
            
            return EmailAnalysis(
                needs_response=result['needs_response'],
                response_priority=result['response_priority'],
                email_type=result['email_type'],
                reasoning=result['reasoning'],
                suggested_response=result['suggested_response'],
                meeting_request=meeting_request
            )
            
        except Exception as e:
            print(f"Error analyzing email: {e}")
            return EmailAnalysis(
                needs_response=False,
                response_priority="low",
                email_type="unknown",
                reasoning="Error in analysis",
                suggested_response="",
                meeting_request=None
            )
    
    def check_calendar_availability(self, date_str, time_str, duration_minutes):
        """Check if requested time slot is available"""
        try:
            # Parse the requested datetime
            if date_str and time_str:
                datetime_str = f"{date_str} {time_str}"
                requested_dt = date_parser.parse(datetime_str)
            else:
                # Default to next business day at 2 PM if no specific time
                requested_dt = self._get_next_business_day()
                requested_dt = requested_dt.replace(hour=14, minute=0, second=0, microsecond=0)
            
            # Check if it's within working hours
            if not self._is_within_working_hours(requested_dt):
                return False, []
            
            # Check calendar for conflicts
            end_dt = requested_dt + timedelta(minutes=duration_minutes)
            
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=requested_dt.isoformat() + 'Z',
                timeMax=end_dt.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # If no conflicts, time is available
            if not events:
                return True, []
            
            # If conflicts, suggest alternative times
            alternatives = self._suggest_alternative_times(requested_dt, duration_minutes)
            return False, alternatives
            
        except Exception as e:
            print(f"Error checking availability: {e}")
            return False, []
    
    def _is_within_working_hours(self, dt):
        """Check if datetime is within working hours"""
        return (dt.weekday() in self.working_hours['days'] and 
                self.working_hours['start'] <= dt.hour < self.working_hours['end'])
    
    def _get_next_business_day(self):
        """Get next business day"""
        today = datetime.now()
        days_ahead = 1
        
        while True:
            next_day = today + timedelta(days=days_ahead)
            if next_day.weekday() in self.working_hours['days']:
                return next_day
            days_ahead += 1
    
    def _suggest_alternative_times(self, requested_dt, duration_minutes):
        """Suggest 2 alternative time slots"""
        alternatives = []
        
        # Try same day, different times
        base_date = requested_dt.date()
        for hour in [10, 11, 14, 15, 16]:
            alt_dt = datetime.combine(base_date, datetime.min.time().replace(hour=hour))
            if self._is_time_slot_free(alt_dt, duration_minutes):
                alternatives.append(alt_dt)
                if len(alternatives) >= 2:
                    return alternatives
        
        # Try next few business days
        for days_ahead in range(1, 8):
            next_date = base_date + timedelta(days=days_ahead)
            next_dt = datetime.combine(next_date, datetime.min.time().replace(hour=14))
            
            if (next_dt.weekday() in self.working_hours['days'] and 
                self._is_time_slot_free(next_dt, duration_minutes)):
                alternatives.append(next_dt)
                if len(alternatives) >= 2:
                    break
        
        return alternatives[:2]
    
    def _is_time_slot_free(self, dt, duration_minutes):
        """Check if a specific time slot is free"""
        try:
            end_dt = dt + timedelta(minutes=duration_minutes)
            
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=dt.isoformat() + 'Z',
                timeMax=end_dt.isoformat() + 'Z',
                singleEvents=True
            ).execute()
            
            return len(events_result.get('items', [])) == 0
        except:
            return False
    
    def create_meeting_if_available(self, meeting_request, sender_email):
        """Create meeting if time is available, otherwise suggest alternatives"""
        available, alternatives = self.check_calendar_availability(
            meeting_request.preferred_date,
            meeting_request.preferred_time,
            meeting_request.duration_minutes
        )
        
        if available:
            # Create the meeting
            try:
                if meeting_request.preferred_date and meeting_request.preferred_time:
                    datetime_str = f"{meeting_request.preferred_date} {meeting_request.preferred_time}"
                    start_dt = date_parser.parse(datetime_str)
                else:
                    start_dt = self._get_next_business_day().replace(hour=14, minute=0)
                
                end_dt = start_dt + timedelta(minutes=meeting_request.duration_minutes)
                
                event = {
                    'summary': meeting_request.purpose,
                    'start': {
                        'dateTime': start_dt.isoformat(),
                        'timeZone': 'UTC',
                    },
                    'end': {
                        'dateTime': end_dt.isoformat(),
                        'timeZone': 'UTC',
                    },
                    'attendees': [{'email': sender_email}] + [{'email': email} for email in meeting_request.attendees],
                }
                
                created_event = self.calendar_service.events().insert(
                    calendarId='primary', body=event
                ).execute()
                
                return True, f"Meeting scheduled for {start_dt.strftime('%B %d, %Y at %I:%M %p')}"
                
            except Exception as e:
                print(f"Error creating meeting: {e}")
                return False, "Error creating meeting"
        
        else:
            # Suggest alternatives
            if alternatives:
                alt_text = "\\n".join([
                    f"• {alt.strftime('%B %d, %Y at %I:%M %p')}" 
                    for alt in alternatives
                ])
                return False, f"The requested time is not available. Here are some alternatives:\\n{alt_text}"
            else:
                return False, "No suitable alternative times found this week."
    
    def create_draft_response(self, email, analysis):
        """Create a draft response in Gmail"""
        try:
            response_body = analysis.suggested_response
            
            # Handle meeting requests
            if analysis.meeting_request:
                meeting_created, meeting_info = self.create_meeting_if_available(
                    analysis.meeting_request, 
                    email['sender']
                )
                
                if meeting_created:
                    response_body += f"\\n\\n{meeting_info}. Calendar invite sent!"
                else:
                    response_body += f"\\n\\n{meeting_info}"
            
            # Create draft message
            message = {
                'message': {
                    'threadId': email['thread_id'],
                    'raw': self._create_message_raw(
                        to=email['sender'],
                        subject=f"Re: {email['subject']}",
                        body=response_body
                    )
                }
            }
            
            draft = self.gmail_service.users().drafts().create(
                userId='me', body=message
            ).execute()
            
            return draft.get('id')
            
        except Exception as e:
            print(f"Error creating draft: {e}")
            return None
    
    def _create_message_raw(self, to, subject, body):
        """Create raw email message"""
        import email.mime.text
        import email.mime.multipart
        
        msg = email.mime.multipart.MIMEMultipart()
        msg['to'] = to
        msg['subject'] = subject
        
        msg.attach(email.mime.text.MIMEText(body, 'plain'))
        
        return base64.urlsafe_b64encode(msg.as_bytes()).decode()
    
    def run(self):
        """Main function to process unread emails"""
        print("Getting unread emails...")
        emails = self.get_unread_emails()
        
        if not emails:
            print("No unread emails found.")
            return
        
        responses_created = 0
        meetings_created = 0
        
        for email in emails:
            print(f"\\nAnalyzing: {email['subject'][:50]}...")
            
            # Analyze email with reasoning
            analysis = self.analyze_email_with_reasoning(email)
            
            print(f"Type: {analysis.email_type}")
            print(f"Needs response: {analysis.needs_response}")
            
            if analysis.needs_response:
                print(f"Priority: {analysis.response_priority}")
                print(f"Reasoning: {analysis.reasoning}")
                
                # Create draft response
                draft_id = self.create_draft_response(email, analysis)
                
                if draft_id:
                    print("✅ Draft response created")
                    responses_created += 1
                    
                    if analysis.meeting_request:
                        meetings_created += 1
                else:
                    print("❌ Failed to create draft")
            else:
                print(f"Skipped: {analysis.reasoning}")
        
        print(f"\\nDone! Created {responses_created} draft responses and {meetings_created} meetings.")


def main():
    """Run the smart email responder"""
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: Please set OPENAI_API_KEY in your .env file")
        return
    
    if not os.path.exists('credentials.json'):
        print("Error: Please add credentials.json file")
        return
    
    responder = SmartEmailResponder()
    responder.run()


if __name__ == "__main__":
    main()