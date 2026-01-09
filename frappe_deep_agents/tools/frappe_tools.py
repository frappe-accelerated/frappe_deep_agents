"""
Frappe-specific tools for querying and manipulating DocTypes.
"""
from typing import Optional, Any
from langchain.tools import BaseTool
from pydantic import Field
import frappe
import json


class FrappeQueryTool(BaseTool):
    """
    Query Frappe DocTypes using filters.

    Allows agents to search and retrieve data from Frappe's database.
    """
    name: str = "frappe_query"
    description: str = """Query Frappe DocTypes to retrieve data.

Use this tool to search for documents in the Frappe database.

Input format (JSON):
{
    "doctype": "DocType Name",
    "filters": {"field": "value"},  // optional
    "fields": ["field1", "field2"],  // optional, defaults to ["name"]
    "limit": 20,  // optional, defaults to 20
    "order_by": "creation desc"  // optional
}

Examples:
- Get all Users: {"doctype": "User", "fields": ["name", "email", "full_name"]}
- Find specific item: {"doctype": "Item", "filters": {"item_code": "ITEM-001"}}
- Search by pattern: {"doctype": "Customer", "filters": {"customer_name": ["like", "%John%"]}}
"""

    session_id: Optional[str] = Field(default=None, exclude=True)

    def _run(self, query: str) -> str:
        """Execute the Frappe query."""
        try:
            # Parse input
            if isinstance(query, str):
                params = json.loads(query)
            else:
                params = query

            doctype = params.get("doctype")
            if not doctype:
                return "Error: 'doctype' is required"

            # Check if doctype exists
            if not frappe.db.exists("DocType", doctype):
                return f"Error: DocType '{doctype}' does not exist"

            # Build query
            filters = params.get("filters", {})
            fields = params.get("fields", ["name"])
            limit = min(params.get("limit", 20), 100)  # Cap at 100
            order_by = params.get("order_by", "creation desc")

            # Execute query
            results = frappe.get_all(
                doctype,
                filters=filters,
                fields=fields,
                limit_page_length=limit,
                order_by=order_by
            )

            if not results:
                return f"No {doctype} documents found matching the filters."

            # Format output
            output = f"Found {len(results)} {doctype} document(s):\n\n"
            output += json.dumps(results, indent=2, default=str)

            return output

        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON input - {str(e)}"
        except frappe.PermissionError:
            return f"Error: Permission denied to access {params.get('doctype', 'unknown')}"
        except Exception as e:
            return f"Error querying Frappe: {str(e)}"


class FrappeGetDocTool(BaseTool):
    """
    Get a specific Frappe document by name.
    """
    name: str = "frappe_get_doc"
    description: str = """Get a specific Frappe document by its name.

Use this tool to retrieve the full details of a single document.

Input format (JSON):
{
    "doctype": "DocType Name",
    "name": "Document Name"
}

Examples:
- Get a User: {"doctype": "User", "name": "Administrator"}
- Get a Customer: {"doctype": "Customer", "name": "CUST-00001"}
"""

    session_id: Optional[str] = Field(default=None, exclude=True)

    def _run(self, query: str) -> str:
        """Get a specific document."""
        try:
            # Parse input
            if isinstance(query, str):
                params = json.loads(query)
            else:
                params = query

            doctype = params.get("doctype")
            name = params.get("name")

            if not doctype or not name:
                return "Error: Both 'doctype' and 'name' are required"

            # Check if document exists
            if not frappe.db.exists(doctype, name):
                return f"Error: {doctype} '{name}' does not exist"

            # Get document
            doc = frappe.get_doc(doctype, name)

            # Convert to dict (excluding internal fields)
            doc_dict = doc.as_dict()

            # Remove some internal fields for cleaner output
            internal_fields = ['docstatus', 'idx', 'modified_by', 'owner',
                             'doctype', '_user_tags', '_comments', '_assign',
                             '_liked_by', '_seen']
            for field in internal_fields:
                doc_dict.pop(field, None)

            return json.dumps(doc_dict, indent=2, default=str)

        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON input - {str(e)}"
        except frappe.PermissionError:
            return f"Error: Permission denied to access this document"
        except Exception as e:
            return f"Error getting document: {str(e)}"


class FrappeCreateDocTool(BaseTool):
    """
    Create a new Frappe document.
    """
    name: str = "frappe_create_doc"
    description: str = """Create a new document in Frappe.

Use this tool to create new records in the Frappe database.

Input format (JSON):
{
    "doctype": "DocType Name",
    "data": {
        "field1": "value1",
        "field2": "value2"
    }
}

Examples:
- Create a ToDo: {"doctype": "ToDo", "data": {"description": "Test task", "status": "Open"}}
- Create a Note: {"doctype": "Note", "data": {"title": "My Note", "content": "Note content"}}

Note: The agent must have permission to create documents of the specified DocType.
"""

    session_id: Optional[str] = Field(default=None, exclude=True)

    def _run(self, query: str) -> str:
        """Create a new document."""
        try:
            # Parse input
            if isinstance(query, str):
                params = json.loads(query)
            else:
                params = query

            doctype = params.get("doctype")
            data = params.get("data", {})

            if not doctype:
                return "Error: 'doctype' is required"

            if not data:
                return "Error: 'data' is required with document fields"

            # Check if doctype exists
            if not frappe.db.exists("DocType", doctype):
                return f"Error: DocType '{doctype}' does not exist"

            # Create document
            doc = frappe.new_doc(doctype)
            doc.update(data)
            doc.insert()
            frappe.db.commit()

            return f"Successfully created {doctype} with name: {doc.name}"

        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON input - {str(e)}"
        except frappe.PermissionError:
            return f"Error: Permission denied to create {params.get('doctype', 'unknown')}"
        except frappe.ValidationError as e:
            return f"Validation error: {str(e)}"
        except Exception as e:
            return f"Error creating document: {str(e)}"


