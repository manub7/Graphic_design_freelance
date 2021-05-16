from django.shortcuts import render, get_object_or_404
from .models import Client

# Create your views here.
def profile(request):
    """ Display users's profile  """
    profile = get_object_or_404(Client, user=request.user)
    template = 'profiles/profile.html'
    context = {
        'profile':profile,
    }

    return render(request, template, context)