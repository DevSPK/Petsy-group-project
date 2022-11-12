from flask import Blueprint, request
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from ..models import db, Product, Review, OrderProduct, ProductImage
from ..forms.item_form import CreateEditProductForm
from ..forms.add_image_form import AddImageForm
from .auth_routes import validation_errors_to_error_messages

item_routes = Blueprint('items', __name__)

@item_routes.route('/test')
def test_route():
    return 'items'



@item_routes.post('/')
@login_required
def create_item():
    """
    Creates/posts a new item
    """
    form = CreateEditProductForm()
    form['csrf_token'].data = request.cookies['csrf_token']
    if form.validate_on_submit():
        new_product = Product(
            user_id=current_user.get_id(),
            name=form.data['name'],
            price=form.data['price'],
            description=form.data['description']
        )
        db.session.add(new_product)
        db.session.commit()

        # Adds item images if provided
        if form.data['images_urls']:
            url_lst = form.data['images_urls'].split(', ')
            for url in url_lst:
                new_image = ProductImage(
                    product_id = new_product.id,
                    url = url,
                    preview_image = True if url_lst.index(url) == 0 else False # Makes first listed url the preview image
                )
                db.session.add(new_image)
                db.session.commit()

        # Gets all reviews of shop then calculates avg rating
        # Uses current user id since current user will always be seller when creating item
        reviews = Review.query.join(Product).filter(Product.user_id == current_user.get_id()).all()
        avg_rating = 0
        for review in reviews:
            avg_rating += review.rating
        avg_rating /= len(reviews)

        # Gets all reviews of store then calculates number of sales
        # Uses current user id since current user will always be seller/store owner when creating item
        orders = OrderProduct.query.join(Product).filter(Product.user_id == current_user.get_id()).all()
        sales = 0
        for order in orders:
            sales += order.quantity

        final_product = {
            "id": new_product.id,
            "sellerId": current_user.id,
            "name": new_product.name,
            "shopName": current_user.username,
            "price": new_product.price,
            "avgShopRating": avg_rating,
            "shopSales": sales,
            "description": new_product.description,
            "shopReviews": len(reviews),
            "itemReviews": 0,
            "imageURLs": form.data['images_urls'].split(', ') if form.data['images_urls'] else [] # Turns urls into list if provided else it will equal an empty list
        }

        return final_product
    else:
        return {'errors': validation_errors_to_error_messages(form.errors)}, 400


@item_routes.put('/<int:product_id>')
@login_required
def edit_product(product_id):
    """
    Edit an item by item id
    """
    form = CreateEditProductForm()
    form['csrf_token'].data = request.cookies['csrf_token']
    if form.validate_on_submit():
        current_product = Product.query.get(product_id)

        if current_product == None:
            return {"message": "Item could not be found"}, 404

        if current_product.user_id != int(current_user.get_id()):
            return {"message": "Forbidden"}, 403


        current_product.name = form.data['name']
        current_product.price = form.data['price']
        current_product.description = form.data['description']

        db.session.commit()

        # Gets all reviews of shop then calculates avg rating
        # Uses current user id since current user must be the seller to be able to edit item
        shop_reviews = Review.query.join(Product).filter(Product.user_id == current_user.get_id()).all()
        avg_rating = 0
        for review in shop_reviews:
            avg_rating += review.rating
        avg_rating /= len(shop_reviews)

        # Gets all reviews of store then calculates number of sales
        # Uses current user id since current user must be the seller to be able to edit item
        orders = OrderProduct.query.join(Product).filter(Product.user_id == current_user.get_id()).all()
        sales = 0
        for order in orders:
            sales += order.quantity

        # Gets all reviews of item
        item_reviews_count = Product.query.join(Review).filter(Review.product_id == current_product.id).count()

        # Gets all image URLs
        images = ProductImage.query.filter(ProductImage.product_id == current_product.id).all()

        final_product = {
            "id": current_product.id,
            "sellerId": current_user.get_id(),
            "name": current_product.name,
            "shopName": current_user.username,
            "price": current_product.price,
            "avgShopRating": avg_rating,
            "shopSales": sales,
            "description": current_product.description,
            "shopReviews": len(shop_reviews),
            "itemReviews": item_reviews_count,
            "imageURLs": [image.url for image in images]
        }

        return final_product
    else:
        return {'errors': validation_errors_to_error_messages(form.errors)}, 400


@item_routes.delete('/<int:product_id>')
@login_required
def delete_product(product_id):
    """
    Delete an item by item id
    """
    current_product = Product.query.get(product_id)
    print(type(current_user.get_id()))
    print(type(current_product.user_id))

    if current_product == None:
        return {"message": "Item could not be found"}, 404

    if current_product.user_id != int(current_user.get_id()):
        return {"message": "Forbidden"}, 403

    db.session.delete(current_product)
    db.session.commit()

    return { "message": "Successfully deleted" }


@item_routes.post('/<int:product_id>/images')
@login_required
def add_image(product_id):
    """
    Add image of item by item id
    """
    form = AddImageForm()
    form['csrf_token'].data = request.cookies['csrf_token']
    if form.validate_on_submit():
        current_product = Product.query.get(product_id)

        if current_product == None:
            return {"message": "Item could not be found"}, 404

        if current_product.user_id != int(current_user.get_id()):
            return {"message": "Forbidden"}, 403

        new_image = ProductImage(
            product_id = product_id,
            url = form.data['url'],
            preview_image = form.data['preview_image']
        )

        db.session.add(new_image)
        db.session.commit()

        return { 'id': new_image.id, 'url': new_image.url, 'preview_image': new_image.preview_image}
    else:
        return {'errors': validation_errors_to_error_messages(form.errors)}, 400


@item_routes.get('/<int:product_id>/reviews')
def get_reviews_by_item(product_id):
    """
    Get all reviews by item Id
    """
    current_product = Product.query.get(product_id)

    if current_product == None:
        return {"message": "Item could not be found"}, 404

    reviews = Review.query.filter(Review.product_id == product_id).options(joinedload(Review.user)).options(joinedload(Review.product)).all()

    review_lst = []
    for review in reviews:
        user_obj = {'id': review.user.id, 'username': review.user.username}

        review_data = {
            'id': review.id,
            'user': user_obj,
            'sellerId': review.product.user_id,
            'itemId': review.product.id,
            'starRating': review.rating,
            'text': review.text,
            'date': review.date_created,
        }
        review_lst.append(review_data)


    return { "itemReviews": review_lst }