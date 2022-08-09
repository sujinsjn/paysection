# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from audioop import avg
import json
import re
from weakref import ref
from django.db.models.aggregates import Max
from django.forms import IntegerField
from django.http.request import HttpRequest
from django.contrib.auth.hashers import make_password
from django.views import View
# from regex import A
import requests
from requests.models import Response
import random
import string
from authentication.views.checkout import payment_cancel
from serializers import business_detailsSerializer, businessSerializer, UsersSerializer, categorySerializer, \
    EmployeeSerializer, dealSerializer, paymentSerializer, RwardsSerialiser,ProductsListSerializer, usersSerializer,walletpaymentSerializer,UserRegistrationSerializer,UserTokenObtainPairSerializer,UserSerializer,UserdetailsSerializer
from ..models import business_details, category, roles,payments
from rest_framework import status
from django.http import response
from ..send_otp import send_otp
from django.shortcuts import render
import requests
import json
import rest_framework
from rest_framework import generics
from rest_framework.views import APIView
from requests.auth import HTTPBasicAuth
from django.shortcuts import (get_object_or_404,
                              render,
                              HttpResponseRedirect)
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, get_user, login
from django.contrib.auth.models import User,auth
from django.forms.utils import ErrorList
from django.http import HttpResponse
from ..forms import dealsForm, LoginForm, dealsForm, rewardsForm, rolesForm
from authentication.models import mobile
from authentication.models import business_details, Employee #payments
from authentication.forms import MobileLoginForm, BusinessForm, categoryForm, paymentForm
from ..forms import business_detailsForm
from django.contrib import messages

from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from geopy.distance import great_circle
from django.shortcuts import render, get_list_or_404
from django.views.generic import TemplateView, ListView
from django.db.models.functions import TruncMonth, TruncYear
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView
from ..models import *
from django.utils.decorators import method_decorator
from itertools import chain
from django.db.models import Count
#from ..helpers.helper import get_tokens_for_user

import razorpay
from datetime import date
import geocoder
from django.conf import settings

from django.http import HttpResponseBadRequest
from rest_framework import viewsets
from django.shortcuts import render, redirect
from rest_framework.response import Response
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.shortcuts import render
from authentication.models import Transactions
from rest_framework.authtoken.models import Token
from rest_framework import status

from rest_framework import generics

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import authentication
from rest_framework import exceptions
from datetime import date            

# Create your views here.


@api_view(["GET"])
@csrf_exempt
def apis(request):
    url = 'https://discover.search.hereapi.com/v1/discover?at=52.5228,13.4124&q=679123&apiKey=vznif5oSnixasCz2y18sz9hYDTh41S8z82jmy07Tk1E'
    params = {'response': response}
    r = requests.get(url, params=params)
    books = r.json()

    return render(request, "business.html", books)


@api_view(["GET"])
@csrf_exempt
def trans(request,id,*args, **kwargs):
    business_id = request.GET.get('business_id', None)
    if business_id is not None:
        business_payments = payments.objects.filter(
            business_id=business_id
        ).select_related('business').only(
            'id',
            'amount',
            'business_id',
            'business__business_name',
        )

        details = []

        for payment in business_payments:
            details.append({
                'id': payment.id,
                'amount': payment.amount,
                'business_id': payment.business_id,
                'business_name': payment.business.business_name,
            })

        return JsonResponse(details, safe=False)

    return JsonResponse({'error': 'Bad request. Need `business_id`'}, status=400)


@api_view(["GET"])
@csrf_exempt
def transact(request):
    
    business_payments = payments.objects.all().select_related('business','user').only(
        'id',
        'amount',
        'business_id',
        'business__business_name',
        'business__categories',
        'user_id'
    )
    print(business_payments,'///////////////////////')
    #return business_payments

    details = []

    for payment in business_payments:
        details.append({
            'id': payment.id,
            'amount': payment.amount,
            'business_id': payment.business_id,
            'business': payment.business.business_name,
            'categories': payment.business.categories.name,
            'user_id':payment.user_id,
        })

    return JsonResponse({'details':details}, safe=False)
    

    
def index(request):
    
    return render(request, 'index.html')



def transactions(request):
    transact = payments.objects.all()
    return render(request, 'transactions.html', {
        'transact': transact})


def normaltransactions(request):
    transact = payments.objects.all()
    return render(request, 'normaltransactions.html', {
        'transact': transact})

from django.db.models import F

def shuffle(request):
    transactions = payments.objects.filter(business__irich__isnull=False, amount__isnull=False).values(username = F('user__username')).order_by('user__username').annotate(irichpercent=F('business__irich'), user_id=F('user__id'), bonus=Sum('irich_bonus'), share=Sum('amount'), weight=Sum((F("amount") * F('business__irich'))/100))
    print(transactions,'...................')
    #count = transactions.count()
    count = len(transactions)
    print(count,'...................')
    total = 0
    shares = []
    factor = sum(range(count + 1))
    print(factor,']]]]]]]]]]]]]]]]]]]]]]]')
    #userfield = payments.objects.aggrigate(avg('user.username'))
    today = date.today()
    for i, item in enumerate(transactions, start=1):
        print(i,item,'/////////////////////')
        if (item is None):
            continue
        
        #check for payment process done
        if(PaymentProcessComplete.objects.filter(user=item['user_id'], payment_date=today).exists()):
            is_processed = True
        else:
            is_processed = False

        #userfield = item.user.username.aggrigate(avg('user.username'))
        #print(userfield,'...................')        
        total = 50*item['share']/100
        shares.append({
            "sl": i,
            "order": count,
            "share": item['share'],
           # "bonus": item['bonus'],
            "user_id": item['user_id'],
            "username":item['username'] if item['username'] else 'Not available',
            "to_give": 0,
            "multiplier": 0,
            "factor": factor,
            "weightage": item['weight'],
            "is_processed": is_processed
        })
        count -= 1 

    count_sl = 1
    multiplier = total / factor
    shares = sorted(shares, key=lambda i: i['share'], reverse=True)
    count_shares = len(shares)
    for dicts in shares:
        dicts['order'] = count_shares
        dicts['sl'] = count_sl
        count_shares = count_shares - 1
        count_sl += 1
    # print(sorted(shares, key=lambda i: i['share'], reverse=True))
    
    give_back = []
    for item in shares:
        item['to_give'] = item['order'] * multiplier
        item['multiplier'] = multiplier
        give_back.append(item)
        # user=User.objects.get(username=item['username'])
        # print(user,'//////////////////')
        
        # wallets=wallet.objects.filter(user_id=user).update(earning=item['order'] * multiplier)
        # for i in wallets:
        #   i['earning'] = item['to_give']
          
        #   earning=item['order'] * multiplier
        #   wallets=wallet(earning=earning)
        #   wallets.save()

    return render(request, 'shuffle.html', {
        'transact': transactions,
        'give_back': give_back
    })


