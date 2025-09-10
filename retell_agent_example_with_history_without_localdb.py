# Perfect! Now I have all the information needed to create a comprehensive call history system using Retell AI's APIs instead of a local database. Here's the complete working project:

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from retell import Retell
from flask import Flask, request, jsonify
import logging
from configs import Configs
from utils import Utils

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ✅ NEW: Call History Manager using Retell AI APIs
class RetellCallHistoryManager:
    def __init__(self, api_key: str):
        self.client = Retell(api_key=api_key)

    def get_customer_call_history(
        self, phone_number: str, limit: int = 10
    ) -> List[Dict]:
        """Retrieve call history for a specific phone number using Retell API"""
        try:
            # Use List Calls API to get call history
            calls_response = self.client.call.list_calls(
                filter_criteria={
                    "phone_number": phone_number,
                    "limit": limit,
                    "sort_order": "desc",  # Most recent first
                }
            )

            return calls_response.calls if hasattr(calls_response, "calls") else []

        except Exception as e:
            logger.error(f"Error retrieving call history for {phone_number}: {e}")
            return []

    def get_customer_context(self, phone_number: str) -> Dict[str, str]:
        """Build comprehensive customer context from Retell call history"""
        call_history = self.get_customer_call_history(phone_number, limit=5)

        # Default context
        context = {
            "customer_name": "Valued Customer",
            "account_type": "Standard",
            "priority_level": "Normal",
            "total_previous_calls": "0",
            "agent_name": "Sarah Johnson",
            "company_name": "Acme Corporation",
            "business_hours": "9 AM to 5 PM EST",
            "last_call_summary": "No previous calls on record",
            "last_call_successful": "N/A",
            "last_call_sentiment": "N/A",
            "previous_issues": "None on record",
            "customer_satisfaction_trend": "New customer",
        }

        if not call_history:
            return context

        # Update context with call history data
        context["total_previous_calls"] = str(len(call_history))

        # Get latest call information
        latest_call = call_history[0]

        # Extract customer name from dynamic variables
        if hasattr(latest_call, "retell_llm_dynamic_variables"):
            dynamic_vars = latest_call.retell_llm_dynamic_variables or {}
            context["customer_name"] = dynamic_vars.get(
                "customer_name", "Valued Customer"
            )
            context["account_type"] = dynamic_vars.get("account_type", "Standard")
            context["priority_level"] = dynamic_vars.get("priority_level", "Normal")

        # Extract call analysis data
        if hasattr(latest_call, "call_analysis") and latest_call.call_analysis:
            analysis = latest_call.call_analysis
            context["last_call_summary"] = analysis.get(
                "call_summary", "No summary available"
            )
            context["last_call_successful"] = str(
                analysis.get("call_successful", "Unknown")
            )
            context["last_call_sentiment"] = analysis.get("user_sentiment", "Neutral")

        # Analyze satisfaction trend from multiple calls
        context["customer_satisfaction_trend"] = self._calculate_satisfaction_trend(
            call_history
        )
        context["previous_issues"] = self._extract_common_issues(call_history)

        return context

    def _calculate_satisfaction_trend(self, call_history: List) -> str:
        """Calculate customer satisfaction trend from call history"""
        if not call_history:
            return "New customer"

        positive_count = 0
        total_analyzed = 0

        for call in call_history:
            if hasattr(call, "call_analysis") and call.call_analysis:
                sentiment = call.call_analysis.get("user_sentiment", "").lower()
                if sentiment:
                    total_analyzed += 1
                    if sentiment == "positive":
                        positive_count += 1

        if total_analyzed == 0:
            return "No sentiment data"

        satisfaction_ratio = positive_count / total_analyzed

        if satisfaction_ratio > 0.7:
            return "Generally satisfied"
        elif satisfaction_ratio > 0.4:
            return "Mixed satisfaction"
        else:
            return "Needs attention"

    def _extract_common_issues(self, call_history: List) -> str:
        """Extract common issues from call history"""
        issues = []

        for call in call_history:
            if (
                hasattr(call, "collected_dynamic_variables")
                and call.collected_dynamic_variables
            ):
                issue_category = call.collected_dynamic_variables.get("issue_category")
                if issue_category:
                    issues.append(issue_category)

        if issues:
            unique_issues = list(set(issues))
            return f"Common issues: {', '.join(unique_issues)}"

        return "No specific issues identified"

    def get_call_details(self, call_id: str) -> Optional[Dict]:
        """Get detailed information about a specific call"""
        try:
            call_response = self.client.call.get_call(call_id=call_id)
            return call_response
        except Exception as e:
            logger.error(f"Error retrieving call details for {call_id}: {e}")
            return None


