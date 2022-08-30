# Carrito (E-commerce Website)

\*Carrito is an ecommerce website powered by mainly Python's <b>Flask</b> framework. <br>
Live demo is available on: [carrito.pythonanywhere.com](https://carrito.pythonanywhere.com)

---

## What is it capable of?

Shortly, most of the e-commerce features that you can think of are also available on Carrito. <br>

- In this app, there are two types of users. There is a customer and merchant profile, however as merchants can create new orders from other merchants they are also eligible becoming a customer. <br><b>Important</b>: Account type is being chosen at signing up process and it is a permanent choice.

### Customers can

- Search for products by name or choose to view products in ascending or descending order at <code>/products</code>

- Go to a page dedicated to the product they wish to inspect, where they can add the product to their cart or _Carrito_ with data containing quantity of the product.

After proceeding to `/checkout` and successfully submitting the form a checkout session will begin. This process is handled by <b>Stripe</b>. <br> Since this application is a demo, you can simulate a successful purchase by using <b>4242 4242 4242 4242</b> as card number, and enter a valid, Valid Until date. If you've done all of that right, the mail adress you've just put in the form at `/checkout` will receive an email saying "You've placed your order!" and will redirect you to another route displaying a similar message.

### Merchants can

- Anything a customer can do.
- Add a product to the database. And, they can delete or edit already existing products.

  > If a product gets deleted while a user has it in their cart, the item will be removed from their cart.

- Merchants have some private pages, which are unaccessable for customers (app automatically redirects them to `/home` if they try sending a request to the endpoint). After a user places an order containing at least one of merchant's items, at `merchant/pending` merchants will see the orders can approve or reject their orders. <br>
  According to the merchant's choice on order, customer receives another email about current status of their order and after that, customer's cart and merchant's pending orders get deleted.

---

_I did not use any client-side frameworks or libraries other than jQuery in order to practice <b>jinja2</b> template engine._

<small><span style="color:red"> \* </span>Carrito is a Spanish word for cart. As it sounds fancier in Spanish I chose that as a mock-up brand name.</small>
