import random
from datetime import date
from datetime import time as time_cls
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from restaurant.models import Feedback, Reservation, Restaurant, Table


class Command(BaseCommand):
    help = "Seed the database with test data. Ensures exactly one Restaurant exists."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Seeding database with test data..."))
        restaurant = self._ensure_single_restaurant()
        self.stdout.write(self.style.SUCCESS(f"Using restaurant: {restaurant.name}"))
        tables = self._ensure_tables()
        self.stdout.write(self.style.SUCCESS(f"Ensured {len(tables)} tables exist"))
        self._seed_reservations(tables)
        self._seed_feedback()
        self.stdout.write(self.style.SUCCESS("Seeding completed."))

    def _ensure_single_restaurant(self) -> Restaurant:
        restaurants = list(Restaurant.objects.all().order_by("id"))
        if not restaurants:
            return Restaurant.objects.create(
                name="Demo Bistro",
                address="123 Demo Street",
                phone="+1-555-0100",
                email="demo@bistro.local",
                description=(
                    "Уютный ресторан для демонстрации. Прекрасная кухня и дружелюбный персонал."
                ),
                opening_hours="Пн-Вс 10:00-22:00",
                rating=4.5,
                is_active=True,
            )
        keeper = restaurants[0]
        to_delete = restaurants[1:]
        if to_delete:
            Restaurant.objects.filter(id__in=[r.id for r in to_delete]).delete()
        return keeper

    def _ensure_tables(self) -> list[Table]:
        ensured_tables: list[Table] = []
        default_capacities = {
            1: 2,
            2: 2,
            3: 4,
            4: 4,
            5: 4,
            6: 6,
            7: 6,
            8: 8,
            9: 2,
            10: 4,
        }
        for number in range(1, 11):
            capacity = default_capacities[number]
            table, _ = Table.objects.get_or_create(
                number=number,
                defaults={
                    "capacity": capacity,
                    "description": f"Столик {number} на {capacity} гостей",
                    "is_active": True,
                },
            )
            if table.capacity <= 0:
                table.capacity = capacity
                table.save(update_fields=["capacity"])
            if not table.is_active:
                table.is_active = True
                table.save(update_fields=["is_active"])
            ensured_tables.append(table)
        return ensured_tables

    def _seed_reservations(self, tables: list[Table]) -> None:
        base_date = date.today() + timedelta(days=1)
        slots = [time_cls(12, 0), time_cls(14, 0), time_cls(18, 0), time_cls(20, 0)]
        clients = [
            ("Иван Петров", "+7 900 000-00-01", "ivan@example.com"),
            ("Анна Смирнова", "+7 900 000-00-02", "anna@example.com"),
            ("John Doe", "+1 555 0101", "john@example.com"),
            ("Jane Roe", "+1 555 0102", "jane@example.com"),
        ]
        created_count = 0
        for day_offset in range(0, 4):
            reservation_date = base_date + timedelta(days=day_offset)
            for idx, slot in enumerate(slots):
                if idx >= len(tables):
                    break
                table = tables[idx]
                defaults = {
                    "client_name": clients[idx % len(clients)][0],
                    "client_phone": clients[idx % len(clients)][1],
                    "client_email": clients[idx % len(clients)][2],
                    "guests_count": min(tables[idx].capacity, random.choice([2, 3, 4])),
                    "special_requests": random.choice(
                        [
                            "Окно, пожалуйста",
                            "Высокий стул для ребенка",
                            "Без особых пожеланий",
                        ]
                    ),
                    "status": random.choice(["pending", "confirmed"]),
                }
                _, created = Reservation.objects.get_or_create(
                    table=table,
                    date=reservation_date,
                    time=slot,
                    defaults=defaults,
                )
                if created:
                    created_count += 1
        self.stdout.write(
            self.style.SUCCESS(f"Reservations ensured, created: {created_count}")
        )

    def _seed_feedback(self) -> None:
        samples = [
            {
                "name": "Мария",
                "phone": "+7 900 100-00-01",
                "email": "maria@example.com",
                "subject": "Спасибо!",
                "message": "Очень вкусно и быстро обслужили!",
            },
            {
                "name": "Алексей",
                "phone": "+7 900 100-00-02",
                "email": "alexey@example.com",
                "subject": "Замечания",
                "message": "Шумно около входа, хотелось бы тише.",
            },
        ]
        created_count = 0
        for fb in samples:
            _, created = Feedback.objects.get_or_create(
                name=fb["name"], subject=fb["subject"], defaults=fb
            )
            if created:
                created_count += 1
        self.stdout.write(
            self.style.SUCCESS(f"Feedback ensured, created: {created_count}")
        )
