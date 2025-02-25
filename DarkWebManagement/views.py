from django.views import View
from django.http import HttpResponse

class DarkWebManagementView(View):
    def get(self, request):
        return HttpResponse("مرحبا بك في DarkWebManagement!")
