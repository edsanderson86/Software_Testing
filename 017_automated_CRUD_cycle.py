{
  "info": {
    "name": "Authenticated Task CRUD Cycle",
    "description": "Run requests in numbered order to authenticate, create, read, update, and delete a task. Set baseUrl, username, and password first. Assumes POST /auth/login returns {\"token\":\"...\"} and task endpoints use /api/tasks and /api/tasks/:id. Adjust URLs or response fields to match your API.",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "baseUrl",
      "value": "http://127.0.0.1:5000",
      "description": "Base address of the API under test."
    },
    {
      "key": "username",
      "value": "",
      "description": "Username used to authenticate before accessing tasks."
    },
    {
      "key": "password",
      "value": "",
      "description": "Password for the test account."
    },
    {
      "key": "token",
      "value": "",
      "description": "Token captured during login and sent with subsequent requests."
    },
    {
      "key": "taskId",
      "value": "",
      "description": "ID captured after creation so later requests target the same task."
    },
    {
      "key": "taskTitle",
      "value": "",
      "description": "Unique title generated before creating the task."
    },
    {
      "key": "updatedTitle",
      "value": "",
      "description": "Replacement title used to verify that updates persist."
    }
  ],
  "item": [
    {
      "name": "1. Authenticate",
      "request": {
        "description": "Submit the configured credentials and capture the returned token for authenticated task requests.",
        "method": "POST",
        "header": [
          { "key": "Content-Type", "value": "application/json" }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"username\":\"{{username}}\",\"password\":\"{{password}}\"}"
        },
        "url": "{{baseUrl}}/auth/login"
      },
      "event": [
        {
          "listen": "test",
          "script": {
            "type": "text/javascript",
            "exec": [
              "// Check that authentication returned the expected success status.",
              "pm.test('Login returns 200', () => pm.response.to.have.status(200));",
              "// Parse the response and verify that it contains a non-empty token.",
              "const body = pm.response.json();",
              "pm.test('Token is present', () => pm.expect(body.token).to.be.a('string').and.not.empty);",
              "// Save the token for the Authorization headers in later requests.",
              "if (body.token) pm.collectionVariables.set('token', body.token);"
            ]
          }
        }
      ]
    },
    {
      "name": "2. Create task",
      "event": [
        {
          "listen": "prerequest",
          "script": {
            "type": "text/javascript",
            "exec": [
              "// Generate distinctive titles to help identify this run's task.",
              "const unique = Date.now() + '-' + Math.random().toString(36).slice(2, 8);",
              "// Store both titles so later checks can compare expected values.",
              "pm.collectionVariables.set('taskTitle', 'CRUD test ' + unique);",
              "pm.collectionVariables.set('updatedTitle', 'Updated CRUD test ' + unique);"
            ]
          }
        },
        {
          "listen": "test",
          "script": {
            "type": "text/javascript",
            "exec": [
              "// Confirm that the API reports successful resource creation.",
              "pm.test('Create returns 201', () => pm.response.to.have.status(201));",
              "const body = pm.response.json();",
              "// Check that the response identifies the task and preserves its title.",
              "pm.test('Created task has an ID', () => pm.expect(body.id).to.exist);",
              "pm.test('Created title matches', () => pm.expect(body.title).to.eql(pm.collectionVariables.get('taskTitle')));",
              "// Save the ID so subsequent requests use the newly created task.",
              "if (body.id !== undefined) pm.collectionVariables.set('taskId', String(body.id));"
            ]
          }
        }
      ],
      "request": {
        "description": "Create a task using the generated title and the token obtained during login.",
        "method": "POST",
        "header": [
          { "key": "Content-Type", "value": "application/json" },
          { "key": "Authorization", "value": "Bearer {{token}}" }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"title\":\"{{taskTitle}}\"}"
        },
        "url": "{{baseUrl}}/api/tasks"
      }
    },
    {
      "name": "3. Read task",
      "event": [
        {
          "listen": "test",
          "script": {
            "type": "text/javascript",
            "exec": [
              "// Confirm that the newly created task can be retrieved.",
              "pm.test('Read returns 200', () => pm.response.to.have.status(200));",
              "const body = pm.response.json();",
              "// Compare the returned ID and title with the creation values.",
              "pm.test('ID matches created task', () => pm.expect(String(body.id)).to.eql(pm.collectionVariables.get('taskId')));",
              "pm.test('Title matches created task', () => pm.expect(body.title).to.eql(pm.collectionVariables.get('taskTitle')));"
            ]
          }
        }
      ],
      "request": {
        "description": "Retrieve the task by its saved ID and verify its original values.",
        "method": "GET",
        "header": [
          { "key": "Authorization", "value": "Bearer {{token}}" }
        ],
        "url": "{{baseUrl}}/api/tasks/{{taskId}}"
      }
    },
    {
      "name": "4. Update task",
      "event": [
        {
          "listen": "test",
          "script": {
            "type": "text/javascript",
            "exec": [
              "// Confirm that the API accepted the update.",
              "pm.test('Update returns 200', () => pm.response.to.have.status(200));",
              "const body = pm.response.json();",
              "// Verify that the response contains the replacement title.",
              "pm.test('Updated title matches', () => pm.expect(body.title).to.eql(pm.collectionVariables.get('updatedTitle')));"
            ]
          }
        }
      ],
      "request": {
        "description": "Replace the task title with the generated updated title.",
        "method": "PUT",
        "header": [
          { "key": "Content-Type", "value": "application/json" },
          { "key": "Authorization", "value": "Bearer {{token}}" }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"title\":\"{{updatedTitle}}\"}"
        },
        "url": "{{baseUrl}}/api/tasks/{{taskId}}"
      }
    },
    {
      "name": "5. Confirm update",
      "event": [
        {
          "listen": "test",
          "script": {
            "type": "text/javascript",
            "exec": [
              "// Retrieve the task again to check persistence independently of the update response.",
              "pm.test('Read returns 200', () => pm.response.to.have.status(200));",
              "pm.test('Updated value was saved', () => pm.expect(pm.response.json().title).to.eql(pm.collectionVariables.get('updatedTitle')));"
            ]
          }
        }
      ],
      "request": {
        "description": "Read the task again to confirm that the updated title was saved.",
        "method": "GET",
        "header": [
          { "key": "Authorization", "value": "Bearer {{token}}" }
        ],
        "url": "{{baseUrl}}/api/tasks/{{taskId}}"
      }
    },
    {
      "name": "6. Delete task",
      "event": [
        {
          "listen": "test",
          "script": {
            "type": "text/javascript",
            "exec": [
              "// Check for the expected successful deletion status.",
              "pm.test('Delete returns 204', () => pm.response.to.have.status(204));"
            ]
          }
        }
      ],
      "request": {
        "description": "Delete the task created during this run.",
        "method": "DELETE",
        "header": [
          { "key": "Authorization", "value": "Bearer {{token}}" }
        ],
        "url": "{{baseUrl}}/api/tasks/{{taskId}}"
      }
    },
    {
      "name": "7. Confirm deletion",
      "event": [
        {
          "listen": "test",
          "script": {
            "type": "text/javascript",
            "exec": [
              "// Confirm that the deleted task is no longer available at its URL.",
              "pm.test('Deleted task returns 404', () => pm.response.to.have.status(404));",
              "// Clear temporary collection values after the final request.",
              "// Clearing these variables does not delete server-side data.",
              "pm.collectionVariables.unset('token');",
              "pm.collectionVariables.unset('taskId');",
              "pm.collectionVariables.unset('taskTitle');",
              "pm.collectionVariables.unset('updatedTitle');"
            ]
          }
        }
      ],
      "request": {
        "description": "Request the deleted task, expect a not-found response, and clear temporary collection variables.",
        "method": "GET",
        "header": [
          { "key": "Authorization", "value": "Bearer {{token}}" }
        ],
        "url": "{{baseUrl}}/api/tasks/{{taskId}}"
      }
    }
  ]
}