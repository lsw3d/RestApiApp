import random
import math

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from faker import Faker

from db.organizations import Organization
from db.activities import Activity
from db.buildings import Building
from db.phone_numbers import PhoneNumber

fake = Faker()


def shift_coordinates(lat, lon, max_distance_km=30):
    # Примерно смещение широты и долготы на max_distance_km
    # 1 градус широты ~ 111 км
    # 1 градус долготы зависит от широты, примерно 111*cos(lat)

    # Случайный радиус от 0 до max_distance_km
    distance = random.uniform(0, max_distance_km)
    # Случайный угол направления в радианах
    angle = random.uniform(0, 2 * math.pi)

    delta_lat = (distance * math.cos(angle)) / 111  # в градусах
    delta_lon = (distance * math.sin(angle)) / (111 * math.cos(math.radians(lat)))

    return lat + delta_lat, lon + delta_lon


async def fill_tables_with_data(session: AsyncSession):
    # Проверяем заполнены ли данные
    result = await session.execute(select(Activity).limit(1))
    exists = result.scalars().first()

    if exists:
        print("Данные уже заполнены")
        return

    # 1. Создадим несколько зданий
    base_lat = 55.75  # Москва, например
    base_lon = 37.62

    buildings = []

    for _ in range(5):
        lat, lon = shift_coordinates(base_lat, base_lon, max_distance_km=30)
        building = Building(address=fake.address(), latitude=lat, longitude=lon)
        buildings.append(building)
        session.add(building)

    # 2. Создадим дерево видов деятельности
    # Корневые виды
    food = Activity(name="Еда", parent_id=None)
    cars = Activity(name="Автомобили", parent_id=None)
    session.add_all([food, cars])

    # Потомки для "Еда"
    meat = Activity(name="Мясная продукция", parent=food)
    dairy = Activity(name="Молочная продукция", parent=food)

    # Потомки для "Автомобили"
    trucks = Activity(name="Грузовые", parent=cars)
    passenger = Activity(name="Легковые", parent=cars)
    parts = Activity(name="Запчасти", parent=passenger)
    accessories = Activity(name="Аксессуары", parent=passenger)

    session.add_all([meat, dairy, trucks, passenger, parts, accessories])

    await session.flush()  # Чтобы получить id для зависимостей

    # 3. Создадим организации
    org_names = [
        "ООО Рога и Копыта",
        "ЗАО Молочная Лавка",
        "ИП Мясной Дом",
        "АвтоПлюс",
        "ТехноМир",
    ]
    organizations = []
    for name in org_names:
        org = Organization(name=name, building=random.choice(buildings))
        session.add(org)
        organizations.append(org)

    # 4. Добавим номера телефонов и виды деятельности организациям
    for org in organizations:
        # Добавим 1-3 номера телефона
        for _ in range(random.randint(1, 3)):
            phone = PhoneNumber(number=fake.phone_number(), organization=org)
            session.add(phone)

        # Назначим 1-2 случайных деятельности
        possible_activities = [
            food,
            meat,
            dairy,
            cars,
            trucks,
            passenger,
            parts,
            accessories,
        ]
        org.activities = random.sample(possible_activities, k=random.randint(1, 2))

    await session.commit()