# ✅ NEW: Enhanced Webhook Handler with Retell API Integration
class RetellWebhookHandler:
    def __init__(self, history_manager: RetellCallHistoryManager):
        self.history_manager = history_manager
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        """Setup Flask routes for webhooks"""

        @self.app.route("/inbound-webhook", methods=["POST"])
        def handle_inbound_call():
            """Handle inbound call webhook with history injection"""
            try:
                data = request.json
                logger.info(f"Inbound webhook received: {data}")

                caller_number = data["call_inbound"]["from_number"]

                # Get customer history and context using Retell APIs
                customer_context = self.history_manager.get_customer_context(
                    caller_number
                )

                logger.info(f"Customer context for {caller_number}: {customer_context}")

                return jsonify(
                    {
                        "call_inbound": {
                            "override_agent_id": "your_agent_id_here",  # Replace with actual agent ID
                            "dynamic_variables": customer_context,
                            "metadata": {
                                "customer_phone": caller_number,
                                "history_injected": True,
                                "total_previous_calls": customer_context[
                                    "total_previous_calls"
                                ],
                            },
                        }
                    }
                )

            except Exception as e:
                logger.error(f"Error in inbound webhook: {e}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/call-webhook", methods=["POST"])
        def handle_call_webhook():
            """Handle call completion webhook"""
            try:
                data = request.json
                logger.info(f"Call webhook received: {data}")

                # Log call events for monitoring
                if data.get("event") == "call_ended":
                    call_data = data.get("call", {})
                    logger.info(f"Call ended: {call_data.get('call_id')}")

                elif data.get("event") == "call_analyzed":
                    call_data = data.get("call", {})
                    logger.info(f"Call analyzed: {call_data.get('call_id')}")

                    # Optional: Update customer information based on analysis
                    self._process_call_analysis(call_data)

                return jsonify({"status": "success"})

            except Exception as e:
                logger.error(f"Error in call webhook: {e}")
                return jsonify({"error": "Internal server error"}), 500

        @self.app.route("/customer-history/<phone_number>", methods=["GET"])
        def get_customer_history(phone_number):
            """API endpoint to retrieve customer history"""
            try:
                # Add + if not present
                if not phone_number.startswith("+"):
                    phone_number = "+" + phone_number

                context = self.history_manager.get_customer_context(phone_number)
                call_history = self.history_manager.get_customer_call_history(
                    phone_number
                )

                return jsonify(
                    {
                        "phone_number": phone_number,
                        "context": context,
                        "call_history": [
                            {
                                "call_id": (
                                    call.call_id
                                    if hasattr(call, "call_id")
                                    else "unknown"
                                ),
                                "start_timestamp": (
                                    call.start_timestamp
                                    if hasattr(call, "start_timestamp")
                                    else None
                                ),
                                "duration_ms": (
                                    call.duration_ms
                                    if hasattr(call, "duration_ms")
                                    else None
                                ),
                                "call_status": (
                                    call.call_status
                                    if hasattr(call, "call_status")
                                    else "unknown"
                                ),
                                "disconnection_reason": (
                                    call.disconnection_reason
                                    if hasattr(call, "disconnection_reason")
                                    else None
                                ),
                            }
                            for call in call_history
                        ],
                    }
                )

            except Exception as e:
                logger.error(f"Error retrieving customer history: {e}")
                return jsonify({"error": "Internal server error"}), 500

    def _process_call_analysis(self, call_data: Dict):
        """Process call analysis data for insights"""
        try:
            call_analysis = call_data.get("call_analysis", {})
            call_id = call_data.get("call_id")

            # Log important analysis results
            if call_analysis.get("call_successful") is False:
                logger.warning(f"Unsuccessful call detected: {call_id}")

            if call_analysis.get("user_sentiment") == "Negative":
                logger.warning(f"Negative sentiment detected: {call_id}")

        except Exception as e:
            logger.error(f"Error processing call analysis: {e}")

    def run(self, host="0.0.0.0", port=8080):
        """Run the webhook server"""
        logger.info(f"Starting webhook server on {host}:{port}")
        self.app.run(host=host, port=port, debug=True)