def business_list(request):
    movies = business_details.objects.all()
    cat = category.objects.all()
    return render(request, 'business_details.html', {"movies": movies, "cat": cat})


def business_favourite(request, id):
    business = business_details.objects.all()
    cat = category.objects.all()
    payment = payments.objects.all()
    movies = payments.objects.filter(irich_id=id)
    return render(request, 'favourite.html', {"movies": movies, "cat": cat, "payment": payment})


@api_view(["GET"])
@csrf_exempt
def favourites(request):    
    business_payments = payments.objects.all()
    print(business_payments[0].amount,'//////////////////////')
        # 'user_id'
        # 'irich_bonus',
        # 'business__business_name',
        # 'business__categories__name',

        # 'business__business_address'
    
    # print(business_payments)

    details = []
    d={}
    for i in business_payments:
        d['id']=i.id
        d["irich_bonus"]=i.irich_bonus,
        
        if i.business:
            d["business_name"]= i.business.business_name,
            #d["categories"]=i.business.categories
        else:
            d["business_name"]="No bussiness"
            
        if i.user:
            d["user"]=i.user.email,
            d["username"]=i.user.username
        else:
            d["user"]="no user"
       
            
        
        details.append(d)
        d={}

        

    # for payment in business_payments:
    #     details.append({
    #         'id': payment.id,
    #         i# 'image1':pay
    # foment.business.image1,
    #         'irich_bonus': payment.irich_bonus,
    #         ##'business_name': payment.business.business_name,
    #         #'categories': payment.business.categories,
    #         'business_address': payment.business_address,
    #     })

    return JsonResponse({"favourites":details}, safe=False)


def paymentss(request):
    id = request.POST.get('id')
    user = User.objects.filter(id=id)
    if request.method == "POST":
        form = paymentForm(request.POST)
        if form.is_valid():
            form.save(user)
            return HttpResponseRedirect("/home")
    else:
        form = paymentForm()
    return render(request, 'payments.html', {"form": form})


def normalpayment(request):
    Payment = payments.objects.all().select_related('irich', 'user').only('irich__business_name', 'irich__irich',
                                                                          'user__username')

    details = []
    # print (business.payments)
    for payment in Payment:
        details.append({
            'username': payment.user.username,
            'amount': payment.amount,
            'irich_percent': payment.irich.irich,
            'business_name': payment.irich.business_name,

        })
    return render(request, "normalpayments.html", {
        "details": details,
    })



def payment(request, id):
    payment = payments.objects.filter(business_id=id).first()

    users = User.objects.all()

    # print (business.payments)

    return render(request, "payment.html", {
        "payment": payment,
        "users": users
    })


def walletsection(request):
    payment = payments.objects.all()                
    return render(request, "payments.html", {
        "details": payment,
        
    })


@api_view(["GET"])
def walletsapi(request):
    transactions = payments.objects.filter().order_by('amount')#.select_related('business__irich', 'user')
    print(transactions,'//////////////////////////////')
    bonus=500
    count = len(transactions)
    total = 0
    shares = []
    factor = sum(range(count + 1))
     
    for i, item in enumerate(transactions, start=1):   
        if (item.business is None):
            continue     
        wallet_user_ids = wallet.objects.all().values('user_id','irich_bonus')        
        Payment = payments.objects.filter().values('business__irich','user__username')
        print(Payment)
        #Payment = payments.objects.all().select_related('irich', 'user').only('irich__business_name', 'irich__irich',
                                                                     # 'user__username')
        for dicts in wallet_user_ids:
            if dicts['user_id'] == item.user_id:
               
                bonus = int(dicts['irich_bonus']) - 75
                from_value = wallet.objects.get(user_id=item.user_id)
                from_value.irich_bonus = bonus
        # print(item.amount)        
        total += int(item.amount)/ int(item.business.irich) / 10*int(item.business.irich)
        shares.append({

            "order": count,
            "spent": int(item.amount),
            "username": item.user.username,
            "share": int(item.amount),
            "earning": 0,
            "multiplier": 0,
            "factor": factor,
        })
        count -= 1

    multiplier = (total * 0.5) / factor

    give_back = []
    for item in shares:
        item['earning'] = item['order'] * multiplier
        item['multiplier'] = multiplier
        give_back.append(item)
    shares = sorted(shares, key=lambda i: i['spent'], reverse=True)
    # print(shares)
    shares_sort = sorted(shares, key=lambda i: i['earning'], reverse=True)
    # print(shares_sort)
    to_give = []
    spent = []

    for dicts in shares_sort:
        to_give.append(dicts['earning'])
    for dict in shares:
        spent.append(dict['spent'])
    # test_share = shares
    counter = 0
    for dict_share in shares:

        print(to_give[counter])

        dict_share['earning'] = to_give[counter]
        # dict_share['spent'] = spent[counter]
        counter += 1
    for dicts in wallet_user_ids:
            bonus = int(dicts['irich_bonus'])
    return JsonResponse({
        
        'give_back': give_back
    })


