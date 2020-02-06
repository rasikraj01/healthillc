from django.urls import path
from .views import Index, About, TermsAndConditions, Privacy , Refund

urlpatterns = [
    path('', Index.as_view(), name='home'),
    path('about/', About.as_view(), name='about'),
    path('tnc/', TermsAndConditions.as_view(), name='tnc'),
    path('privacy/', Privacy.as_view(), name='privacy'),
    # path('refund/', Refund.as_view(), name='refund'),
]