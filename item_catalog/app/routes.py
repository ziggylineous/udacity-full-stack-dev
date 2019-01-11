# the first app is the package,
# the second is the Flask application
from app import app, db, images
from app.item_search import search_item as search_item_in_index
from app.models import Item, Category
from flask import render_template, request, flash, url_for, redirect, jsonify
from app.forms import ItemForm
from flask_login import login_required


# item CRUD routes
@app.route('/')
@app.route('/items')
def show_items():
    """
    Shows all items (TODO: paginate)
    """
    return render_template(
        'items.html',
        items=Item.query.all(),
        categories=Category.query.all()
    )


@app.route('/items/<int:item_id>')
def view_item(item_id):
    """
    Show item's page
    """
    item = Item.query.get_or_404(item_id)

    return render_template(
        'item.html',
        title='Item Catalog: {}'.format(item.name),
        item=item
    )


@app.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    form = ItemForm(formdata=request.form, obj=item)
    
    if form.validate_on_submit():
        filename = save_image_get_filename(form.image.data)
        update_item(item, form, filename)
        flash('Updated item: {}'.format(item.name))
        return redirect(url_for('view_item', item_id=item.id))
    
    return render_template(
        'item-form.html',
        form=form,
        item_action='Edit'
    )


def update_item(item, item_form, filename):
    """
    Update an item with form data.

    :param item: the item to update
    :param item_form: the item's form
    :param filename: the item's image name
    """
    item_form.populate_obj(item)
    item.category = Category.query.filter_by(id=item.category_id).one()
    item.image = filename

    db.session.commit()


@app.route('/items/new', methods=['GET', 'POST'])
@login_required
def create_item():
    form = ItemForm()
    
    if form.validate_on_submit():
        filename = save_image_get_filename(form.image.data)
        item = _create_item(form, filename)
        flash('Created new item: {}'.format(item.name))
        return redirect(url_for('show_items'))

    return render_template(
        'item-form.html',
        title='Create New Item',
        form=form,
        item_action='Create'
    )


def _create_item(item_form, filename):
    category_id = item_form.category_id.data
    cat = Category.query.filter_by(id=category_id).one()
    
    item = Item(
        name=item_form.name.data,
        description=item_form.description.data,
        category_id=category_id,
        category=cat,
        image=filename
    )
        
    db.session.add(item)
    db.session.commit()

    return item


def save_image_get_filename(image_file):
    """
    If the user attached an image, save it
    and return its url. Otherwise return an empty str
    meaning the item has no image.

    :param image_file: An image file of the item
    :return: the image url to save in the Item table
    """
    if image_file:
        filename = images.save(
            image_file,
            name=image_file.filename
        )
        
        return filename
    
    return ''


@app.route('/items/<int:item_id>/delete', methods=['DELETE'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    item_name = item.name

    db.session.delete(item)
    db.session.commit()

    flash('Deleted item: {}'.format(item_name))

    return ''




@app.route('/categories/<category_name>/items')
def category_items(category_name):
    """
    Creates the page for a selected category

    :param category_name: The selected category name
    :return: Category page response
    """
    category = Category\
        .query\
        .filter_by(name=category_name)\
        .first_or_404()

    return render_template(
        'items.html',
        items=category.items,
        category=category,
        categories=Category.query.all()
    )


# api requirement
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
