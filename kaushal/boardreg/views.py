from django.shortcuts import render

# Create your views here.
def boardreg(request):
    context = {"is_index": True}
    return render(request, "boardreg/boardreg.html", context)
