from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import mysql.connector

app = FastAPI()

templates = Jinja2Templates(directory="templates")


# Database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="enter_your_password",
        database="product"
    )
    return connection


# Home page
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={}
    )


# Display all products
@app.get("/products")
def show_products(request: Request):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    cursor.close()
    connection.close()

    return templates.TemplateResponse(
        request=request,
        name="products.html",
        context={"products": products}
    )


# Display one product
@app.get("/product/{product_id}")
def product_details(request: Request, product_id: int):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM products WHERE id = %s",
        (product_id,)
    )

    product = cursor.fetchone()

    cursor.close()
    connection.close()

    if product is None:
        return {"message": "Product not found"}

    return templates.TemplateResponse(
        request=request,
        name="product.html",
        context={
            "product": product,
            "show_details": True
        }
    )


# Display add product form
@app.get("/add-product")
def add_product_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="product.html",
        context={
            "product": None,
            "show_details": False
        }
    )


# Save product in database
@app.post("/add-product")
def add_product(
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    image_url: str = Form(...)
):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO products (name, description, price, image_url)
        VALUES (%s, %s, %s, %s)
        """,
        (name, description, price, image_url)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return RedirectResponse(
        url="/products",
        status_code=303
    )
