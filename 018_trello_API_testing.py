# build_trello_collection.py
# Run: python build_trello_collection.py
# Import the generated trello_crud.postman_collection.json into Postman.
# Set collection variables apiKey and apiToken locally, then run the collection.
# The run creates a disposable board and deletes it at the end.
#
# Trello endpoint reference:
# https://developer.atlassian.com/cloud/trello/rest/api-group-boards/
# https://developer.atlassian.com/cloud/trello/rest/api-group-lists/
# https://developer.atlassian.com/cloud/trello/rest/api-group-cards/

import json
from pathlib import Path


def script(*lines):
    return {"type": "text/javascript", "exec": list(lines)}


def request(name, method, path, params=None, before=None, tests=None):
    query = [
        {"key": "key", "value": "{{apiKey}}"},
        {"key": "token", "value": "{{apiToken}}"},
    ]
    query += [
        {"key": key, "value": value}
        for key, value in (params or {}).items()
    ]

    item = {
        "name": name,
        "request": {
            "method": method,
            "url": {
                "raw": "https://api.trello.com/1" + path,
                "protocol": "https",
                "host": ["api", "trello", "com"],
                "path": ["1"] + path.strip("/").split("/"),
                "query": query,
            },
        },
        "event": [],
    }

    if before:
        item["event"].append({
            "listen": "prerequest",
            "script": script(*before),
        })
    if tests:
        item["event"].append({
            "listen": "test",
            "script": script(*tests),
        })

    return item


