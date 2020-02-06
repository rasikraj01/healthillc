from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_datetime

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt

import hashlib
import hmac
import base64
import secrets
import string
import datetime
import pytz

from django.views import View
from .models import Plan, Coupon, Profile
from .forms import UserCreationForm, ProfileUpdateForm



cashfree_secretKey = "fa8e99f85500139601ee501559cbf958798c770b"
cashfree_AppId = "60613b4fa1545bc35c6e096c1606"

class Plans(View):
    def get(self, request):
        show_plan = True
        if request.user != 'AnonymousUser':
            try:
               if request.user.profile.expiry_date > pytz.utc.localize(datetime.datetime.today()):
                   show_plan = False
            except:
                pass

        context = {
            "Plans" : Plan.objects.all(),
            "show_plan" : show_plan
        }
        return render(request, 'users/plans.html', context)

class Register(View):
    def get(self, request, *args, **kwrgs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:
            form = UserCreationForm()
            return render(request, 'users/register.html', {'form': form})
        
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, 'users/register.html', {'form': form})


class Dashboard(LoginRequiredMixin, View):
    def get(self, request):
        form_profile = ProfileUpdateForm(instance=request.user.profile)

        profile_user = Profile.objects.get(user=request.user)
        expiry_date =  datetime.time()
        try:
            expiry_date = profile_user.expiry_date.strftime('%b %d,%Y')
        except:
            pass
        context = {
            'form_profile' : form_profile,
            'current_plan' : profile_user.current_plan,
            'expiry_date' : expiry_date
        }

        return render(request, 'users/dashboard.html', context)

    def post(self, request):
        form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, f'Profile Updated')
            return redirect('dashboard')
        messages.success(request, f'not updated')
        return render(request, 'users/dashboard.html', context)

final_cost = 0.0
class Checkout(LoginRequiredMixin, View):
    @method_decorator(csrf_protect)
    def get(self, request):
        global final_cost
        
        if request.user.profile.contact_no != '':
            if 'coupon' in request.GET and 'planid' in request.GET:
                selected_plan = Plan.objects.get(plan_id=request.GET['planid'])
                coupon = {}
                coupon['validity'] = False
                
                try:
                    coupon = Coupon.objects.get(coupon_id=request.GET['coupon'].upper())
                    if coupon.status:
                        discount = coupon.discount_percent/100
                        selected_plan.cost = selected_plan.cost - (selected_plan.cost*discount)
                        coupon.validity =  True 
                    else:
                        coupon.validity =  True
                        print('coupon Expired')
                except:
                    print('invalid coupon')
                    pass

                context = {
                    'order_currency' : 'INR',
                    'selected_plan' : selected_plan,
                    'coupon' : coupon
                }

                final_cost = selected_plan.cost 

                return render(request, 'users/checkout.html', context)

            elif 'planid' in request.GET:
                selected_plan = Plan.objects.get(plan_id=request.GET['planid'])
                context = {
                    'order_currency' : 'INR',
                    'selected_plan' : selected_plan,
                }

                final_cost = selected_plan.cost
                return render(request, 'users/checkout.html', context)
            else:
                return redirect('plans')
        else:
            return redirect('dashboard')
    
    @method_decorator(csrf_protect)
    def post(self, request):
        mode = "TEST"

        user_email  = request.user.email
        user_contact = request.user.profile.contact_no
        user_name = request.user.username
        order_id = request.GET['planid'] + secrets.token_hex(7) + user_name

        postData = {
            "appId" : cashfree_AppId, 
            "orderId" : order_id,
            "orderAmount" : str(final_cost), 
            "orderCurrency" : 'INR', 
            "customerName" : user_name, 
            "customerPhone" : user_contact, 
            "customerEmail" : user_email,
            "returnUrl" : 'http://localhost:8000/response/'
            }
        sortedKeys = sorted(postData)
        signatureData = ""
        for key in sortedKeys:
            signatureData += key+postData[key]
        message = signatureData.encode('utf-8')
        secret = cashfree_secretKey.encode('utf-8')
        signature = base64.b64encode(hmac.new(secret,message,digestmod=hashlib.sha256).digest()).decode("utf-8")

        postData.update({'signature': signature})
        
        if mode == 'TEST':
            url = 'https://test.cashfree.com/billpay/checkout/post/submit'
        else:
            url = 'https://www.cashfree.com/checkout/post/submit'

        postData.update({'url' : url})

        profile = Profile.objects.get(user=request.user)
        profile.order_id = order_id
        profile.save()

        print(postData)
        return render(request, 'users/request.html', postData)


@csrf_exempt
def response(request):
    if request.method == 'POST':
        print(request.user)
        postData = {
            "orderId" : request.POST['orderId'],
            "orderAmount" : request.POST['orderAmount'], 
            "referenceId" : request.POST['referenceId'], 
            "txStatus" : request.POST['txStatus'], 
            "paymentMode" : request.POST['paymentMode'], 
            "txMsg" : request.POST['txMsg'], 
            "signature" : request.POST['signature'], 
            "txTime" : request.POST['txTime']
        }

        signatureData = ""
        signatureData = postData['orderId'] + postData['orderAmount'] + postData['referenceId'] + postData['txStatus'] + postData['paymentMode'] + postData['txMsg'] + postData['txTime']
        message = signatureData.encode('utf-8')
        secret = cashfree_secretKey.encode('utf-8')
        computedsignature = base64.b64encode(hmac.new(secret,message,digestmod=hashlib.sha256).digest()).decode('utf-8')
        if computedsignature == postData['signature']:
            body = f'''
            Order Details :

            Order ID : {postData['orderId']}
            Order Amount : {postData['orderAmount']}
            Reference ID : {postData['referenceId']}
            Transaction Status : {postData['txStatus']}
            Payment Mode : {postData['paymentMode']}
            Message : {postData['txMsg']}
            Transaction Time : {postData['txTime']}

            '''
            subject = f'''Transaction Made to your Account orderID : {postData['orderId']}'''
            email = EmailMessage(subject, body, to=['healthillc@gmail.com'])
            print('sent')
            email.send()
            return render(request, 'users/response.html', postData)
        else:
            return render(request, 'users/payement_failed.html')
    elif request.method == 'GET':
        context = {
            "orderId" : request.GET['orderId'],
            "txStatus" : request.GET['txStatus'],
            "txTime" : request.GET['txTime']
        }
        if request.user.profile.order_id == context['orderId'] and context['txStatus'] == 'SUCCESS':
            
            profile = Profile.objects.get(user=request.user)
            profile.order_TxTime = context['txTime']
            profile.order_Status = context['txStatus']

            Plans = Plan.objects.all()
            for plan in Plans:
                if profile.order_id.startswith(plan.plan_id):
                    profile.current_plan = plan.name
                    profile.expiry_date = parse_datetime(context['txTime']) + datetime.timedelta(days=(plan.duration*7))
            
            profile.save()

            body = f'''

            Thank You For buying our Plan.
            Your Trainer will contact you within 24hrs.

            Regards,
            Team Healhtillc
            '''
            
            email = EmailMessage('Payment Confirmation', body, to=[request.user.email])
            print('sent')
            email.send()
            return redirect('dashboard')
        else:
            profile = Profile.objects.get(user=request.user)
            profile.order_id = ''
            profile.order_Status = context['txStatus']
            profile.save()
            return redirect('dashboard')
