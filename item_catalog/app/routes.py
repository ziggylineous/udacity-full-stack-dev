# the first app is the package,
# the second is the Flask application
from app import app, db
from app.models import User, Item, Category
from flask import render_template, request, flash, url_for, redirect
from app.forms import ItemForm

@app.route('/')
@app.route('/items')
def show_items():
    return render_template(
        'items.html',
        items=Item.query.all()
    )


@app.route('/items/<int:item_id>')
def view_item(item_id):
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
        update_item(item, form)
        flash('Updated item: {}'.format(item.name))
        return redirect(url_for('view_item', item_id=item.id))
    
    return render_template(
        'item-form.html',
        form=form,
        item_action='Edit'
    )


def update_item(item, item_form):
    item_form.populate_obj(item)
    item.category = Category.query.filter_by(id=item.category_id).one()

    db.session.commit()


@app.route('/items/new', methods=['GET', 'POST'])
def create_item():
    form = ItemForm()
    
    if form.validate_on_submit():
        item = _create_item(form)
        flash('Created new item: {}'.format(item.name))
        return redirect(url_for('show_items'))

    return render_template(
        'item-form.html',
        title='Create New Item',
        form=form,
        item_action='Create'
    )


def _create_item(item_form):
    category_id = item_form.category_id.data
    cat = Category.query.filter_by(id=category_id).one()
    
    item = Item(
        name=item_form.name.data,
        description=item_form.description.data,
        category_id=category_id,
        category=cat
    )
        
    db.session.add(item)
    db.session.commit()

    return item


@app.route('/items/<int:item_id>/delete', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    item_name = item.name

    db.session.delete(item)
    db.session.commit()

    flash('Deleted item: {}'.format(item_name))

    return ''
