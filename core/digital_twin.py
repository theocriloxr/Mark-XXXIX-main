"""
Digital Twin - Asynchronous Proxy for Communications

JARVIS operates headlessly while you sleep or work:
- Reads and summarizes emails
- Responds to meeting requests based on calendar
- Negotiates and books meetings
- Manages Slack/Discord communications

Using your ChromaDB persona data to mimic your writing style.

Usage:
    from core.digital_twin import DigitalTwin, start_digital_twin
    
    start_digital_twin()
    
    # Get morning briefing
    briefing = get_morning_briefing()
"""

import logging
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# Email providers
GMAIL = "gmail"
OUTLOOK = "outlook"
IMAP = "imap"

# Calendar providers
GOOGLE_CALENDAR = "google_calendar"
OUTLOOK_CALENDAR = "outlook_calendar"


@dataclass
class EmailMessage:
    """Email message."""
    subject: str = ""
    sender: str = ""
    body: str = ""
    timestamp: float = 0
    read: bool = False
    action_taken: str = ""


@dataclass
class CalendarEvent:
    """Calendar event."""
    title: str = ""
    start_time: float = 0
    end_time: float = 0
    attendees: List[str] = None
    location: str = ""
    response: str = "pending"  # pending, accepted, declined


class DigitalTwin:
    """
    Digital twin that operates on your behalf.
    Manages email, calendar, and messaging.
    """
    
    def __init__(self):
        self.is_running = False
        self._enabled = True
        
        # Communication configs
        self._email_config: Dict[str, Any] = {}
        self._calendar_config: Dict[str, Any] = {}
        self._slack_config: Dict[str, Any] = {}
        
        # Queues
        self._pending_emails: deque = deque(maxlen=50)
        self._scheduled_meetings: deque = deque(maxlen=20)
        
        # Activity log
        self._activity_log: deque = deque(maxlen=100)
        
        # Lock
        self._lock = threading.Lock()
        
        # Statistics
        self._emails_processed = 0
        self._meetings_booked = 0
        self._last_activity = 0
        
        # Initialize integrations
        self._init_integrations()
    
    def _init_integrations(self):
        """Initialize communication integrations."""
        # Gmail API (configure in config/digital_twin.json)
        self._email_config = {
            "provider": "gmail",
            "enabled": False
        }
        
        # Google Calendar
        self._calendar_config = {
            "provider": "google_calendar",
            "enabled": False
        }
        
        # Slack
        self._slack_config = {
            "enabled": False
        }
        
        logger.info("[DigitalTwin] Initialized integrations")
    
    def start(self):
        """Start the digital twin."""
        if self.is_running:
            return
        
        self.is_running = True
        thread = threading.Thread(target=self._main_loop, daemon=True)
        thread.start()
        
        logger.info("[DigitalTwin] Started")
    
    def stop(self):
        """Stop the digital twin."""
        self.is_running = False
        logger.info("[DigitalTwin] Stopped")
    
    def _main_loop(self):
        """Main processing loop."""
        while self.is_running:
            try:
                # Process pending emails
                self._process_emails()
                
                # Handle meeting requests
                self._process_meeting_requests()
                
                # Process Slack messages
                self._process_slack()
                
                self._last_activity = time.time()
                
            except Exception as e:
                logger.debug(f"[DigitalTwin] Loop error: {e}")
            
            # Check every 5 minutes
            time.sleep(300)
    
    def _process_emails(self):
        """Process pending emails."""
        if not self._email_config.get("enabled"):
            return
        
        try:
            # Fetch emails from provider
            emails = self._fetch_emails()
            
            for email in emails:
                # Classify email
                action = self._classify_email(email)
                
                if action == "respond":
                    self._respond_to_email(email)
                elif action == "archive":
                    self._archive_email(email)
                
                self._emails_processed += 1
                self._log_activity(f"Processed email: {email.subject}")
                
        except Exception as e:
            logger.debug(f"[DigitalTwin] Email processing: {e}")
    
    def _fetch_emails(self) -> List[EmailMessage]:
        """Fetch emails from provider."""
        # In production, use Gmail API
        return []
    
    def _classify_email(self, email: EmailMessage) -> str:
        """Classify email and determine action.""" keywords = email.subject.lower()
        
        # Meeting request
        if "meeting" in keywords or "call" in keywords or "zoom" in keywords:
            return "respond"
        
        # Newsletter/promo
        if "unsubscribe" in keywords:
            return "archive"
        
        # Important
        if "urgent" in keywords or "important" in keywords:
            return "respond"
        
        return "wait"
    
    def _respond_to_email(self, email: EmailMessage):
        """Respond to email using persona."""
        # Get persona from memory
        persona = self._get_persona()
        
        # Generate response
        response = self._generate_response(email, persona)
        
        # Send reply
        self._send_email_reply(email, response)
        
        email.action_taken = "replied"
    
    def _generate_response(self, email: EmailMessage, persona: str) -> str:
        """Generate response using persona style."""
        # In production, use LLM to generate
        # For now, return simple acknowledgment
        
        if "meeting" in email.subject.lower():
            return "Thanks for reaching out. I'm happy to connect. Could we schedule for next week?"
        
        return "Thanks for your message. I'll follow up shortly."
    
    def _send_email_reply(self, email: EmailMessage, response: str):
        """Send email reply."""
        # In production, use Gmail API
        logger.info(f"[DigitalTwin] Sent reply to: {email.sender}")
    
    def _archive_email(self, email: EmailMessage):
        """Archive email."""
        email.action_taken = "archived"
    
    def _process_meeting_requests(self):
        """Process meeting requests from emails."""
        if not self._calendar_config.get("enabled"):
            return
        
        try:
            # Check calendar for new invites
            invites = self._fetch_calendar_invites()
            
            for invite in invites:
                # Accept or decline based on availability
                response = self._evaluate_meeting(invite)
                
                if response == "accept":
                    self._accept_meeting(invite)
                    self._meetings_booked += 1
                
                self._log_activity(f"Meeting {response}: {invite.title}")
                
        except Exception as e:
            logger.debug(f"[DigitalTwin] Meeting processing: {e}")
    
    def _fetch_calendar_invites(self) -> List[CalendarEvent]:
        """Fetch calendar invites."""
        # In production, use Google Calendar API
        return []
    
    def _evaluate_meeting(self, event: CalendarEvent) -> str:
        """Evaluate meeting and decide response."""
        # Check for conflicts
        # In production, check against calendar
        
        return "accept"
    
    def _accept_meeting(self, event: CalendarEvent):
        """Accept meeting invitation."""
        event.response = "accepted"
        self._log_activity(f"Accepted: {event.title}")
    
    def _process_slack(self):
        """Process Slack messages."""
        if not self._slack_config.get("enabled"):
            return
        
        # In production, use Slack API
        pass
    
    def _get_persona(self) -> str:
        """Get user persona from memory."""
        try:
            from core.chroma_memory import chroma_memory
            
            # Search for persona data
            memories = chroma_memory.recall("writing style", n_results=1)
            
            if memories:
                return memories[0]
                
        except:
            pass
        
        return "Professional, concise, friendly"
    
    def _log_activity(self, description: str):
        """Log digital twin activity."""
        with self._lock:
            self._activity_log.append({
                "description": description,
                "timestamp": time.time()
            })
    
    def get_morning_briefing(self) -> str:
        """Get morning briefing of overnight activity."""
        with self._lock:
            activities = list(self._activity_log)
        
        if not activities:
            return "No overnight activity."
        
        lines = ["Overnight Activity:"]
        
        for activity in activities[-10:]:
            ts = activity["timestamp"]
            time_str = time.strftime("%H:%M", time.localtime(ts))
            lines.append(f"  {time_str}: {activity['description']}")
        
        lines.append(f"\nSummary:")
        lines.append(f"  Emails processed: {self._emails_processed}")
        lines.append(f"  Meetings booked: {self._meetings_booked}")
        
        return "\n".join(lines)
    
    def get_activity_log(self, count: int = 10) -> List[Dict]:
        """Get recent activity log."""
        with self._lock:
            return list(self._activity_log)[-count:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get digital twin statistics."""
        return {
            "emails_processed": self._emails_processed,
            "meetings_booked": self._meetings_booked,
            "last_activity": self._last_activity,
            "status": "running" if self.is_running else "stopped"
        }
    
    def configure_email(self, provider: str, credentials: Dict) -> str:
        """Configure email integration."""
        self._email_config = {
            "provider": provider,
            "enabled": True,
            "credentials": credentials
        }
        return f"Email configured: {provider}"
    
    def configure_calendar(self, provider: str, credentials: Dict) -> str:
        """Configure calendar integration."""
        self._calendar_config = {
            "provider": provider,
            "enabled": True,
            "credentials": credentials
        }
        return f"Calendar configured: {provider}"
    
    def configure_slack(self, token: str) -> str:
        """Configure Slack."""
        self._slack_config = {
            "enabled": True,
            "token": token
        }
        return "Slack configured"
    
    def enable(self):
        """Enable digital twin."""
        self._enabled = True
    
    def disable(self):
        """Disable digital twin."""
        self._enabled = False


# === GLOBAL INSTANCE ===

_digital_twin: Optional[DigitalTwin] = None


def get_digital_twin() -> DigitalTwin:
    """Get global digital twin instance."""
    global _digital_twin
    if _digital_twin is None:
        _digital_twin = DigitalTwin()
    return _digital_twin


def start_digital_twin() -> str:
    """Start digital twin."""
    twin = get_digital_twin()
    twin.start()
    return "Digital twin started. I'll handle communications while you sleep."


def stop_digital_twin() -> str:
    """Stop digital twin."""
    get_digital_twin().stop()
    return "Digital twin stopped."


def get_morning_briefing() -> str:
    """Get morning briefing."""
    return get_digital_twin().get_morning_briefing()


# === DISPATCHER ===

def digital_twin(
    parameters: dict = None,
    response=None,
    player=None,
    speak=None,
) -> str:
    """Main dispatcher for digital twin."""
    params = parameters or {}
    action = params.get("action", "status").lower().strip()
    
    if player:
        player.write_log(f"[DigitalTwin] {action}")
    
    twin = get_digital_twin()
    
    try:
        if action == "status":
            stats = twin.get_statistics()
            return f"Emails: {stats['emails_processed']} | Meetings: {stats['meetings_booked']} | Status: {stats['status']}"
        
        elif action == "briefing":
            return twin.get_morning_briefing()
        
        elif action == "activity":
            activities = twin.get_activity_log(count=5)
            if activities:
                lines = ["Recent Activity:"]
                for a in activities:
                    lines.append(f"- {a['description']}")
                return "\n".join(lines)
            return "No recent activity"
        
        elif action == "configure":
            what = params.get("what", "").lower()
            provider = params.get("provider", "")
            
            if what == "email":
                return twin.configure_email(provider, {})
            elif what == "calendar":
                return twin.configure_calendar(provider, {})
            elif what == "slack":
                token = params.get("token", "")
                return twin.configure_slack(token)
            
            return "Specify what: email, calendar, slack"
        
        elif action == "enable":
            twin.enable()
            return "Digital twin enabled."
        
        elif action == "disable":
            twin.disable()
            return "Digital twin disabled."
        
        else:
            stats = twin.get_statistics()
            return f"DigitalTwin: {stats['emails_processed']} emails, {stats['meetings_booked']} meetings"
    
    except Exception as e:
        return f"DigitalTwin error: {e}"


if __name__ == "__main__":
    print("=== Digital Twin Test ===")
    
    twin = get_digital_twin()
    print(f"Status: {twin.get_statistics()}")
    
    print("\n✅ Digital Twin ready")
