from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Product, Order


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    request = request.data
    if not request.get("products") or not isinstance(request.get("products"), list):
        return Response({"error": "products: Этот list не может быть пустым и не может быть null или его нет"},
                        status=status.HTTP_400_BAD_REQUEST)
    product_count = Product.objects.count()
    for product in request.get("products"):
        if not 0 <= product["product"] <= product_count:
            return Response({"error": f"products: Недопустимый первичный ключ {product["product"]}"},
                            status=status.HTTP_400_BAD_REQUEST)
    if not request.get("firstname") or not isinstance(request.get("firstname"), str):
        return Response({"error": "firstname: Этот str не может быть пустым и не может быть null или его нет"},
                        status=status.HTTP_400_BAD_REQUEST)
    if not request.get("lastname") or not isinstance(request.get("lastname"), str):
        return Response({"error": "lastname: Этот str не может быть пустым и не может быть null или его нет"},
                        status=status.HTTP_400_BAD_REQUEST)
    if not request.get("phonenumber") or not isinstance(request.get("phonenumber"), str):
        return Response({"error": "phonenumber: Этот str не может быть пустым и не может быть null или его нет"},
                        status=status.HTTP_400_BAD_REQUEST)
    elif not PhoneNumber.from_string(phone_number=request.get("phonenumber"), region="RU").is_valid():
        return Response({"error": "phonenumber: Введен некорректный номер телефона"},
                        status=status.HTTP_400_BAD_REQUEST)
    if not request.get("address") or not isinstance(request.get("address"), str):
        return Response({"error": "address: Этот str не может быть пустым и не может быть null или его нет"},
                        status=status.HTTP_400_BAD_REQUEST)
    try:
        order = Order.objects.create(
            firstname=request.get("firstname"),
            lastname=request.get("lastname"),
            phonenumber=request.get("phonenumber"),
            address=request.get("address"),
        )
        for product in request.get("products"):
            order.orders.create(
                product=Product.objects.get(id=product.get("product")),
                count=product.get("quantity"),
            )
        return Response({"status": "200"})
    except ValueError:
        return Response({"error": "ValueError"}, status=status.HTTP_400_BAD_REQUEST)
