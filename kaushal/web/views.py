from django.shortcuts import render

# Create your views here.
def index(request):
    context = {"is_index": True}
    return render(request, "web/index.html", context)
