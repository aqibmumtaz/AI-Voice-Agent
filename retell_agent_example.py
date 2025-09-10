from retell import Retell

from configs import Configs

# Initialize the Retell client
client = Retell(
    api_key=Configs.RETELL_API_KEY,
)

# Step 1: Create a Retell LLM with dynamic variables in prompt
llm_response = client.llm.create(
    model="gpt-4o",
    model_temperature=0.7,
    # ✅ UPDATED: Prompt now includes dynamic variable placeholders
    general_prompt="""You are a helpful customer service assistant for {{company_name}}.

## Identity
You are professional, friendly, and knowledgeable about our products and services.
Your name is {{agent_name}} and you're speaking with {{customer_name}}.

## Customer Context
- Customer Name: {{customer_name}}
- Account Type: {{account_type}}
- Priority Level: {{priority_level}}
- Previous Issue: {{previous_issue}}

## Style Guidelines  
- Address the customer by name: "Hello {{customer_name}}"
- Be concise and clear in your responses
- Ask one question at a time
- Always confirm important details with the customer
- Use a warm, conversational tone
- Business hours are {{business_hours}}

## Tasks
1. Greet {{customer_name}} personally and acknowledge their {{account_type}} status
2. Help customers with product inquiries
3. Schedule appointments when requested
4. Transfer to human support for complex issues
5. End calls politely when conversation is complete

## Function Usage
- Use 'book_appointment' when {{customer_name}} wants to schedule a meeting
- Use 'transfer_call' for issues requiring human assistance
- Use 'end_call' when {{customer_name}} indicates they're done
- Use 'extract_customer_info' to capture additional customer details during the call""",
    # ✅ UPDATED: Begin message with dynamic variables
    begin_message="Hello {{customer_name}}! Thank you for calling {{company_name}}. I'm {{agent_name}}, and I see you're one of our {{account_type}} customers. How can I assist you today?",
    general_tools=[
        {
            "type": "end_call",
            "name": "end_call",
            "description": "End the call when the conversation is complete or customer requests to hang up.",
        },
        {
            "type": "transfer_call",
            "name": "transfer_to_support",
            "description": "Transfer the call to human support for complex issues that require human assistance.",
            "transfer_destination": {"type": "predefined", "number": "+14155551234"},
            "transfer_option": {
                "type": "warm_transfer",
                "show_transferee_as_caller": True,
            },
        },
        {
            "type": "book_appointment_cal",
            "name": "book_appointment",
            "description": "Book an appointment for {{customer_name}} when they request scheduling.",
            "cal_api_key": "cal_live_your_api_key_here",
            "event_type_id": 12345,
            "timezone": "America/New_York",
        },
        # ✅ NEW: Extract dynamic variables tool
        {
            "type": "extract_dynamic_variables",
            "name": "extract_customer_info",
            "description": "Extract and store customer information during the conversation",
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
                    "description": "Category of customer's issue",
                    "type": "enum",
                    "enum_options": ["billing", "technical", "general", "complaint"],
                },
                {
                    "name": "satisfaction_score",
                    "description": "Customer satisfaction rating from 1-10",
                    "type": "number",
                },
            ],
        },
    ],
    # ✅ UPDATED: Default dynamic variables with more comprehensive data
    default_dynamic_variables={
        "company_name": "Acme Company",
        "agent_name": "Sarah",
        "customer_name": "Valued Customer",
        "account_type": "Standard",
        "priority_level": "Normal",
        "business_hours": "9 AM to 5 PM EST",
        "previous_issue": "None on record",
    },
)

print(f"Created LLM with ID: {llm_response.llm_id}")

