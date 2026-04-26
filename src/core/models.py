from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class HeroFact:
    label: str
    value: str
    extra: str = ""

@dataclass
class HeroData:
    name: str
    subtitle: str
    facts: List[HeroFact] = field(default_factory=list)

@dataclass
class SectionData:
    heading: str
    content: Dict[str, str] = field(default_factory=dict)

@dataclass
class PeptideData:
    name: str
    full_name: str
    method: str
    url: str
    hero: HeroData
    quick_guide: Dict[str, str] = field(default_factory=dict)
    community_insights: Dict[str, str] = field(default_factory=dict)
    poll_results: Dict[str, str] = field(default_factory=dict)
    sections: List[Dict[str, str]] = field(default_factory=list)
