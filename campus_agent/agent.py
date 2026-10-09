import json
from pathlib import Path

from google.adk.agents.llm_agent import Agent

# The data file lives in the same folder as agent.py.
# Using Path(__file__).parent means the code still works even if the
# agent folder is moved to a different location.
RESOURCE_FILE = Path(__file__).parent / "campus_resources.json"


def get_campus_resource_info(resource_name: str) -> dict:
    """Looks up hours, location, and contact information for a campus resource.

    Use this tool whenever someone asks about a campus service or facility,
    such as the library, tutoring center, advising office, financial aid,
    or another campus resource.

    Args:
        resource_name: The campus resource to look up. Examples include
            "library", "tutoring", "advising", or "financial aid".
            You can also pass "all" or "list" to see every available resource.

    Returns:
        A dictionary with the resource's location, hours, phone, email,
        website, description, verification information, and a status field.
        If the resource cannot be found, status is "error" and the
        dictionary contains an error_message with the available resources.
    """
    data = json.loads(RESOURCE_FILE.read_text())
    query = resource_name.lower().strip()

    # Special case: the model may ask to list everything available.
    if query in ("all", "list", "everything"):
        return {
            "status": "success",
            "available_resources": [r["name"] for r in data["resources"]],
        }

    # Match the query against the official name and any aliases.
    for resource in data["resources"]:
        names = [resource["name"].lower()]
        names.extend(alias.lower() for alias in resource.get("aliases", []))
        if query in names:
            return {"status": "success", **resource}

    # If no match is found, tell the truth instead of inventing data.
    available = ", ".join(r["name"] for r in data["resources"])
    return {
        "status": "error",
        "error_message": (
            f"No information was found for '{resource_name}'. "
            f"Available resources: {available}."
        ),
    }


root_agent = Agent(
    model="gemini-flash-latest",
    name="campus_resource_agent",
    description="Answers questions about college campus resources.",
    instruction=(
        "You are the Campus Resource Assistant for a community college. "
        "You help students, staff, and visitors find accurate information "
        "about campus resources such as the library, tutoring center, "
        "advising office, and financial aid office. "
        "Whenever a user asks about a campus resource, call the "
        "get_campus_resource_info tool first. Do not answer from memory. "
        "If the tool returns status 'error', do not invent information. "
        "Explain that the resource was not found and tell the user which "
        "resources are available based on the error_message. "
        "If a question is not about campus resources, kindly explain that "
        "you can only help with campus resource questions."
    ),
    tools=[get_campus_resource_info],
)