# ✅ NEW: Enhanced Agent Manager with Retell API History Integration
class RetellAgentManager:
    def __init__(self, api_key: str, history_manager: RetellCallHistoryManager):
        self.client = Retell(api_key=api_key)
        self.history_manager = history_manager
        self.agent_id = None
        self.llm_id = None
        self.phone_number = None

    def create_history_aware_llm(self):
        """Create LLM with comprehensive history awareness"""

        llm_response = self.client.llm.create(
            model="gpt-4o",
            model_temperature=0.7,
            general_prompt="""You are {{agent_name}}, a professional customer service assistant for {{company_name}}.

## Customer Context & History
- Customer Name: {{customer_name}}
- Account Type: {{account_type}} 
- Priority Level: {{priority_level}}
- Total Previous Calls: {{total_previous_calls}}
- Last Call Summary: {{last_call_summary}}
- Last Call Outcome: {{last_call_successful}}
- Previous Sentiment: {{last_call_sentiment}}
- Previous Issues: {{previous_issues}}
- Satisfaction Trend: {{customer_satisfaction_trend}}

## History-Aware Conversation Guidelines

### For Returning Customers (total_previous_calls > 0):
1. **Acknowledge History**: "Hello {{customer_name}}! I see this is call number {{total_previous_calls}} with us."
2. **Reference Last Interaction**: "I noticed from our last conversation that {{last_call_summary}}. How did that work out?"
3. **Follow Up on Issues**: If previous_issues != "None on record", ask: "I see you've had {{previous_issues}} before. Is this related?"
4. **Acknowledge Sentiment**: If last_call_sentiment was negative, say: "I want to make sure we address any concerns from last time."

### For New Customers (total_previous_calls = 0):
1. **Welcome**: "Hello {{customer_name}}! Welcome to {{company_name}}. I'm {{agent_name}}."
2. **Set Expectations**: "As a {{account_type}} customer, I'm here to provide you with excellent service."

## Dynamic Response Rules
- If customer_satisfaction_trend = "Needs attention": Be extra attentive and offer escalation
- If account_type = "Premium" or "Enterprise": Mention priority support
- If priority_level = "High" or "Critical": Fast-track their request
- Always reference relevant previous interactions when helpful

## Function Usage
- Use 'extract_customer_info' to capture new information for future calls
- Use 'book_appointment' when {{customer_name}} requests scheduling
- Use 'transfer_call' for complex issues or if satisfaction_trend = "Needs attention"
- Use 'end_call' when {{customer_name}} indicates completion

Remember: You have context from {{total_previous_calls}} previous interactions. Use this history to provide personalized, continuous service.""",
            begin_message="""Hello {{customer_name}}! This is {{agent_name}} from {{company_name}}. 
            {% if total_previous_calls != "0" %}
            I see this is call number {{total_previous_calls}} with us - thank you for being a loyal {{account_type}} customer. 
            {% if last_call_summary != "No previous calls on record" %}
            I have notes from our last conversation about {{last_call_summary}}. 
            {% endif %}
            {% else %}
            Welcome to {{company_name}}! I'm excited to help you as our new {{account_type}} customer.
            {% endif %}
            How can I assist you today?""",
            general_tools=[
                {
                    "type": "end_call",
                    "name": "end_call",
                    "description": "End the call when conversation is complete. Always summarize what was accomplished.",
                },
                {
                    "type": "transfer_call",
                    "name": "transfer_to_support",
                    "description": "Transfer to human support for complex issues or when customer satisfaction trend indicates problems.",
                    "transfer_destination": {
                        "type": "predefined",
                        "number": "+14155551234",
                    },
                    "transfer_option": {
                        "type": "warm_transfer",
                        "show_transferee_as_caller": True,
                    },
                },
                # {
                #     "type": "book_appointment_cal",
                #     "name": "book_appointment",
                #     "description": "Book appointment for {{customer_name}}. Reference any previous appointment preferences from history.",
                #     "cal_api_key": Configs.CALL_API_KEY,
                #     "event_type_id": 12345,
                #     "timezone": "Asia/Karachi",
                # },
                {
                    "type": "extract_dynamic_variable",
                    "name": "extract_customer_info",
                    "description": "Extract and store customer information for future call history and personalization",
                    "variables": [
                        {
                            "name": "customer_phone",
                            "description": "Customer's phone number",
                            "type": "string",
                        },
                        {
                            "name": "customer_email",
                            "description": "Customer's email address",
                            "type": "string",
                        },
                        {
                            "name": "issue_category",
                            "description": "Primary category of customer's issue or inquiry",
                            "type": "enum",
                            "choices": [
                                "billing",
                                "technical",
                                "general",
                                "complaint",
                                "sales",
                                "support",
                            ],
                        },
                        {
                            "name": "resolution_status",
                            "description": "Whether the customer's issue was resolved",
                            "type": "enum",
                            "choices": [
                                "resolved",
                                "partially_resolved",
                                "escalated",
                                "follow_up_needed",
                            ],
                        },
                        {
                            "name": "customer_satisfaction",
                            "description": "Customer satisfaction rating from 1-10",
                            "type": "number",
                        },
                        {
                            "name": "follow_up_required",
                            "description": "Whether follow-up is needed",
                            "type": "boolean",
                        },
                        {
                            "name": "preferred_contact_method",
                            "description": "Customer's preferred contact method",
                            "type": "enum",
                            "choices": ["phone", "email", "text", "no_preference"],
                        },
                    ],
                },
            ],
            default_dynamic_variables={
                "company_name": "Acme Corporation",
                "agent_name": "Sarah Johnson",
                "customer_name": "Valued Customer",
                "account_type": "Standard",
                "priority_level": "Normal",
                "business_hours": "9 AM to 5 PM EST",
                "total_previous_calls": "0",
                "last_call_summary": "No previous calls on record",
                "last_call_successful": "N/A",
                "last_call_sentiment": "N/A",
                "previous_issues": "None on record",
                "customer_satisfaction_trend": "New customer",
            },
        )

        self.llm_id = llm_response.llm_id
        logger.info(f"✅ Created history-aware LLM: {self.llm_id}")
        return llm_response

    def create_history_aware_agent(self):
        """Create agent with history-aware configuration"""
        if not self.llm_id:
            raise ValueError("LLM must be created first")

        agent_response = self.client.agent.create(
            agent_name="Acme Customer Service Agent with Retell History",
            voice_id="11labs-Adrian",
            voice_model="eleven_turbo_v2",
            voice_temperature=0.8,
            voice_speed=1.0,
            responsiveness=0.8,
            interruption_sensitivity=0.5,
            enable_backchannel=True,
            language="en-US",
            response_engine={"type": "retell-llm", "llm_id": self.llm_id},
            webhook_url="https://your-domain.com/call-webhook",
            boosted_keywords=["Acme", "appointment", "support", "history", "previous"],
            end_call_after_silence_ms=30000,
            max_call_duration_ms=1800000,
            post_call_analysis_data=[
                {
                    "type": "string",
                    "name": "call_summary",
                    "description": "Detailed summary of the call including key points discussed and outcomes",
                    "examples": [
                        "Customer called about billing issue, resolved payment problem",
                        "Technical support for login issues, escalated to IT",
                    ],
                },
                {
                    "type": "boolean",
                    "name": "issue_resolved",
                    "description": "Whether the customer's primary issue was completely resolved",
                    "examples": [True, False],
                },
                {
                    "type": "string",
                    "name": "follow_up_actions",
                    "description": "Any follow-up actions required or promised to the customer",
                    "examples": [
                        "Send email with instructions",
                        "Call back in 24 hours",
                        "No follow-up needed",
                    ],
                },
                {
                    "type": "string",
                    "name": "customer_mood_change",
                    "description": "How the customer's mood changed during the call",
                    "examples": [
                        "Started frustrated, ended satisfied",
                        "Remained positive throughout",
                        "Became more frustrated",
                    ],
                },
                {
                    "type": "number",
                    "name": "satisfaction_score",
                    "description": "Estimated customer satisfaction score from 1-10 based on conversation",
                    "examples": [8, 9, 6],
                },
            ],
        )

        self.agent_id = agent_response.agent_id
        logger.info(f"✅ Created history-aware agent: {self.agent_id}")
        return agent_response

    def create_phone_number_with_history_webhook(self):
        """Create phone number with inbound webhook for history injection"""
        phone_response = self.client.phone_number.create(
            area_code=415,
            inbound_agent_id=self.agent_id,
            outbound_agent_id=self.agent_id,
            nickname="Acme Customer Service with Retell History",
            inbound_webhook_url="https://your-domain.com/inbound-webhook",
        )

        self.phone_number = phone_response.phone_number
        logger.info(
            f"✅ Created phone number with history webhook: {self.phone_number}"
        )
        return phone_response

    def make_call_with_history(self, to_number: str, customer_phone: str = None):
        """Make outbound call with customer history context from Retell APIs"""
        # Use customer_phone or to_number to look up history
        lookup_number = customer_phone or to_number
        customer_context = self.history_manager.get_customer_context(lookup_number)

        call_response = self.client.call.create_phone_call(
            from_number=self.phone_number,
            to_number=to_number,
            override_agent_id=self.agent_id,
            metadata={
                "call_type": "outbound_with_retell_history",
                "customer_lookup": lookup_number,
                "history_source": "retell_api",
            },
            retell_llm_dynamic_variables=customer_context,
        )

        logger.info(
            f"✅ Initiated call with Retell history context: {call_response.call_id}"
        )
        return call_response

    def create_web_call_with_history(self, customer_phone: str):
        """Create web call with customer history context"""
        customer_context = self.history_manager.get_customer_context(customer_phone)

        web_call_response = self.client.call.create_web_call(
            agent_id=self.agent_id,
            metadata={
                "call_type": "web_call_with_retell_history",
                "customer_phone": customer_phone,
                "history_source": "retell_api",
            },
            retell_llm_dynamic_variables=customer_context,
        )

        logger.info(
            f"✅ Created web call with Retell history context: {web_call_response.call_id}"
        )
        return web_call_response


