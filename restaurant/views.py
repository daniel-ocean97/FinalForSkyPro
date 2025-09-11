import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from restaurant.forms import (ReservationEditForm, ReservationStep1Form,
                              ReservationStep2Form, ReservationStep3Form)
from restaurant.services import calculate_available_times, get_available_tables

from .models import Feedback, Reservation, Restaurant, Table


def restaurant_detail(request):
    # Получаем активный ресторан (например, первый)
    restaurant = get_object_or_404(Restaurant, is_active=True)
    return render(
        request, "restaurant/restaurant_detail.html", {"restaurant": restaurant}
    )


def contacts(request):
    restaurant = Restaurant.objects.first()

    if request.method == "POST":
        # Обработка формы
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        feedback = Feedback.objects.create(
            name=name, phone=phone, email=email, subject=subject, message=message
        )
        feedback.save()

        messages.success(
            request, "Ваше сообщение отправлено! Мы свяжемся с вами в ближайшее время."
        )
        return redirect("restaurant:contacts")

    return render(request, "restaurant/contacts.html", {"restaurant": restaurant})


def about(request):
    restaurant = Restaurant.objects.first()
    return render(request, "restaurant/about.html", {"restaurant": restaurant})


def reservation(request):
    restaurant = Restaurant.objects.first()
    today = timezone.now().date()

    step = request.GET.get("step", "1")

    form = None
    available_hours = []
    reservation_data = request.session.get("reservation_data", {})
    show_success_modal = request.GET.get("success") == "true"
    last_reservation = request.session.get("last_reservation", {})
    tables_with_availability = []

    display_date = ""
    table_number = ""

    # Обработка POST-запросов
    if request.method == "POST":
        if step == "1":
            form = ReservationStep1Form(request.POST)
            if form.is_valid():
                request.session["reservation_data"] = {
                    "date": form.cleaned_data["date"].isoformat(),
                    "time": form.cleaned_data["time"].strftime("%H:%M"),
                    "guests_count": form.cleaned_data["guests_count"],
                }
                return redirect(reverse("restaurant:reservation") + "?step=2")
            else:
                # Если форма невалидна, пересчитываем доступное время
                date_str = request.POST.get("date")
                guests_count = request.POST.get("guests_count", 2)

                try:
                    if date_str:
                        selected_date = datetime.datetime.strptime(
                            date_str, "%Y-%m-%d"
                        ).date()
                        guests_count = int(guests_count)
                        available_hours = calculate_available_times(
                            selected_date, guests_count
                        )
                except (ValueError, TypeError):
                    available_hours = []

                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")

        elif step == "2":
            # Получаем данные из сессии
            date_str = reservation_data.get("date", "")
            time_str = reservation_data.get("time", "")
            guests_count = int(reservation_data.get("guests_count", 2))

            if not date_str or not time_str:
                messages.error(request, "Сначала выберите дату и время")
                return redirect(reverse("restaurant:reservation") + "?step=1")

            try:
                selected_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                selected_time = datetime.datetime.strptime(time_str, "%H:%M").time()

                # Получаем столики с информацией о доступности
                tables_with_availability = get_available_tables(
                    selected_date, selected_time, guests_count
                )

                # Создаем форму с доступными столиками
                available_table_ids = [
                    t.id for t in tables_with_availability if t.available
                ]
                form = ReservationStep2Form(request.POST)
                form.fields["table"].queryset = Table.objects.filter(
                    id__in=available_table_ids
                )

                if form.is_valid():
                    reservation_data = request.session.get("reservation_data", {})
                    reservation_data["table"] = form.cleaned_data["table"].id
                    request.session["reservation_data"] = reservation_data
                    return redirect(reverse("restaurant:reservation") + "?step=3")
                else:
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(
                                request, f"{form.fields[field].label}: {error}"
                            )

            except (ValueError, TypeError):
                messages.error(request, "Ошибка в данных бронирования")
                return redirect(reverse("restaurant:reservation") + "?step=1")

        elif step == "3":
            form = ReservationStep3Form(request.POST)
            if form.is_valid():
                reservation_data = request.session.get("reservation_data", {})
                reservation = form.save(commit=False)

                reservation.date = datetime.datetime.strptime(
                    reservation_data.get("date"), "%Y-%m-%d"
                ).date()
                reservation.time = datetime.datetime.strptime(
                    reservation_data.get("time"), "%H:%M"
                ).time()
                reservation.guests_count = reservation_data.get("guests_count")
                reservation.table_id = reservation_data.get("table")
                # Привязываем пользователя, если он авторизован
                if request.user.is_authenticated:
                    reservation.user = request.user
                reservation.save()

                request.session["last_reservation"] = {
                    "date": reservation.date.isoformat(),
                    "time": reservation.time.strftime("%H:%M"),
                    "guests_count": reservation.guests_count,
                    "table_number": reservation.table.number,
                    "table_description": reservation.table.description,
                    "client_name": reservation.client_name,
                    "client_phone": reservation.client_phone,
                    "client_email": reservation.client_email,
                    "special_requests": reservation.special_requests,
                }

                request.session.pop("reservation_data", None)
                return redirect(reverse("restaurant:reservation") + "?success=true")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")

    # Обработка GET-запросов
    if step == "2":
        # Получаем данные из сессии
        date_str = reservation_data.get("date", "")
        time_str = reservation_data.get("time", "")
        guests_count = int(reservation_data.get("guests_count", 2))

        if not date_str or not time_str:
            messages.error(request, "Сначала выберите дату и время")
            return redirect(reverse("restaurant:reservation") + "?step=1")

        try:
            selected_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            selected_time = datetime.datetime.strptime(time_str, "%H:%M").time()

            # Получаем столики с информацией о доступности
            tables_with_availability = get_available_tables(
                selected_date, selected_time, guests_count
            )

            # Создаем форму с доступными столиками ДЛЯ GET-запроса
            form = ReservationStep2Form()
            available_table_ids = [
                t.id for t in tables_with_availability if t.available
            ]
            form.fields["table"].queryset = Table.objects.filter(
                id__in=available_table_ids
            )

        except (ValueError, TypeError):
            messages.error(request, "Ошибка в данных бронирования")
            return redirect(reverse("restaurant:reservation") + "?step=1")

    elif step == "1":
        if form is None:
            form = ReservationStep1Form(initial=reservation_data)

        # Всегда рассчитываем доступное время для шага 1
        date_str = reservation_data.get("date", "")
        guests_count = int(reservation_data.get("guests_count", 2))

        if date_str:
            try:
                selected_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                available_hours = calculate_available_times(selected_date, guests_count)
            except (ValueError, TypeError):
                available_hours = []
        else:
            # Если дата не выбрана, показываем доступное время для сегодняшнего дня
            try:
                available_hours = calculate_available_times(today, guests_count)
            except (ValueError, TypeError):
                available_hours = []

    elif step == "3":
        # Подготовка данных для отображения
        date_str = reservation_data.get("date", "")
        time_str = reservation_data.get("time", "")
        table_id = reservation_data.get("table", "")

        # Форматирование даты для отображения
        display_date = ""
        if date_str:
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                # Форматируем дату по-русски (например: "15 мая")
                months = {
                    1: "января",
                    2: "февраля",
                    3: "марта",
                    4: "апреля",
                    5: "мая",
                    6: "июня",
                    7: "июля",
                    8: "августа",
                    9: "сентября",
                    10: "октября",
                    11: "ноября",
                    12: "декабря",
                }
                display_date = f"{date_obj.day} {months[date_obj.month]}"
            except (ValueError, TypeError):
                display_date = date_str

        # Получаем номер столика
        table_number = ""
        if table_id:
            try:
                table = Table.objects.get(id=table_id)
                table_number = table.number
            except Table.DoesNotExist:
                table_number = "Неизвестный столик"

        if form is None:
            form = ReservationStep3Form()
    else:
        if form is None:
            form = ReservationStep1Form()
        step = "1"

    return render(
        request,
        "restaurant/reservation.html",
        {
            "restaurant": restaurant,
            "today": today,
            "step": step,
            "form": form,
            "reservation_data": reservation_data,
            "show_success_modal": show_success_modal,
            "last_reservation": last_reservation,
            "available_hours": available_hours,
            "tables_with_availability": tables_with_availability,
            "display_date": display_date,  # Добавьте это
            "table_number": table_number,  # И это
        },
    )


