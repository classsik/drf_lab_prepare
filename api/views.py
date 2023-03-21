from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from .models import Product, Cart, Order
from .serializers import UserSerializer, ProductSerializer, CartSerializer, OrderSerializer


@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    if email is None or password is None:
        return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)
    user = authenticate(email=email, password=password)
    if not user:
        return Response({'error': {
            'code': 401,
            'message': 'Authentication failed'
        }}, status=status.HTTP_401_UNAUTHORIZED)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'user_token': token.key}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {'user_token': token.key}, status=status.HTTP_201_CREATED
        )
    else:
        return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, data={
            'error': {
                'code': 422,
                'message': 'Validation error',
                'errors': serializer.errors
            }
        })


@api_view(["GET"])
def logout(request):
    Token.objects.get(user=request.user).delete()

    return Response(status=status.HTTP_200_OK, data={
        "data": {
            "message": "logout"
        }})


@api_view(["GET"])
@permission_classes((AllowAny,))
def all_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user)
    cart.products.add(product)
    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def remove_from_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user)
    cart.products.remove(product)
    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def get_cart(request):
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user)
    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def create_order(request):
    user = request.user
    cart, _ = Cart.objects.get_or_create(user=user)

    if cart.products.count() != 0:
        products = cart.products.all()
        total = 0

        for product in products:
            total += product.price

        order = Order.objects.create(total_price=total)
        order.products.set(products)
        order.save()

        cart.products.clear()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_orders(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def create_product(request):
    if request.user.is_staff:
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(["PATCH"])
def edit_product(request, product_id):
    if request.user.is_staff:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(data=request.data, instance=product)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['DELETE'])
def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    product.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
