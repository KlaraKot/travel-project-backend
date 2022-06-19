from django.http import JsonResponse
from myapp.models import *
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
#łączenie użytkownika z domem
def connectUH(request):
    if request.method == 'PUT':
        json_data = json.loads(request.body)
        idU = json_data['idU']
        idM = json_data['idM']
        try:
            user = User.nodes.get(id=idU)
            place = Place.nodes.get(id=idM)
            res = user.home.connect(place)
            response= {"result":res}
            return JsonResponse(response, safe=False)
        except:
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)

#łączenie użytkownika z miejscem, do którego chce pojechać
def connectUS(request):
    if request.method == 'PUT':
        json_data = json.loads(request.body)
        idU = json_data['idU']
        idM = json_data['idM']
        try:
            user = User.nodes.get(id=idU)
            place = Place.nodes.get(id=idM)
            res = user.summerPlace.connect(place)
            response= {"result":res}
            return JsonResponse(response, safe=False)
        except:
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)

#łączenie użytkownika z foodRate
def connectUF(request):
    if request.method == 'PUT':
        json_data = json.loads(request.body)
        id = json_data['id']
        rating = json_data['rating']
        try:
            user = User.nodes.get(id=id)
            place = Rating.nodes.get(rating=rating)
            res = user.foodRate.connect(place)
            response= {"result":res}
            return JsonResponse(response, safe=False)
        except:
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)