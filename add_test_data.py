import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from restaurant.models import DishCategory, Dish

# Создаем категории блюд
categories = [
    {
        'name': 'Закуски',
        'description': 'Легкие блюда для начала трапезы',
        'slug': 'zakuski'
    },
    {
        'name': 'Основные блюда',
        'description': 'Сытные и вкусные основные блюда',
        'slug': 'osnovnye-blyuda'
    },
    {
        'name': 'Десерты',
        'description': 'Сладкие блюда для завершения трапезы',
        'slug': 'deserty'
    },
    {
        'name': 'Напитки',
        'description': 'Освежающие и согревающие напитки',
        'slug': 'napitki'
    }
]

# Создаем категории
created_categories = {}
for category_data in categories:
    category, created = DishCategory.objects.get_or_create(
        slug=category_data['slug'],
        defaults={
            'name': category_data['name'],
            'description': category_data['description']
        }
    )
    created_categories[category.name] = category
    print(f"Категория {'создана' if created else 'уже существует'}: {category.name}")

# Создаем блюда
dishes = [
    # Закуски
    {
        'name': 'Карпаччо из говядины',
        'slug': 'karpachcho-iz-govyadiny',
        'category': 'Закуски',
        'description': 'Тонко нарезанная маринованная говядина с рукколой и пармезаном',
        'ingredients': 'Говядина, руккола, пармезан, оливковое масло, лимонный сок',
        'price': 590,
        'is_special': True,
        'is_vegetarian': False,
        'is_spicy': False
    },
    {
        'name': 'Брускетта с томатами',
        'slug': 'brusketta-s-tomatami',
        'category': 'Закуски',
        'description': 'Хрустящий багет с томатами, базиликом и чесноком',
        'ingredients': 'Багет, томаты, базилик, чеснок, оливковое масло',
        'price': 350,
        'is_special': False,
        'is_vegetarian': True,
        'is_spicy': False
    },
    {
        'name': 'Тартар из лосося',
        'slug': 'tartar-iz-lososya',
        'category': 'Закуски',
        'description': 'Свежий лосось с авокадо, каперсами и красным луком',
        'ingredients': 'Лосось, авокадо, каперсы, красный лук, соевый соус',
        'price': 650,
        'is_special': False,
        'is_vegetarian': False,
        'is_spicy': False
    },
    
    # Основные блюда
    {
        'name': 'Стейк Рибай',
        'slug': 'steik-ribai',
        'category': 'Основные блюда',
        'description': 'Сочный стейк из мраморной говядины с картофельным пюре и соусом демиглас',
        'ingredients': 'Говядина, картофель, сливочное масло, розмарин, тимьян',
        'price': 1590,
        'is_special': True,
        'is_vegetarian': False,
        'is_spicy': False
    },
    {
        'name': 'Паста Карбонара',
        'slug': 'pasta-karbonara',
        'category': 'Основные блюда',
        'description': 'Классическая итальянская паста с беконом, яйцом и сыром пекорино',
        'ingredients': 'Спагетти, бекон, яйцо, сыр пекорино, черный перец',
        'price': 590,
        'is_special': False,
        'is_vegetarian': False,
        'is_spicy': False
    },
    {
        'name': 'Ризотто с грибами',
        'slug': 'rizotto-s-gribami',
        'category': 'Основные блюда',
        'description': 'Кремовое ризотто с белыми грибами и трюфельным маслом',
        'ingredients': 'Рис арборио, белые грибы, лук-шалот, сливочное масло, трюфельное масло',
        'price': 690,
        'is_special': False,
        'is_vegetarian': True,
        'is_spicy': False
    },
    {
        'name': 'Острая курица по-тайски',
        'slug': 'ostraya-kuritsa-po-taiski',
        'category': 'Основные блюда',
        'description': 'Жареная курица с овощами в остром соусе с рисом',
        'ingredients': 'Куриное филе, перец чили, имбирь, чеснок, соевый соус, рис',
        'price': 550,
        'is_special': False,
        'is_vegetarian': False,
        'is_spicy': True
    },
    
    # Десерты
    {
        'name': 'Тирамису',
        'slug': 'tiramisu',
        'category': 'Десерты',
        'description': 'Классический итальянский десерт с кофе и маскарпоне',
        'ingredients': 'Печенье савоярди, маскарпоне, кофе, какао, яйца',
        'price': 390,
        'is_special': False,
        'is_vegetarian': True,
        'is_spicy': False
    },
    {
        'name': 'Шоколадный фондан',
        'slug': 'shokoladnyi-fondan',
        'category': 'Десерты',
        'description': 'Теплый шоколадный кекс с жидкой начинкой и ванильным мороженым',
        'ingredients': 'Темный шоколад, сливочное масло, яйца, мука, ванильное мороженое',
        'price': 450,
        'is_special': True,
        'is_vegetarian': True,
        'is_spicy': False
    },
    
    # Напитки
    {
        'name': 'Домашний лимонад',
        'slug': 'domashnii-limonad',
        'category': 'Напитки',
        'description': 'Освежающий лимонад с мятой и имбирем',
        'ingredients': 'Лимон, мята, имбирь, сахар, газированная вода',
        'price': 250,
        'is_special': False,
        'is_vegetarian': True,
        'is_spicy': False
    },
    {
        'name': 'Глинтвейн',
        'slug': 'glintveyn',
        'category': 'Напитки',
        'description': 'Согревающий напиток из красного вина со специями',
        'ingredients': 'Красное вино, корица, гвоздика, апельсин, мед',
        'price': 350,
        'is_special': True,
        'is_vegetarian': True,
        'is_spicy': False
    }
]

# Создаем блюда
for dish_data in dishes:
    category = created_categories[dish_data['category']]
    dish, created = Dish.objects.get_or_create(
        slug=dish_data['slug'],
        defaults={
            'name': dish_data['name'],
            'category': category,
            'description': dish_data['description'],
            'ingredients': dish_data['ingredients'],
            'price': dish_data['price'],
            'is_special': dish_data['is_special'],
            'is_vegetarian': dish_data['is_vegetarian'],
            'is_spicy': dish_data['is_spicy']
        }
    )
    print(f"Блюдо {'создано' if created else 'уже существует'}: {dish.name}")

print("Тестовые данные успешно добавлены!")