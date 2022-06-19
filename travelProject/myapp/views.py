from curses.ascii import NUL
import traceback
from django.http import HttpResponse
from django.http import JsonResponse
from myapp import models
from django.views.decorators.csrf import csrf_exempt
import json
from myapp.algorithms.averageRate import averageRateToCity, tenBestRated
from myapp.serializers import UserSerializer
from rest_framework.views import APIView
from myapp.serializers import UserSerializer
from rest_framework.response import Response
from myapp.models import User
from rest_framework.exceptions import AuthenticationFailed
import jwt
import datetime



#Rejestracja nowych użytkowników
class RegisterView(APIView):
    def post(self, request):
        dane = request.data
        id = models.lastId.objects.get()
        idNumber = id.lastId
        idNumber += 1
        newId = models.lastId(lastId=idNumber)
        dane['id'] = idNumber
        serializer = UserSerializer(data=dane)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        newId.save()
        id.delete()
        return Response(serializer.data)

#Logowanie użytkownika
class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect Password!')


        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')#.decode('utf-8')\

        response = Response()

        response.set_cookie(key='jwt', value=token, httponly=True)


        response.data = {
            'jwt': token
        }

        return response

#Widok, do którego dostęp ma tylko zalogowany użytkownik
class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Expired Authentication!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)


        return Response(serializer.data)


#wylogowywanie użytkownika
class LogoutView(APIView):
    def post(self, request):
        response= Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response

#wybieranie 10 najlepiej ocenionych miast (tylko dla zalogowanych uzytkowników)
class TenBestView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Expired Authentication!')
        try:
            response = []
            tenBest = []
            tenBest = tenBestRated()

            names = tenBest['cityName']
            countries = tenBest['country']
            raters = tenBest['raters']
            score = tenBest['score']
            for i in range(len(names)):
                obj = {
                    "cityName": names[i],
                    "country": countries[i],
                    "raters": str(raters[i]),
                    "score": str(score[i])
                }
                response.append(obj)

            

            return JsonResponse(response, safe=False)
        except:
            response={"error"}
            return JsonResponse(response, safe=False)


#ocenianie miasta(tylko zalogowani użytkownicy)
class RateCityView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Expired Authentication!')

        identyfikator = payload['id']
        json_data = json.loads(request.body)
        cityName = json_data['cityName']
        rate = json_data['rate']

        rating = models.cityRate.objects.filter(userId=identyfikator, cityName=cityName).first()
        
        if rating is None:
            try:
                rate = models.cityRate(cityName=cityName,rate = rate,
                userId = identyfikator)
                rate.save()
                averageRateToCity()
                response = {
                    "cityName": rate.cityName,
                    "rate": rate.rate,
                    "userId": rate.userId
                }
                return JsonResponse(response)
            except:
                response = {"error": "Error ed"}
                return JsonResponse(response, safe=False)


        return Response({"This user has already rated this city"})


# zmiana hasła
class ChangePasswordView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Expired Authentication!')

        identyfikator = payload['id']
        json_data = json.loads(request.body)

        ps = json_data['password']

        user = models.User.objects.get(id=identyfikator)
        dataR = {
            "name": user.name,
            "surname": user.surname,
            "id": user.id,
            "city": user.city,
            "age": user.age,
            "email": user.email,
            "password": ps,
            "languageNative": user.languageNative,
            "languageForeign": user.languageForeign
        }
        print(user.name)
        user.delete()
        serializer = UserSerializer(data=dataR)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        
        return Response({"Password changed"})
        

#formularz
class FillSurveyView(APIView):
    def post(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Expired Authentication!')

        identyfikator = payload['id']
        json_data = json.loads(request.body)
        survey = models.Survey(
            id = identyfikator,
            visitedPlaces = json_data['visitedPlaces'],
            preferencePlaces = json_data['preferencePlaces'],
            language = json_data['language'],
            seaOrMountains = json_data['seaOrMountains'],
            companion = json_data['companion'],
            wheelchair = json_data['wheelchair'],
            animals = json_data['animals'],
            listOfPreferences = json_data['listOfPreferences'],
            weather = json_data['weather'],
            typeOfCity = json_data['typeOfCity']
        )
        survey.save()
        return Response('survey saved')



def index(request):
    return HttpResponse('<h1>Travel Kaleidoscope</h1>')


# OPERACJE POBIERAJĄCE DANE Z BAZY


# pobieranie informacji o wszystkich miejscach zarejestrowanych w bazie
def getAllPlaces(request):
    if request.method == 'GET':
        try:
            places = models.Place.objects.all()
            response = []
            for place in places:
                obj = {
                    "id": place.id,
                    "name": place.name,
                    "city": place.city,
                    "country": place.country,
                }
                response.append(obj)
            return JsonResponse(response, safe=False)
        except:
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)


