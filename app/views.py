import datetime
import stripe

from flask import abort, flash, redirect, render_template, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message

from app.models import *
from app.config import *


@login.user_loader
def load_user(id):
    return db.session.query(User).filter_by(id=id).first()

@app.route("/", methods=["POST", "GET"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        id = request.form.get("id")
        is_seller = request.form.get("is_seller")

        is_signed_up = bool(db.session.query(User.email).filter_by(email=email).first())

        if email != None and password != None and len(email) > 6 and len(password) > 6:
            if is_seller == "I'm a merchant":
                new_user = User(id=id, email=email, password=generate_password_hash(password), is_seller=True)

                if is_signed_up:
                    flash("This email address is already in use")
                    return render_template("index.html")

                db.session.add(new_user)
                db.session.commit()
            else:
                new_user = User(id=id, email=email, password=generate_password_hash(password), is_seller=False)

                if is_signed_up: 
                    flash("This email address is already in use")
                    return render_template("index.html")

                db.session.add(new_user)
                db.session.commit()

            return redirect("/signin")
        else:
            flash("Email or password is too short")
            return render_template("index.html")
    elif request.method == "GET" and current_user.is_authenticated:
        return redirect("/home")       

    return render_template("index.html")


@app.route("/signin", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.session.query(User).filter_by(email=email).first()
        does_exist = bool(user)
        
        if does_exist and len(email) > 6 and len(password) > 6 and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/home")
        
        flash("Email or password is invalid")
        return render_template("signin.html")
    elif request.method == "GET" and current_user.is_authenticated:
        return redirect("/home")

    return render_template("signin.html")


@app.route("/home", methods=["GET"])
@login_required
def home():
    return render_template("home.html")


@app.route("/merchant/edit", methods=["GET", "POST"])
@login_required
def merchant_home():
    if current_user.is_seller == False:
        return redirect("/home")    

    choice = request.args.get("del")
    save_or_del = request.form.get("edit")
    url_id = request.args.get("id")

    if request.method == "POST":
        id = request.form.get("id")
        name = request.form.get("name")
        price = request.form.get("price")
        image = request.form.get("image")
        desc = request.form.get("desc")

        if choice is None and name is not None:
            new_product = db.session.query(Product).filter_by(name=name.capitalize()).first()
            is_in_stock = bool(new_product)
            
            if not is_in_stock and len(name) > 0 and len(price) > 0 and len(image) > 0: 
                save_new_product = Product(id=id, name=name, price=price, image=image, desc=desc, seller=current_user.id)

                db.session.add(save_new_product)
                db.session.commit()
                flash("Product added successfully!")
            else:
                flash("Another product with this name already exists or some required fields are left blank!")

    if choice == "True":
        items_by_seller = db.session.query(Product).filter_by(seller=current_user.id)

        if url_id != None:
            new_name = request.form.get("new_name")
            new_price = request.form.get("new_price")
            new_img = request.form.get("new_img")
            new_desc = request.form.get("new_desc")

            item_to_be_updated = db.session.query(Product).filter_by(seller=current_user.id, id=url_id).first()
            if save_or_del == "Save":
                if new_name != None:
                    item_to_be_updated.name = new_name
                if new_price != None:
                    item_to_be_updated.price = new_price
                if new_img != None:
                    item_to_be_updated.img = new_img
                if new_desc != None:
                    item_to_be_updated.desc = new_desc    
            elif save_or_del == "Delete":
                db.session.delete(item_to_be_updated)
            db.session.commit()

        return render_template("addproduct.html", deletion=True, data=items_by_seller)

    return render_template("addproduct.html")

    
@app.route("/products", methods=["GET", "POST"])
@login_required
def products():
    page = request.args.get("page", 1, type=int)
    product_hl = Product.query.order_by(Product.price.desc()).paginate(page=page, per_page=12)

    if request.method == "POST":
        sorting = request.form.get("option")
        query = request.form.get("searchbar")
        
        # List items by search params
        if query != None:
            products_to_return = Product.query.filter(Product.name.contains(query.lower())).order_by(Product.price.desc()).paginate(page=page, per_page=12)
            return render_template("products.html", sorting=sorting, data=products_to_return)

        if sorting == "Highest to lowest":
            return render_template("products.html", sorting=sorting, data=product_hl)
        elif sorting == "Lowest to highest":
            product_lh = Product.query.order_by(Product.price.asc()).paginate(page=page, per_page=12)
            return render_template("products.html", sorting=sorting, data=product_lh)

    return render_template("products.html", data=product_hl)


@app.route("/products/details", methods=["GET", "POST"])
@login_required
def detailed_view():
    item_id = request.args.get("item_id")
    product = db.session.query(Product).filter_by(id=item_id).first()
    order = db.session.query(Order).filter_by(product_id=item_id, customer_id=current_user.id, is_done=False).first()
    orders_bool = bool(order)
    
    if request.method == "POST":
        id = request.form.get("id")
        quantity_raw = request.form.get("form_qtn")
        
        if quantity_raw != None:
            quantity = int(quantity_raw)

            if quantity <= 0:
                abort(400, "0 and/or negative numbers are invalid units of quantity")

            # if such order exists update the quantity value instead of adding a new row
            if orders_bool:
                order.quantity = quantity
            elif product != None:    
                new_order = Order(id=id, customer_id=current_user.id, product_id=item_id, product_name=product.name, product_unit_price=product.price, quantity=quantity, is_done=False, seller_id=product.seller)
                db.session.add(new_order)

            db.session.commit()
            return render_template("shop-details.html", data=item_id, product=product, quantity=quantity)

    return render_template("shop-details.html", data=item_id, product=product, quantity=1)


@app.route("/products/cart", methods=["GET", "POST"])
@login_required
def cart():
    get_all_by_user = db.session.query(Order).filter_by(customer_id=current_user.id, is_done=False).all()
    user_cart = []
    total_price = []

    for item in get_all_by_user:
        item_obj = db.session.query(Product).filter_by(id=item.product_id).first()
        user_cart.append(item_obj)

    for idx, i in enumerate(user_cart):
        try:
            total_price.append(i.price * get_all_by_user[idx].quantity)
        except AttributeError:
            continue   

    # remove item from cart
    if request.method == "POST":
        item_id = request.form.get("id")
        db.session.query(Order).filter_by(customer_id=current_user.id, product_id=item_id, is_done=False).delete()
        db.session.commit()
        
        return redirect("/products/cart")

    try:
        return render_template("shopping-cart.html", user_cart=user_cart, quantity=get_all_by_user, total=total_price)
    except UnboundLocalError:
        return render_template("shopping-cart.html", user_cart=user_cart, quantity=1, total=total_price) 


@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    user_cart = db.session.query(Order).filter_by(customer_id=current_user.id, is_done=False).all()
    total_price = []

    for i in user_cart:
        check_query = db.session.query(Product).filter_by(name=i.product_name).first()
        check = bool(check_query)
        
        if check == True:
            total_price.append(i.product_unit_price * i.quantity)
        else:
            db.session.query(Order).filter_by(product_name=i.product_name).delete()
            cart_updated = db.session.query(Order).filter_by(customer_id=current_user.id, is_done=False).all()
            db.session.commit()

            return render_template("checkout.html", total_price=total_price, cart=cart_updated)        
    
    if request.method == "POST":
        # Invoice data
        name = request.form.get("name")
        last_name = request.form.get("last_name")        
        address = request.form.get("address")
        city = request.form.get("city")        
        state = request.form.get("state")        
        zip = request.form.get("zip")        
        phone = request.form.get("phone")        
        email = request.form.get("email")

        if name != None and last_name != None and address != None and email != None and phone != None:
            if len(name) > 0 and len(last_name) > 0 and len(address) > 0 and len(email) > 0 and len(phone) > 0 and len(city) > 0 and len(state) > 0:
                user_cart[0].customer_name = name.capitalize()
                user_cart[0].customer_last_name = last_name.capitalize()
                user_cart[0].customer_email = email
                user_cart[0].customer_phone = phone

                if zip == "":
                    user_cart[0].address = f"{address}, {city.capitalize()} / {state.capitalize()}"
                else:
                    user_cart[0].address = f"{address} {zip}, {city.capitalize()} / {state.capitalize()}"

                db.session.commit()

                # Credit/Debit card data
                # api_key is a public test key
                stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"
                session = stripe.checkout.Session.create(
                    line_items=[{
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": "Carrito Purchase",
                            },
                            "unit_amount": round((sum(total_price) * 100)),
                        },
                        "quantity": 1
                    }],
                    mode="payment",
                    success_url="https://carrito.onrender.com/checkout/success",
                    cancel_url="https://carrito.onrender.com/localhost:5000/checkout"
                )

                return redirect(session.url, 303)
            else:
                flash("Missing required fields!")    
                return render_template("checkout.html", total_price=total_price, cart=user_cart)

    return render_template("checkout.html", total_price=total_price, cart=user_cart)


@app.route("/checkout/success", methods=["GET"])
def order_success():
    try:
        order = db.session.query(Order).filter_by(customer_id=current_user.id, is_done=False).all()
    except AttributeError:
        return redirect("/home")
        
    if current_user == False or len(order) == 0:
        return redirect("/home")

    html_orders = []
    total = []
    items_for_pending = []
    order_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for i in order:
        html_orders.append(f"{i.product_name} | Price: ${i.product_unit_price}, Qtn: {i.quantity} <br/>")
        items_for_pending.append(f" {i.product_name} x {i.quantity}, ")
        total.append(i.product_unit_price * i.quantity)

    msg = Message(
        "We have your order! 📦", 
        sender="service.carrito@gmail.com", 
        recipients=[order[0].customer_email]
    )

    # Email html template
    msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <meta http-equiv="X-UA-Compatible" content="ie=edge" />
        </head>
        
        <body style='
                    font-family: 'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande',
                'Lucida Sans', Arial, sans-serif;'>
            <p>We've received your order!</p><h3>Please wait for the seller to approve or reject your order.</h3>
            
            <h2><ins>Order Summary</ins></h2>
            <div>
                <b style='color: #dd1313'>Date: </b><span>{order_date}</span> <br>
                <b style='color: #dd1313'>Name & Last Name: </b><span>{order[0].customer_name} {order[0].customer_last_name}</span> <br>
                <b style='color: #dd1313'>Email: </b> <span>{order[0].customer_email}</span> <br>
                <b style='color: #dd1313'>Shipping Address: </b> <span>{(order[0].address).upper()}</span> <br> <br>
                <b style='color: #dd1313'>Purchased Items: </b>
                <h4 style='font-weight: 500 !important;'>{"".join(html_orders)}</h4>
                <h4>Total Price: <span style='color:#2bb673'>${round(sum(total), 2)}</span> </h4>

                <h5>Enjoy shopping on Carrito!</h5>
                <span style='color:gray'>Carrito, {order_date[0:4]} - All rights reserved.</span>   
            </div>            
        </body>
        </html>
    """
    mail.send(msg)

    mark_as_done = db.session.query(Order).filter_by(customer_id=current_user.id, is_done=False).all()
    for i in mark_as_done:
        i.is_done = True

    create_pending = PendingOrders(
        date=order_date, 
        customer_id=order[0].customer_id,
        product_quantity="".join(items_for_pending), 
        total=round(sum(total), 2), 
        address=(order[0].address).upper(), 
        customer_email=order[0].customer_email, 
        seller_id=order[0].seller_id
    )

    db.session.add(create_pending)
    db.session.commit()

    return render_template("success.html")


@app.route("/merchant/pending", methods=["GET"])
@login_required
def merchant_pending():
    if current_user.is_seller == False:
        return redirect("/home")

    order_accept = request.args.get("accept")
    order_delete = request.args.get("reject")

    orders_by_seller = db.session.query(PendingOrders).filter_by(seller_id=current_user.id)

    # Approval & Deletion check
    if order_accept != None:
        item = db.session.query(PendingOrders).filter_by(seller_id=current_user.id, id=order_accept).first()
        item_bool = bool(item)
        
        if item_bool:
            msg = Message(
                "Your Order is Complete! ✅", 
                sender="service.carrito@gmail.com", 
                recipients=[item.customer_email]
            )

            # Email html template
            msg.html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                    <meta http-equiv="X-UA-Compatible" content="ie=edge" />
                </head>
                
                <body style='
                            font-family: 'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande',
                        'Lucida Sans', Arial, sans-serif;'>
                    <p>Seller received & approved your order!</p><h3>Thank you for your purchase.</h3>
                    
                    <h2><ins>Order Summary</ins></h2>
                    <div>
                        <b style='color: #dd1313'>Date: </b><span>{item.date}</span> <br>
                        <b style='color: #dd1313'>Customer ID: </b><span>{item.customer_id}</span> <br>
                        <b style='color: #dd1313'>Email: </b> <span>{item.customer_email}</span> <br>
                        <b style='color: #dd1313'>Shipping Address: </b> <span>{(item.address).upper()}</span> <br> <br>
                        <b style='color: #dd1313'>Purchased Items: </b>
                        <h4 style='font-weight: 500 !important;'>{"".join(item.product_quantity)}</h4>
                        <h4>Total Price: <span style='color:#2bb673'>${item.total}</span> </h4>

                        <h5>Enjoy shopping on Carrito!</h5>
                        <span style='color:gray'>Carrito, {item.date[0:4]} - All rights reserved.</span>   
                    </div>            
                </body>
                </html>
            """ 
            mail.send(msg)
            db.session.delete(item)
            db.session.commit()

            return render_template("approveorders.html", data=orders_by_seller)

    elif order_delete != None:
        item = db.session.query(PendingOrders).filter_by(seller_id=current_user.id, id=order_delete).first()
        item_bool = bool(item)

        if item_bool:
            msg = Message(
                "Seller rejected your order!", 
                sender="service.carrito@gmail.com", 
                recipients=[item.customer_email]
            )

            # Email html template
            msg.html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8" />
                    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                    <meta http-equiv="X-UA-Compatible" content="ie=edge" />
                </head>
                
                <body style='
                            font-family: 'Trebuchet MS', 'Lucida Sans Unicode', 'Lucida Grande',
                        'Lucida Sans', Arial, sans-serif;'>
                    <p>Unfortunately, seller rejected your order!</p><h3>Thank you for choosing Carrito.</h3>
                    
                    <h2><ins>Failed Order Summary</ins></h2>
                    <div>
                        <b style='color: #dd1313'>Date: </b><span>{item.date}</span> <br>
                        <b style='color: #dd1313'>User ID: </b><span>{item.customer_id}</span> <br>
                        <b style='color: #dd1313'>Email: </b> <span>{item.customer_email}</span> <br>
                        <b style='color: #dd1313'>Shipping Address: </b> <span>{(item.address).upper()}</span> <br> <br>
                        <b style='color: #dd1313'>Purchased Items: </b>
                        <h4 style='font-weight: 500 !important;'>{"".join(item.product_quantity)}</h4>
                        <h4>Total Price: <span style='color:#2bb673'>${item.total}</span> </h4>
                        <h4>${item.total} will be transferred back to your account within 3 to 5 business days.</h4>
                        <h5>Enjoy shopping on Carrito!</h5>
                        <span style='color:gray'>Carrito, {item.date[0:4]} - All rights reserved.</span>   
                    </div>            
                </body>
                </html>
            """ 
            mail.send(msg)
            db.session.delete(item)
            db.session.commit()

            return render_template("approveorders.html", data=orders_by_seller)

    return render_template("approveorders.html", data=orders_by_seller)


@app.route("/about", methods=["GET"])
@login_required
def about():
    return render_template("about.html")


@app.route("/signout", methods=["GET"])
def sign_out():
    if current_user.is_authenticated:
        logout_user()

    return redirect("/signin")
    
