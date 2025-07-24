"""
Conversation Memory Management System
Advanced memory management for GPT conversations with optimization features
"""

import json
import sqlite3
import hashlib
import pickle
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ConversationMessage:
    """Single conversation message"""
    role: str  # 'system', 'user', 'assistant'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    token_count: Optional[int] = None

@dataclass
class ConversationSession:
    """Complete conversation session"""
    session_id: str
    session_type: str  # 'hfacs', 'causal', 'investigation', etc.
    incident_id: Optional[str]
    messages: List[ConversationMessage]
    created_at: datetime
    last_updated: datetime
    total_tokens: int = 0
    total_cost: float = 0.0
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AnalysisCache:
    """Cached analysis result"""
    cache_key: str
    analysis_type: str
    input_hash: str
    result: Any
    created_at: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None

class ConversationMemoryManager:
    """Advanced conversation memory management with optimization"""
    
    def __init__(self, db_path: str = "conversation_memory.db", 
                 max_memory_tokens: int = 50000,
                 cache_ttl_hours: int = 24):
        self.db_path = Path(db_path)
        self.max_memory_tokens = max_memory_tokens
        self.cache_ttl_hours = cache_ttl_hours
        self._lock = threading.Lock()
        
        # In-memory cache for active sessions
        self._active_sessions: Dict[str, ConversationSession] = {}
        self._result_cache: Dict[str, AnalysisCache] = {}
        
        # Token pricing (per 1M tokens)
        self.token_pricing = {
            'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
            'gpt-4o': {'input': 2.50, 'output': 10.00},
            'gpt-4': {'input': 30.00, 'output': 60.00}
        }
        
        self._init_database()
        self._load_active_sessions()
        logger.info(f"ConversationMemoryManager initialized with {len(self._active_sessions)} active sessions")

    def _init_database(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    session_type TEXT NOT NULL,
                    incident_id TEXT,
                    created_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    total_tokens INTEGER DEFAULT 0,
                    total_cost REAL DEFAULT 0.0,
                    metadata TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    token_count INTEGER,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_cache (
                    cache_key TEXT PRIMARY KEY,
                    analysis_type TEXT NOT NULL,
                    input_hash TEXT NOT NULL,
                    result_data BLOB NOT NULL,
                    created_at TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_type ON sessions(session_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_session_incident ON sessions(incident_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_type ON analysis_cache(analysis_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_hash ON analysis_cache(input_hash)")

    def create_session(self, session_type: str, incident_id: Optional[str] = None, 
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create new conversation session"""
        session_id = f"{session_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(datetime.now().microsecond)) % 10000:04d}"
        
        session = ConversationSession(
            session_id=session_id,
            session_type=session_type,
            incident_id=incident_id,
            messages=[],
            created_at=datetime.now(),
            last_updated=datetime.now(),
            metadata=metadata or {}
        )
        
        with self._lock:
            self._active_sessions[session_id] = session
        
        # Save to database
        self._save_session_to_db(session)
        
        logger.info(f"Created new conversation session: {session_id}")
        return session_id

    def add_message(self, session_id: str, role: str, content: str, 
                   token_count: Optional[int] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add message to conversation session"""
        if session_id not in self._active_sessions:
            logger.warning(f"Session {session_id} not found")
            return False
        
        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata,
            token_count=token_count or self._estimate_tokens(content)
        )
        
        with self._lock:
            session = self._active_sessions[session_id]
            session.messages.append(message)
            session.last_updated = datetime.now()
            session.total_tokens += message.token_count or 0
        
        # Save message to database
        self._save_message_to_db(session_id, message)
        
        # Optimize memory usage
        self._optimize_session_memory(session_id)
        
        return True

    def get_conversation_history(self, session_id: str, 
                               max_tokens: Optional[int] = None) -> List[Dict[str, str]]:
        """Get conversation history for API calls"""
        if session_id not in self._active_sessions:
            return []
        
        session = self._active_sessions[session_id]
        max_tokens = max_tokens or self.max_memory_tokens
        
        # Get recent messages within token limit
        messages = []
        current_tokens = 0
        
        # Add messages in reverse order (most recent first), then reverse
        for message in reversed(session.messages):
            msg_tokens = message.token_count or 0
            if current_tokens + msg_tokens > max_tokens and messages:
                break
            
            messages.insert(0, {
                'role': message.role,
                'content': message.content
            })
            current_tokens += msg_tokens
        
        logger.info(f"Retrieved {len(messages)} messages ({current_tokens} tokens) for session {session_id}")
        return messages

    def calculate_cost(self, session_id: str, model: str = 'gpt-4o-mini') -> float:
        """Calculate conversation cost"""
        if session_id not in self._active_sessions:
            return 0.0
        
        session = self._active_sessions[session_id]
        
        if model not in self.token_pricing:
            logger.warning(f"Unknown model {model}, using gpt-4o-mini pricing")
            model = 'gpt-4o-mini'
        
        input_tokens = sum(msg.token_count or 0 for msg in session.messages if msg.role != 'assistant')
        output_tokens = sum(msg.token_count or 0 for msg in session.messages if msg.role == 'assistant')
        
        pricing = self.token_pricing[model]
        cost = (input_tokens * pricing['input'] + output_tokens * pricing['output']) / 1000000
        
        # Update session cost
        with self._lock:
            session.total_cost = cost
        
        return cost

    def cache_analysis_result(self, analysis_type: str, input_data: Any, result: Any) -> str:
        """Cache analysis result for reuse"""
        # Create cache key from input data hash
        input_str = json.dumps(input_data, sort_keys=True, default=str)
        input_hash = hashlib.md5(input_str.encode()).hexdigest()
        cache_key = f"{analysis_type}_{input_hash}"
        
        cache_entry = AnalysisCache(
            cache_key=cache_key,
            analysis_type=analysis_type,
            input_hash=input_hash,
            result=result,
            created_at=datetime.now()
        )
        
        with self._lock:
            self._result_cache[cache_key] = cache_entry
        
        # Save to database
        self._save_cache_to_db(cache_entry)
        
        logger.info(f"Cached analysis result: {cache_key}")
        return cache_key

    def get_cached_result(self, analysis_type: str, input_data: Any) -> Optional[Any]:
        """Retrieve cached analysis result"""
        input_str = json.dumps(input_data, sort_keys=True, default=str)
        input_hash = hashlib.md5(input_str.encode()).hexdigest()
        cache_key = f"{analysis_type}_{input_hash}"
        
        # Check in-memory cache first
        if cache_key in self._result_cache:
            cache_entry = self._result_cache[cache_key]
            
            # Check if cache is still valid
            if datetime.now() - cache_entry.created_at < timedelta(hours=self.cache_ttl_hours):
                cache_entry.access_count += 1
                cache_entry.last_accessed = datetime.now()
                logger.info(f"Cache hit: {cache_key}")
                return cache_entry.result
            else:
                # Remove expired cache
                del self._result_cache[cache_key]
                logger.info(f"Cache expired: {cache_key}")
        
        # Try to load from database
        cache_entry = self._load_cache_from_db(cache_key)
        if cache_entry and datetime.now() - cache_entry.created_at < timedelta(hours=self.cache_ttl_hours):
            self._result_cache[cache_key] = cache_entry
            cache_entry.access_count += 1
            cache_entry.last_accessed = datetime.now()
            logger.info(f"Cache loaded from DB: {cache_key}")
            return cache_entry.result
        
        return None

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get session statistics"""
        if session_id not in self._active_sessions:
            return {}
        
        session = self._active_sessions[session_id]
        
        return {
            'session_id': session_id,
            'session_type': session.session_type,
            'incident_id': session.incident_id,
            'message_count': len(session.messages),
            'total_tokens': session.total_tokens,
            'total_cost': session.total_cost,
            'created_at': session.created_at.isoformat(),
            'last_updated': session.last_updated.isoformat(),
            'duration_minutes': (session.last_updated - session.created_at).total_seconds() / 60
        }

    def cleanup_old_sessions(self, days: int = 7) -> int:
        """Clean up old inactive sessions"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT session_id FROM sessions 
                WHERE last_updated < ? AND is_active = 0
            """, (cutoff_date.isoformat(),))
            
            old_sessions = [row[0] for row in cursor.fetchall()]
            
            for session_id in old_sessions:
                # Remove from memory
                if session_id in self._active_sessions:
                    del self._active_sessions[session_id]
                
                # Remove from database
                conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} old sessions")
        return cleaned_count

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Simple estimation: ~4 characters per token on average
        return max(1, len(text) // 4)

    def _optimize_session_memory(self, session_id: str):
        """Optimize session memory usage"""
        if session_id not in self._active_sessions:
            return
        
        session = self._active_sessions[session_id]
        
        # If session exceeds token limit, summarize older messages
        if session.total_tokens > self.max_memory_tokens:
            self._summarize_old_messages(session_id)

    def _summarize_old_messages(self, session_id: str):
        """Summarize old messages to reduce token usage"""
        # This could be enhanced to actually call GPT to summarize
        # For now, we'll just keep the most recent messages
        session = self._active_sessions[session_id]
        
        if len(session.messages) <= 10:
            return
        
        # Keep last 10 messages, summarize the rest
        old_messages = session.messages[:-10]
        recent_messages = session.messages[-10:]
        
        # Create summary message
        summary_content = f"[SUMMARY] Previous conversation included {len(old_messages)} messages covering analysis and discussion."
        summary_message = ConversationMessage(
            role='system',
            content=summary_content,
            timestamp=datetime.now(),
            token_count=self._estimate_tokens(summary_content)
        )
        
        session.messages = [summary_message] + recent_messages
        session.total_tokens = sum(msg.token_count or 0 for msg in session.messages)
        
        logger.info(f"Summarized {len(old_messages)} old messages in session {session_id}")

    def _save_session_to_db(self, session: ConversationSession):
        """Save session to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO sessions 
                (session_id, session_type, incident_id, created_at, last_updated, 
                 total_tokens, total_cost, metadata, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.session_id,
                session.session_type,
                session.incident_id,
                session.created_at.isoformat(),
                session.last_updated.isoformat(),
                session.total_tokens,
                session.total_cost,
                json.dumps(session.metadata) if session.metadata else None,
                1
            ))

    def _save_message_to_db(self, session_id: str, message: ConversationMessage):
        """Save message to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO messages 
                (session_id, role, content, timestamp, token_count, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                message.role,
                message.content,
                message.timestamp.isoformat(),
                message.token_count,
                json.dumps(message.metadata) if message.metadata else None
            ))

    def _save_cache_to_db(self, cache_entry: AnalysisCache):
        """Save cache entry to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO analysis_cache 
                (cache_key, analysis_type, input_hash, result_data, created_at, access_count, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                cache_entry.cache_key,
                cache_entry.analysis_type,
                cache_entry.input_hash,
                pickle.dumps(cache_entry.result),
                cache_entry.created_at.isoformat(),
                cache_entry.access_count,
                cache_entry.last_accessed.isoformat() if cache_entry.last_accessed else None
            ))

    def _load_cache_from_db(self, cache_key: str) -> Optional[AnalysisCache]:
        """Load cache entry from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT cache_key, analysis_type, input_hash, result_data, created_at, access_count, last_accessed
                FROM analysis_cache WHERE cache_key = ?
            """, (cache_key,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return AnalysisCache(
                cache_key=row[0],
                analysis_type=row[1],
                input_hash=row[2],
                result=pickle.loads(row[3]),
                created_at=datetime.fromisoformat(row[4]),
                access_count=row[5] or 0,
                last_accessed=datetime.fromisoformat(row[6]) if row[6] else None
            )

    def _load_active_sessions(self):
        """Load active sessions from database"""
        with sqlite3.connect(self.db_path) as conn:
            # Load sessions from last 24 hours
            cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
            
            cursor = conn.execute("""
                SELECT session_id, session_type, incident_id, created_at, last_updated, 
                       total_tokens, total_cost, metadata
                FROM sessions 
                WHERE is_active = 1 AND last_updated > ?
                ORDER BY last_updated DESC
                LIMIT 50
            """, (cutoff,))
            
            for row in cursor.fetchall():
                session = ConversationSession(
                    session_id=row[0],
                    session_type=row[1],
                    incident_id=row[2],
                    messages=[],  # Messages will be loaded on demand
                    created_at=datetime.fromisoformat(row[3]),
                    last_updated=datetime.fromisoformat(row[4]),
                    total_tokens=row[5] or 0,
                    total_cost=row[6] or 0.0,
                    metadata=json.loads(row[7]) if row[7] else {}
                )
                
                # Load recent messages
                msg_cursor = conn.execute("""
                    SELECT role, content, timestamp, token_count, metadata
                    FROM messages 
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 20
                """, (row[0],))
                
                messages = []
                for msg_row in msg_cursor.fetchall():
                    message = ConversationMessage(
                        role=msg_row[0],
                        content=msg_row[1],
                        timestamp=datetime.fromisoformat(msg_row[2]),
                        token_count=msg_row[3],
                        metadata=json.loads(msg_row[4]) if msg_row[4] else None
                    )
                    messages.insert(0, message)  # Reverse order to get chronological
                
                session.messages = messages
                self._active_sessions[row[0]] = session

# Global memory manager instance
_memory_manager = None

def get_memory_manager() -> ConversationMemoryManager:
    """Get global memory manager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = ConversationMemoryManager()
    return _memory_manager

# Convenience functions
def create_conversation(session_type: str, incident_id: Optional[str] = None) -> str:
    """Create new conversation session"""
    return get_memory_manager().create_session(session_type, incident_id)

def add_conversation_message(session_id: str, role: str, content: str, token_count: Optional[int] = None) -> bool:
    """Add message to conversation"""
    return get_memory_manager().add_message(session_id, role, content, token_count)

def get_conversation_messages(session_id: str, max_tokens: Optional[int] = None) -> List[Dict[str, str]]:
    """Get conversation messages for API"""
    return get_memory_manager().get_conversation_history(session_id, max_tokens)

def cache_analysis(analysis_type: str, input_data: Any, result: Any) -> str:
    """Cache analysis result"""
    return get_memory_manager().cache_analysis_result(analysis_type, input_data, result)

def get_cached_analysis(analysis_type: str, input_data: Any) -> Optional[Any]:
    """Get cached analysis result"""
    return get_memory_manager().get_cached_result(analysis_type, input_data)

if __name__ == "__main__":
    # Test the memory manager
    manager = ConversationMemoryManager()
    
    # Create test session
    session_id = manager.create_session("test", "incident_001")
    
    # Add test messages
    manager.add_message(session_id, "system", "You are a helpful assistant")
    manager.add_message(session_id, "user", "What is HFACS?")
    manager.add_message(session_id, "assistant", "HFACS is the Human Factors Analysis and Classification System...")
    
    # Get conversation history
    history = manager.get_conversation_history(session_id)
    print("Conversation history:")
    for msg in history:
        print(f"  {msg['role']}: {msg['content'][:50]}...")
    
    # Test caching
    cache_key = manager.cache_analysis_result("test_analysis", {"input": "test"}, {"result": "cached"})
    cached_result = manager.get_cached_result("test_analysis", {"input": "test"})
    print(f"Cache test: {cached_result}")
    
    # Get stats
    stats = manager.get_session_stats(session_id)
    print(f"Session stats: {stats}")