@csrf_exempt
def placeDetails(request):
    if request.method == 'GET':
        # pobieranie informacji o miejscu o konkretnym id
        id = request.GET.get('id', ' ')
        try:
            place = models.Place.objects.get(id=id)
            response = {
                "id": place.id,
                "name": place.name,
                "city": place.city,
                "country": place.country,
            }
            return JsonResponse(response, safe=False)
        except:
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)

    if request.method == 'POST':
        # tworzenie miejsca
        json_data = json.loads(request.body)
        id = json_data['id']
        name = json_data['name']
        city = json_data['city']
        country = json_data['country']
        try:
            place = models.Place(id=id, name=name, city=city, country=country)
            place.save()
            response = {
                "id": place.id,
                "name": place.name,
                "city": place.city,
                "country": place.country,
            }
            return JsonResponse(response)
        except:
            response = {"error": "Error ed"}
            return JsonResponse(response, safe=False)

    if request.method == 'PUT':
        # aktualizacja danych jednego miejsca
        json_data = json.loads(request.body)
        id = json_data['id']
        name = json_data['name']
        city = json_data['city']
        country = json_data['country']
        try:
            place = models.Place.objects.get(id=id)
            place.name = name
            place.city = city
            place.country = country
            place.save()
            response = {
                "id": place.id,
                "name": place.name,
                "city": place.city,
                "country": place.country,
            }
            return JsonResponse(response)
        except:
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)

    if request.method == 'DELETE':
        # usuwanie miejsca
        json_data = json.loads(request.body)
        id = json_data['id']
        try:
            place = models.Place.objects.get(id=id)
            place.delete()
            response = {"success": "Place deleted"}
            return JsonResponse(response, safe=False)
        except:
            response = {"error": "Error occurred"}
            return JsonResponse(response, safe=False)


# Pobieranie informacji o wszystkich użytkownikach
def getAllUsers(request):
    if request.method == 'GET':
        print("cos")
        try:
            users = models.User.objects.all()
            response = []
            for user in users:
                obj = {
                    "id": user.id,
                    "name": user.name,
                    "surname": user.surname,
                    "city": user.city,
                    "age": user.age,
                    "email": user.email,
                    "password": user.password,
                    "languageNative": user.languageNative,
                    "languageForeign": user.languageForeign,
                }
                response.append(obj)
            return JsonResponse(response, safe=False)
        except:
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)


@csrf_exempt
def userDetails(request):
    if request.method == 'GET':
        # pobieranie informacji o użytkowniku o konkretnym id
        id = request.GET.get('id', ' ')
        try:
            user = models.User.objects.get(id=id)
            response = {
                "id": user.id,
                "name": user.name,
                "surname": user.surname,
                "city": user.city,
                "age": user.age,
                "email": user.email,
                "password": user.password,
                "languageNative": user.languageNative,
                "languageForeign": user.languageForeign,
            }

            return JsonResponse(response, safe=False)
        except:
            response = {"error": "stg occured"}
            return JsonResponse(response, safe=False)

    if request.method == 'POST':
        # tworzenie użytkownika
        json_data = json.loads(request.body)
        id = json_data['id']
        name = json_data['name']
        surname = json_data['surname']
        city = json_data['city']
        age = json_data['age']
        email = json_data['age']
        password = json_data['password']
        languageNative = json_data['languageNative']
        languageForeign = json_data['languageForeign']

        try:
            user = models.User(
                id=id,
                name=name,
                surname=surname,
                city=city,
                age=age,
                email=email,
                password=password,
                languageNative=languageNative,
                languageForeign=languageForeign
            )
            user.save()
            response = {
                "id": user.id,
                "name": user.name,
                "surname": user.surname,
                "city": user.city,
                "age": user.age,
                "email": user.email,
                "password": user.password,
                "languageNative": user.languageNative,
                "languageForeign": user.languageForeign,
            }
            return JsonResponse(response)
        except Exception as e:
            message = traceback.format_exc()
            print(message)
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)

    if request.method == 'PUT':
        # aktualizacja danych jednej osoby
        json_data = json.loads(request.body)
        id = json_data['id']
        name = json_data['name']
        surname = json_data['surname']
        city = json_data['city']
        age = json_data['age']
        email = json_data['age']
        password = json_data['password']
        languageNative = json_data['languageNative']
        languageForeign = json_data['languageForeign']
        try:
            user = models.User.objects.get(id=id)
            user.name = name
            user.surname = surname
            user.city = city
            user.age = age
            user.email = email
            user.password = password
            user.languageNative = languageNative
            user.languageForeign = languageForeign
            response = {
                "id": user.id,
                "name": user.name,
                "surname": user.surname,
                "city": user.city,
                "age": user.age,
                "email": user.email,
                "password": user.password,
                "languageNative": user.languageNative,
                "languageForeign": user.languageForeign,
            }
            return JsonResponse(response)
        except:
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)

    if request.method == 'DELETE':
        # usuwanie użytkownika
        json_data = json.loads(request.body)
        id = json_data['id']
        try:
            user = models.User.objects.get(id=id)
            user.delete()
            response = {"success": "Person deleted"}
            return JsonResponse(response, safe=False)
        except:
            response = {"error": "Error occurred"}
            return JsonResponse(response, safe=False)