@csrf_exempt
def get_available_times(request):
    if request.method == "POST":
        date_str = request.POST.get("date")
        guests_count = int(request.POST.get("guests_count", 2))

        try:
            selected_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            available_hours = calculate_available_times(selected_date, guests_count)
            return JsonResponse({"available_hours": available_hours})
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid date format"}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def my_reservations(request):
    restaurant = Restaurant.objects.first()
    active_reservations = Reservation.objects.filter(
        user=request.user, status__in=["pending", "confirmed"]
    ).order_by("date", "time")
    past_reservations = Reservation.objects.filter(
        user=request.user, status__in=["completed", "cancelled"]
    ).order_by("-date", "-time")
    return render(
        request,
        "restaurant/my_reservations.html",
        {
            "restaurant": restaurant,
            "active_reservations": active_reservations,
            "past_reservations": past_reservations,
        },
    )


@login_required
def edit_reservation(request, pk):
    restaurant = Restaurant.objects.first()
    reservation = get_object_or_404(
        Reservation, pk=pk, user=request.user, status__in=["pending", "confirmed"]
    )
    if request.method == "POST":
        form = ReservationEditForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, "Бронирование обновлено")
            return redirect("restaurant:my_reservations")
    else:
        form = ReservationEditForm(instance=reservation)
    return render(
        request,
        "restaurant/edit_reservation.html",
        {
            "restaurant": restaurant,
            "form": form,
            "reservation": reservation,
        },
    )


@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(
        Reservation, pk=pk, user=request.user, status__in=["pending", "confirmed"]
    )
    reservation.status = "cancelled"
    reservation.save(update_fields=["status"])
    messages.success(request, "Бронирование отменено")
    return redirect("restaurant:my_reservations")
