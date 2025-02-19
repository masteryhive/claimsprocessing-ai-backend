import pytest
from langchain_core.messages import HumanMessage
from src.teams.stirring_agent import super_graph, members
from src.models.claim_processing import UpdateClaimsReportModel
from src.database.schemas import Task, TaskStatus
from src.workflow_orch.manager import database_session

@pytest.fixture(autouse=True)
def mock_vertexai(monkeypatch):
    """Mock VertexAI responses"""
    def mock_response(*args, **kwargs):
        # Return a string response that matches the expected JSON format
        return """
        {
            "claim_form_screening": {
                "status": "VALID",
                "findings": "All required fields are present and properly filled.",
                "recommendations": "Proceed with claim processing"
            },
            "policy_review": {
                "status": "VALID",
                "findings": "Policy is active and covers the claimed damages",
                "recommendations": "Claim is within policy coverage"
            },
            "fraud_detection": {
                "risk_level": "LOW",
                "findings": "No suspicious patterns detected",
                "recommendations": "Process claim normally"
            },
            "settlement_offer": {
                "recommended_amount": 500000,
                "justification": "Based on provided evidence and policy terms",
                "recommendations": "Proceed with settlement"
            }
        }
        """
    
    monkeypatch.setattr("src.ai_models.model.init_vertexai", lambda: None)
    monkeypatch.setattr("langchain_google_vertexai.ChatVertexAI.invoke", mock_response)

@pytest.fixture(autouse=True)
def clean_database():
    """Clean up database before each test"""
    with database_session() as db:
        db.query(Task).delete()
        db.commit()

def create_test_claim():
    """Creates a test claim using the example from the codebase"""
    return {
        "id": 85,
        "nameOfInsured": "Ayo Samuel",
        "policyNumber": "ZG/P/1000/010101/22/000346",
        "addressOfInsured": "plot 23, colegeorge estate, college road, ogba Ikeja",
        "phoneNumberOfInsured": "+2348012675443",
        "declaration": True,
        "signature": "Ayo Samuel",
        "status": "Examining claim form",
        "signatureDate": "December 19 2024",
        "extentOfLossOrDamage": [
            {"item": "Driver side mirror", "costPrice": 1200000, "amountClaimed": 700000},
            {
                "item": "Partial Paint Job (oven baked)",
                "costPrice": 80000,
                "amountClaimed": 600000,
            },
            {"item": "Driver side door handle", "costPrice": 90000, "amountClaimed": 90000},
        ],
        "particularsAddress": "not provided",
        "particularsPhoneNo": "not provided",
        "personInCharge": "Ayo Samuel",
        "addressOfPersonInCharge": "plot 23, colegeorge estate, college road, ogba Ikeja",
        "permissionConfirmation": "Yes",
        "otherInsuranceConfirmation": "No",
        "purposeOfUse": "Personal use",
        "durationOfOwnership": "2 years",
        "previousOwner": "SKymit motors",
        "servicedBy": "A+ mechanics",
        "lastServiceDate": "December 19 2024",
        "totalMileage": "1001043",
        "vehicleMake": "Hyundai",
        "claimType": "accident",
        "registrationNumber": "LND 242 JC",
        "claimantName": "Ayo Samuel",
        "vehicleCC": "not provided",
        "vehicleColor": "Blue",
        "typeOfBody": "SUV",
        "yearOfManufacture": "2019",
        "chassisNumber": "KMD4567483993JJ",
        "engineNumber": "not provided",
        "evidenceProvided": [
            "This image presents compelling visual documentation of damage to a vehicle, specifically a blue car, and can therefore serve as valid evidence for a vehicle insurance claim. The photograph clearly shows substantial damage to the driver's side. The driver's side door exhibits significant deformation and denting, suggesting a forceful impact. The side mirror is also damaged and appears to be partially detached from the vehicle. The front fender, adjacent to the driver's side door, also displays noticeable crumpling and damage. This collection of damage points to a collision or impact event affecting the front left quadrant of the car. The extent of the damage visible in the image warrants an insurance claim.\n",
            'This document is an **invoice** from Timothy Auto Shop. It likely serves as evidence for a vehicle insurance claim for repairs necessitated by an incident that damaged the driver\'s side and trunk of the vehicle.\n\n**Items:**\n\n* **Partial oven baked painting for the driver side to the trunk (Labour):** ₦32,000 (4 x ₦8,000)\n* **Parts:** ₦265,000 (Not itemized)\n\n**Total Price:**\n\n* **Total:** ₦300,000\n\n**Narration:**\n\nThere isn\'t a specific descriptive narration beyond the item description "Partial oven baked painting for the driver side to the trunk." This indicates the repair work performed.\n\n**Purpose:**\n\nThe purpose of this invoice is to bill the customer (or their insurance company) for the repairs completed on their vehicle. It serves as a record of the services provided, the costs associated with those services, and the payment terms. In the context of an insurance claim, it provides evidence of the cost of repairs to justify the claim amount.'
        ],
        "dateClaimFiled": "December 6 2024"
    }

