import httpx
import asyncio
import logging
import json
from typing import Dict, Any, Optional, Tuple, Union
import pandas as pd
from token_minter import TokenMinter
from utils.config import DATABRICKS_HOST, CLIENT_ID, CLIENT_SECRET, GENIE_SPACE_ID

logger = logging.getLogger(__name__)

GENIE_MCP_BASE_URL = f"https://{DATABRICKS_HOST}/api/2.0/mcp/genie/{GENIE_SPACE_ID}"


class GenieMCPClient:
    """Client for interacting with Genie Space via MCP server."""
    
    def __init__(self, token_minter: TokenMinter):
        self.token_minter = token_minter
        self.client = httpx.AsyncClient(timeout=120)
        self.conversation_ids: Dict[str, str] = {}
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with fresh token."""
        return {
            "Authorization": f"Bearer {self.token_minter.get_token()}",
            "Content-Type": "application/json"
        }
    
    async def query_genie(
        self, 
        query: str, 
        session_id: str,
        conversation_id: Optional[str] = None
    ) -> Tuple[str, Optional[str], Optional[str]]:
        """
        Query the Genie Space MCP server.
        
        Args:
            query: The natural language query
            session_id: The chat session ID for tracking conversation
            conversation_id: Optional existing Genie conversation ID for follow-ups
            
        Returns:
            Tuple of (response_text, conversation_id, error_message)
        """
        try:
            headers = self._get_headers()
            
            tool_name = f"query_space_{GENIE_SPACE_ID}"
            arguments = {"query": query}
            if conversation_id:
                arguments["conversation_id"] = conversation_id
            
            payload = {
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            logger.info(f"Querying Genie Space with: {query[:50]}...")
            
            response = await self.client.post(
                GENIE_MCP_BASE_URL,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 429:
                return "", None, "The service is currently experiencing high demand. Please try again in a few moments."
            
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                error_msg = result.get("error", {}).get("message", "Unknown error from Genie")
                logger.error(f"Genie error: {error_msg}")
                return "", None, error_msg
            
            content = result.get("result", {}).get("content", [])
            if content and len(content) > 0:
                text_content = content[0].get("text", "")
                
                try:
                    parsed = json.loads(text_content)
                    new_conversation_id = parsed.get("conversation_id")
                    message_id = parsed.get("message_id")
                    status = parsed.get("status", "")
                    
                    if new_conversation_id:
                        self.conversation_ids[session_id] = new_conversation_id
                    
                    if status.lower() not in ["completed", "complete"]:
                        response_text, error = await self._poll_for_completion(
                            new_conversation_id or conversation_id,
                            message_id
                        )
                        if error:
                            return "", new_conversation_id, error
                        return response_text, new_conversation_id, None
                    
                    response_text = parsed.get("response", text_content)
                    return self._format_response(response_text), new_conversation_id, None
                    
                except json.JSONDecodeError:
                    return self._format_response(text_content), conversation_id, None
            
            return "No response from Genie Space.", conversation_id, None
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                return "", conversation_id, "The service is currently experiencing high demand. Please try again in a few moments."
            logger.error(f"HTTP error querying Genie: {e}")
            return "", conversation_id, f"Error querying Genie Space: {str(e)}"
        except Exception as e:
            logger.error(f"Error querying Genie: {e}")
            return "", conversation_id, f"Error querying Genie Space: {str(e)}"
    
    async def _poll_for_completion(
        self, 
        conversation_id: str, 
        message_id: str,
        max_attempts: int = 60,
        poll_interval: float = 2.0
    ) -> Tuple[str, Optional[str]]:
        """
        Poll for completion of an async Genie query.
        
        Args:
            conversation_id: The Genie conversation ID
            message_id: The message ID to poll
            max_attempts: Maximum polling attempts
            poll_interval: Seconds between polls
            
        Returns:
            Tuple of (response_text, error_message)
        """
        tool_name = f"poll_response_{GENIE_SPACE_ID}"
        
        for attempt in range(max_attempts):
            try:
                headers = self._get_headers()
                
                payload = {
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": {
                            "conversation_id": conversation_id,
                            "message_id": message_id
                        }
                    }
                }
                
                response = await self.client.post(
                    GENIE_MCP_BASE_URL,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 429:
                    await asyncio.sleep(poll_interval * 2)
                    continue
                
                response.raise_for_status()
                result = response.json()
                
                if "error" in result:
                    error_msg = result.get("error", {}).get("message", "Unknown error")
                    if "expired" in error_msg.lower() or "not found" in error_msg.lower():
                        return "", "The conversation has expired. Please try your query again."
                    return "", error_msg
                
                content = result.get("result", {}).get("content", [])
                if content and len(content) > 0:
                    text_content = content[0].get("text", "")
                    
                    try:
                        parsed = json.loads(text_content)
                        status = parsed.get("status", "")
                        
                        if status.lower() in ["completed", "complete"]:
                            response_text = parsed.get("response", text_content)
                            return self._format_response(response_text), None
                        elif status.lower() in ["error", "failed"]:
                            return "", parsed.get("error", "Query failed")
                    except json.JSONDecodeError:
                        pass
                
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                logger.warning(f"Poll attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(poll_interval)
        
        return "", "Query timed out. Please try again."
    
    def _format_response(self, response: Any) -> str:
        """Format the Genie response for display."""
        if isinstance(response, str):
            try:
                data = json.loads(response)
                if isinstance(data, list):
                    return self._format_data_as_table(data)
                elif isinstance(data, dict):
                    if "data" in data:
                        return self._format_data_as_table(data["data"])
                    return json.dumps(data, indent=2)
                return response
            except json.JSONDecodeError:
                return response
        elif isinstance(response, list):
            return self._format_data_as_table(response)
        elif isinstance(response, dict):
            if "data" in response:
                return self._format_data_as_table(response["data"])
            return json.dumps(response, indent=2)
        return str(response)
    
    def _format_data_as_table(self, data: list) -> str:
        """Format list data as a markdown table."""
        if not data:
            return "No data found."
        
        try:
            df = pd.DataFrame(data)
            return df.to_markdown(index=False)
        except Exception:
            return json.dumps(data, indent=2)
    
    def get_conversation_id(self, session_id: str) -> Optional[str]:
        """Get the Genie conversation ID for a chat session."""
        return self.conversation_ids.get(session_id)
    
    def clear_conversation(self, session_id: str) -> None:
        """Clear the Genie conversation ID for a chat session."""
        if session_id in self.conversation_ids:
            del self.conversation_ids[session_id]
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
