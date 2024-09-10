from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView

from .models import CardsList, Card

name_th = ["Модель", "Название", "Кол-во", "Цена"]




class BijinHome(ListView):
    model = CardsList
    template_name = "inventory_system/index.html"
    context_object_name = "products"
    extra_context = {
        "title": "Главная страница",
        "name_th": name_th,
    }


def date_filter(request):
    return HttpResponse("Hello world!")


class CreateCard(CreateView):

    model = Card
    fields = ["num", "name", "price", "note", "photo"]
    template_name = "inventory_system/newcard.html"
    success_url = reverse_lazy("")
    extra_context = {
        "title": "Добавление новой карточки",
    }


class AddProduct(CreateView):
    model = CardsList
    fields = ["quantity", "model"]
    template_name = "inventory_system/addproduct.html"
    success_url = reverse_lazy("")
    extra_context = {"title": "Добавление продукта в список"}


class Cards(ListView):
    model = Card
    context_object_name = "cards"
    template_name = "inventory_system/cards.html"
    extra_context = {"title": "Список карточек"}


class CardPage(DetailView):
    model = Card
    template_name = "inventory_system/card.html"
    slug_url_kwarg = "card_slug"
    context_object_name = "card"
    extra_context = {"title": "Информация о карточке"}


def shipment(request):
    return HttpResponse("Product Shipment")