def wallets(request):
    transactions = payments.objects.filter().order_by('amount').select_related('irich', 'user')
    bonus=500
    count = len(transactions)
    total = 0
    shares = []
    factor = sum(range(count + 1))
     
    for i, item in enumerate(transactions, start=1):
        wallet_user_ids = wallet.objects.all().values('user_id','irich_bonus')
        Payment = payments.objects.all().select_related('irich', 'user').only('irich__business_name', 'irich__irich',
                                                                       'user__username')
        for dicts in wallet_user_ids:
            if dicts['user_id'] == item.user_id:
               
                bonus = int(dicts['irich_bonus']) - 75
                from_value = wallet.objects.get(user_id=item.user_id)
                from_value.irich_bonus = bonus
        # print(item.amount)
        total += int(item.amount)/ int(item.irich.irich) / 10*int(item.irich.irich) 
        shares.append({

            "order": count,
            "spent": int(item.amount),
            "username": item.user.username,
            # "share": int(item.amount),
            "earning": 0,
            # "multiplier": 0,
            # "factor": factor,
        })
        count -= 1

    multiplier = (total * 0.5) / factor

    give_back = []
    for item in shares:
        item['earning'] = item['order'] * multiplier
        item['multiplier'] = multiplier
        give_back.append(item)
    shares = sorted(shares, key=lambda i: i['spent'], reverse=True)
    # print(shares)
    shares_sort = sorted(shares, key=lambda i: i['earning'], reverse=True)
    # print(shares_sort)
    to_give = []
    spent = []

    for dicts in shares_sort:
        to_give.append(dicts['earning'])
    for dict in shares:
        spent.append(dict['spent'])
    # test_share = shares
    counter = 0
    for dict_share in shares:

        print(to_give[counter])

        dict_share['earning'] = to_give[counter]
        # dict_share['spent'] = spent[counter]
        counter += 1
    for dicts in wallet_user_ids:
            
                
            bonus = int(dicts['irich_bonus'])
    return render(request, "wallet.html", {
        "shares": shares,
        "give_back":give_back
    })



@api_view(["GET"])
@csrf_exempt
def business_pay(request, id):
    payment = payments.objects.filter(irich_id=id)

    users = User.objects.all()

    return JsonResponse({
        "payments": paymentSerializer(payment, many=True).data,
        "users": UserSerializer(users, many=True).data,
    })


def notification(request):
    return render(request, 'notification.html')


def normaluser(request):
    paymentoption = payments.objects.all()
    return render(request, 'normalusers.html', {"paymentoption": paymentoption})

def showrewards(request):
    transact = payments.objects.all()
    transactions = payments.objects.filter().order_by('amount').annotate(bonus=Sum('irich_bonus'), purchase_amount=Sum('amount'))
    print(transactions,'/////////////')
    count = len(transactions)
    total = 0
    shares = []
    factor = sum(range(count + 1))

    for i, item in enumerate(transactions, start=1):
        # print(item.amount)
        #total += int(item.amount)/ int(item.irich_bonus) / 10*int(item.irich.irich) 
        shares.append({
            "sl": i,
            "order": count,
            "share": int(item.amount)/10,
            "id": item.id,

            "to_give": 0,
            "multiplier": 0,
            "factor": factor,
        })
        count -= 1

    count_sl = 1
    multiplier = (total * 0.125) / factor
    shares = sorted(shares, key=lambda i: i['share'], reverse=True)
    count_shares = len(shares)
    for dicts in shares:
        dicts['order'] = count_shares
        dicts['sl'] = count_sl
        count_shares = count_shares - 1
        count_sl += 1
    print(sorted(shares, key=lambda i: i['share'], reverse=True))

    give_back = []
    for item in shares:
        item['to_give'] = item['order'] * multiplier
        item['multiplier'] = multiplier
        give_back.append(item)

    return render(request, 'reward.html', {
        'transact': transact,
        'give_back': give_back
    })
# def wallets(request):
#     transactions = payments.objects.filter().order_by('amount').select_related('irich', 'user')
#     bonus=500
#     count = len(transactions)
#     total = 0
#     shares = []
#     factor = sum(range(count + 1))

#     for i, item in enumerate(transactions, start=1):
#         # print(item.amount)
#         total += int(item.amount)/ int(item.irich.irich) / 10*int(item.irich.irich) 
#         shares.append({

#             "order": count,
#             "share": int(item.amount)/10,
#             "id": item.id,
#             "username":item.user.username,
#             "to_give": 0,
#             "multiplier": 0,
#             "factor": factor,
#         })
#         count -= 1

#     count_sl = 1
#     multiplier = (total * 0.125) / factor
#     shares = sorted(shares, key=lambda i: i['share'], reverse=True)
#     count_shares = len(shares)
#     for dicts in shares:
#         dicts['order'] = count_shares
#         dicts['sl'] = count_sl
#         count_shares = count_shares - 1
#         count_sl += 1
#     print(sorted(shares, key=lambda i: i['share'], reverse=True))

#     give_back = []
#     for item in shares:
#         item['to_give'] = item['order'] * multiplier
#         item['multiplier'] = multiplier
#         give_back.append(item)

#     return render(request, 'wallet.html', {
       
#         'give_back': give_back,
#         "available_balance":int(bonus)
#     })

  


def setting(request):
    return render(request, 'settings.html')


def pay(request):
    return render(request, 'pay.html')


def get_books(request):
    business_detail = request.user.id
    business_detail = business_details.objects.all()
    serializer = business_detailsSerializer(business_detail, many=True)
    return JsonResponse({'business_details': serializer.data}, safe=False, status=status.HTTP_200_OK)


@api_view(["GET"])
@csrf_exempt
def show_category(request):
    cs = request.user.id
    cs = category.objects.all()
    serializer = categorySerializer(cs, many=True)
    return JsonResponse({'category': serializer.data}, safe=False, status=status.HTTP_200_OK)


@api_view(["GET"])
@csrf_exempt
def show_business(request):
    cs = business_details.objects.all()
    serializer = business_detailsSerializer(cs, many=True)
    return JsonResponse({"cs": serializer.data}, safe=False, status=status.HTTP_200_OK)


class RewardsApi(APIView):
    def get(self, request):
        try:
            cs = rewards.objects.all().values()
            
            # data = RwardsSerialiser(cs, many=True)
            return Response({"cs": cs}, status=status.HTTP_200_OK)
        except exceptions as e:
            return Response(e)


