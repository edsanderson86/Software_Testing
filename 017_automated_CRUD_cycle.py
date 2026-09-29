{
  "info": {
    "name": "Authenticated Task CRUD Cycle",
    "description": "Example Postman collection. Assumes POST /auth/login returns {\"token\":\"...\"}; task endpoints use /api/tasks and /api/tasks/:id. Set baseUrl, username, and password before running. Adjust URLs or response fields to match your API.",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    { "key": "baseUrl", "value": "http://127.0.0.1:5000" },
    { "key": "username", "value": "" },
    { "key": "password", "value": "" },
    { "key": "token", "value": "" },
    { "key": "taskId", "value": "" },
    { "key": "taskTitle", "value": "" },
    { "key": "updatedTitle", "value": "" }
  ],
  "item": [
    {
      "name": "1. Authenticate",
      "request": {
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
              "pm.test('Login returns 200', () => pm.response.to.have.status(200));",
              "const body = pm.response.json();",
              "pm.test('Token is present', () => pm.expect(body.token).to.be.a('string').and.not.empty);",
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
              "const unique = Date.now() + '-' + Math.random().toString(36).slice(2, 8);",
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
              "pm.test('Create returns 201', () => pm.response.to.have.status(201));",
              "const body = pm.response.json();",
              "pm.test('Created task has an ID', () => pm.expect(body.id).to.exist);",
              "pm.test('Created title matches', () => pm.expect(body.title).to.eql(pm.collectionVariables.get('taskTitle')));",
              "if (body.id !== undefined) pm.collectionVariables.set('taskId', String(body.id));"
            ]
          }
        }
      ],
      "request": {
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
              "pm.test('Read returns 200', () => pm.response.to.have.status(200));",
              "const body = pm.response.json();",
              "pm.test('ID matches created task', () => pm.expect(String(body.id)).to.eql(pm.collectionVariables.get('taskId')));",
              "pm.test('Title matches created task', () => pm.expect(body.title).to.eql(pm.collectionVariables.get('taskTitle')));"
            ]
          }
        }
      ],
      "request": {
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
              "pm.test('Update returns 200', () => pm.response.to.have.status(200));",
              "const body = pm.response.json();",
              "pm.test('Updated title matches', () => pm.expect(body.title).to.eql(pm.collectionVariables.get('updatedTitle')));"
            ]
          }
        }
      ],
      "request": {
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
              "pm.test('Read returns 200', () => pm.response.to.have.status(200));",
              "pm.test('Updated value was saved', () => pm.expect(pm.response.json().title).to.eql(pm.collectionVariables.get('updatedTitle')));"
            ]
          }
        }
      ],
      "request": {
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
              "pm.test('Delete returns 204', () => pm.response.to.have.status(204));"
            ]
          }
        }
      ],
      "request": {
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
              "pm.test('Deleted task returns 404', () => pm.response.to.have.status(404));",
              "pm.collectionVariables.unset('token');",
              "pm.collectionVariables.unset('taskId');",
              "pm.collectionVariables.unset('taskTitle');",
              "pm.collectionVariables.unset('updatedTitle');"
            ]
          }
        }
      ],
      "request": {
        "method": "GET",
        "header": [
          { "key": "Authorization", "value": "Bearer {{token}}" }
        ],
        "url": "{{baseUrl}}/api/tasks/{{taskId}}"
      }
    }
  ]
}