# pobieranie informacji o wszystkich wpisach w historii zarejestrowanych w bazie
def getAllPlacesH(request):
    if request.method == 'GET':
        try:
            records = models.HistoryRecord.objects.all()
            response = []
            for record in records:
                obj = {
                    "id": record.id,
                    "actionType": record.actionType,
                    "actionContent": record.actionContent,
                    "date": record.date,
                }
                response.append(obj)
            return JsonResponse(response, safe=False)
        except:
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)


@csrf_exempt
def placeDetailsH(request):
    if request.method == 'GET':
        # pobieranie informacji o wpisie o konkretnym id
        id = request.GET.get('id', ' ')
        try:
            record = models.HistoryRecord.objects.get(id=id)
            response = {
                "id": record.id,
                "actionType": record.actionType,
                "actionContent": record.actionContent,
                "date": record.date,
            }
            return JsonResponse(response, safe=False)
        except:
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)

    if request.method == 'POST':
        # tworzenie wpisu
        json_data = json.loads(request.body)
        id = json_data['id']
        actionType = json_data['actionType']
        actionContent = json_data['actionContent']
        date = json_data['date']
        try:
            record = models.HistoryRecord(
                id=id,
                actionType=actionType,
                actionContent=actionContent,
                date=date
            )
            record.save()
            response = {
                "id": record.id,
                "actionType": record.actionType,
                "actionContent": record.actionContent,
                "date": record.date,
            }
            return JsonResponse(response)
        except:
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)

    if request.method == 'PUT':
        # aktualizacja danych jednego wpisu
        json_data = json.loads(request.body)
        id = json_data['id']
        actionType = json_data['actionType']
        actionContent = json_data['actionContent']
        date = json_data['date']
        try:
            record = models.HistoryRecord.objects.get(id=id)
            record.actionType = actionType
            record.actionContent = actionContent
            record.date = date
            record.save()
            response = {
                "id": record.id,
                "actionType": record.actionType,
                "actionContent": record.actionContent,
                "date": record.date,
            }
            return JsonResponse(response)
        except:
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)

    if request.method == 'DELETE':
        # usuwanie wpisu
        json_data = json.loads(request.body)
        id = json_data['id']
        try:
            record = models.HistoryRecord.objects.get(id=id)
            record.delete()
            response = {"success": "History Record deleted"}
            return JsonResponse(response, safe=False)
        except:
            response = {"error": "Error occurred"}
            return JsonResponse(response, safe=False)


# pobieranie informacji o wszystkich obiektach typu Entartainment
def getAllEntartainmentPlaces(request):
    if request.method == 'GET':
        try:
            places = models.Entertainment.objects.all()
            response = []
            for place in places:
                obj = {
                    "EntartainmentType": place.EntertainmentType
                }
                response.append(obj)
            return JsonResponse(response, safe=False)
        except:
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)


@csrf_exempt
def placeEntartainmentDetails(request):

    if request.method == 'POST':
        # tworzenie miejsca
        json_data = json.loads(request.body)
        EntertainmentType = json_data['EntertainmentType']
        try:
            place = models.Entertainment(EntertainmentType=EntertainmentType)
            place.save()
            response = {
                "EnterteinmentType": place.EntertainmentType
            }
            return JsonResponse(response)
        except:
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)

    if request.method == 'PUT':
        # aktualizacja danych jednego miejsca
        json_data = json.loads(request.body)
        EntertainmentType = json_data['EntertainmentType']
        try:
            place = models.Entertainment.objects.get(
                EntertainmentType=EntertainmentType)
            place.EntertainmentType = EntertainmentType
            place.save()
            response = {
                "EntertainmentType": place.EntertainmentType
            }
            return JsonResponse(response)
        except:
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)

    if request.method == 'DELETE':
        # usuwanie miejsca
        json_data = json.loads(request.body)
        EntertainmentType = json_data['EntertainmentType']
        try:
            place = models.Entertainment.objects.get(
                EntertainmentType=EntertainmentType)
            place.delete()
            response = {"success": "Place deleted"}
            return JsonResponse(response, safe=False)
        except:
            response = {"error": "Error occurred"}
            return JsonResponse(response, safe=False)