class FrappeUpdateDocTool(BaseTool):
    """
    Update an existing Frappe document.
    """
    name: str = "frappe_update_doc"
    description: str = """Update an existing document in Frappe.

Use this tool to modify existing records in the Frappe database.

Input format (JSON):
{
    "doctype": "DocType Name",
    "name": "Document Name",
    "data": {
        "field1": "new_value1",
        "field2": "new_value2"
    }
}

Examples:
- Update a ToDo: {"doctype": "ToDo", "name": "TODO-00001", "data": {"status": "Closed"}}

Note: The agent must have permission to write to the specified document.
"""

    session_id: Optional[str] = Field(default=None, exclude=True)

    def _run(self, query: str) -> str:
        """Update an existing document."""
        try:
            # Parse input
            if isinstance(query, str):
                params = json.loads(query)
            else:
                params = query

            doctype = params.get("doctype")
            name = params.get("name")
            data = params.get("data", {})

            if not doctype or not name:
                return "Error: Both 'doctype' and 'name' are required"

            if not data:
                return "Error: 'data' is required with fields to update"

            # Check if document exists
            if not frappe.db.exists(doctype, name):
                return f"Error: {doctype} '{name}' does not exist"

            # Update document
            doc = frappe.get_doc(doctype, name)
            doc.update(data)
            doc.save()
            frappe.db.commit()

            return f"Successfully updated {doctype} '{name}'"

        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON input - {str(e)}"
        except frappe.PermissionError:
            return f"Error: Permission denied to update this document"
        except frappe.ValidationError as e:
            return f"Validation error: {str(e)}"
        except Exception as e:
            return f"Error updating document: {str(e)}"


class FrappeDeleteDocTool(BaseTool):
    """
    Delete a Frappe document.
    """
    name: str = "frappe_delete_doc"
    description: str = """Delete a document from Frappe.

Use this tool with CAUTION - deletion is permanent!

Input format (JSON):
{
    "doctype": "DocType Name",
    "name": "Document Name"
}

Note: The agent must have permission to delete documents of the specified DocType.
This action cannot be undone.
"""

    session_id: Optional[str] = Field(default=None, exclude=True)

    def _run(self, query: str) -> str:
        """Delete a document."""
        try:
            # Parse input
            if isinstance(query, str):
                params = json.loads(query)
            else:
                params = query

            doctype = params.get("doctype")
            name = params.get("name")

            if not doctype or not name:
                return "Error: Both 'doctype' and 'name' are required"

            # Check if document exists
            if not frappe.db.exists(doctype, name):
                return f"Error: {doctype} '{name}' does not exist"

            # Delete document
            frappe.delete_doc(doctype, name)
            frappe.db.commit()

            return f"Successfully deleted {doctype} '{name}'"

        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON input - {str(e)}"
        except frappe.PermissionError:
            return f"Error: Permission denied to delete this document"
        except frappe.LinkExistsError as e:
            return f"Cannot delete: Document is linked to other documents. {str(e)}"
        except Exception as e:
            return f"Error deleting document: {str(e)}"


class FrappeRunMethodTool(BaseTool):
    """
    Call a whitelisted Frappe method.
    """
    name: str = "frappe_run_method"
    description: str = """Call a whitelisted Frappe API method.

Use this tool to execute Frappe server methods that are marked with @frappe.whitelist().

Input format (JSON):
{
    "method": "frappe.client.get_count",
    "args": {
        "doctype": "User"
    }
}

Common methods:
- frappe.client.get_count - Count documents
- frappe.client.get_value - Get specific field value
- frappe.client.set_value - Set field value

Note: Only whitelisted methods can be called.
"""

    session_id: Optional[str] = Field(default=None, exclude=True)

    def _run(self, query: str) -> str:
        """Execute a whitelisted Frappe method."""
        try:
            # Parse input
            if isinstance(query, str):
                params = json.loads(query)
            else:
                params = query

            method = params.get("method")
            args = params.get("args", {})

            if not method:
                return "Error: 'method' is required"

            # Execute method
            result = frappe.call(method, **args)

            if result is None:
                return "Method executed successfully (no return value)"

            return json.dumps(result, indent=2, default=str)

        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON input - {str(e)}"
        except frappe.PermissionError:
            return f"Error: Permission denied to call this method"
        except Exception as e:
            return f"Error calling method: {str(e)}"
