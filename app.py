from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(10), nullable=True)  

def load_initial_data():
    with open("data.json", "r", encoding="utf-8") as file:
        products_data = json.load(file)
        for product in products_data:
            existing_product = Product.query.filter_by(name=product['name']).first()
            if not existing_product:
                new_product = Product(
                    name=product['name'],
                    description=product['description'],
                    price=product['price'],
                    category=product['category'],
                    image_url=product['image_url'],
                    gender=product.get('gender')  
                )
                db.session.add(new_product)
        db.session.commit()

@app.route('/')
def home():
    categories = db.session.query(
        Product.category, db.func.count(Product.id).label('product_count')
    ).group_by(Product.category).all()
    products = Product.query.all()
    return render_template('home.html', products=products, categories=categories)

@app.route('/search')
def search():
    query = request.args.get('q', '').strip().lower()  
    if query:
        if query in ['women', 'man', 'men']:  
            products = Product.query.filter_by(gender=query.capitalize()).all()
        else:
            
            products = Product.query.filter(
                Product.name.ilike(f"%{query}%") |
                Product.description.ilike(f"%{query}%") |
                Product.category.ilike(f"%{query}%")
            ).all()
    else:
        products = []  
    return render_template('search_results.html', products=products, query=query)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    breadcrumbs = [
        {"name": "ShopEase", "url": "/"},
        {"name": product.category, "url": f"/category/{product.category}"},
        {"name": product.name, "url": f"/product/{product.id}"}
    ]
    return render_template('product_detail.html', product=product, breadcrumbs=breadcrumbs)

@app.route('/category/<category_name>')
def category_view(category_name):
    products = Product.query.filter_by(category=category_name).all()
    if not products:
        return redirect('/')
    return render_template('category.html', category_name=category_name, products=products)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        load_initial_data()
    app.run(debug=True)
