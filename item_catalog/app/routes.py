# the first app is the package,
# the second is the Flask application
from app import app, db
from app.models import User, Item
from flask import render_template, request, flash, url_for, redirect
from app.forms import NewItemForm

@app.route('/')
@app.route('/items')
def show_items():
    return render_template(
        'items.html',
        items=Item.query.all()
    )


@app.route('/items/<string:item_name>')
def view_item(item_name):
    


@app.route('/items/new', methods=['GET', 'POST'])
def new_item():
    form = NewItemForm()
    
    if form.validate_on_submit():
        item = create_item(
            form.name.data,
            form.description.data
        )    
        flash('Created new item: {}'.format(item.name))
        return redirect(url_for('show_items'))
    
    else:
        return render_template(
            'new-item.html',
            title='Create New Item',
            form=form
        )


def create_item(name, description):
    item = Item(
        name=name,
        description=description
    )
        
    db.session.add(item)
    db.session.commit()

    return item