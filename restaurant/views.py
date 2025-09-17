import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import TemplateView, UpdateView

from restaurant.forms import (ReservationEditForm, ReservationStep1Form,
                              ReservationStep2Form, ReservationStep3Form)
from restaurant.services import (calculate_available_times,
                                 compute_available_hours_for_step1,
                                 format_display_date_ru, get_active_restaurant,
                                 get_available_tables, get_table_number_safe)

from .models import Dish, DishCategory, Feedback, Reservation, Table


class RestaurantDetailView(TemplateView):
    template_name = "restaurant/restaurant_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["restaurant"] = get_active_restaurant()
        return context


class ContactsView(TemplateView):
    template_name = "restaurant/contacts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["restaurant"] = get_active_restaurant()
        return context

    def post(self, request, *args, **kwargs):
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


class AboutView(TemplateView):
    template_name = "restaurant/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["restaurant"] = get_active_restaurant()
        return context


class MenuView(TemplateView):
    template_name = "restaurant/menu.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["restaurant"] = get_active_restaurant()
        
        # Получаем все видимые категории блюд
        categories = DishCategory.objects.filter(is_visible=True).order_by('order')
        
        # Для каждой категории получаем доступные блюда
        for category in categories:
            category.available_dishes = category.dishes.filter(is_available=True)
        
        context["categories"] = categories
        
        # Получаем специальные предложения
        context["special_dishes"] = Dish.objects.filter(is_special=True, is_available=True)[:3]
        
        return context


class ReservationView(TemplateView):
    template_name = "restaurant/reservation.html"

    def get(self, request, *args, **kwargs):
        return self._handle(request)

    def post(self, request, *args, **kwargs):
        return self._handle(request)

    def _handle(self, request):
        restaurant = get_active_restaurant()
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
                    date_str = request.POST.get("date")
                    guests_count = request.POST.get("guests_count", 2)
                    available_hours = compute_available_hours_for_step1(
                        date_str, guests_count, today
                    )
                    for field, errors in form.errors.items():
                        for error in errors:
                            messages.error(
                                request, f"{form.fields[field].label}: {error}"
                            )

            elif step == "2":
                date_str = reservation_data.get("date", "")
                time_str = reservation_data.get("time", "")
                guests_count = int(reservation_data.get("guests_count", 2))

                if not date_str or not time_str:
                    messages.error(request, "Сначала выберите дату и время")
                    return redirect(reverse("restaurant:reservation") + "?step=1")

                try:
                    selected_date = datetime.datetime.strptime(
                        date_str, "%Y-%m-%d"
                    ).date()
                    selected_time = datetime.datetime.strptime(time_str, "%H:%M").time()

                    tables_with_availability = get_available_tables(
                        selected_date, selected_time, guests_count
                    )

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
                            messages.error(
                                request, f"{form.fields[field].label}: {error}"
                            )

        if step == "2":
            date_str = reservation_data.get("date", "")
            time_str = reservation_data.get("time", "")
            guests_count = int(reservation_data.get("guests_count", 2))

            if not date_str or not time_str:
                messages.error(request, "Сначала выберите дату и время")
                return redirect(reverse("restaurant:reservation") + "?step=1")

            try:
                selected_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                selected_time = datetime.datetime.strptime(time_str, "%H:%M").time()
                tables_with_availability = get_available_tables(
                    selected_date, selected_time, guests_count
                )
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
            date_str = reservation_data.get("date", "")
            guests_count = int(reservation_data.get("guests_count", 2))
            available_hours = compute_available_hours_for_step1(
                date_str, guests_count, today
            )

        elif step == "3":
            date_str = reservation_data.get("date", "")
            time_str = reservation_data.get("time", "")
            table_id = reservation_data.get("table", "")
            display_date = format_display_date_ru(date_str)
            table_number = get_table_number_safe(table_id)
            if form is None:
                form = ReservationStep3Form()
        else:
            if form is None:
                form = ReservationStep1Form()
            step = "1"

        context = {
            "restaurant": restaurant,
            "today": today,
            "step": step,
            "form": form,
            "reservation_data": reservation_data,
            "show_success_modal": show_success_modal,
            "last_reservation": last_reservation,
            "available_hours": available_hours,
            "tables_with_availability": tables_with_availability,
            "display_date": display_date,
            "table_number": table_number,
        }
        return self.render_to_response(context)


class GetAvailableTimesView(View):
    def post(self, request, *args, **kwargs):
        date_str = request.POST.get("date")
        guests_count = int(request.POST.get("guests_count", 2))
        try:
            selected_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            available_hours = calculate_available_times(selected_date, guests_count)
            return JsonResponse({"available_hours": available_hours})
        except (ValueError, TypeError):
            return JsonResponse({"error": "Invalid date format"}, status=400)

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(["POST"])


class MyReservationsView(LoginRequiredMixin, TemplateView):
    template_name = "restaurant/my_reservations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["restaurant"] = get_active_restaurant()
        context["active_reservations"] = Reservation.objects.filter(
            user=self.request.user, status__in=["pending", "confirmed"]
        ).order_by("date", "time")
        context["past_reservations"] = Reservation.objects.filter(
            user=self.request.user, status__in=["completed", "cancelled"]
        ).order_by("-date", "-time")
        return context


class EditReservationView(LoginRequiredMixin, UpdateView):
    model = Reservation
    form_class = ReservationEditForm
    template_name = "restaurant/edit_reservation.html"

    def get_queryset(self):
        return Reservation.objects.filter(
            user=self.request.user, status__in=["pending", "confirmed"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["restaurant"] = get_active_restaurant()
        return context

    def form_valid(self, form):
        messages.success(self.request, "Бронирование обновлено")
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse("restaurant:my_reservations")


class CancelReservationView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        reservation = get_object_or_404(
            Reservation, pk=pk, user=request.user, status__in=["pending", "confirmed"]
        )
        reservation.status = "cancelled"
        reservation.save(update_fields=["status"])
        messages.success(request, "Бронирование отменено")
        return redirect("restaurant:my_reservations")

    def get(self, request, pk, *args, **kwargs):
        return HttpResponseNotAllowed(["POST"])
