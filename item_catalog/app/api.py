from app import app
from app.item_search import search_item as search_item_in_index
from flask import request, jsonify


@app.route('/api/item')
def search_item():
    query_args = request.args.getlist('q')

    if len(query_args) == 0:
        error_message = """
        No 'q' query args sent.
        Usage: send several search words separated by commas, like this:
        /api/item?q=word1,word2,word3
        """
        response = jsonify(error=error_message)
        response.status_code = 400
        return response

    joined_words = query_args[0]
    words = joined_words.split(',')
    items = search_item_in_index(words)

    return jsonify([item.as_dict() for item in items])