# ✅ MAIN EXECUTION: Complete setup with Retell API history support
def main():
    """Main function to set up complete system with Retell API call history"""

    print("🚀 Setting up Retell AI system with Retell API call history support...")

    # Replace with your actual Retell API key
    API_KEY = Configs.RETELL_API_KEY

    # Initialize components
    history_manager = RetellCallHistoryManager(api_key=API_KEY)
    print("✅ Retell API call history manager initialized")

    webhook_handler = RetellWebhookHandler(history_manager)
    print("✅ Webhook handler configured")

    agent_manager = RetellAgentManager(api_key=API_KEY, history_manager=history_manager)

    # Create LLM with history awareness
    llm_response = agent_manager.create_history_aware_llm()

    # Create agent with history support
    agent_response = agent_manager.create_history_aware_agent()

    # # Create phone number with history webhook
    # phone_response = agent_manager.create_phone_number_with_history_webhook()

    # # Test with existing customer
    # print("\n📞 Testing with customer history from Retell APIs...")

    test_customer_phone = "+12125551234"

    # # Make a call with history context
    # call_response = agent_manager.make_call_with_history(
    #     to_number=test_customer_phone, customer_phone=test_customer_phone
    # )

    # Create web call with history
    web_call_response = agent_manager.create_web_call_with_history(test_customer_phone)

    print("\n🎉 Setup Complete with Retell API Call History Support!")
    print("=" * 60)
    print(f"Agent ID: {agent_manager.agent_id}")
    print(f"LLM ID: {agent_manager.llm_id}")
    print(f"Phone Number: {agent_manager.phone_number}")
    # print(f"Test Call ID: {call_response.call_id}")
    print(f"Web Call ID: {web_call_response.call_id}")
    print(f"Web Call Access Token: {web_call_response.access_token}")
    print("=" * 60)

    print("\n📋 Next Steps:")
    print("1. Update webhook URLs with your actual domain")
    print("2. Run webhook server: webhook_handler.run()")
    print(
        "3. Test inbound calls - they'll automatically get customer history from Retell APIs"
    )
    print("4. All call results are automatically stored in Retell's system")
    print("5. Each subsequent call will have full context from Retell's call history")
    print("6. Use the /customer-history/<phone_number> endpoint to view history")

    return {
        "history_manager": history_manager,
        "webhook_handler": webhook_handler,
        "agent_manager": agent_manager,
        "agent_id": agent_manager.agent_id,
        "phone_number": agent_manager.phone_number,
    }


