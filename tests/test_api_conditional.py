"""Quick API test for the conditional expressions."""

import pytest
import requests
import json


@pytest.mark.skip(reason="Requires server running. Run manually with: python start.py")
def test_api_conditional():
    """Test the API with conditional expressions."""
    url = "http://localhost:8000/api/v1/transform"

    # Test case 1: if-else with array
    payload = {
        "input_json": {"foo": {"bar": [1, 2, 3, 4, 5]}},
        "jslt_expression": """if (.foo.bar)
    {
        "array" : [for (.foo.bar) string(.)],
        "size"  : size(.foo.bar)
    }
else
    "No array today"
""",
    }

    print("Testing API with conditional expression...")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload)
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("\n✓ API Test PASSED!")
            else:
                print(f"\n❌ Transform failed: {data.get('error')}")
        else:
            print(f"\n❌ API request failed with status {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("\n⚠ Server is not running. Start it with: python start.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
