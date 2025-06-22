"""
LLM Client for Noumi AI Agents
Handles communication with Google Gemini and other language models.
"""

import json
import os
from typing import Dict, Any, List, Optional

# Try to import Google GenAI, but handle gracefully if not available
try:
    from google import genai
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False

# Fallback to OpenAI if needed
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class NoumiLLMClient:
    """
    Client for interacting with language models for financial planning.
    Now primarily uses Google Gemini API.
    """

    def __init__(self, api_key: Optional[str] = None, 
                 provider: str = "google"):
        self.provider = provider
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY') or \
            os.getenv('OPENAI_API_KEY')
        self.client = None
        
        if self.provider == "google" and self.api_key and \
                GOOGLE_GENAI_AVAILABLE:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Google GenAI: {e}")
        elif self.provider == "openai" and self.api_key and \
                OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize OpenAI: {e}")
        
        if not self.client:
            print("Warning: No AI client available. Running in demo mode.")

    def query_financial_planner(self,
                                content: str,
                                system_role: str,
                                model_name: str = "gemini-2.0-flash",
                                return_json: bool = True) -> Any:
        """
        Query language model for financial planning advice.

        Args:
            content: The user input/context for the query
            system_role: The system role/instructions for the AI
            model_name: Which model to use (default: gemini-2.0-flash)
            return_json: Whether to expect JSON response

        Returns:
            Parsed JSON response or string response
        """
        print(f"🤖 Making LLM call to {self.provider}...")
        print(f"📝 Query length: {len(content)} characters")
        
        # Return mock data if no client available
        if not self.client:
            print("⚠️ No LLM client available - using mock response")
            return self._get_mock_response(content, return_json)
            
        try:
            print(f"🔄 Sending request to {model_name}...")
            if self.provider == "google":
                result = self._query_google_gemini(
                    content, system_role, model_name, return_json
                )
            elif self.provider == "openai":
                result = self._query_openai(
                    content, system_role, model_name, return_json
                )
            
            print("✅ LLM response received successfully!")
            if return_json and isinstance(result, dict):
                print(f"📊 JSON response with {len(result)} keys")
            else:
                print(f"📝 Text response: {len(str(result))} characters")
            
            return result
            
        except Exception as e:
            print(f"❌ LLM query failed: {e}")
            print("🔄 Falling back to mock response...")
            return self._get_mock_response(content, return_json)

    def _query_google_gemini(self, content: str, system_role: str,
                             model_name: str, return_json: bool) -> Any:
        """Query Google Gemini using the new GenAI SDK."""
        print("🔗 Connecting to Google Gemini API...")
        
        # Combine system role and user content for Gemini
        full_prompt = f"{system_role}\n\nUser Request: {content}"
        
        if return_json:
            full_prompt += (
                "\n\nCRITICAL: You MUST return ONLY a complete, valid JSON object. "
                "Requirements:\n"
                "1. Start with { and end with }\n"
                "2. Use double quotes for all strings\n"
                "3. No trailing commas\n"
                "4. No comments or explanations outside the JSON\n"
                "5. Ensure all brackets are properly closed\n"
                "6. Do NOT include markdown code blocks (```json)\n"
                "7. Return the complete JSON in a single response\n\n"
                "Example format: {\"key\": \"value\", \"number\": 123}"
            )

        print("⏳ Waiting for Gemini response...")
        response = self.client.models.generate_content(
            model=model_name,
            contents=full_prompt
        )
        print("📨 Raw response received from Gemini")

        response_text = response.text.strip()
        print(f"📄 Response length: {len(response_text)} characters")

        if return_json:
            print("🔍 Parsing JSON response...")
            # Enhanced JSON parsing with multiple strategies
            result = self._robust_json_parse(response_text)
            print("✅ JSON parsing completed")
            return result
        else:
            print("✅ Text response ready")
            return response_text

    def _robust_json_parse(self, response_text: str) -> Any:
        """
        Enhanced JSON parsing with multiple fallback strategies.
        Based on common JSON parsing issues from GeeksforGeeks.
        """
        # Strategy 1: Try parsing the response as-is
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Clean and try again
        try:
            cleaned = self._clean_json_response(response_text)
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass
        
        # Strategy 3: Handle streaming/partial responses
        try:
            complete_json = self._reconstruct_streaming_json(response_text)
            return json.loads(complete_json)
        except json.JSONDecodeError:
            pass
        
        # Strategy 4: Extract JSON from mixed content
        try:
            extracted = self._extract_json_from_mixed_content(response_text)
            return json.loads(extracted)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Strategy 5: Fix common JSON errors
        try:
            fixed = self._fix_common_json_errors(response_text)
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass
        
        print(f"Warning: All JSON parsing strategies failed for response: "
              f"{response_text[:200]}...")
        # Return mock response as final fallback
        return self._get_mock_response(response_text, True)

    def _clean_json_response(self, response: str) -> str:
        """
        Clean the LLM response to extract valid JSON.
        """
        # Remove code block markers if present
        response = response.replace("```json", "").replace("```", "")
        response = response.strip()

        # Find the first { and last } to extract JSON
        start_idx = response.find('{')
        end_idx = response.rfind('}')

        if start_idx != -1 and end_idx != -1:
            return response[start_idx:end_idx + 1]
        else:
            return response

    def _reconstruct_streaming_json(self, response: str) -> str:
        """
        Handle streaming responses where JSON is built incrementally.
        """
        lines = response.split('\n')
        json_parts = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('"') or line.startswith('{')):
                # This looks like a JSON fragment
                json_parts.append(line)
        
        # Try to reconstruct complete JSON
        reconstructed = '\n'.join(json_parts)
        
        # Clean up any incomplete parts
        if '"' in reconstructed:
            # Find incomplete string values and complete them
            import re
            # Pattern to find incomplete strings like "key": "incomplete_val
            pattern = r'"([^"]+)":\s*"([^"]*?)(?!")[^,}\]]*(?=,|}|\]|$)'
            reconstructed = re.sub(pattern, r'"\1": "\2"', reconstructed)
        
        return reconstructed

    def _extract_json_from_mixed_content(self, response: str) -> str:
        """
        Extract JSON from mixed content that includes explanations.
        """
        # Look for JSON-like structures
        import re
        
        # Pattern to match JSON objects
        json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        if matches:
            # Return the largest match (likely the main JSON)
            return max(matches, key=len)
        
        # If no complete JSON found, try to build one from key-value pairs
        return self._build_json_from_fragments(response)

    def _build_json_from_fragments(self, response: str) -> str:
        """
        Build JSON from fragmented key-value pairs.
        """
        import re
        
        # Extract key-value patterns
        kv_pattern = r'"([^"]+)":\s*([^,}\n]+)'
        matches = re.findall(kv_pattern, response)
        
        if matches:
            json_obj = {}
            for key, value in matches:
                # Clean and parse the value
                value = value.strip().rstrip(',')
                try:
                    # Try to parse as number
                    if value.replace('.', '').replace('-', '').isdigit():
                        json_obj[key] = float(value) if '.' in value else int(value)
                    elif value.lower() in ['true', 'false']:
                        json_obj[key] = value.lower() == 'true'
                    elif value.startswith('"') and value.endswith('"'):
                        json_obj[key] = value[1:-1]
                    else:
                        json_obj[key] = value
                except:
                    json_obj[key] = value
            
            return json.dumps(json_obj)
        
        raise ValueError("Could not extract JSON from response")

    def _fix_common_json_errors(self, response: str) -> str:
        """
        Fix common JSON formatting errors.
        """
        # Remove any non-JSON prefixes/suffixes
        response = response.strip()
        
        # Fix trailing commas
        import re
        response = re.sub(r',\s*}', '}', response)
        response = re.sub(r',\s*\]', ']', response)
        
        # Fix missing quotes around keys
        response = re.sub(r'(\w+):', r'"\1":', response)
        
        # Fix single quotes to double quotes
        response = response.replace("'", '"')
        
        # Ensure strings are properly quoted
        response = re.sub(r':\s*([^"\d\[\{][^,}\]]*)', r': "\1"', response)
        
        # Remove any trailing incomplete parts
        if response.count('{') > response.count('}'):
            # Add missing closing braces
            missing_braces = response.count('{') - response.count('}')
            response += '}' * missing_braces
        
        return response

    def _query_openai(self, content: str, system_role: str,
                      model_name: str, return_json: bool) -> Any:
        """Fallback to OpenAI if needed."""
        if return_json:
            system_role += (
                "\n\nIMPORTANT: Return your response in valid JSON "
                "format only. Do not include any text outside the JSON."
            )

        response = self.client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": content}
            ],
            temperature=0.7
        )

        response_text = response.choices[0].message.content.strip()

        if return_json:
            response_text = self._clean_json_response(response_text)
            return json.loads(response_text)
        else:
            return response_text

    def _get_mock_response(self, content: str, return_json: bool) -> Any:
        """Generate mock responses for demo purposes."""
        if return_json:
            if "spending_patterns" in content.lower():
                return {
                    "spending_patterns": [
                        "High dining expenses", 
                        "Regular subscriptions"
                    ],
                    "top_categories": [
                        "Food & Dining", 
                        "Entertainment", 
                        "Transportation"
                    ],
                    "savings_opportunities": [
                        "Reduce dining out", 
                        "Cancel unused subscriptions"
                    ],
                    "recommendations": [
                        "Cook more meals at home", 
                        "Review monthly subscriptions"
                    ]
                }
            elif "weekly savings plan" in content.lower():
                return {
                    "week_start_date": "2024-01-15",
                    "savings_target": {"amount": 125, "currency": "USD"},
                    "spending_limits": {
                        "Food & Dining": {
                            "daily_limit": 25, 
                            "weekly_limit": 175
                        }
                    },
                    "daily_recommendations": [
                        {
                            "day": "Monday",
                            "actions": [
                                "Check account balance", 
                                "Set weekly goals"
                            ],
                            "focus_area": "Goal Setting",
                            "motivation": "Start your week strong!"
                        }
                    ],
                    "tracking_metrics": [
                        {
                            "metric_name": "Weekly Savings", 
                            "target_value": 125, 
                            "current_value": 0
                        }
                    ],
                    "weekly_challenges": [
                        "Cook at home 5 days", 
                        "Track all expenses"
                    ],
                    "success_tips": [
                        "Celebrate small wins", 
                        "Review progress daily"
                    ]
                }
            elif "financial personality" in content.lower():
                return {
                    "personality_type": "Cautious Saver",
                    "behavioral_patterns": [
                        "Prefers low-risk options", 
                        "Values financial security"
                    ],
                    "obstacles": ["Lack of motivation", "Unclear goals"],
                    "strategies": [
                        "Automated savings", 
                        "Clear milestone tracking"
                    ],
                    "communication_style": "Supportive and encouraging"
                }
            else:
                return {"message": "Mock response for demo purposes"}
        else:
            return ("This is a mock response for demo purposes when no "
                    "API key is available.")

    def analyze_transactions_with_llm(self,
                                      transactions: List[Dict],
                                      user_preferences: Dict) -> \
            Dict[str, Any]:
        """
        Use LLM to analyze transaction patterns and identify savings.
        """
        system_role = """
        You are a financial advisor AI specializing in personal finance 
        and savings optimization. Analyze the provided transaction data 
        and user preferences to identify spending patterns and savings 
        opportunities. You must respond with a valid JSON object only.
        """

        # Limit for token efficiency
        limited_transactions = transactions[:50]
        content = f"""
        Transaction Data: {json.dumps(limited_transactions)}
        User Preferences: {json.dumps(user_preferences)}

        Analyze these transactions and provide insights. Return ONLY a valid 
        JSON object with these exact keys:
        - spending_patterns: array of strings describing patterns
        - top_categories: array of category names  
        - savings_opportunities: array of strings describing opportunities
        - recommendations: array of actionable recommendation strings

        Do not include explanations outside the JSON.
        """

        return self.query_financial_planner(content, system_role)

    def generate_savings_plan_with_llm(self,
                                       spending_analysis: Dict,
                                       user_goals: Dict,
                                       quiz_insights: Dict) -> \
            Dict[str, Any]:
        """
        Generate a comprehensive weekly savings plan using LLM.
        """
        system_role = """
        You are an expert financial planning AI that creates personalized 
        weekly savings plans. Create actionable, realistic weekly savings 
        plans based on user data. You must respond with a valid JSON object only.
        """

        content = f"""
        Spending Analysis: {json.dumps(spending_analysis)}
        User Goals: {json.dumps(user_goals)}
        Quiz Insights: {json.dumps(quiz_insights)}

        Create a detailed weekly savings plan. Return ONLY a valid JSON object 
        with this EXACT structure (no additional fields):
        {{
            "week_start_date": "YYYY-MM-DD",
            "savings_target": {{
                "amount": number,
                "currency": "USD"
            }},
            "spending_limits": {{
                "category_name": {{"daily_limit": number, 
                                   "weekly_limit": number}}
            }},
            "daily_recommendations": [
                {{
                    "day": "Monday",
                    "actions": ["action1", "action2"],
                    "focus_area": "string",
                    "motivation": "string"
                }}
            ],
            "tracking_metrics": [
                {{
                    "metric_name": "string",
                    "target_value": number,
                    "current_value": number
                }}
            ],
            "weekly_challenges": ["challenge1", "challenge2"],
            "success_tips": ["tip1", "tip2"]
        }}

        Ensure all numbers are valid, all strings are complete, and all 
        brackets are properly closed. Do not include explanations outside the JSON.
        """

        return self.query_financial_planner(content, system_role) 