# Step 2: Create an agent using the LLM
agent_response = client.agent.create(
    agent_name="Acme Customer Service Agent",
    voice_id="11labs-Adrian",
    voice_model="eleven_turbo_v2",
    voice_temperature=0.8,
    voice_speed=1.0,
    responsiveness=0.8,
    interruption_sensitivity=0.5,
    enable_backchannel=True,
    language="en-US",
    response_engine={"type": "retell-llm", "llm_id": llm_response.llm_id},
    webhook_url="https://your-domain.com/webhook",
    boosted_keywords=["Acme", "appointment", "support"],
    end_call_after_silence_ms=30000,
    max_call_duration_ms=1800000,
    post_call_analysis_data=[
        {
            "type": "string",
            "name": "customer_satisfaction",
            "description": "Rate customer satisfaction from 1-10 based on the conversation",
            "examples": ["8", "9", "10"],
        },
        {
            "type": "boolean",
            "name": "issue_resolved",
            "description": "Whether the customer's issue was resolved",
            "examples": [True, False],
        },
    ],
)

print(f"Created Agent with ID: {agent_response.agent_id}")

# Step 3: Create a phone number and bind the agent
phone_response = client.phone_number.create(
    area_code=415,
    inbound_agent_id=agent_response.agent_id,
    outbound_agent_id=agent_response.agent_id,
    nickname="Acme Customer Service Line",
)

print(f"Phone number created: {phone_response.phone_number}")

# Step 4: Make a test outbound call with dynamic variables
call_response = client.call.create_phone_call(
    from_number=phone_response.phone_number,
    to_number="+12125551234",
    override_agent_id=agent_response.agent_id,
    metadata={"test_call": True, "purpose": "agent_testing"},
    # ✅ UPDATED: Comprehensive dynamic variables for personalization
    retell_llm_dynamic_variables={
        "customer_name": "John Smith",
        "account_type": "Premium",
        "priority_level": "High",
        "agent_name": "Sarah Johnson",
        "company_name": "Acme Corporation",
        "business_hours": "24/7 for Premium customers",
        "previous_issue": "Billing inquiry resolved last week",
    },
)

print(f"Test call initiated: {call_response.call_id}")

# Step 5: Create a web call with different dynamic variables
web_call_response = client.call.create_web_call(
    agent_id=agent_response.agent_id,
    metadata={"test_type": "web_call", "environment": "development"},
    # ✅ UPDATED: Different dynamic variables for web call
    retell_llm_dynamic_variables={
        "customer_name": "Jane Doe",
        "account_type": "Enterprise",
        "priority_level": "Critical",
        "agent_name": "Michael Chen",
        "company_name": "Acme Solutions",
        "business_hours": "24/7 Enterprise Support",
        "previous_issue": "Technical integration support needed",
    },
)

print(f"Web call created: {web_call_response.call_id}")
print(f"Access token: {web_call_response.access_token}")

print("\n=== Setup Complete ===")
print(f"Agent ID: {agent_response.agent_id}")
print(f"LLM ID: {llm_response.llm_id}")
print(f"Phone Number: {phone_response.phone_number}")
print(f"Web Call Access Token: {web_call_response.access_token}")


# ## Key Changes Highlighted:

# ### ✅ **1. Dynamic Variables in Prompt**
# - Added `{{customer_name}}`, `{{company_name}}`, `{{account_type}}`, etc. throughout the prompt
# - Created a "Customer Context" section that displays dynamic variables
# - Personalized greetings and instructions using variables

# ### ✅ **2. Enhanced Begin Message**
# - Uses `{{customer_name}}`, `{{company_name}}`, `{{agent_name}}`, and `{{account_type}}`
# - Creates personalized greeting for each call

# ### ✅ **3. Comprehensive Default Variables**
# - Added `agent_name`, `account_type`, `priority_level`, `previous_issue`
# - Provides fallback values when specific variables aren't passed

# ### ✅ **4. Extract Dynamic Variables Tool**
# - Added tool to capture customer information during calls
# - Stores phone, email, issue category, and satisfaction score
# - Variables can be referenced later in the conversation

# ### ✅ **5. Call-Specific Dynamic Variables**
# - Phone call uses Premium customer variables
# - Web call uses Enterprise customer variables
# - Each call gets personalized context

# The agent now properly handles dynamic variables throughout the conversation, personalizing responses based on customer data passed at call creation time.

# ```suggestions
# (Dynamic Variables Guide)[/build/dynamic-variables]
# (Create Retell LLM API)[/api-references/create-retell-llm]
# (Create Phone Call API)[/api-references/create-phone-call]
# ```