@pytest.fixture(autouse=True)
def mock_yaml_load(monkeypatch):
    """Mock YAML file loading for tests"""
    def mock_load_yaml_file(file_path):
        # Mock prompt templates for different teams
        mock_templates = {
            "src/teams/policy_review/prompts/instruction.yaml": {
                "STIRRINGAGENTSYSTEMPROMPT": "Test system prompt",
                "INSURANCE_CLAIM_POLICY_DATA": "Test policy data prompt",
                "PERIOD_VERIFICATION": "Test period verification prompt",
                "POLICY_VERIFICATION": "Test policy verification prompt",
                "PROCESS_CLERK_PROMPT": "Test clerk prompt"
            },
            "src/teams/document_processing/prompts/instruction.yaml": {
                "STIRRINGAGENTSYSTEMPROMPT": "Test system prompt",
                "CLAIMS_DOCUMENT_VERIFIER_AGENT_SYSTEM_PROMPT": "Test doc verifier prompt",
                "SUPPORTING_DOCUMENT_VERIFIER_AGENT_SYSTEM_PROMPT": "Test support doc prompt",
                "PROCESS_CLERK_PROMPT": "Test clerk prompt"
            },
            "src/teams/fraud_detection/prompts/instruction.yaml": {
                "STIRRINGAGENTSYSTEMPROMPT": "Test system prompt",
                "CLAIMS_FORM_FRAUD_INVESTIGATOR_AGENT_SYSTEM_PROMPT": "Test fraud investigator prompt",
                "VEHICLE_FRAUD_INVESTIGATOR_AGENT_SYSTEM_PROMPT": "Test vehicle fraud prompt",
                "DAMAGE_COST_FRAUD_INVESTIGATOR_AGENT_SYSTEM_PROMPT": "Test damage cost prompt",
                "FRAUD_RISK_AGENT_SYSTEM_PROMPT": "Test risk agent prompt",
                "PROCESS_CLERK_PROMPT": "Test clerk prompt"
            },
            "src/teams/settlement_offer/prompts/instruction.yaml": {
                "STIRRINGAGENTSYSTEMPROMPT": "Test system prompt",
                "OFFER_ANALYST_AGENT_SYSTEM_PROMPT": "Test offer analyst prompt",
                "PROCESS_CLERK_PROMPT": "Test clerk prompt"
            },
            "src/teams/report/prompts/instruction.yaml": {
                "STIRRINGAGENTSYSTEMPROMPT": "Test system prompt",
                "CLAIM_ADJUSTER_SUMMARY_PROMPT": "Test summary prompt"
            }
        }
        
        # Return mock data based on file path
        if file_path in mock_templates:
            return mock_templates[file_path]
        return {}  # Return empty dict for unknown paths
    
    # Replace the real load_yaml_file function with our mock
    monkeypatch.setattr("src.utilities.helpers.load_yaml_file", mock_load_yaml_file)

@pytest.fixture
def test_state():
    claim_data = create_test_claim()
    return {
        "messages": [
            HumanMessage(
                content=(
                    "Important information:"
                    "\nThis service is currently run in Nigeria, this means:"
                    "\n1. The currency is ₦"
                    f"\n\nBegin this claim processing using this claim form JSON data:\n {claim_data}"
                    "\n\nYOU MUST USE THE SUMMARY TEAM TO PRESENT THE RESULT OF THIS TASK."
                )
            )
        ],
        "claim_form_json": [HumanMessage(content=str(claim_data))],
        "agent_history": []
    }

