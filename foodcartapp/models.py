from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def get_restaurants_for_order(self):
        menu_items = RestaurantMenuItem.objects.filter(availability=True).select_related("restaurant", "product")
        for order in self:
            restaurant = []
            for ordered_product in order.orders.values("product"):
                restaurant.append([menu_item.restaurant for menu_item in menu_items
                                   if ordered_product["product"] == menu_item.product.id])
            order.selected_restaurants = restaurant[0]
        return self


class Order(models.Model):
    class StatusChoice(models.TextChoices):
        MANAGER = "M", "Передан менеджеру"
        RESTAURANT = "R", "Передан ресторану"
        COURIER = "C", "Передан курьеру"
        PROCESSED = "P", "Обработанный"

    class PaymentChoice(models.TextChoices):
        CASH = "C", "Наличные"
        NONCASH = "N", "Безналичные"

    status = models.CharField(max_length=1, choices=StatusChoice.choices, verbose_name="Статус", db_index=True,
                              default=StatusChoice.MANAGER)
    firstname = models.CharField(max_length=20, verbose_name="Имя")
    lastname = models.CharField(max_length=20, verbose_name="Фамилия")
    phonenumber = PhoneNumberField(region="RU", db_index=True, verbose_name="Телефон")
    address = models.TextField(verbose_name="Адрес доставки")
    comment = models.TextField(max_length=200, verbose_name="Комментарий", blank=True)
    registered_at = models.DateTimeField(verbose_name="Зарегистрирован в", default=timezone.now)
    called_at = models.DateTimeField(verbose_name="Позвонили в", db_index=True, blank=True, null=True)
    delivered_at = models.DateTimeField(verbose_name="Доставлен в", db_index=True, blank=True, null=True)
    payment = models.CharField(max_length=1, choices=PaymentChoice.choices, verbose_name="Способ оплаты", db_index=True,
                               default=PaymentChoice.CASH)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, verbose_name="ресторан", blank=True, null=True,
                                   related_name="restaurants")

    objects = OrderQuerySet.as_manager()

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderElement(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name="Заказ",
        related_name="orders"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="товар",
        related_name="products",
    )
    price = models.DecimalField(verbose_name="цена заказа", max_digits=8, decimal_places=2,
                                validators=[MinValueValidator(0)], default=0)
    quantity = models.IntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
