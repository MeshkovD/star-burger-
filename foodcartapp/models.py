from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField('название', max_length=50)
    address = models.CharField('адрес', max_length=100, blank=True)
    contact_phone = models.CharField('контактный телефон', max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'


class ProductQuerySet(models.QuerySet):
    def available(self):
        return self.distinct().filter(menu_items__availability=True)


class ProductCategory(models.Model):
    name = models.CharField('название', max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField('название', max_length=50)
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL,
                                 verbose_name='категория', related_name='products')
    price = models.DecimalField('цена', max_digits=8, decimal_places=2)
    image = models.ImageField('картинка')
    special_status = models.BooleanField('спец.предложение', default=False, db_index=True)
    description = models.TextField('описание', max_length=200, blank=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items',
                                   verbose_name="ресторан")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='menu_items',
                                verbose_name='продукт')
    availability = models.BooleanField('в продаже', default=True, db_index=True)

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]


class Order(models.Model):
    firstname = models.CharField(
        max_length = 255,
        verbose_name = 'Имя',
    )
    lastname = models.CharField(
        max_length = 255,
        verbose_name='Фамилия',
    )
    phone_number = PhoneNumberField(
        unique=True,
        verbose_name='Номер телефона',
    )
    address = models.CharField(
        max_length = 255,
        verbose_name='Адрес',
    )

    def add_product(self, id, quantity):
        OrderElement.objects.create(
            product=Product.objects.get(id=id),
            quantity=quantity,
            order=self
        )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f"Заказ {self.firstname} {self.lastname} {self.address}"


class OrderElement(models.Model):
    product=models.ForeignKey(
        Product,
        related_name = 'product',
        on_delete = models.CASCADE,
        verbose_name = 'Товар',
    )
    quantity = models.IntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)],
        verbose_name='Количество',
    )
    order = models.ForeignKey(
        Order,
        related_name='order_elements',
        on_delete=models.CASCADE,
        verbose_name='Заказ',
    )

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f"Входит в заказ #{self.order.pk} {self.product} ({self.quantity} шт.)"
