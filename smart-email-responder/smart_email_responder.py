#!/usr/bin/env python3
"""
Smart Email Response Agent

An AI agent that:
1. Reads unread emails from Gmail
2. Uses reasoning to detect which emails need responses
3. Filters out spam, junk, and marketing emails
4. Creates draft responses for important emails
5. Handles meeting requests with calendar availability
6. Includes built-in evaluation capabilities for quality assurance

Usage: 
    python smart_email_responder.py                    # Run the agent
    python smart_email_responder.py --evaluate all     # Run full evaluation
    python smart_email_responder.py --evaluate accuracy,bias_detection  # Run specific evaluators
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

        For emails that need responses, write a professional response body (without greeting/closing - those will be added automatically).

        IMPORTANT: For meeting requests, extract dates and times exactly as mentioned:
        - If email says "tomorrow", use "tomorrow" as preferred_date
        - If email says "next Tuesday", use "next Tuesday" as preferred_date  
        - If email says "7pm" or "19:00", use that exact format as preferred_time
        - Extract attendee email addresses from the email content

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

        If needs_response is true, provide a professional response in suggested_response field.
        For meeting requests, extract meeting details and set has_meeting_request to true.
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
    
    def check_calendar_availability_dt(self, requested_dt, duration_minutes):
        """Check if requested datetime slot is available"""
        try:
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

    def check_calendar_availability(self, date_str, time_str, duration_minutes):
        """Check if requested time slot is available (legacy method)"""
        try:
            # Parse the requested datetime
            if date_str and time_str:
                datetime_str = f"{date_str} {time_str}"
                requested_dt = date_parser.parse(datetime_str)
            else:
                # Default to next business day at 2 PM if no specific time
                requested_dt = self._get_next_business_day()
                requested_dt = requested_dt.replace(hour=14, minute=0, second=0, microsecond=0)
            
            return self.check_calendar_availability_dt(requested_dt, duration_minutes)
            
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
    
    def create_meeting_if_available(self, meeting_request, sender_email, email_subject=None, email_body=None):
        """Create meeting if time is available, otherwise suggest alternatives"""
        try:
            # Determine meeting time with proper date parsing
            if meeting_request.preferred_date and meeting_request.preferred_time:
                # Handle "tomorrow" specifically - always use actual tomorrow
                if "tomorrow" in meeting_request.preferred_date.lower():
                    # Get tomorrow's date
                    tomorrow = datetime.now() + timedelta(days=1)
                    try:
                        # Parse time (handle formats like "19:00", "7pm", "7:00 PM")
                        time_str = meeting_request.preferred_time.lower().replace(" ", "")
                        if "pm" in time_str:
                            time_str = time_str.replace("pm", "")
                            hour = int(time_str.split(":")[0])
                            if hour != 12:
                                hour += 12
                            minute = int(time_str.split(":")[1]) if ":" in time_str else 0
                        elif "am" in time_str:
                            time_str = time_str.replace("am", "")
                            hour = int(time_str.split(":")[0])
                            minute = int(time_str.split(":")[1]) if ":" in time_str else 0
                        else:
                            # 24-hour format like "19:00"
                            if ":" in meeting_request.preferred_time:
                                hour = int(meeting_request.preferred_time.split(":")[0])
                                minute = int(meeting_request.preferred_time.split(":")[1])
                            else:
                                hour = int(meeting_request.preferred_time)
                                minute = 0
                        
                        start_dt = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
                        print(f"🗓️ Parsed 'tomorrow {meeting_request.preferred_time}' as: {start_dt}")
                        
                    except Exception as e:
                        print(f"⚠️ Error parsing time '{meeting_request.preferred_time}': {e}")
                        # Default to tomorrow 7 PM if parsing fails
                        start_dt = tomorrow.replace(hour=19, minute=0, second=0, microsecond=0)
                else:
                    # Try parsing other date formats
                    try:
                        datetime_str = f"{meeting_request.preferred_date} {meeting_request.preferred_time}"
                        start_dt = date_parser.parse(datetime_str)
                        # Ensure it's not in the past
                        if start_dt < datetime.now():
                            start_dt = start_dt.replace(year=datetime.now().year + 1)
                    except:
                        # Default to next business day at 2 PM if parsing fails
                        start_dt = self._get_next_business_day().replace(hour=14, minute=0, second=0, microsecond=0)
            else:
                # Default to next business day at 2 PM if no specific time
                start_dt = self._get_next_business_day().replace(hour=14, minute=0, second=0, microsecond=0)
            
            # Check availability using the parsed datetime
            available, alternatives = self.check_calendar_availability_dt(
                start_dt,
                meeting_request.duration_minutes
            )
            
            print(f"🕐 Meeting time: {start_dt}")
            print(f"📅 Available: {available}")
            print(f"🔄 Alternatives: {len(alternatives) if alternatives else 0}")
            
            if available:
                # Create the actual calendar event
                end_dt = start_dt + timedelta(minutes=meeting_request.duration_minutes)
                
                # Clean up attendee emails
                attendee_emails = []
                if sender_email:
                    # Extract email from "Name <email>" format
                    clean_sender = sender_email.split('<')[-1].replace('>', '').strip()
                    attendee_emails.append({'email': clean_sender})
                
                # Add other attendees if any
                for email in meeting_request.attendees:
                    if email and '@' in email:
                        attendee_emails.append({'email': email.strip()})
                
                print(f"📧 Creating event for attendees: {[att['email'] for att in attendee_emails]}")
                
                # Generate meaningful meeting subject
                meeting_subject = self._generate_meeting_subject(
                    meeting_request, 
                    sender_email, 
                    email_subject,
                    email_body
                )
                
                event = {
                    'summary': meeting_subject,
                    'description': f'Meeting requested via email.\n\nOriginal request: {meeting_request.purpose}\nEmail subject: {email_subject}',
                    'start': {
                        'dateTime': start_dt.isoformat(),
                        'timeZone': 'UTC',
                    },
                    'end': {
                        'dateTime': end_dt.isoformat(),
                        'timeZone': 'UTC',
                    },
                    'attendees': attendee_emails,
                    'reminders': {
                        'useDefault': True
                    },
                    'visibility': 'default',
                    'status': 'confirmed'
                }
                
                created_event = self.calendar_service.events().insert(
                    calendarId='primary', 
                    body=event,
                    sendNotifications=True  # This ensures calendar invites are sent!
                ).execute()
                
                event_id = created_event.get('id')
                print(f"✅ Calendar event created: {event_id}")
                print(f"📧 Calendar invites sent to: {[att['email'] for att in attendee_emails]}")
                return True, f"Meeting scheduled for {start_dt.strftime('%B %d, %Y at %I:%M %p')}"
                
            else:
                # Suggest alternatives
                if alternatives:
                    alt_text = "\n".join([
                        f"• {alt.strftime('%B %d, %Y at %I:%M %p')}" 
                        for alt in alternatives
                    ])
                    return False, f"The requested time is not available. Here are some alternatives:\n{alt_text}"
                else:
                    return False, "No suitable alternative times found this week."
                    
        except Exception as e:
            print(f"Error in meeting creation: {e}")
            # Still try to suggest a time even if calendar creation fails
            next_day = self._get_next_business_day().replace(hour=14, minute=0)
            return False, f"I'd be happy to meet. How about {next_day.strftime('%B %d, %Y at %I:%M %p')}?"
    
    def create_draft_response(self, email, analysis):
        """Create a draft response in Gmail"""
        try:
            # Extract sender name from email address
            sender_name = self._extract_sender_name(email['sender'])
            
            # Start with a proper greeting
            response_body = f"Hi {sender_name},\n\n"
            
            # Add the main response content
            if analysis.suggested_response:
                response_body += analysis.suggested_response + "\n\n"
            
            # Handle meeting requests - ACTUALLY CREATE CALENDAR EVENTS
            if analysis.meeting_request:
                meeting_created, meeting_info = self.create_meeting_if_available(
                    analysis.meeting_request, 
                    email['sender'],
                    email['subject'],  # Pass email subject for better meeting titles
                    email['body']      # Pass email body for context extraction
                )
                
                if meeting_created:
                    response_body += f"{meeting_info}. I've sent you a calendar invite.\n\n"
                else:
                    response_body += f"{meeting_info}\n\n"
            
            # Add professional closing
            response_body += "Best regards,\n[Your Name]"
            
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
    
    def _extract_sender_name(self, sender_email):
        """Extract a friendly name from sender email"""
        # Handle formats like "John Doe <john@example.com>" or just "john@example.com"
        if '<' in sender_email:
            name_part = sender_email.split('<')[0].strip()
            if name_part:
                return name_part
        
        # If no name, use the part before @ in email
        email_part = sender_email.split('<')[-1].replace('>', '').strip()
        username = email_part.split('@')[0]
        
        # Capitalize and make it friendly
        return username.replace('.', ' ').replace('_', ' ').title()
    
    def _generate_meeting_subject(self, meeting_request, sender_email, email_subject=None, email_body=None):
        """Generate a meaningful meeting subject using email subject first, then derive from context"""
        
        # Step 1: Try to use email subject line if it's meaningful
        if email_subject and len(email_subject.strip()) > 5:
            subject = email_subject.strip()
            
            # Remove "Re: " prefix if present
            if subject.lower().startswith('re:'):
                subject = subject[3:].strip()
            
            # Check if subject is vague/generic
            vague_subjects = [
                'meeting', 'send meeting invite', 'calendar invite', 'schedule meeting',
                'let\'s meet', 'meeting request', 'invitation', 'catch up', 'chat',
                'quick call', 'sync', 'touch base', 'follow up', 'let\'s schedule',
                'schedule a call', 'call', 'discussion', 'talk', 'connect'
            ]
            
            is_vague = any(vague.lower() in subject.lower() for vague in vague_subjects)
            
            # If subject is not vague, use it directly
            if not is_vague:
                return subject
        
        # Step 2: If subject is vague, derive context from email content
        if meeting_request.purpose and len(meeting_request.purpose.strip()) > 10:
            purpose = meeting_request.purpose.strip()
            
            # Use AI to create a concise meeting title from the purpose
            try:
                context_prompt = f"""
                Create a concise, professional meeting subject line (max 60 characters) from this meeting request:
                
                "{purpose}"
                
                Rules:
                - Make it specific and actionable
                - Don't start with "Meeting:" or "Meeting about"
                - Focus on the main topic/goal
                - Use title case
                - Examples: "Q4 Budget Review", "Product Launch Strategy", "Team Performance Discussion"
                
                Return only the subject line, nothing else.
                """
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert at creating concise, professional meeting titles."},
                        {"role": "user", "content": context_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=50
                )
                
                ai_subject = response.choices[0].message.content.strip().strip('"')
                if ai_subject and len(ai_subject) > 5:
                    return ai_subject
                    
            except Exception as e:
                print(f"Error generating AI subject: {e}")
                # Fallback to cleaned purpose
                if purpose.lower().startswith('meeting'):
                    return purpose
                else:
                    return f"Meeting: {purpose}"
        
        # Step 3: Try to extract context from email body if available
        if email_body and len(email_body.strip()) > 20:
            try:
                body_context_prompt = f"""
                Extract the main topic/purpose for a meeting from this email content and create a concise meeting subject (max 60 characters):
                
                Email: "{email_body[:500]}"
                
                Rules:
                - Focus on the business purpose/topic
                - Make it specific and professional
                - Don't start with "Meeting:" 
                - Use title case
                - Examples: "Project Status Review", "Contract Discussion", "Team Sync"
                
                Return only the subject line, nothing else.
                """
                
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert at extracting meeting topics from email content."},
                        {"role": "user", "content": body_context_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=50
                )
                
                body_subject = response.choices[0].message.content.strip().strip('"')
                if body_subject and len(body_subject) > 5:
                    return body_subject
                    
            except Exception as e:
                print(f"Error extracting context from body: {e}")
        
        # Step 4: Fallback to sender-based format
        sender_name = self._extract_sender_name(sender_email)
        sender_first_name = sender_name.split()[0] if sender_name else "Guest"
        
        return f"Meeting with {sender_first_name}"
    
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
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Smart Email Responder with built-in evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python smart_email_responder.py                           # Run the agent normally
  python smart_email_responder.py --evaluate all            # Run full evaluation
  python smart_email_responder.py --evaluate accuracy       # Run specific evaluator
  python smart_email_responder.py --evaluate all --output report.json  # Save evaluation report
        """
    )
    
    parser.add_argument(
        '--evaluate',
        help='Run evaluation with specified evaluators (comma-separated) or "all"'
    )
    
    parser.add_argument(
        '--output',
        help='Output file for evaluation report (JSON format)'
    )
    
    args = parser.parse_args()
    
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: Please set OPENAI_API_KEY in your .env file")
        return
    
    if not os.path.exists('credentials.json'):
        print("Error: Please add credentials.json file")
        return
    
    # Run evaluation if requested
    if args.evaluate:
        print("🔍 Running Smart Email Responder Evaluation")
        print("=" * 50)
        
        try:
            # Import evaluation module
            from evaluation_framework.agent_integration import SmartEmailResponderEvaluator
            
            # Parse evaluators
            if args.evaluate.lower() == 'all':
                evaluators = None
            else:
                evaluators = [e.strip() for e in args.evaluate.split(',')]
            
            # Run evaluation
            evaluator = SmartEmailResponderEvaluator()
            report = evaluator.evaluate(evaluators=evaluators, output_file=args.output)
            
            # Print summary
            summary = report["evaluation_summary"]
            print(f"\n📊 EVALUATION COMPLETE")
            print(f"Overall Score: {summary['average_overall_score']:.1%}")
            print(f"Pass Rate: {summary['pass_rate']:.1%}")
            print(f"Tests Passed: {summary['passed_tests']}/{summary['total_test_cases']}")
            
            if args.output:
                print(f"📄 Detailed report saved to: {args.output}")
            
        except ImportError:
            print("❌ Evaluation framework not available. Please ensure evaluation_framework is installed.")
        except Exception as e:
            print(f"❌ Evaluation failed: {str(e)}")
        
        return
    
    # Run agent normally
    responder = SmartEmailResponder()
    responder.run()


if __name__ == "__main__":
    main()