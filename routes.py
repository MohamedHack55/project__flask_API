from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User, Product
from database import db

routes = Blueprint('routes', __name__)

@routes.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'])
    new_user = User(name=data['name'], username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=str(user.id))  # ✅ تأكد أن الهوية (identity) نص وليس رقم
    return jsonify({'access_token': access_token})


@routes.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    data = request.get_json()
    new_product = Product(
        pname=data['pname'], description=data.get('description', ''),
        price=data['price'], stock=data['stock']
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product added successfully'}), 201


@routes.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    products = Product.query.all()
    return jsonify([
        {
            "pid": p.pid,
            "pname": p.pname,
            "description": p.description,
            "price": p.price,
            "stock": p.stock,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for p in products
    ])


@routes.route('/products/<int:pid>', methods=['GET'])
@jwt_required()
def get_product(pid):
    product = Product.query.get(pid)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    return jsonify({
        "pid": product.pid,
        "pname": product.pname,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "created_at": product.created_at.strftime("%Y-%m-%d %H:%M:%S")
    })

# update product 
@routes.route('/products/<int:pid>', methods=['PUT'])
@jwt_required()
def update_product(pid):
    product = Product.query.get(pid)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    data = request.get_json()
    product.pname = data.get('pname', product.pname)
    product.description = data.get('description', product.description)
    product.price = data.get('price', product.price)
    product.stock = data.get('stock', product.stock)

    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})


@routes.route('/products/<int:pid>', methods=['DELETE'])
@jwt_required()
def delete_product(pid):
    product = Product.query.get(pid)
    if not product:
        return jsonify({'message': 'Product not found'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})
