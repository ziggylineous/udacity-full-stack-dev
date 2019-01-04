# the first app is the package,
# the second is the Flask application
from app import app, db, images
from app.models import User, Item, Category
from flask import render_template, request, flash, url_for, redirect
from app.forms import ItemForm


# item CRUD routes
@app.route('/')
@app.route('/items')
def show_items():
    """
    Shows all items (TODO: paginate)
    """
    return render_template(
        'items.html',
        items=Item.query.all()
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
    if image_file:
        filename = images.save(
            image_file,
            name=image_file.filename
        )
        
        return filename
    
    return ''


@app.route('/items/<int:item_id>/delete', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    item_name = item.name

    db.session.delete(item)
    db.session.commit()

    flash('Deleted item: {}'.format(item_name))

    return ''