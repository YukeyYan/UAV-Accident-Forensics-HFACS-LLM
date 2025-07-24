"""
Token Usage Optimization Module
Advanced token management and cost optimization for conversation memory system
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import tiktoken
import re
from .conversation_memory import get_memory_manager, ConversationMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TokenUsageStats:
    """Token usage statistics"""
    total_tokens: int
    input_tokens: int
    output_tokens: int
    cost: float
    cache_hits: int
    cache_misses: int
    cache_hit_rate: float
    sessions_count: int
    average_tokens_per_session: float

@dataclass
class OptimizationSuggestion:
    """Token optimization suggestion"""
    category: str
    suggestion: str
    potential_savings: int
    potential_cost_savings: float
    priority: str  # HIGH, MEDIUM, LOW

class TokenOptimizer:
    """Advanced token usage optimizer"""
    
    def __init__(self):
        self.memory_manager = get_memory_manager()
        
        # Initialize tokenizer for accurate token counting
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer
        except Exception as e:
            logger.warning(f"Failed to load tiktoken encoder: {e}")
            self.tokenizer = None
        
        # Token limits for different models
        self.model_limits = {
            'gpt-4o-mini': {'context': 128000, 'output': 16384},
            'gpt-4o': {'context': 128000, 'output': 4096},
            'gpt-4': {'context': 8192, 'output': 4096}
        }
        
        # Optimization strategies
        self.optimization_strategies = [
            self._optimize_message_summarization,
            self._optimize_redundant_content,
            self._optimize_prompt_efficiency,
            self._optimize_cache_usage,
            self._optimize_session_management
        ]
    
    def count_tokens(self, text: str) -> int:
        """Accurate token counting using tiktoken"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Fallback estimation
            return max(1, len(text) // 4)
    
    def analyze_token_usage(self, days: int = 7) -> TokenUsageStats:
        """Analyze token usage patterns over specified period"""
        try:
            # Get recent sessions
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # This would query the database for recent sessions
            # For now, we'll simulate with current active sessions
            sessions = self.memory_manager._active_sessions
            
            total_tokens = 0
            input_tokens = 0
            output_tokens = 0
            total_cost = 0.0
            cache_hits = 0
            cache_misses = len(sessions)  # Simplified
            
            for session_id, session in sessions.items():
                session_tokens = 0
                for message in session.messages:
                    token_count = self.count_tokens(message.content)
                    session_tokens += token_count
                    
                    if message.role in ['system', 'user']:
                        input_tokens += token_count
                    else:
                        output_tokens += token_count
                
                total_tokens += session_tokens
                total_cost += session.total_cost
            
            # Calculate cache statistics
            total_requests = cache_hits + cache_misses
            cache_hit_rate = (cache_hits / max(1, total_requests)) * 100
            
            return TokenUsageStats(
                total_tokens=total_tokens,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=total_cost,
                cache_hits=cache_hits,
                cache_misses=cache_misses,
                cache_hit_rate=cache_hit_rate,
                sessions_count=len(sessions),
                average_tokens_per_session=total_tokens / max(1, len(sessions))
            )
            
        except Exception as e:
            logger.error(f"Token usage analysis failed: {e}")
            return TokenUsageStats(0, 0, 0, 0.0, 0, 0, 0.0, 0, 0.0)
    
    def generate_optimization_suggestions(self, stats: TokenUsageStats) -> List[OptimizationSuggestion]:
        """Generate optimization suggestions based on usage patterns"""
        suggestions = []
        
        # High token usage per session
        if stats.average_tokens_per_session > 20000:
            suggestions.append(OptimizationSuggestion(
                category="Session Management",
                suggestion="Sessions have high token usage. Consider implementing message summarization or reducing conversation history length.",
                potential_savings=int(stats.average_tokens_per_session * 0.3),
                potential_cost_savings=stats.cost * 0.3,
                priority="HIGH"
            ))
        
        # Low cache hit rate
        if stats.cache_hit_rate < 20:
            suggestions.append(OptimizationSuggestion(
                category="Caching",
                suggestion="Low cache hit rate detected. Consider improving cache strategies or increasing cache TTL.",
                potential_savings=int(stats.total_tokens * 0.15),
                potential_cost_savings=stats.cost * 0.15,
                priority="HIGH"
            ))
        
        # High input/output ratio
        if stats.input_tokens > 0 and stats.output_tokens / stats.input_tokens > 0.5:
            suggestions.append(OptimizationSuggestion(
                category="Prompt Engineering",
                suggestion="High output-to-input token ratio. Consider optimizing prompts for more concise responses.",
                potential_savings=int(stats.output_tokens * 0.2),
                potential_cost_savings=(stats.output_tokens * 0.0006 / 1000) * 0.2,  # GPT-4o-mini output cost
                priority="MEDIUM"
            ))
        
        # Many active sessions
        if stats.sessions_count > 50:
            suggestions.append(OptimizationSuggestion(
                category="Session Cleanup",
                suggestion="High number of active sessions. Consider implementing automatic session cleanup.",
                potential_savings=int(stats.total_tokens * 0.1),
                potential_cost_savings=stats.cost * 0.1,
                priority="MEDIUM"
            ))
        
        return suggestions
    
    def optimize_conversation_history(self, session_id: str, target_tokens: int = 15000) -> Dict[str, Any]:
        """Optimize conversation history for a specific session"""
        try:
            if session_id not in self.memory_manager._active_sessions:
                return {"error": "Session not found"}
            
            session = self.memory_manager._active_sessions[session_id]
            messages = session.messages.copy()
            
            # Calculate current token usage
            current_tokens = sum(self.count_tokens(msg.content) for msg in messages)
            
            if current_tokens <= target_tokens:
                return {
                    "status": "no_optimization_needed",
                    "current_tokens": current_tokens,
                    "target_tokens": target_tokens
                }
            
            # Apply optimization strategies
            optimized_messages = messages.copy()
            tokens_saved = 0
            
            for strategy in self.optimization_strategies:
                if current_tokens - tokens_saved <= target_tokens:
                    break
                
                optimized_messages, saved = strategy(optimized_messages, target_tokens - (current_tokens - tokens_saved))
                tokens_saved += saved
            
            # Update session messages
            session.messages = optimized_messages
            session.total_tokens = sum(self.count_tokens(msg.content) for msg in optimized_messages)
            
            return {
                "status": "optimized",
                "original_tokens": current_tokens,
                "optimized_tokens": session.total_tokens,
                "tokens_saved": tokens_saved,
                "optimization_rate": (tokens_saved / current_tokens) * 100
            }
            
        except Exception as e:
            logger.error(f"Conversation optimization failed: {e}")
            return {"error": str(e)}
    
    def _optimize_message_summarization(self, messages: List[ConversationMessage], target_reduction: int) -> Tuple[List[ConversationMessage], int]:
        """Summarize older messages to reduce token count"""
        if len(messages) <= 5:  # Keep at least 5 recent messages
            return messages, 0
        
        # Keep system message and recent messages
        system_messages = [msg for msg in messages if msg.role == 'system']
        recent_messages = messages[-3:]  # Keep last 3 messages
        older_messages = messages[len(system_messages):-3]
        
        if not older_messages:
            return messages, 0
        
        # Create summary of older messages
        summary_content = f"[SUMMARIZED] Previous conversation included {len(older_messages)} messages covering analysis and discussion from {older_messages[0].timestamp.strftime('%Y-%m-%d %H:%M')} to {older_messages[-1].timestamp.strftime('%Y-%m-%d %H:%M')}."
        
        summary_message = ConversationMessage(
            role='system',
            content=summary_content,
            timestamp=datetime.now(),
            token_count=self.count_tokens(summary_content)
        )
        
        # Calculate tokens saved
        original_tokens = sum(self.count_tokens(msg.content) for msg in older_messages)
        tokens_saved = original_tokens - summary_message.token_count
        
        optimized_messages = system_messages + [summary_message] + recent_messages
        return optimized_messages, tokens_saved
    
    def _optimize_redundant_content(self, messages: List[ConversationMessage], target_reduction: int) -> Tuple[List[ConversationMessage], int]:
        """Remove redundant or repetitive content"""
        optimized_messages = []
        tokens_saved = 0
        
        for message in messages:
            original_content = message.content
            
            # Remove excessive whitespace
            optimized_content = re.sub(r'\s+', ' ', original_content.strip())
            
            # Remove repeated phrases (simple approach)
            lines = optimized_content.split('\n')
            unique_lines = []
            for line in lines:
                if line not in unique_lines or line.startswith('**') or len(line) < 20:
                    unique_lines.append(line)
            
            optimized_content = '\n'.join(unique_lines)
            
            # Calculate savings
            original_tokens = self.count_tokens(original_content)
            optimized_tokens = self.count_tokens(optimized_content)
            tokens_saved += original_tokens - optimized_tokens
            
            # Update message
            optimized_message = ConversationMessage(
                role=message.role,
                content=optimized_content,
                timestamp=message.timestamp,
                metadata=message.metadata,
                token_count=optimized_tokens
            )
            
            optimized_messages.append(optimized_message)
        
        return optimized_messages, tokens_saved
    
    def _optimize_prompt_efficiency(self, messages: List[ConversationMessage], target_reduction: int) -> Tuple[List[ConversationMessage], int]:
        """Optimize prompt efficiency by removing verbose instructions"""
        tokens_saved = 0
        optimized_messages = []
        
        for message in messages:
            if message.role == 'system':
                # Simplify system prompts by removing verbose examples
                content = message.content
                
                # Remove example blocks
                content = re.sub(r'<example>.*?</example>', '', content, flags=re.DOTALL)
                content = re.sub(r'Example:.*?(?=\n\n|\Z)', '', content, flags=re.DOTALL)
                
                # Remove excessive formatting
                content = re.sub(r'\*{2,}', '**', content)
                content = re.sub(r'#{3,}', '###', content)
                
                # Calculate savings
                original_tokens = self.count_tokens(message.content)
                optimized_tokens = self.count_tokens(content)
                tokens_saved += original_tokens - optimized_tokens
                
                optimized_message = ConversationMessage(
                    role=message.role,
                    content=content,
                    timestamp=message.timestamp,
                    metadata=message.metadata,
                    token_count=optimized_tokens
                )
                optimized_messages.append(optimized_message)
            else:
                optimized_messages.append(message)
        
        return optimized_messages, tokens_saved
    
    def _optimize_cache_usage(self, messages: List[ConversationMessage], target_reduction: int) -> Tuple[List[ConversationMessage], int]:
        """Optimize for better cache utilization"""
        # This would implement cache-aware optimization
        # For now, return messages unchanged
        return messages, 0
    
    def _optimize_session_management(self, messages: List[ConversationMessage], target_reduction: int) -> Tuple[List[ConversationMessage], int]:
        """Optimize session structure for better management"""
        # Keep only the most relevant messages
        if len(messages) > 20:
            # Keep system messages and recent user/assistant pairs
            system_messages = [msg for msg in messages if msg.role == 'system']
            conversation_messages = [msg for msg in messages if msg.role != 'system']
            
            # Keep recent conversation
            recent_messages = conversation_messages[-10:]
            
            tokens_saved = sum(self.count_tokens(msg.content) for msg in conversation_messages[:-10])
            
            return system_messages + recent_messages, tokens_saved
        
        return messages, 0
    
    def get_cost_breakdown(self, days: int = 30) -> Dict[str, Any]:
        """Get detailed cost breakdown by analysis type and model"""
        try:
            # This would analyze costs across different analysis types
            # For now, return a mock breakdown
            return {
                "total_cost": 12.45,
                "by_analysis_type": {
                    "hfacs_analysis": 4.20,
                    "ai_analysis": 3.15,
                    "professional_investigation": 3.80,
                    "smart_form": 1.30
                },
                "by_model": {
                    "gpt-4o-mini": 8.90,
                    "gpt-4o": 3.55
                },
                "cache_savings": 2.35,
                "optimization_potential": 1.85
            }
        except Exception as e:
            logger.error(f"Cost breakdown analysis failed: {e}")
            return {}
    
    def schedule_optimization(self, session_id: str, target_tokens: int, schedule_time: datetime) -> Dict[str, Any]:
        """Schedule automatic optimization for a session"""
        try:
            # This would implement scheduled optimization
            # For now, perform immediate optimization
            return self.optimize_conversation_history(session_id, target_tokens)
        except Exception as e:
            logger.error(f"Scheduled optimization failed: {e}")
            return {"error": str(e)}

def main():
    """Test token optimizer"""
    optimizer = TokenOptimizer()
    
    # Analyze token usage
    stats = optimizer.analyze_token_usage(days=7)
    print("Token Usage Statistics:")
    print(f"- Total tokens: {stats.total_tokens:,}")
    print(f"- Input tokens: {stats.input_tokens:,}")
    print(f"- Output tokens: {stats.output_tokens:,}")
    print(f"- Total cost: ${stats.cost:.4f}")
    print(f"- Cache hit rate: {stats.cache_hit_rate:.1f}%")
    print(f"- Sessions: {stats.sessions_count}")
    print(f"- Average tokens/session: {stats.average_tokens_per_session:.0f}")
    
    # Generate optimization suggestions
    suggestions = optimizer.generate_optimization_suggestions(stats)
    print(f"\nOptimization Suggestions ({len(suggestions)}):")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. [{suggestion.priority}] {suggestion.category}")
        print(f"   {suggestion.suggestion}")
        print(f"   Potential savings: {suggestion.potential_savings:,} tokens, ${suggestion.potential_cost_savings:.4f}")
        print()
    
    # Get cost breakdown
    cost_breakdown = optimizer.get_cost_breakdown()
    print("Cost Breakdown:")
    print(json.dumps(cost_breakdown, indent=2))

if __name__ == "__main__":
    main()