items = [
    request(
        "01 Create board",
        "POST",
        "/boards/",
        {
            "name": "{{boardName}}",
            "defaultLists": "false",
        },
        before=[
            "const suffix = Date.now() + '-' + Math.random().toString(36).slice(2, 8);",
            "pm.collectionVariables.set('boardName', 'API Test ' + suffix);",
            "pm.collectionVariables.set('updatedBoardName', 'Updated API Test ' + suffix);",
            "pm.collectionVariables.set('cardName', 'Test Card ' + suffix);",
        ],
        tests=[
            "pm.test('Board created', () => pm.response.to.have.status(200));",
            "const board = pm.response.json();",
            "pm.test('Board name matches', () => pm.expect(board.name).to.eql(pm.collectionVariables.get('boardName')));",
            "pm.test('Board ID exists', () => pm.expect(board.id).to.be.a('string').and.not.empty);",
            "if (board.id) pm.collectionVariables.set('boardId', board.id);",
        ],
    ),
    request(
        "02 Create list",
        "POST",
        "/lists",
        {"name": "To Do", "idBoard": "{{boardId}}"},
        tests=[
            "pm.test('List created', () => pm.response.to.have.status(200));",
            "const list = pm.response.json();",
            "pm.test('List belongs to board', () => pm.expect(list.idBoard).to.eql(pm.collectionVariables.get('boardId')));",
            "if (list.id) pm.collectionVariables.set('listId', list.id);",
        ],
    ),
    request(
        "03 Create card",
        "POST",
        "/cards",
        {"idList": "{{listId}}", "name": "{{cardName}}"},
        tests=[
            "pm.test('Card created', () => pm.response.to.have.status(200));",
            "const card = pm.response.json();",
            "pm.test('Card belongs to list', () => pm.expect(card.idList).to.eql(pm.collectionVariables.get('listId')));",
            "pm.test('Card name matches', () => pm.expect(card.name).to.eql(pm.collectionVariables.get('cardName')));",
            "if (card.id) pm.collectionVariables.set('cardId', card.id);",
        ],
    ),
    request(
        "04 Read board",
        "GET",
        "/boards/{{boardId}}",
        tests=[
            "pm.test('Board found', () => pm.response.to.have.status(200));",
            "pm.test('Board ID matches', () => pm.expect(pm.response.json().id).to.eql(pm.collectionVariables.get('boardId')));",
        ],
    ),
    request(
        "05 Read list",
        "GET",
        "/lists/{{listId}}",
        tests=[
            "pm.test('List found', () => pm.response.to.have.status(200));",
            "pm.test('List name matches', () => pm.expect(pm.response.json().name).to.eql('To Do'));",
        ],
    ),
    request(
        "06 Read card",
        "GET",
        "/cards/{{cardId}}",
        tests=[
            "pm.test('Card found', () => pm.response.to.have.status(200));",
            "pm.test('Card name matches', () => pm.expect(pm.response.json().name).to.eql(pm.collectionVariables.get('cardName')));",
        ],
    ),
    request(
        "07 Update board",
        "PUT",
        "/boards/{{boardId}}",
        {"name": "{{updatedBoardName}}"},
        tests=[
            "pm.test('Board updated', () => pm.response.to.have.status(200));",
            "pm.test('New board name returned', () => pm.expect(pm.response.json().name).to.eql(pm.collectionVariables.get('updatedBoardName')));",
        ],
    ),
    request(
        "08 Update list",
        "PUT",
        "/lists/{{listId}}",
        {"name": "In Progress"},
        tests=[
            "pm.test('List updated', () => pm.response.to.have.status(200));",
            "pm.test('New list name returned', () => pm.expect(pm.response.json().name).to.eql('In Progress'));",
        ],
    ),
    request(
        "09 Update card",
        "PUT",
        "/cards/{{cardId}}",
        {"name": "Updated {{cardName}}", "desc": "Updated by API test"},
        tests=[
            "pm.test('Card updated', () => pm.response.to.have.status(200));",
            "pm.test('New card name returned', () => pm.expect(pm.response.json().name).to.eql('Updated ' + pm.collectionVariables.get('cardName')));",
        ],
    ),
    request(
        "10 Confirm updates",
        "GET",
        "/boards/{{boardId}}",
        tests=[
            "pm.test('Updated board persisted', () => {",
            "  pm.response.to.have.status(200);",
            "  pm.expect(pm.response.json().name).to.eql(pm.collectionVariables.get('updatedBoardName'));",
            "});",
        ],
    ),
    request(
        "11 Delete card",
        "DELETE",
        "/cards/{{cardId}}",
        tests=[
            "pm.test('Card deleted', () => pm.response.to.have.status(200));",
        ],
    ),
    request(
        "12 Confirm card deletion",
        "GET",
        "/cards/{{cardId}}",
        tests=[
            "pm.test('Deleted card is unavailable', () => pm.response.to.have.status(404));",
        ],
    ),
    request(
        "13 Delete board",
        "DELETE",
        "/boards/{{boardId}}",
        tests=[
            "pm.test('Board deleted', () => pm.response.to.have.status(200));",
        ],
    ),
    request(
        "14 Confirm board deletion",
        "GET",
        "/boards/{{boardId}}",
        tests=[
            "pm.test('Deleted board is unavailable', () => pm.response.to.have.status(404));",
            "pm.collectionVariables.unset('boardId');",
            "pm.collectionVariables.unset('listId');",
            "pm.collectionVariables.unset('cardId');",
        ],
    ),
]

collection = {
    "info": {
        "name": "Trello API — Board, List and Card CRUD",
        "description": (
            "Run requests in order using Postman's Collection Runner. "
            "Provide your own Trello API key and token as local collection values. "
            "The test board is deleted at the end; deleting it also removes its list."
        ),
        "schema": (
            "https://schema.getpostman.com/json/"
            "collection/v2.1.0/collection.json"
        ),
    },
    "variable": [
        {"key": key, "value": ""}
        for key in (
            "apiKey", "apiToken", "boardName", "updatedBoardName",
            "boardId", "listId", "cardName", "cardId",
        )
    ],
    "item": items,
}

output = Path("trello_crud.postman_collection.json")
output.write_text(json.dumps(collection, indent=2), encoding="utf-8")
print(f"Created {output}")