@api_view(["GET"])
@csrf_exempt
def dealapi(request):
    cs = deals.objects.all()
    serializer = dealSerializer(cs, many=True)
    return JsonResponse({"cs": serializer.data}, safe=False, status=status.HTTP_200_OK)


@api_view(["GET"])
@csrf_exempt
def show_users(request):
    employee = Employee.objects.all()
    users = User.objects.all()

    return JsonResponse({
        "employee": EmployeeSerializer(employee, many=True).data,
        "users": UserSerializer(users, many=True).data,
    })



class paysection(APIView):
    def get(self,request):
        try:
            user_id=request.data['user']
            purchase_amount=request.data['amount']
            print(user_id,purchase_amount)
            return JsonResponse({
            "user_id": user_id,
            "purchase_amount":purchase_amount,
        })
        except exceptions as e:
            return e

    def post(self, request):
        try:
            user_id = request.data['user']
            user_wallet = wallet.objects.filter(user=user_id).last()
            #payments.objects.all().aggregate(Sum('irich_bonus'))
            #print(user_wallet.starting_irich_bonus,'/////////')
            purchase_amount = float(request.data['amount'])

            # call payemnt gateway to proceed payment
            try:
                client = razorpay.Client(auth=("rzp_test_fNN7BgVDDfS2Vf", "iQrrBDw9pZjTuy5mQ0tS2mFr"))
                payment = client.order.create({'amount': purchase_amount, 'currency': 'INR',
                                        'payment_capture': '1'})
            except Exception as e:
                return Response('Purchase failed', status=status.HTTP_503_SERVICE_UNAVAILABLE) 

            dataArr = {
                'user': user_id,
                'amount': payment['amount'], # amount received from payemnt gateway
                'business': request.data['business']
            }
            data = paymentSerializer(data=dataArr)
            if (data.is_valid()):
                payment = data.save()
                payment_id = payment._get_pk_val()

                
                # get business percent
                business = business_details.objects.get(pk=request.data['business'])
                business_percent = business.irich # value in %

                # calculate business percent of purchase amount
                business_amount = (purchase_amount * int(business_percent))/100
                # calculating bonus
                amount25_percent = (purchase_amount * 25)/100
                balance_wallet = float(user_wallet.irich_bonus) - purchase_amount
                print(balance_wallet,'/////////////')
                for_rewards=user_wallet.starting_irich_bonus-purchase_amount
                if for_rewards<=0:
                    for_rewards=0
                print(for_rewards,'...........')
                if (amount25_percent <= 75):
                    bonus_amount = amount25_percent
                else:
                    bonus_amount = 75
                
                if (balance_wallet < 1):
                    balance_wallet = bonus_amount                     
                else:
                    balance_wallet = balance_wallet + bonus_amount 
                print(bonus_amount,'//////////////////')
                
                wallet.objects.filter(pk=user_wallet.id).update(irich_bonus=balance_wallet, starting_irich_bonus=for_rewards) # update wallet amount
                rewards=wallet.objects.get(pk=user_wallet.id)
                
                payments.objects.filter(pk=payment_id).update(irich_bonus=bonus_amount)
                 # update user bonus amount
                
                payment_data = payments.objects.get(pk=payment_id)
                
                return Response({"paysection":{
                    'id': payment_data.pk,
                    'amount': payment_data.amount,
                    'bonusAmount': payment_data.irich_bonus,
                    'user': payment_data.user.pk,
                    'for_rewards':rewards.starting_irich_bonus
                    
                    
                }}, status=status.HTTP_200_OK)
            else:
                return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)                
        except Exception as e:
            return Response(str(e), status=status.HTTP_503_SERVICE_UNAVAILABLE) 

class walletpaysection(APIView):
    def post(self, request):
        try:
            user_wallet = wallet.objects.filter(user=request.data['user']).last()
            bonus = payments.objects.filter(user=request.data['user']).last()
            print(bonus,'//////////////')
            print(user_wallet)     
            if bonus :
                data = {
                    'user': request.data['user'],
                    #'irich_walletamount': request.data['irich_walletamount'],
                    'business': request.data['business'],
                    'walletAmount': bonus.irich_bonus,
                    'irich_bonus':user_wallet.irich_bonus
                }
                return Response({"data":data})   
            else:
                data = {
                    'user': request.data['user'],
                    #'irich_walletamount': request.data['irich_walletamount'],
                    'business': request.data['business'],
                    'walletAmount': 0.0,
                    'irich_bonus':user_wallet.irich_bonus
                    }
                return Response({'data':data})
        except Exception as e:
            return Response('no user', status=status.HTTP_400_BAD_REQUEST)         


class ProcessPayment(View):
    def post(self,request):
        try:
            today = date.today()
            user_id = int(request.POST.get('user_id'))
            if (PaymentProcessComplete.objects.filter(user=user_id, payment_date=today).exists()):
                return HttpResponse(3) # already exists
            to_give = request.POST.get('to_give')
            wallet_user = wallet.objects.get(user=user_id)
            irich_bonus = wallet_user.irich_bonus
            wallet_amount = float(to_give) + float(irich_bonus)
            wallet_user.irich_bonus = wallet_amount
            wallet_user.save()
            PaymentProcessComplete.objects.create(
                user_id=int(request.POST.get('user_id')),
                payment_date=today
            )
            return HttpResponse(1) # success
        except Exception as e:
            return HttpResponse(2) # failed

#class adduser(APIView):

#     serializer_class =UserSerializer
    
#     def post(self, request):
#         username=request.POST.get('username')
    
        
#         Serializer=UserSerializer(data=request.data)
        
#         if username is not None:
#             # print(request.data)
#             if Serializer.is_valid():
                 
#                  Serializer.save()
#                  earning=0
#                  irich_bonus=500
#                  username=request.POST.get('username')
#                  print(username)
#                  user = User.objects.get(username=username)
#                  phone=request.POST.get('phone')
#                  print(phone)
                
                 
#                  print(user.id)
                
                
#                  ob=wallet(user_id=user.id,irich_bonus=irich_bonus,earning=earning)
            
            
                
