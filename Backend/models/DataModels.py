from dataclasses import dataclass, field, asdict

@dataclass
class ExtractedData:
    """Container for all extracted data"""
    comparisons: list = field(default_factory=list)
    breakdowns: list = field(default_factory=list)
    time_series: list = field(default_factory=list)
    key_facts: list = field(default_factory=list)
    tables: list = field(default_factory=list)
    raw_text: str = ""
    source_url: str = ""
    
    def to_dict(self):
        return asdict(self)
    
    def is_empty(self):
        return (not self.comparisons and not self.breakdowns and 
                not self.time_series and not self.key_facts and not self.tables)


@dataclass
class Comparison:
    """Represents a comparison between entities"""
    metric: str
    entities: dict  # {"India": 29, "Vietnam": 8}
    unit: str = ""
    source_snippet: str = ""


@dataclass
class Breakdown:
    """Represents a percentage or value breakdown"""
    category: str
    values: dict  # {"Manufacturing": 35, "Services": 45, "Agriculture": 20}
    unit: str = "%"


@dataclass
class TimeSeries:
    """Represents time-based data"""
    label: str
    data: list  # [{"year": 2020, "value": 123}, ...]
    unit: str = ""

@dataclass
class KeyFact:
    """Represents a single key statistic"""
    fact: str
    value: str
    context: str = ""