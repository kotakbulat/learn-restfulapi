from fastapi import FastAPI, HTTPException, Response, status, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- 1. Define Data Models (Resource Representation) ---
# Using Pydantic models for automatic validation and documentation

class Link(BaseModel):
    """Represents a HATEOAS link"""
    rel: str  # Relation type (e.g., 'self', 'collection', 'edit')
    href: str # The URL for the link
    method: str = "GET" # Default method

class ProjectBase(BaseModel):
    title: str
    description: str
    technologies: List[str]
    url: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass # Inherits all fields from ProjectBase for creation

class ProjectUpdate(BaseModel):
    # All fields are optional for partial updates (PATCH)
    title: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = None
    url: Optional[str] = None

class ProjectInDB(ProjectBase):
    id: int
    _links: List[Link] = [] # For HATEOAS

class ProjectCollection(BaseModel):
    items: List[ProjectInDB]
    _links: List[Link] = [] # Links for the collection itself

# --- 2. In-Memory "Database" ---
# Simple dictionary to store projects. In production, use a real DB.
projects_db: Dict[int, ProjectBase] = {
    1: ProjectBase(title="Personal Website", description="My personal portfolio website.", technologies=["HTML", "CSS", "JavaScript"], url="https://example.com"),
    2: ProjectBase(title="Data Analysis Tool", description="Tool for analyzing sales data.", technologies=["Python", "Pandas", "FastAPI"], url="https://github.com/example/data-tool"),
}
project_id_counter = len(projects_db)

# --- Helper function for HATEOAS links ---
def get_project_links(request: Request, project_id: int) -> List[Link]:
    base_url = str(request.base_url)
    return [
        Link(rel="self", href=f"{base_url}projects/{project_id}", method="GET"),
        Link(rel="edit", href=f"{base_url}projects/{project_id}", method="PUT"),
        Link(rel="partial_edit", href=f"{base_url}projects/{project_id}", method="PATCH"),
        Link(rel="delete", href=f"{base_url}projects/{project_id}", method="DELETE"),
        Link(rel="collection", href=f"{base_url}projects", method="GET"),
    ]

def get_collection_links(request: Request) -> List[Link]:
    base_url = str(request.base_url)
    return [
        Link(rel="self", href=f"{base_url}projects", method="GET"),
        Link(rel="create", href=f"{base_url}projects", method="POST"),
    ]

# --- 3. FastAPI Application ---
app = FastAPI(
    title="Simple Portfolio API",
    description="A RESTful API example demonstrating key features.",
    version="1.0.0"
)

# --- 4. API Endpoints (Resource Identification & Manipulation) ---

@app.get(
    "/projects",
    response_model=ProjectCollection,
    tags=["Projects"],
    summary="Retrieve all projects",
    description="Returns a list of all projects with HATEOAS links."
)
async def get_all_projects(request: Request, response: Response):
    """
    Demonstrates:
    - GET method (Resource Manipulation)
    - `/projects` URI (Resource Identification)
    - JSON response (Representation)
    - HATEOAS (_links in collection)
    - Cacheability (Cache-Control header)
    - Statelessness (Request is self-contained)
    - Client-Server (Implicit)
    - Self-descriptive (Status code 200, Content-Type)
    """
    response.headers["Cache-Control"] = "public, max-age=60" # Cache for 60 seconds
    project_items = []
    for pid, project in projects_db.items():
        project_data = project.dict()
        project_data['id'] = pid
        project_data['_links'] = get_project_links(request, pid)
        project_items.append(ProjectInDB(**project_data))

    return ProjectCollection(
        items=project_items,
        _links=get_collection_links(request)
    )

@app.post(
    "/projects",
    response_model=ProjectInDB,
    status_code=status.HTTP_201_CREATED,
    tags=["Projects"],
    summary="Create a new project",
    description="Adds a new project to the collection."
)
async def create_project(request: Request, project: ProjectCreate):
    """
    Demonstrates:
    - POST method (Resource Manipulation)
    - `/projects` URI (Resource Identification)
    - JSON request/response (Representation)
    - Status Code 201 Created (Self-descriptive)
    - HATEOAS (_links in response for the new resource)
    - Statelessness
    """
    global project_id_counter
    project_id_counter += 1
    new_project_id = project_id_counter
    projects_db[new_project_id] = ProjectBase(**project.dict())

    # Prepare response data including ID and links
    response_data = projects_db[new_project_id].dict()
    response_data['id'] = new_project_id
    response_data['_links'] = get_project_links(request, new_project_id)

    return ProjectInDB(**response_data)

