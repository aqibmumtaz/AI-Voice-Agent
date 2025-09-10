import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from retell import Retell
from flask import Flask, request, jsonify


# ✅ NEW: Database Manager Class for Call History
class CallHistoryManager:
    def __init__(self, db_path: str = "call_history.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for call history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                phone_number TEXT PRIMARY KEY,
                name TEXT,
                account_type TEXT,
                priority_level TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS call_history (
                call_id TEXT PRIMARY KEY,
                customer_phone TEXT,
                agent_id TEXT,
                call_type TEXT,
                direction TEXT,
                start_timestamp INTEGER,
                end_timestamp INTEGER,
                duration_ms INTEGER,
                call_summary TEXT,
                call_successful BOOLEAN,
                user_sentiment TEXT,
                disconnection_reason TEXT,
                extracted_variables TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_phone) REFERENCES customers (phone_number)
            )
        """
        )

        conn.commit()
        conn.close()

    def get_customer_context(self, phone_number: str) -> Dict[str, str]:
        """Retrieve comprehensive customer context for dynamic variables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get customer info
        cursor.execute(
            """
            SELECT name, account_type, priority_level 
            FROM customers 
            WHERE phone_number = ?
        """,
            (phone_number,),
        )

        customer = cursor.fetchone()

        # Get call history
        cursor.execute(
            """
            SELECT call_summary, call_successful, user_sentiment, 
                   start_timestamp, extracted_variables
            FROM call_history 
            WHERE customer_phone = ? 
            ORDER BY start_timestamp DESC 
            LIMIT 5
        """,
            (phone_number,),
        )

        call_history = cursor.fetchall()
        conn.close()

        # Build context
        context = {
            "customer_name": customer[0] if customer else "Valued Customer",
            "account_type": customer[1] if customer else "Standard",
            "priority_level": customer[2] if customer else "Normal",
            "total_previous_calls": str(len(call_history)),
            "agent_name": "Sarah Johnson",
            "company_name": "Acme Corporation",
            "business_hours": "9 AM to 5 PM EST",
        }

        if call_history:
            latest_call = call_history[0]
            context.update(
                {
                    "last_call_summary": latest_call[0] or "No summary available",
                    "last_call_successful": (
                        str(latest_call[1]) if latest_call[1] is not None else "Unknown"
                    ),
                    "last_call_sentiment": latest_call[2] or "Neutral",
                    "previous_issues": self._extract_common_issues(call_history),
                    "customer_satisfaction_trend": self._calculate_satisfaction_trend(
                        call_history
                    ),
                }
            )
        else:
            context.update(
                {
                    "last_call_summary": "No previous calls on record",
                    "last_call_successful": "N/A",
                    "last_call_sentiment": "N/A",
                    "previous_issues": "None on record",
                    "customer_satisfaction_trend": "New customer",
                }
            )

        return context

    def store_call_result(self, call_data: Dict[str, Any]):
        """Store call results for future reference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Extract phone number based on call direction
        if call_data.get("direction") == "inbound":
            customer_phone = call_data.get("from_number")
        else:
            customer_phone = call_data.get("to_number")

        if not customer_phone:
            return

        # Update or insert customer
        dynamic_vars = call_data.get("retell_llm_dynamic_variables", {})
        customer_name = dynamic_vars.get("customer_name", "Unknown")
        account_type = dynamic_vars.get("account_type", "Standard")
        priority_level = dynamic_vars.get("priority_level", "Normal")

        cursor.execute(
            """
            INSERT OR REPLACE INTO customers 
            (phone_number, name, account_type, priority_level, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                customer_phone,
                customer_name,
                account_type,
                priority_level,
                datetime.now(),
            ),
        )

        # Store call history
        call_analysis = call_data.get("call_analysis", {})
        extracted_vars = json.dumps(call_data.get("collected_dynamic_variables", {}))

        cursor.execute(
            """
            INSERT OR REPLACE INTO call_history 
            (call_id, customer_phone, agent_id, call_type, direction,
             start_timestamp, end_timestamp, duration_ms, call_summary,
             call_successful, user_sentiment, disconnection_reason,
             extracted_variables)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                call_data.get("call_id"),
                customer_phone,
                call_data.get("agent_id"),
                call_data.get("call_type"),
                call_data.get("direction"),
                call_data.get("start_timestamp"),
                call_data.get("end_timestamp"),
                call_data.get("duration_ms"),
                call_analysis.get("call_summary"),
                call_analysis.get("call_successful"),
                call_analysis.get("user_sentiment"),
                call_data.get("disconnection_reason"),
                extracted_vars,
            ),
        )

        conn.commit()
        conn.close()

    def _extract_common_issues(self, call_history: List) -> str:
        """Extract common issues from call history"""
        issues = []
        for call in call_history:
            if call[4]:  # extracted_variables
                try:
                    vars_dict = json.loads(call[4])
                    if "issue_category" in vars_dict:
                        issues.append(vars_dict["issue_category"])
                except:
                    pass

        if issues:
            return f"Common issues: {', '.join(set(issues))}"
        return "No specific issues identified"

    def _calculate_satisfaction_trend(self, call_history: List) -> str:
        """Calculate customer satisfaction trend"""
        sentiments = [call[2] for call in call_history if call[2]]
        if not sentiments:
            return "No sentiment data"

        positive_count = sum(1 for s in sentiments if s == "Positive")
        total_count = len(sentiments)

        if positive_count / total_count > 0.7:
            return "Generally satisfied"
        elif positive_count / total_count > 0.4:
            return "Mixed satisfaction"
        else:
            return "Needs attention"


# ✅ NEW: Webhook Handler Class
class WebhookHandler:
    def __init__(self, history_manager: CallHistoryManager):
        self.history_manager = history_manager
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        """Setup Flask routes for webhooks"""

        @self.app.route("/inbound-webhook", methods=["POST"])
        def handle_inbound_call():
            """Handle inbound call webhook with history injection"""
            data = request.json
            caller_number = data["call_inbound"]["from_number"]

            # Get customer history and context
            customer_context = self.history_manager.get_customer_context(caller_number)

            return jsonify(
                {
                    "call_inbound": {
                        "override_agent_id": "your_agent_id_here",  # Will be set dynamically
                        "dynamic_variables": customer_context,
                    }
                }
            )

        @self.app.route("/call-webhook", methods=["POST"])
        def handle_call_webhook():
            """Handle call completion webhook to store results"""
            data = request.json

            if data.get("event") == "call_ended":
                self.history_manager.store_call_result(data["call"])
            elif data.get("event") == "call_analyzed":
                # Update with analysis results
                self.history_manager.store_call_result(data["call"])

            return jsonify({"status": "success"})

    def run(self, host="0.0.0.0", port=8080):
        """Run the webhook server"""
        self.app.run(host=host, port=port)


# ✅ NEW: Agent Manager Class
class RetellAgentManager:
    def __init__(self, api_key: str, history_manager: CallHistoryManager):
        self.client = Retell(api_key=api_key)
        self.history_manager = history_manager
        self.agent_id = None
        self.llm_id = None
        self.phone_number = None

    def create_llm_with_history_support(self):
        """Create LLM with history-aware prompt and dynamic variables"""

        # ✅ UPDATED: Enhanced prompt with comprehensive history variables
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
1. **Acknowledge History**: "Hello {{customer_name}}! I see this is your {{total_previous_calls}} call with us."
2. **Reference Last Interaction**: "I noticed from our last conversation that {{last_call_summary}}. How did that work out?"
3. **Follow Up on Issues**: If previous_issues != "None on record", ask: "I see you've had {{previous_issues}} before. Is this related?"
4. **Acknowledge Sentiment**: If last_call_sentiment was negative, say: "I want to make sure we address any concerns from last time."

### For New Customers (total_previous_calls = 0):
1. **Welcome**: "Hello {{customer_name}}! Welcome to {{company_name}}. I'm {{agent_name}}."
2. **Set Expectations**: "As a {{account_type}} customer, I'm here to provide you with excellent service."

## Conversation Flow
1. Greet with history awareness
2. Address any follow-up items from previous calls
3. Listen to current needs
4. Provide solutions while referencing past preferences
5. Use appropriate tools based on customer history and current needs
6. End with personalized closing

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
            # ✅ UPDATED: History-aware begin message
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
                {
                    "type": "book_appointment_cal",
                    "name": "book_appointment",
                    "description": "Book appointment for {{customer_name}}. Reference any previous appointment preferences from history.",
                    "cal_api_key": "cal_live_your_api_key_here",
                    "event_type_id": 12345,
                    "timezone": "America/New_York",
                },
                # ✅ UPDATED: Enhanced extract tool for better history tracking
                {
                    "type": "extract_dynamic_variables",
                    "name": "extract_customer_info",
                    "description": "Extract and store customer information for future call history and personalization",
                    "variables": [
                        {
                            "name": "customer_phone",
                            "description": "Customer's phone number",
                            "type": "text",
                        },
                        {
                            "name": "customer_email",
                            "description": "Customer's email address",
                            "type": "text",
                        },
                        {
                            "name": "issue_category",
                            "description": "Primary category of customer's issue or inquiry",
                            "type": "enum",
                            "enum_options": [
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
                            "enum_options": [
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
                            "enum_options": ["phone", "email", "text", "no_preference"],
                        },
                    ],
                },
            ],
            # ✅ UPDATED: Comprehensive default variables
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
        print(f"✅ Created history-aware LLM: {self.llm_id}")
        return llm_response

    def create_agent_with_history_support(self):
        """Create agent with history-aware configuration"""
        if not self.llm_id:
            raise ValueError("LLM must be created first")

        agent_response = self.client.agent.create(
            agent_name="Acme Customer Service Agent with History",
            voice_id="11labs-Adrian",
            voice_model="eleven_turbo_v2",
            voice_temperature=0.8,
            voice_speed=1.0,
            responsiveness=0.8,
            interruption_sensitivity=0.5,
            enable_backchannel=True,
            language="en-US",
            response_engine={"type": "retell-llm", "llm_id": self.llm_id},
            # ✅ UPDATED: Webhook URL for call history tracking
            webhook_url="https://your-domain.com/call-webhook",
            boosted_keywords=["Acme", "appointment", "support", "history", "previous"],
            end_call_after_silence_ms=30000,
            max_call_duration_ms=1800000,
            # ✅ UPDATED: Enhanced post-call analysis for better history tracking
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
        print(f"✅ Created history-aware agent: {self.agent_id}")
        return agent_response

    def create_phone_number_with_history_webhook(self):
        """Create phone number with inbound webhook for history injection"""
        phone_response = self.client.phone_number.create(
            area_code=415,
            inbound_agent_id=self.agent_id,
            outbound_agent_id=self.agent_id,
            nickname="Acme Customer Service with History",
            # ✅ NEW: Inbound webhook for history injection
            inbound_webhook_url="https://your-domain.com/inbound-webhook",
        )

        self.phone_number = phone_response.phone_number
        print(f"✅ Created phone number with history webhook: {self.phone_number}")
        return phone_response

    def make_call_with_history(self, to_number: str, customer_phone: str = None):
        """Make outbound call with customer history context"""
        # Use customer_phone or to_number to look up history
        lookup_number = customer_phone or to_number
        customer_context = self.history_manager.get_customer_context(lookup_number)

        call_response = self.client.call.create_phone_call(
            from_number=self.phone_number,
            to_number=to_number,
            override_agent_id=self.agent_id,
            metadata={
                "call_type": "outbound_with_history",
                "customer_lookup": lookup_number,
            },
            # ✅ UPDATED: Pass comprehensive history context
            retell_llm_dynamic_variables=customer_context,
        )

        print(f"✅ Initiated call with history context: {call_response.call_id}")
        return call_response


# ✅ MAIN EXECUTION: Complete setup with history support
def main():
    """Main function to set up complete system with call history"""

    # Initialize components
    print("🚀 Setting up Retell AI system with call history support...")

    # ✅ NEW: Initialize call history manager
    history_manager = CallHistoryManager()
    print("✅ Call history database initialized")

    # ✅ NEW: Initialize webhook handler
    webhook_handler = WebhookHandler(history_manager)
    print("✅ Webhook handler configured")

    # ✅ NEW: Initialize agent manager with history support
    agent_manager = RetellAgentManager(
        api_key="YOUR_RETELL_API_KEY", history_manager=history_manager
    )

    # Create LLM with history awareness
    llm_response = agent_manager.create_llm_with_history_support()

    # Create agent with history support
    agent_response = agent_manager.create_agent_with_history_support()

    # Create phone number with history webhook
    phone_response = agent_manager.create_phone_number_with_history_webhook()

    # ✅ NEW: Test with simulated customer history
    print("\n📞 Testing with customer history...")

    # Simulate existing customer with history
    test_customer_phone = "+12125551234"

    # Add some test history
    test_call_data = {
        "call_id": "test_call_123",
        "direction": "inbound",
        "from_number": test_customer_phone,
        "agent_id": agent_manager.agent_id,
        "call_type": "phone_call",
        "start_timestamp": 1703302407333,
        "end_timestamp": 1703302428855,
        "duration_ms": 21522,
        "retell_llm_dynamic_variables": {
            "customer_name": "John Smith",
            "account_type": "Premium",
            "priority_level": "High",
        },
        "call_analysis": {
            "call_summary": "Customer called about billing discrepancy, resolved payment issue",
            "call_successful": True,
            "user_sentiment": "Positive",
        },
        "disconnection_reason": "user_hangup",
        "collected_dynamic_variables": {
            "issue_category": "billing",
            "resolution_status": "resolved",
            "customer_satisfaction": "9",
        },
    }

    history_manager.store_call_result(test_call_data)
    print("✅ Test customer history added")

    # Make a call with history context
    call_response = agent_manager.make_call_with_history(
        to_number=test_customer_phone, customer_phone=test_customer_phone
    )

    # Create web call with history
    customer_context = history_manager.get_customer_context(test_customer_phone)
    web_call_response = agent_manager.client.call.create_web_call(
        agent_id=agent_manager.agent_id,
        metadata={
            "test_type": "web_call_with_history",
            "customer_phone": test_customer_phone,
        },
        retell_llm_dynamic_variables=customer_context,
    )

    print("\n🎉 Setup Complete with Call History Support!")
    print("=" * 60)
    print(f"Agent ID: {agent_manager.agent_id}")
    print(f"LLM ID: {agent_manager.llm_id}")
    print(f"Phone Number: {agent_manager.phone_number}")
    print(f"Test Call ID: {call_response.call_id}")
    print(f"Web Call ID: {web_call_response.call_id}")
    print(f"Web Call Access Token: {web_call_response.access_token}")
    print("=" * 60)

    print("\n📋 Next Steps:")
    print("1. Update webhook URLs with your actual domain")
    print("2. Run webhook server: webhook_handler.run()")
    print("3. Test inbound calls - they'll automatically get customer history")
    print("4. All call results will be stored for future reference")
    print("5. Each subsequent call will have full context of previous interactions")

    return {
        "history_manager": history_manager,
        "webhook_handler": webhook_handler,
        "agent_manager": agent_manager,
        "agent_id": agent_manager.agent_id,
        "phone_number": agent_manager.phone_number,
    }


if __name__ == "__main__":
    # Run the complete setup
    system_components = main()

    # Optionally start webhook server
    # system_components["webhook_handler"].run()


"""
## 🔥 **Key Changes Made:**

### ✅ **1. CallHistoryManager Class**
- **SQLite database** for persistent call history storage
- **Customer context retrieval** with comprehensive history
- **Call result storage** after each interaction
- **Satisfaction trend analysis** and common issue tracking

### ✅ **2. WebhookHandler Class**
- **Inbound webhook** that injects customer history automatically
- **Call completion webhook** that stores results for future use
- **Flask server** for handling webhook requests

### ✅ **3. Enhanced Prompt with History Variables**
- **History-aware conversation flow** based on previous interactions
- **Dynamic responses** based on customer satisfaction trends
- **Personalized greetings** for returning vs new customers
- **Follow-up capabilities** on previous issues

### ✅ **4. Comprehensive Dynamic Variables**
- **12+ history variables** including call count, summaries, sentiment
- **Customer satisfaction trends** and issue patterns
- **Account-specific context** (Premium, Enterprise, etc.)

### ✅ **5. Enhanced Function Calls**
- **Extract customer info tool** captures data for future calls
- **History-aware tool descriptions** reference previous interactions
- **Better post-call analysis** for richer history storage

### ✅ **6. Complete Integration**
- **Automatic history injection** for inbound calls
- **History-aware outbound calls** with customer context
- **Persistent storage** of all interactions
- **Trend analysis** and satisfaction tracking

## 🎯 **How Call History Works:**

1. **First Call**: Customer gets standard greeting, info stored in database
2. **Subsequent Calls**: Agent automatically knows previous interactions
3. **Inbound Calls**: Webhook injects history before call connects
4. **Outbound Calls**: History retrieved and passed as dynamic variables
5. **Post-Call**: Results stored for next interaction

The system now provides **complete call history awareness** with personalized, continuous customer service across all interactions!

```suggestions
(Dynamic Variables Guide)[/build/dynamic-variables]
(Inbound Call Webhook)[/features/inbound-call-webhook]
(Webhook Overview)[/features/webhook-overview]
```

"""