@csrf_exempt
def surveyDetails(request):
    if request.method == "POST":
        json_data = json.loads(request.body)
        id = json_data['id']
        visitedPlaces = json_data['visitedPlaces'] 
        preferencePlaces = json_data['preferencePlaces'] 
        language = json_data['language'] 
        seaOrMountains = json_data["seaOrMountains"]
        companion = json_data['companion']
        wheelchair = json_data['wheelchair']
        animals = json_data['animals']
        listOfPreferences = json_data['listOfPreferences'] 
        weather = json_data['weather']
        typeOfCity = json_data['typeOfCity']
        try:
            survey = models.Survey(id=id,visitedPlaces = visitedPlaces,
            preferencePlaces = preferencePlaces,
            seaOrMountains = seaOrMountains, companion = companion, wheelchair = wheelchair, animals = animals,
            listOfPreferences = listOfPreferences, weather = weather, typeOfCity=typeOfCity, language=language)
            survey.save()
            response = {
                "id": survey.id,
                "visitedPlaces": survey.visitedPlaces,
                "preferencePlaces": survey.preferencePlaces,
                "listOfPreferences": survey.listOfPreferences,
            }
            return JsonResponse(response)
        except:
            response = {"error": "Error ed"}
            return JsonResponse(response, safe=False)

    if request.method == 'GET':
        # pobieranie informacji o wpisie o konkretnym id
        id = request.GET.get('id', ' ')
        try:
            surveys = models.Survey.objects.all()
            response = []
            for survey in surveys:
                obj = {
                    "id": survey.id,
                    "visitedPlaces": survey.visitedPlaces,
                    "preferencePlaces": survey.preferencePlaces,
                    "listOfPreferences": survey.listOfPreferences,
                }
                response.append(obj)
            return JsonResponse(response, safe=False)
        except:
            response = {"error": "Error occured"}
            return JsonResponse(response, safe=False)

@csrf_exempt
def cityDetails(request):
    if request.method == "POST":
        json_data = json.loads(request.body)
        cityName = json_data['cityName']
        country = json_data['country'] 
        description = json_data['description'] 
        monuments = json_data['monuments']
        averageRate = 0
        try:
            city = models.City(cityName=cityName,country = country,
            description = description,monuments = monuments, averageRate = averageRate)
            city.save()
            response = {
                "cityName": city.cityName,
                "country": city.country,
                "description": city.description,
                "monuments" : city.monuments,
                "averageRate": city.averageRate
            }
            return JsonResponse(response)
        except:
            response = {"error": "Error ed"}
            return JsonResponse(response, safe=False)

    if request.method == 'GET':
        # pobieranie informacji o wpisie o konkretnym id
        try:
            cities = models.City.objects.all()
            response = []
            for city in cities:
                obj = {
                    "cityName": city.cityName,
                    "country": city.country,
                    "description": city.description,
                    "monuments" : city.monuments,
                    "averageRate": city.averageRate,
                }
                response.append(obj)
            return JsonResponse(response, safe=False)
        except:
            response = {"error"}
            return JsonResponse(response, safe=False)

@csrf_exempt
def cityRate(request):
    if request.method == "POST":
        json_data = json.loads(request.body)
        cityName = json_data['cityName']
        rate = json_data['rate'] 
        userId = json_data['userId'] 
        try:
            rate = models.cityRate(cityName=cityName,rate = rate,
            userId = userId)
            rate.save()
            averageRateToCity()
            response = {
                "cityName": rate.cityName,
                "rate": rate.rate,
                "userId": rate.userId
            }
            return JsonResponse(response)
        except:
            response = {"error": "Error ed"}
            return JsonResponse(response, safe=False)
    
    if request.method == "GET":
        try:
            rates = models.cityRate.objects.all()
            response = []
            for rate in rates:
                obj = {
                    "cityName": rate.cityName,
                    "rate": rate.rate,
                    "userId": rate.userId
                }
                response.append(obj)
            return JsonResponse(response, safe=False)
        except:
            response = {"error"}
            return JsonResponse(response, safe=False)


def tenBest(request):
    if request.method == "GET":
        try:
            response = []
            tenBest = []
            tenBest = tenBestRated()
            print("best")
            print(tenBest)

            names = tenBest['cityName']
            countries = tenBest['country']
            raters = tenBest['raters']
            score = tenBest['score']
            for i in range(len(names)):
                obj = {
                    "cityName": names[i],
                    "country": countries[i],
                    "raters": str(raters[i]),
                    "score": str(score[i])
                }
                response.append(obj)

            return JsonResponse(response, safe=False)
        except:
            response={"error"}
            return JsonResponse(response, safe=False)