@app.get(
    "/projects/{project_id}",
    response_model=ProjectInDB,
    tags=["Projects"],
    summary="Retrieve a specific project by ID",
    description="Returns details for a single project with HATEOAS links."
)
async def get_project_by_id(request: Request, project_id: int, response: Response):
    """
    Demonstrates:
    - GET method (Resource Manipulation)
    - `/projects/{id}` URI (Resource Identification)
    - Path parameter usage
    - JSON response (Representation)
    - HATEOAS (_links)
    - Error Handling (404 Not Found) (Self-descriptive)
    - Cacheability (Cache-Control header)
    - Statelessness
    """
    if project_id not in projects_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    response.headers["Cache-Control"] = "public, max-age=300" # Cache for 5 minutes
    project = projects_db[project_id]

    # Prepare response data including ID and links
    response_data = project.dict()
    response_data['id'] = project_id
    response_data['_links'] = get_project_links(request, project_id)

    return ProjectInDB(**response_data)

@app.put(
    "/projects/{project_id}",
    response_model=ProjectInDB,
    tags=["Projects"],
    summary="Update/Replace a project by ID",
    description="Completely replaces the project data for the given ID."
)
async def update_project(request: Request, project_id: int, project_update: ProjectCreate):
    """
    Demonstrates:
    - PUT method (Resource Manipulation - Replace)
    - `/projects/{id}` URI (Resource Identification)
    - JSON request/response (Representation)
    - Idempotency (calling PUT multiple times with same data yields same result)
    - Error Handling (404 Not Found)
    - HATEOAS (_links in response)
    - Statelessness
    """
    if project_id not in projects_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Replace the entire resource
    projects_db[project_id] = ProjectBase(**project_update.dict())

    # Prepare response data including ID and links
    response_data = projects_db[project_id].dict()
    response_data['id'] = project_id
    response_data['_links'] = get_project_links(request, project_id)

    return ProjectInDB(**response_data)

@app.patch(
    "/projects/{project_id}",
    response_model=ProjectInDB,
    tags=["Projects"],
    summary="Partially update a project by ID",
    description="Updates only the provided fields for the project."
)
async def partial_update_project(request: Request, project_id: int, project_patch: ProjectUpdate):
    """
    Demonstrates:
    - PATCH method (Resource Manipulation - Partial Update)
    - `/projects/{id}` URI (Resource Identification)
    - JSON request/response (Representation)
    - Handling partial data
    - Error Handling (404 Not Found)
    - HATEOAS (_links in response)
    - Statelessness
    """
    if project_id not in projects_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    stored_project_model = projects_db[project_id]
    update_data = project_patch.dict(exclude_unset=True) # Get only fields that were sent
    updated_project_model = stored_project_model.copy(update=update_data)
    projects_db[project_id] = ProjectBase(**updated_project_model.dict()) # Store as ProjectBase

    # Prepare response data including ID and links
    response_data = projects_db[project_id].dict()
    response_data['id'] = project_id
    response_data['_links'] = get_project_links(request, project_id)

    return ProjectInDB(**response_data)

@app.delete(
    "/projects/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Projects"],
    summary="Delete a project by ID",
    description="Removes the project from the collection."
)
async def delete_project(project_id: int, response: Response):
    """
    Demonstrates:
    - DELETE method (Resource Manipulation)
    - `/projects/{id}` URI (Resource Identification)
    - Status Code 204 No Content (Self-descriptive) - No response body needed
    - Error Handling (404 Not Found)
    - Idempotency (calling DELETE multiple times has same effect after the first)
    - Statelessness
    """
    if project_id not in projects_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    del projects_db[project_id]
    # No body needed for 204, FastAPI handles this. Explicitly set header just in case.
    response.status_code = status.HTTP_204_NO_CONTENT
    return response # Return the Response object directly for 204

# Optional: Add a root endpoint for basic info
@app.get("/", tags=["Root"], include_in_schema=False) # Hide from OpenAPI docs
async def read_root():
    return {"message": "Welcome to the Simple Portfolio API. Visit /docs for API documentation."}

# --- 5. Run the API (using Uvicorn) ---
# This part is usually run from the command line:
# uvicorn main:app --reload