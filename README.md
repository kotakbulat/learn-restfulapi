- Save the code above as main.py.

- Open your terminal or command prompt.

- Navigate to the directory where you saved main.py.

- Run the Uvicorn server:

     uvicorn main:app --reload

Use code with caution.
Bash
main: the file main.py.

app: the FastAPI() instance created in the file.

--reload: makes the server restart automatically after code changes (useful for development).

===============================================================================================================

Interactive Docs (Swagger UI): Open your browser and go to http://127.0.0.1:8000/docs. This interface is automatically generated by FastAPI and lets you explore and test all endpoints directly. It showcases Resource Identification (URIs), Resource Manipulation (HTTP Methods), and Representations (Schema definitions).

Using curl or API Clients (Postman, Insomnia):

Feature Check: Client-Server & Statelessness: Each curl command is a separate client request. The server responds without needing prior context from other requests.

Feature Check: Resource Identification (URIs) & Manipulation (HTTP Methods):

# GET all projects (List)
curl -X GET "http://127.0.0.1:8000/projects" -H "accept: application/json"

# POST a new project (Create)
curl -X POST "http://127.0.0.1:8000/projects" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"title": "New API Client", "description": "Testing the API", "technologies": ["curl", "HTTP"], "url": null}'

# GET a specific project (Retrieve - use an ID returned by GET all or POST)
curl -X GET "http://127.0.0.1:8000/projects/1" -H "accept: application/json"

# PUT (Replace) project 1
curl -X PUT "http://127.0.0.1:8000/projects/1" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"title": "Updated Website", "description": "Fully updated description.", "technologies": ["HTML5", "CSS3", "React"], "url": "https://new.example.com"}'

# PATCH (Partially Update) project 2 - only description
curl -X PATCH "http://127.0.0.1:8000/projects/2" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '{"description": "A new partial description"}'

# DELETE project 1
curl -X DELETE "http://127.0.0.1:8000/projects/1" -H "accept: application/json"
Use code with caution.
Bash
Feature Check: Representations (JSON): Observe the request bodies (-d '...') and the responses. They are in JSON format. The -H "Content-Type: application/json" and -H "accept: application/json" headers explicitly state this.

Feature Check: Self-descriptive Messages:

Notice the HTTP methods (GET, POST, PUT, PATCH, DELETE) used.

Check the HTTP Status Codes returned (e.g., 200 OK, 201 Created, 204 No Content, 404 Not Found if you try an invalid ID).

Look at response headers like Content-Type: application/json.

Feature Check: HATEOAS: Examine the JSON responses for GET /projects and GET /projects/{id}. You will see the _links array containing related actions and their URIs (e.g., self, edit, delete, collection). This tells the client what it can do next without hardcoding URLs.

// Example response for GET /projects/2
{
  "title": "Data Analysis Tool",
  "description": "A new partial description", // Updated by PATCH
  "technologies": [ "Python", "Pandas", "FastAPI" ],
  "url": "https://github.com/example/data-tool",
  "id": 2,
  "_links": [
    { "rel": "self", "href": "http://127.0.0.1:8000/projects/2", "method": "GET" },
    { "rel": "edit", "href": "http://127.0.0.1:8000/projects/2", "method": "PUT" },
    { "rel": "partial_edit", "href": "http://127.0.0.1:8000/projects/2", "method": "PATCH" },
    { "rel": "delete", "href": "http://127.0.0.1:8000/projects/2", "method": "DELETE" },
    { "rel": "collection", "href": "http://127.0.0.1:8000/projects", "method": "GET" }
  ]
}
Use code with caution.
Json
Feature Check: Cacheability: When making GET requests (e.g., curl -I -X GET "http://127.0.0.1:8000/projects/2" - the -I fetches headers only), look for the Cache-Control header (e.g., Cache-Control: public, max-age=300). This tells clients/proxies they can cache the response.

Feature Check: Layered System: While you can't directly see layers here, the design (using standard HTTP, URIs, self-contained requests) allows intermediaries (like Nginx acting as a reverse proxy or cache) to be placed in front of the Uvicorn server without changing the API code or the client's interaction logic.