#                  ob.save()
#                 #  return redirect('/signin')
#                  return JsonResponse(Serializer.data)
#         return JsonResponse(Serializer.errors)
           
 
# class loginApi(APIView):
    # serializer_class =usersSerializer
    # def post(self, request):

        
    #     Serializer=usersSerializer(data=request.data)
    #     phone=request.POST.get('phone')
    #     password=request.POST.get('password')
    #     designation = request.POST.get('designation')
        
        
        
    #     # print(phone)
    #     # id=request.POST.get('id')
    #     role=roles.objects.filter(designation=designation)
    #     print(designation)
    #     # print(role.id)
        
    #     employee=Employee.objects.get(phone=phone)
    #     print(phone)
       
    #     # user=User.objects.get(id=employee.user_id)
    #     user=User.objects.get(password=password)
    #     print(user)
    #     # print(employee.designation_id)
    #     if role == employee.designation:
    #         login(user)
    #         return redirect('/BusinessAdd')
    #     elif role != employee.designation:

    #         login(user)
    #         print('logined')
    #         return redirect('/mybusiness',{'phone' == phone})
            
       
           
    #     if Serializer.is_valid():
                
                
            
    #            return JsonResponse("error",safe=False) 
    #     return JsonResponse(Serializer.data)
        
def categories(request):
    cat = category.objects.all()
    print(cat)
    return render(request, 'categories.html', {"cat": cat})


def normalcategories(request):
    cat = category.objects.all()
    return render(request, 'normalcategory.html', {"cat": cat})


def Home(request):
    if request.method == "POST":
        categories_id = request.POST.get('categories_id')
        bank_name = request.POST.get('bank_name')

        business_name = request.POST.get('business_name')
        business_desc = request.POST.get('business_desc')
        business_address = request.POST.get('business_address')
        email = request.POST.get('email')
        IFSC_code = request.POST.get('IFSC_code')
        irich = request.POST.get('irich')
        business_code = request.POST.get('business_code')
        Account_details = request.POST.get('Account_details')
        account_number = request.POST.get('account_number')
        business_contact = request.POST.get('business_contact')
        image1 = request.FILES.get('image1')
        subcategory = request.POST.get('subcategory')
        categories = category.objects.filter(id=categories_id).first()
        business_code = request.POST.get('business_code')
        # check = request.POST.get('lat')
        # business_code = categories.name[0:3] + business_name[0:3] + str(random.randint(100, 200))

        loc = str(business_address)
        print(loc)
        geolocator = Nominatim(user_agent="my_request")
        location = geolocator.geocode(loc)
        print(location)
        latitude = location.latitude
        # latitude = latitude[0]

        longitude = location.longitude
        # print(longitude)
        print(request.GET.get('check'))
        obj = business_details(
            categories_id=categories_id,
            bank_name=bank_name,
            IFSC_code=IFSC_code,
            business_name=business_name,
            business_desc=business_desc,
            business_address=business_address,
            email=email,
            subcategory=subcategory,
            Account_details=Account_details,
            business_code=business_code,
            irich=irich,
            account_number=account_number,
            business_contact=business_contact,
            image1=image1,


        )
        check = "true"
        print(check)
        # obj.save()
        cat = category.objects.all()
        return render(request, 'business_search.html', {"lat": latitude,
                                                        "long": longitude,
                                                        "categories_id": categories_id,
                                                        "bank_name": bank_name,
                                                        "business_name": business_name,
                                                        "IFSC_code": IFSC_code,
                                                        "business_desc":business_desc,
                                                        "business_address":business_address,
                                                        "email":email,
                                                        "subcategory":subcategory,
                                                        "Account_details":Account_details,
                                                        "business_code":business_code,
                                                        "irich":irich,
                                                        "account_number":account_number,
                                                        "business_contact":business_contact,
                                                        "image1":image1,
                                                         "cat":cat,

                                                     })

    
    cat = category.objects.all()
    return render(request, 'business.html',{"cat":cat})


def addsales(request):
    m = request.POST.get('username')
    det = User.objects.filter(username=m)
    if request.method == "POST":
        categories_id = request.POST.get('categories_id')
        bank_name = request.POST.get('bank_name')

        business_name = request.POST.get('business_name')
        business_desc = request.POST.get('business_desc')
        business_address = request.POST.get('business_address')
        email = request.POST.get('email')
        IFSC_code = request.POST.get('IFSC_code')
        irich = request.POST.get('irich')
        business_code = request.POST.get('business_code')
        Account_details = request.POST.get('Account_details')
        account_number = request.POST.get('account_number')
        business_contact = request.POST.get('business_contact')
        image1 = request.FILES.get('image1')

        categories = category.objects.filter(id=categories_id).first()
        business_code = request.POST.get('business_code')
        business_code = categories.name[0:3] + business_name[0:3] + str(random.randint(100, 200))
        # obj = business_details(
        #     categories_id=categories_id,
        #     bank_name=bank_name,
        #     IFSC_code=IFSC_code,
        #     business_name=business_name,
        #     business_desc=business_desc,
        #     business_address=business_address,
        #     email=email,
        #     Account_details=Account_details,
        #     business_code=business_code.upper(),
        #     irich=irich,
        #     account_number=account_number,
        #     business_contact=business_contact,
        #     image1=image1,
        #
        # )
        #
        # obj.save()
    cat = category.objects.all()

    return render(request, 'salesperson.html', {"cat": cat, "det": det})


@api_view(["GET"])
def Categoryapi(request):
    categories = category.objects.all()


    serializer = categorySerializer(categories, many=True)
    return JsonResponse({"categories": serializer.data}, safe=False, status=status.HTTP_200_OK)


def Category(request):
    print(request)
    if request.method == "POST":
        form = categoryForm(request.POST)
        print(form)
        #return form
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/category")
    else:
        form = categoryForm()
    return render(request, 'category.html', {"form": form})


def role(request):
    if request.method == "POST":
        form = rolesForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/showrole")
    else:
        form = rolesForm()
    return render(request, 'roles.html', {"form": form})


