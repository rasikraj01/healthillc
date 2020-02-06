from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetCompleteView, PasswordResetConfirmView
from users.views import Dashboard, Register, Plans, Checkout
from users import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('', include('about.urls')),
    
    path('plans/', Plans.as_view(), name='plans'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),

    path('checkout', Checkout.as_view(), name='checkout'),
    # path('request/', Request.as_view(), name='request'),
    path('response/', views.response, name='response'),
    #path('notify/', views.notification_email, name='notification_email'),

    path('register/', Register.as_view(), name='register'),
    path('login/', LoginView.as_view(template_name='users/login.html'), name="login"),
    path('logout/', LogoutView.as_view(template_name='users/logout.html'), name="logout"),

    path('password-reset/',
        PasswordResetView.as_view(template_name='users/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
        PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
        PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete')
]