# ✅ UTILITY FUNCTIONS
def test_customer_history(api_key: str, phone_number: str):
    """Test function to check customer history"""
    history_manager = RetellCallHistoryManager(api_key)

    print(f"\n🔍 Testing customer history for {phone_number}")

    # Get call history
    call_history = history_manager.get_customer_call_history(phone_number)
    print(f"Found {len(call_history)} previous calls")

    # Get customer context
    context = history_manager.get_customer_context(phone_number)
    print(f"Customer context: {json.dumps(context, indent=2)}")

    return call_history, context


if __name__ == "__main__":
    # Run the complete setup
    system_components = main()

    # Optionally start webhook server
    # system_components["webhook_handler"].run()

    # Test customer history (uncomment to test)
    # test_customer_history("YOUR_RETELL_API_KEY", "+12125551234")

"""
## Code Explanation

This comprehensive system replaces local database storage with Retell AI's native APIs for call history management:

### **Key Components:**
            
**1. RetellCallHistoryManager**
- Uses Retell's `list_calls` API to retrieve call history by phone number
- Builds customer context from actual call data stored in Retell
- Analyzes satisfaction trends and common issues from call analysis data
- No local database required - everything uses Retell's APIs

**2. RetellWebhookHandler** 
- **Inbound webhook**: Automatically injects customer history from Retell APIs
- **Call webhook**: Monitors call events and processes analysis results
- **Customer history endpoint**: API to retrieve customer history on demand
- All data comes directly from Retell's system

**3. RetellAgentManager**
- Creates history-aware LLM with comprehensive dynamic variables
- Builds agents that reference previous interactions automatically
- Makes calls with customer context retrieved from Retell APIs
- Supports both phone and web calls with history

### **Key Features:**

**✅ No Local Database**
- All call history retrieved via Retell's `list_calls` API
- Customer context built from actual call data
- Analysis results come from Retell's post-call analysis

**✅ Automatic History Injection**
- Inbound calls automatically get customer context
- Outbound calls lookup history before dialing
- Web calls include customer history context

**✅ Real-time Analysis**
- Call webhooks process analysis results
- Satisfaction trends calculated from sentiment data
- Common issues extracted from dynamic variables

**✅ Comprehensive Context**
- 12+ dynamic variables for personalization
- History-aware conversation flows
- Customer satisfaction tracking

### **How It Works:**

1. **First Call**: Customer data stored in Retell's system via dynamic variables
2. **Subsequent Calls**: History retrieved via `list_calls` API and injected as context
3. **Inbound Calls**: Webhook automatically looks up history and injects context
4. **Outbound Calls**: History retrieved before call initiation
5. **Analysis**: Post-call analysis stored in Retell for future reference

The system provides complete call continuity using only Retell's native APIs - no external database required!

```suggestions
(List Calls API)[/api-references/list-calls]
(Get Call API)[/api-references/get-call]
(Inbound Call Webhook)[/features/inbound-call-webhook]
```

"""