def rewardcreation(request):
    if request.method == "POST":
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        targeted_amount = request.POST.get('targeted_amount')
        referral_member = request.POST.get('referral_member')

        obj = rewards(
            start_date=start_date,
            end_date=end_date,
            targeted_amount=targeted_amount,
            referral_member=referral_member,

        )

        obj.save()
    return render(request, 'rewards.html')


def showrole(request):
    roleshow = roles.objects.all()
    return render(request, 'role.html', {"roleshow": roleshow})


def createdeal(request):
    if request.method == "POST":
        title=request.POST.get('title')
        description=request.POST.get('description')

        obj = deals(title=title,
        description=description
           
        )

        obj.save()
    
    return render(request, 'createdeal.html')


def showdeal(request):
    dealshow = deals.objects.all()
    return render(request, 'deals.html', {"dealshow": dealshow})


# def percentage(part, whole):
#     return 100 * float(part)/float(whole)

#     print(percentage(5, 7))

#     print('{:.2f}'.format(percentage(5, 7)))
#     return render(request, "tables.html")

@api_view(["GET"])
def business(request):
    if request.GET.get('category_id', False):
        category_id = request.GET.get('category_id', False)
        movies = business_details.objects.filter(categories_id=category_id)
    else:
        movies = business_details.objects.all()

    serializer = business_detailsSerializer(movies, many=True)
    return JsonResponse({"movies": serializer.data}, safe=False, status=status.HTTP_200_OK)
@api_view(["GET"])
def mybusiness(request):
    # id = request.POST.get('id')
    # phone=request.POST.get('phone')
    # username=request.POST.get('username')
    # print(phone)
    # # if user == 'business owner':
    
    # user=User.objects.filter(username=username, id=id)
    # business=business_details.objects.filter(user=user)
    # # if user == '1':
    # #     businesslist=business_details.objects.filter(user=user)
        
    # serializer = business_detailsSerializer(business, many=True)
    # usernames=serializer.data
    # list_usernames = []
    # for name in usernames:
    #     if name['user'] == user.id:
    #       username = name['user']
    #       print(username)  
    #       print('shifa')
    # return JsonResponse({"business":serializer.data}, safe=False)
    user=request.user
    print(user)
    business=business_details.objects.filter(user=user)
    serializer = business_detailsSerializer(business, many=True)
    return Response(serializer.data)


def tablelist(request):
    if request.GET.get('category_id', False):
        category_id = request.GET.get('category_id', False)
        movies = business_details.objects.filter(categories_id=category_id)
    else:

        movies = business_details.objects.all()
    codes = Transactions.objects.all()
    cat = category.objects.all()
    context = {"movie": movies, "cat": cat, "codes": codes}

    return render(request, "tables.html", context)

def saleslist(request):
    if request.GET.get('category_id', False):
        category_id = request.GET.get('category_id', False)
        movies = business_details.objects.filter(categories_id=category_id)
    else:

        movies = business_details.objects.all()
    codes = Transactions.objects.all()
    cat = category.objects.all()
    context = {"movie": movies, "cat": cat, "codes": codes}

    return render(request, "saleslist.html", context)

def normallist(request):
    if request.GET.get('category_id', False):
        category_id = request.GET.get('category_id', False)
        movies = business_details.objects.filter(categories_id=category_id)
    else:

        movies = business_details.objects.all()
    codes = Transactions.objects.all()
    cat = category.objects.all()
    context = {"movie": movies, "cat": cat, "codes": codes, "host": 'http://13.232.49.240:8000'}

    return render(request, "normallist.html", context)


def businesslist(request):
    print('hiiii')
    user=request.POST.get('user')
    # user_id=request.POST.get('user_id')
    print(user)
    
    movies = business_details.objects.all()
    print(movies)
    details = []
    # print (business.payments)
    for movie in movies:
        details.append({
            'business_name': movie.business_name,
            'name': movie.categories.name,
            'business_desc': movie.business_desc,
            'business_address': movie.business_address,
            'email': movie.email,
            'Account_details': movie.Account_details,
            'account_number': movie.account_number,
            'business_contact': movie.business_contact,

        })
    return render(request, "businesslist.html", {
        "details": details,
    })

def signin(request):
    
     return redirect('/categories') 


 

def logout(request):
    try:
        del request.session['name']
    except KeyError:
        pass
    return HttpResponse("You're logged out.")

def LoginView(request):
    try:
        request.session.flush()
        messages.add_message(request, messages.SUCCESS, 'Thank you for using our service!!!')
        return HttpResponseRedirect(redirect_to='/login')
    except Exception as e:
        messages.add_message(request, messages.WARNING, 'Something went wrong. Error: '+str(e))
    return HttpResponseRedirect(redirect_to='/login')


def users(request):
    employee = Employee.objects.select_related('user', 'designation', 'business').all()
    print(employee)

    return render(request, "users.html", {"employee": employee})

def register_page(request):
    return render(request,'accounts/register.html')


def register_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        is_staff = 1
        is_active = 1
        is_superuser = False
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = make_password(request.POST.get('password'))
        earning=0
        irich_bonus=500
        starting_irich_bonus=500
        
        date_joined = datetime.date.today()
        user = User.objects.create(
            username=username,
            is_staff=is_staff,
            is_active=is_active,
            is_superuser=is_superuser,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            date_joined=date_joined
        )
        N = 8
        phone = request.POST.get('phone')
        referral_code = request.POST.get('referral_code')
        postcode = request.POST.get('postcode')

        referral = ''.join(random.choices(string.ascii_uppercase +
                                          string.digits, k=N))

        obj = Employee(
            user_id=user.id,
            phone=phone,
            referral_code=referral_code,
            postcode=postcode,
            referral=referral,
            
        )
        ob=wallet(user_id=user.id,irich_bonus=irich_bonus,earning=earning,starting_irich_bonus=starting_irich_bonus)
       # paymentobj=payments(irich_bonus=irich_bonus)
        
        
        obj.save()
        ob.save()
        #paymentobj.save()
        print('hello')
    object=Employee.objects.all()
    return redirect('signin')



def bonus(request):
    user_id=request.POST.get('user_id')
    movies = wallet.objects.filter(user_id=user_id).first()

    details = []
    # print (business.payments)
    for movie in movies:
        details.append({
            'irich_bonus':movie.irich_bonus

        })

        
        
    
    
    return render(request, 'wallet.html',{"details":details})

