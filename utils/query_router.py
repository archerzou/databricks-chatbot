import re
import logging
from typing import Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Types of queries the chatbot can handle."""
    DATA = "data"
    GENERAL = "general"


DATA_QUERY_PATTERNS = [
    r"\bhow many\b",
    r"\bshow me\b.*\b(data|record|client|metric|table|result)",
    r"\bwhat data\b",
    r"\bquery\b",
    r"\btable[s]?\b",
    r"\bclient[s]?\b",
    r"\bmetric[s]?\b",
    r"\bcount\b.*\b(record|client|row|entry|item)",
    r"\blist\b.*\b(all|client|record|data|table)",
    r"\bfind\b.*\b(record|client|data|entry)",
    r"\bsearch\b.*\b(database|record|client|data)",
    r"\bdatabase\b",
    r"\brecord[s]?\b",
    r"\bhousing risk\b",
    r"\bdisability\b",
    r"\bmental health\b",
    r"\bdemographic[s]?\b",
    r"\bmeasureresponse[s]?\b",
    r"\boutcome[s]?\b",
    r"\bprogram evaluation\b",
    r"\baverage\b.*\b(score|value|count|number)",
    r"\btotal\b.*\b(count|number|client|record)",
    r"\bsum\b",
    r"\bpercentage\b",
    r"\bdistribution\b",
    r"\bbreakdown\b",
    r"\banalyze\b.*\b(data|record|client)",
    r"\banalysis\b.*\b(data|record|client)",
    r"\bstatistic[s]?\b",
    r"\btrend[s]?\b.*\b(data|client|record)",
    r"\bcompare\b.*\b(data|client|record|metric)",
    r"\bcomparison\b.*\b(data|client|record)",
    r"\bfilter\b.*\b(data|record|client|by)",
    r"\bgroup by\b",
    r"\bsort\b.*\b(by|data|record)",
    r"\border by\b",
    r"\bselect\b.*\b(from|data|record)",
    r"\bwhere\b.*\b(=|>|<|is|are)",
    r"\bfrom\b.*\btable\b",
    r"\bai.?final\b",
    r"\bcleaned\b",
    r"\blongitudinal\b",
    r"\bsingle.?record\b",
    r"\bsupport need[s]?\b",
    r"\brisk level[s]?\b",
    r"\bassessment[s]?\b",
]

GENERAL_QUERY_INDICATORS = [
    r"\bexplain\b",
    r"\bwhat is\b.*\b(machine learning|ai|artificial intelligence|programming|coding|concept)\b",
    r"\bhow does\b.*\bwork\b",
    r"\bwrite\b.*\b(code|script|program|story|poem|essay)\b",
    r"\bcreate\b.*\b(story|poem|essay|content)\b",
    r"\btell me about\b",
    r"\bdefine\b",
    r"\bdescribe\b.*\b(concept|how|what)\b",
    r"\bhelp me understand\b",
    r"\bwhat are the benefits\b",
    r"\bwhat are the advantages\b",
    r"\bwhat are the disadvantages\b",
    r"\bpros and cons\b",
    r"\bopinion\b",
    r"\bthink about\b",
    r"\bsuggestion[s]?\b",
    r"\brecommend\b",
    r"\badvice\b",
    r"\btips\b",
    r"\bbest practice[s]?\b",
    r"\bhow to\b.*\b(learn|improve|start|begin)\b",
    r"\btutorial\b",
    r"\bguide\b",
    r"\bbenefits of\b",
    r"\badvantages of\b",
    r"\bdisadvantages of\b",
    r"\busing\b.*\b(ai|machine learning|python|programming)\b",
]


class QueryRouter:
    """Routes queries to appropriate service based on content analysis."""
    
    def __init__(self):
        self.data_patterns = [re.compile(p, re.IGNORECASE) for p in DATA_QUERY_PATTERNS]
        self.general_patterns = [re.compile(p, re.IGNORECASE) for p in GENERAL_QUERY_INDICATORS]
    
    def classify_query(self, query: str) -> Tuple[QueryType, float]:
        """
        Classify a query as either data-related or general.
        
        Args:
            query: The user's query text
            
        Returns:
            Tuple of (QueryType, confidence_score)
            confidence_score ranges from 0.0 to 1.0
        """
        query_lower = query.lower().strip()
        
        data_matches = sum(1 for p in self.data_patterns if p.search(query_lower))
        general_matches = sum(1 for p in self.general_patterns if p.search(query_lower))
        
        total_data_patterns = len(self.data_patterns)
        total_general_patterns = len(self.general_patterns)
        
        data_score = data_matches / total_data_patterns if total_data_patterns > 0 else 0
        general_score = general_matches / total_general_patterns if total_general_patterns > 0 else 0
        
        if data_matches > 0 and general_matches == 0:
            confidence = min(0.5 + (data_matches * 0.1), 0.95)
            return QueryType.DATA, confidence
        
        if general_matches > 0 and data_matches == 0:
            confidence = min(0.5 + (general_matches * 0.1), 0.95)
            return QueryType.GENERAL, confidence
        
        if data_matches > general_matches:
            confidence = 0.5 + ((data_matches - general_matches) * 0.05)
            return QueryType.DATA, min(confidence, 0.85)
        
        if general_matches > data_matches:
            confidence = 0.5 + ((general_matches - data_matches) * 0.05)
            return QueryType.GENERAL, min(confidence, 0.85)
        
        return QueryType.GENERAL, 0.5
    
    def should_route_to_genie(self, query: str) -> bool:
        """
        Determine if a query should be routed to Genie Space.
        
        Args:
            query: The user's query text
            
        Returns:
            True if query should go to Genie, False for Claude
        """
        query_type, confidence = self.classify_query(query)
        
        logger.info(f"Query classification: {query_type.value} (confidence: {confidence:.2f})")
        
        return query_type == QueryType.DATA and confidence >= 0.5
    
    def get_routing_explanation(self, query: str) -> str:
        """
        Get a human-readable explanation of the routing decision.
        
        Args:
            query: The user's query text
            
        Returns:
            Explanation string
        """
        query_type, confidence = self.classify_query(query)
        
        if query_type == QueryType.DATA:
            return f"Routing to Genie Space (data query, confidence: {confidence:.0%})"
        else:
            return f"Routing to Claude LLM (general query, confidence: {confidence:.0%})"


query_router = QueryRouter()