def test_workflow_execution(test_state):
    """Test the complete workflow execution"""
    team_summaries = []
    
    # Stream through the workflow
    for step in super_graph.stream(test_state):
        if "__end__" not in step:
            # Store each team's response
            if "messages" in step:
                messages = [m.content for m in step["messages"] if isinstance(m, HumanMessage)]
                if messages:
                    team_summaries.append({
                        "step": len(team_summaries) + 1,
                        "team": members[len(team_summaries)],
                        "response": messages[0]
                    })
    
    # Verify each team's participation
    assert len(team_summaries) >= len(members), "Not all teams participated"
    
    # Verify team order
    for idx, summary in enumerate(team_summaries[:len(members)]):
        assert summary["team"] == members[idx], f"Incorrect team order: expected {members[idx]}, got {summary['team']}"
        
    # Verify responses are not empty
    for summary in team_summaries:
        assert summary["response"], f"Empty response from {summary['team']}"

def test_document_processing_team(test_state):
    """Test document processing team specifically"""
    from src.teams.document_processing.agents import document_check_graph
    
    result = None
    for step in document_check_graph.stream(test_state):
        if "messages" in step:
            result = step
    
    assert result is not None
    assert "messages" in result
    messages = [m.content for m in result["messages"] if isinstance(m, HumanMessage)]
    assert any(messages), "Document processing team should provide a response"
    # Add specific assertions about the document processing response content

def test_policy_review_team(test_state):
    """Test policy review team specifically"""
    from src.teams.policy_review.agents import policy_review_graph
    
    result = None
    for step in policy_review_graph.stream(test_state):
        if "messages" in step:
            result = step
    
    assert result is not None
    assert "messages" in result
    messages = [m.content for m in result["messages"] if isinstance(m, HumanMessage)]
    assert any(messages), "Policy review team should provide a response"
    # Add specific assertions about the policy review response content

def test_fraud_detection_team(test_state):
    """Test fraud detection team specifically"""
    from src.teams.fraud_detection.agents import fraud_detection_graph
    
    result = None
    for step in fraud_detection_graph.stream(test_state):
        if "messages" in step:
            result = step
    
    assert result is not None
    assert "messages" in result
    messages = [m.content for m in result["messages"] if isinstance(m, HumanMessage)]
    assert any(messages), "Fraud detection team should provide a response"
    # Add specific assertions about the fraud detection response content

def test_settlement_offer_team(test_state):
    """Test settlement offer team specifically"""
    from src.teams.settlement_offer.agents import settlement_offer_graph
    
    result = None
    for step in settlement_offer_graph.stream(test_state):
        if "messages" in step:
            result = step
    
    assert result is not None
    assert "messages" in result
    messages = [m.content for m in result["messages"] if isinstance(m, HumanMessage)]
    assert any(messages), "Settlement offer team should provide a response"
    # Add specific assertions about the settlement offer response content

def test_error_handling():
    """Test workflow error handling"""
    bad_state = {
        "messages": [HumanMessage(content="Invalid data")],
        "claim_form_json": [HumanMessage(content="Invalid JSON")],
        "agent_history": []
    }
    
    try:
        for step in super_graph.stream(bad_state):
            pass
        assert False, "Should have raised an exception"
    except Exception as e:
        assert str(e), "Error should have a message"

@pytest.mark.integration
def test_database_integration():
    """Test workflow database integration"""
    with database_session() as db:
        # Create test claim in database
        claim_data = create_test_claim()
        test_task = Task(
            claim_id=str(claim_data["id"]),  # Convert to string since that's what the schema expects
            status=TaskStatus.PENDING
        )
        db.add(test_task)
        db.commit()
        
        # Run workflow
        test_state = {
            "messages": [HumanMessage(content=str(claim_data))],
            "claim_form_json": [HumanMessage(content=str(claim_data))],
            "agent_history": []
        }
        
        for step in super_graph.stream(test_state):
            if "__end__" not in step:
                continue
        
        # Verify database updates
        updated_task = db.query(Task).filter_by(
            claim_id=str(claim_data["id"])
        ).first()
        assert updated_task is not None
        assert updated_task.status is not None 