def edit(request, id):
    object = business_details.objects.get(id=id)
    return render(request, 'edit.html', {'object': object})


def useredit(request, id):
    object = Employee.objects.get(id=id)
    return render(request, 'useredit.html', {'object': object})


def edit_user_role(request, id):
    user_roles = roles.objects.all()
    user = User.objects.get(id=id)

    if request.method == "POST":
        designation_id = request.POST.get('role')

        employee = Employee.objects.filter(user_id=id).first()
        if employee is None:
            employee = Employee.objects.create(
                designation_id=designation_id,
                user_id=id
            )
        else:
            employee.designation_id = designation_id
            employee.save()

    else:
        employee = Employee.objects.filter(user_id=id).first()

    return render(request, 'edit-role.html', {
        'roles': user_roles,
        'user': user,
        'role_id': employee.designation_id if employee is not None else ''
    })


def edit_business(request, id):
    business_edit = business_details.objects.all()
    user = User.objects.get(id=id)

    if request.method == "POST":
        business_id = request.POST.get('business_name')

        employee = Employee.objects.filter(user_id=id).first()
        if employee is None:
            employee = business_details.objects.create(
                business_id=business_id,
                user_id=id
            )
        else:
            employee.business_id = business_id
            employee.save()

    else:
        employee = Employee.objects.filter(user_id=id).first()

    return render(request, 'business-edit.html', {
        'business_edit': business_edit,
        'user': user,
        'business_id': employee.business_id if employee is not None else ''
    })


def categoryedit(request, id):
    object = category.objects.get(id=id)
    return render(request, 'categoryedit.html', {'object': object})


def roledit(request, id):
    object = roles.objects.get(id=id)
    return render(request, 'roleedit.html', {'object': object})


def dealedit(request, id):
    object = deals.objects.get(id=id)
    return render(request, 'dealedit.html', {'object': object})


def userupdate(request, id):
    object = User.objects.get(id=id)
    form = UserCreationForm(request.POST, instance=object)
    if form.is_valid:
        form.save()
        object = Employee.objects.all()
        return redirect('/users')


def update(request, id):
    object = business_details.objects.get(id=id)
    form = business_detailsForm(request.POST, instance=object)
    if form.is_valid:
        form.save()
        object = business_details.objects.all()
        return redirect('/categories')


def businessupdate(id):
    object = business_details.objects.get(id=id)

    return redirect('/businesslist', {'object': object})


def categoryupdate(request, id):
    object = category.objects.get(id=id)
    form = categoryForm(request.POST, instance=object)
    if form.is_valid:
        form.save()
        object = category.objects.all()
        return redirect('/categories')


def roleupdate(request, id):
    object = roles.objects.get(id=id)
    form = rolesForm(request.POST, instance=object)
    if form.is_valid:
        form.save()
        object = roles.objects.all()
        return redirect('/showrole')


def dealupdate(request, id):
    object = deals.objects.get(id=id)
    form = dealsForm(request.POST, instance=object)
    if form.is_valid:
        form.save()
        object = deals.objects.all()
        return redirect('/deals')


def delete(request, id):
    business_details.objects.filter(id=id).delete()
    return redirect('/categories')


def userdelete(request, id):
    Employee.objects.filter(id=id).delete()
    return redirect('/users')


def categorydelete(request, id):
    category.objects.filter(id=id).delete()
    return redirect('/categories')


def roledelete(request, id):
    roles.objects.filter(id=id).delete()
    return redirect('/showrole')
    


def dealdelete(request, id):
    deals.objects.filter(id=id).delete()
    return redirect('/deals')



@method_decorator(csrf_exempt,name="dispatch")
class BusinessAddApi(APIView):
    serializer_class = businessSerializer

    def post(self, request):
        Serializer = businessSerializer(data=request.data)

        categoryobject = category.objects.all().only('name')
        if Serializer.is_valid():
            categories = request.POST.get('categories')
            bank_name = request.POST.get('bank_name')
            business_name = request.POST.get('business_name')
            business_desc = request.POST.get('business_desc')
            business_address = request.POST.get('business_address')
            loc = str(business_address)
            print(loc)
           # geolocator = Nominatim(user_agent="my_request")
            #location = geolocator.geocode(loc)
           # print(location)
            #latitude = location.latitude
            # latitude = latitude[0]

            #longitude = location.longitude
            email = request.POST.get('email')
            IFSC_code = request.POST.get('IFSC_code')
            irich = request.POST.get('irich')
            business_code = request.POST.get('business_code')
            Account_details = request.POST.get('Account_details')
            account_number = request.POST.get('account_number')
            business_contact = request.POST.get('business_contact')
            image1 = request.FILES.get('image1')
            subcategory = request.POST.get('subcategory')
            # categories = category.objects.filter(id=categories_id).first()
            print(categories)
            business_code = request.POST.get('business_code')
            # check = request.POST.get('lat')
            business_code =  business_name[0:3] + str(random.randint(100, 200))


            obj = business_details(
                categories_id=categories,
                bank_name=bank_name,
                IFSC_code=IFSC_code,
                business_name=business_name,
                business_desc=business_desc,
                business_address=business_address,
                email=email,
                subcategory=subcategory,
                Account_details=Account_details,
                business_code=business_code,
                irich=irich,
                account_number=account_number,
                business_contact=business_contact,
                image1=image1,
                #latitude=latitude,
                #longitude=longitude,

            )
            
            obj.save()
        
        return JsonResponse(Serializer.data)


