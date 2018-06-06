from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.http import JsonResponse
from rest_framework import status
from rest_framework import status
from trading.models import BotDetail, BotAction, BotPortfolio
from django.utils.dateparse import parse_date
import datetime
# Create your views here.

@api_view(['POST'])
@permission_classes((AllowAny, ))
def bot(request):
    if request.method == "POST":
        name = JSONParser().parse(request)['name']
        bot = BotDetail.objects.create(name=name, capital=1000000)
        bot.save()

        return JsonResponse({}, status = status.HTTP_200_OK)

@api_view(['PUT', 'GET'])
@permission_classes((AllowAny, ))
def capital(request):
    if request.method == "PUT":
        data = JSONParser().parse(request)
        bot = BotDetail.objects.get(name=data['name'])
        bot.capital = float(data['capital'])
        bot.lastUpdate = datetime.datetime.strptime(data['date'], "%Y-%m-%d").date()
        bot.save()

        return JsonResponse({}, status = status.HTTP_200_OK)
    
    elif request.method == "GET":
        name = request.GET['name']
        bot = BotDetail.objects.get(name = name)

        return JsonResponse({'capital': bot.capital}, status = status.HTTP_200_OK)

@api_view(['POST', 'GET'])
@permission_classes((AllowAny, ))
def trade(request):
    if request.method == "POST":
        data = JSONParser().parse(request)

        bot = BotDetail.objects.get(name = data['name'])
        action = BotAction.objects.create(name = bot, 
                        action = data['action'],
                        symbol = data['symbol'],
                        volume = data['volume'],
                        averagePrice = data['averagePrice'],
                        date = datetime.datetime.strptime(data['date'], "%Y-%m-%d").date())
        action.save()

        return JsonResponse({}, status = status.HTTP_200_OK)

    elif request.method == "GET":
        name = request.GET['name']
        bot = BotDetail.objects.get(name = name)

        actions = BotAction.objects.filter(name = bot).order_by('-id')
        actions = [ {
            "symbol": action.symbol,
            "action": action.action,
            "volume": action.volume,
            "averagePrice": action.averagePrice
        } for action in actions]
        return JsonResponse({"actions":actions}, status = status.HTTP_200_OK)

@api_view(['POST', 'GET'])
@permission_classes((AllowAny, ))
def portfolio(request):
    if request.method == 'GET':
        name = request.GET['name']
        bot = BotDetail.objects.get(name = name)
        portfolios = BotPortfolio.objects.filter(name = bot)
        portfolios = [ {
            "symbol": portfolio.symbol,
            "volume": portfolio.volume,
            "averagePrice": portfolio.averagePrice,
            "marketPrice": portfolio.marketPrice,
            "profit": portfolio.profit
        } for portfolio in portfolios]
        
        return JsonResponse({"portfolios": portfolios}, status = status.HTTP_200_OK)

    elif request.method == 'POST':
        data = JSONParser().parse(request)

        bot = BotDetail.objects.get(name = data['name'])
        portfolios = data['portfolios']
        for portfolio in portfolios:
            try:
                botPortfolio = BotPortfolio.objects.get(name = bot, symbol = portfolio['symbol'])
                botPortfolio.volume = portfolio['volume']
                botPortfolio.averagePrice = portfolio['averagePrice']
                botPortfolio.marketPrice = portfolio['marketPrice']
                botPortfolio.profit = portfolio['averagePrice'] - portfolio['marketPrice'] if portfolio['averagePrice'] != 0 else 0
                botPortfolio.save()
            except:
                botPortfolio = BotPortfolio.objects.create(name = bot,
                                symbol = portfolio['symbol'],
                                volume = portfolio['volume'],
                                averagePrice = portfolio['averagePrice'],
                                marketPrice = portfolio['marketPrice'],
                                profit = 0)
                botPortfolio.save()

        return JsonResponse({}, status = status.HTTP_200_OK)