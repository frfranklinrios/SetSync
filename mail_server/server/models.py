from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: int
    email: str
    password_hash: str
    is_admin: bool
    created_at: datetime


@dataclass
class Email:
    id: int
    message_id: str
    sender: str
    recipients: str
    subject: str
    body_text: str
    body_html: Optional[str]
    folder: str
    is_read: bool
    owner_email: str
    created_at: datetime