def search_map(request):
    print('hiii')
    if request.method == "POST":
        categories_id = request.POST.get('categories_id')
        bank_name = request.POST.get('bank_name')
        business_name = request.POST.get('business_name')
        business_desc = request.POST.get('business_desc')
        business_address = request.POST.get('business_address')
        loc = str(business_address)
        print(loc)
        geolocator = Nominatim(user_agent="my_request")
        location = geolocator.geocode(loc)
        print(location)
        latitude = location.latitude
        # latitude = latitude[0]

        longitude = location.longitude
        email = request.POST.get('email')
        IFSC_code = request.POST.get('IFSC_code')
        irich = request.POST.get('irich')
        business_code = request.POST.get('business_code')
        Account_details = request.POST.get('Account_details')
        account_number = request.POST.get('account_number')
        business_contact = request.POST.get('business_contact')
        image1 = request.FILES.get('image1')
        subcategory = request.POST.get('subcategory')
        categories = category.objects.filter(id=categories_id).first()
        print(categories)
        business_code = request.POST.get('business_code')
        # check = request.POST.get('lat')
        business_code =  business_name[0:3] + str(random.randint(100, 200))


        obj = business_details(
            categories_id=categories_id,
            bank_name=bank_name,
            IFSC_code=IFSC_code,
            business_name=business_name,
            business_desc=business_desc,
            business_address=business_address,
            email=email,
            subcategory=subcategory,
            Account_details=Account_details,
            business_code=business_code,
            irich=irich,
            account_number=account_number,
            business_contact=business_contact,
            image1=image1,
            latitude=latitude,
            longitude=longitude,

        )
        check = "true"
        print(check)
        obj.save()
    cat=category.objects.all()
    return render(request, 'business.html',{"cat":cat} )




# class ExampleAuthentication(authentication.BaseAuthentication):
#     def authenticate(self, request):
#         username = request.META.get('HTTP_X_USERNAME')
#         if not username:
#             return None

#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             raise exceptions.AuthenticationFailed('No such user')

#         return (user, None)

@api_view(["POST"])
@csrf_exempt
def adduser(request):
        parser_classes = [MultiPartParser, FormParser]

    
        serializer = UserRegistrationSerializer(data=request.data)
        print(serializer)
        if serializer.is_valid():
            employee = serializer.save()
            data = {}
            data['response'] = 'Registration successful'
            
            refresh = RefreshToken.for_user(employee)
            data['token'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            earning=0
            irich_bonus=500
            starting_irich_bonus=500
            username=request.POST.get('username')
            print(username)
            user = User.objects.get(username=username)
            phone=request.POST.get('phone')

            ob=wallet(user_id=user.id,irich_bonus=irich_bonus,earning=earning,starting_irich_bonus=starting_irich_bonus)
    
    
        
            ob.save()
        else:
            data = serializer.errors
        
        return Response(data, status=status.HTTP_200_OK)       



@method_decorator(csrf_exempt,name="dispatch")
class UserTokenObtainPairView(TokenObtainPairView):
   
        serializer_class = UserTokenObtainPairSerializer


    
# class UserLogin(APIView):
#     def post(self, request):
#         try:
#             request_data = json.loads(json.dumps(request.data))
#             username = request_data['username']
#             password = request_data['password']
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 user_data = {
#                     'userId': user.pk,
#                     'firstName': user.first_name,
#                     'lastName': user.last_name,
#                     'email': user.email,
#                 }
#                 # get user jwt token
#                 user_token = get_tokens_for_user(user)
#                 return Response({
#                     'hasError': False,
#                     'message': 'success',
#                     'response': {
#                         'userData': user_data,
#                         'auth': user_token
#                     }
#                 }, status=status.HTTP_200_OK)
#             else:
#                 return Response({
#                     'hasError': True,
#                     'message': 'User data not exist',
#                     "response": None
#                 }, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({
#                 'hasError': True,
#                 'message': str(e),
#                 'response': None
#             }, status=status.HTTP_200_OK)

 
class loginApi(APIView):
    serializer_class =usersSerializer
    def post(self, request):

        
        Serializer=usersSerializer(data=request.data)
        phone=request.POST.get('phone')
        password=request.POST.get('password')
        designation = request.POST.get('designation')
        
        
        
        # print(phone)
        # id=request.POST.get('id')
        role=roles.objects.filter(designation=designation)
        print(designation)
        # print(role.id)
        
        employee=Employee.objects.get(phone=phone)
        print(phone)
       
        # user=User.objects.get(id=employee.user_id)
        user=User.objects.get(password=make_password(password))
        print(user)
        # print(employee.designation_id)
        if role == employee.designation:
            login(user)
            return redirect('/BusinessAdd')
        elif role != employee.designation:

            login(user)
            print('logined')
            return redirect('/mybusiness',{'phone' == phone})
            
       
           
        if Serializer.is_valid():
                
                
            
               return JsonResponse("error",safe=False) 
        return JsonResponse(Serializer.data)





class ViewProfile(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, format=None):
        userdetail = request.user.id
        
        print(userdetail)
       # referal = User.objects.filter(account__id= userdetail)
        referal= User.objects.get(id=userdetail)
        #code = Employee.objects.filter(pk=referal)
        try:
            d={}
            if referal:
                d['useranme']=referal.username
                d['email']= referal.email
                d['phone']=referal.account.phone
                d['referral']=referal.account.referral
            else:
                d["message"]="Wrong user"
            # print(referal.password,"//////////////////////////////")
            # print(referal.account.referral,"/////////////////")
            # serialize = UserSerializer(data= referal)

            # serialize.is_valid()
            # print(serialize.data)
            return Response({"profile":d}) 
        except:
            return Response({"message":"somethingwrong"})


# class ViewProfile(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     print(queryset)
#     serializer_class = UserdetailsSerializer

#     def get_queryset(self):
#         if self.action == 'list':
#             return self.queryset.filter(user=self.request.user)
#         return self.queryset        



@api_view(["GET"])
def categoryapi(request,id):
    categories = category.objects.get(id=id)
    print(categories)
    categoryserilizer = businessSerializer(categories)
    
    return JsonResponse(categoryserilizer.data)


class CategoryBusiness(APIView):
    def get(self,request):
        try:
            products = ProductsListSerializer(
                business_details.objects.filter(id=request.data['categoryId']), many=True
            ).data
            return Response({
                'hasError': False,
                'message': 'Success',
                'categoryId': request.data['categoryId'],
                'cat_business': products
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'hasError': True,
                'message': f'Failed: {str(e)}',
                'response': None
            }, status=status.HTTP_200_OK)


from django.contrib.auth.hashers import make_password

