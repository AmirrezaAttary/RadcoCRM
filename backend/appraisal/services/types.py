from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union


@dataclass(frozen=True)
class CalendarPerson:
    id: int
    full_name: str


@dataclass(frozen=True)
class CalendarEvent:
    id: int
    title: str
    start: Optional[datetime]
    end: Optional[datetime]
    type: str
    people: Optional[
        Dict[
            str,
            Union[
                List[CalendarPerson],
                CalendarPerson
            ]
        ]
    ] = None