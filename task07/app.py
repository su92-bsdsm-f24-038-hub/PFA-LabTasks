from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# In-memory data store for demonstration
items = [
    {"id": 1, "name": "Sample Item 1", "description": "This is the first sample item"},
    {"id": 2, "name": "Sample Item 2", "description": "This is the second sample item"}
]
next_id = 3

# Original joke endpoint

@app.route("/joke")
def joke():
    url = "https://official-joke-api.appspot.com/random_joke"
    r = requests.get(url)
    data = r.json()
    out = {"setup": data.get("setup"), "punchline": data.get("punchline")}
    return jsonify(out)

# GET - Retrieve all items
@app.route("/items", methods=["GET"])
def get_items():
    return jsonify({"items": items, "count": len(items)})

# GET - Retrieve a specific item by ID
@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = next((item for item in items if item["id"] == item_id), None)
    if item:
        return jsonify(item)
    return jsonify({"error": "Item not found"}), 404

# POST - Create a new item
@app.route("/items", methods=["POST"])
def create_item():
    global next_id
    data = request.get_json()
    
    if not data or "name" not in data:
        return jsonify({"error": "Name is required"}), 400
    
    new_item = {
        "id": next_id,
        "name": data["name"],
        "description": data.get("description", "")
    }
    
    items.append(new_item)
    next_id += 1
    
    return jsonify({"message": "Item created successfully", "item": new_item}), 201

# PUT - Update an existing item
@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    item = next((item for item in items if item["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Update item fields
    if "name" in data:
        item["name"] = data["name"]
    if "description" in data:
        item["description"] = data["description"]
    
    return jsonify({"message": "Item updated successfully", "item": item})

# DELETE - Delete an item
@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    global items
    item = next((item for item in items if item["id"] == item_id), None)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    items = [item for item in items if item["id"] != item_id]
    return jsonify({"message": f"Item {item_id} deleted successfully"})

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to the REST API",
        "endpoints": {
            "GET /items": "Get all items",
            "GET /items/<id>": "Get specific item",
            "POST /items": "Create new item",
            "PUT /items/<id>": "Update existing item",
            "DELETE /items/<id>": "Delete item",
            "GET /joke": "Get random joke"
        }
    })

if __name__ == "__main__":
    app.run(debug=True)
