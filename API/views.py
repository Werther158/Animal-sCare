from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.contrib.auth.models import User
from recensioni.models import Recensione
from API.serializers import (AnagraficaSerializer,
                                AnnuncioSerializer,
                                UserSerializer,
                                ServizioOffertoSerializer,
                                AnnuncioConServizi,
                                DatiUtenteCompleti,
                                CompletaRegPetsitterSerializer,
                                CompletaRegUtenteNormale,
                                RecensioniSerializer,
                                ContattaciSerializer,
                            )
from annunci.views import ordina_annunci as ordina_geograficamente
from .permissions import *
from django.core.mail import EmailMessage
from django.conf import settings


from rest_framework.parsers import JSONParser, MultiPartParser, FileUploadParser




class userInfoLogin(generics.RetrieveAPIView):
    """
    Questa view restituisce la lista completa degli utenti registrati
    """
    # permission_classes = [IsSameUserOrReadOnly,IsUserLogged]
    serializer_class = DatiUtenteCompleti
    def get_object(self):
        """
        Modifico il query set in modo da ottenere l'utente con l'id
        prelevato dall'url
        """
        oid = self.kwargs['pk']
        return Profile.objects.get(user=oid)

class selfUserInfoLogin(generics.RetrieveUpdateAPIView):
    '''
    restituisco di default il profilo dell'utente loggato
    '''
    permission_classes = [IsSameUserOrReadOnly, IsUserLogged]
    serializer_class = DatiUtenteCompleti

    def get_object(self):

        return Profile.objects.get(user=self.request.user)

class completaRegPetsitter(generics.RetrieveUpdateAPIView):
    permission_classes = [IsSameUserOrReadOnly]
    serializer_class = CompletaRegPetsitterSerializer
    def get_object(self):
        return Profile.objects.get(user=self.request.user)


class completaRegUtentenormale(generics.RetrieveUpdateAPIView):
    permission_classes = [IsSameUserOrReadOnly]
    serializer_class = CompletaRegUtenteNormale
    def get_object(self):
        return Profile.objects.get(user=self.request.user)


class listaAnnunci(generics.ListAPIView):
    """
     Questa view restituisce la lista completa di tutti gli annunci
     """
    serializer_class = AnnuncioSerializer

    def get_queryset(self):
        return Annuncio.objects.filter(user_accetta__isnull=True)


class ordinaAnnunci(generics.ListAPIView):
    '''
    API per ordinamento degli annunci
    url : /api/annunci/ordina/ < animale > / < ordinamento > / < tipo_utente > /

    Parametri :

    animale :       < Cane, Gatto, Coniglio, Volatile, Rettile, Altro >

    ordinamento :   < crescente, decrescente>

    tipo_utente :   < petsitter, normale >

    Attenzione per ignorare il criterio di ordinamento inserire " * "

    in tal caso se inseriti tutti '*' fornirà i dati normalmente come lista annunci
    '''
    serializer_class = AnnuncioSerializer
    def get_queryset(self):
        ordinamento = self.kwargs['ordinamento']
        tipo_utente = self.kwargs['tipo_utente']
        animale = self.kwargs['animale']
        lista = Annuncio.objects.filter(user_accetta__isnull=True)

        if tipo_utente == '*' and animale != '*':
            lista = Annuncio.objects.filter(user_accetta__isnull=True, pet=animale)

        if tipo_utente == '*' and animale == '*':
            lista = Annuncio.objects.filter(user_accetta__isnull=True)

        if tipo_utente == 'petsitter' and animale != '*':
            lista = Annuncio.objects.filter(user_accetta__isnull=True, pet=animale, annuncio_petsitter=True)

        if tipo_utente == 'normale'and animale != '*':
            lista = Annuncio.objects.filter(user_accetta__isnull=True, pet=animale, annuncio_petsitter=False)

        if tipo_utente == 'petsitter' and animale == '*':
            lista = Annuncio.objects.filter(user_accetta__isnull=True, annuncio_petsitter=True)

        if tipo_utente == 'normale'and animale == '*':
            lista = Annuncio.objects.filter(user_accetta__isnull=True, annuncio_petsitter=False)

        if ordinamento == 'crescente' or ordinamento == 'decrescente':
            profilo_utente = Profile.objects.get(user=self.request.user)
            indici = []
            indici = ordina_geograficamente(profilo_utente, lista, ordinamento)

            lista = list(lista)
            new_annunci_validi = list()
            # Ordina annunci_validi
            for i, annuncio in enumerate(lista):
                new_annunci_validi.append(lista[indici[i]])
            return new_annunci_validi

        return lista

class dettaglioAnnuncio(generics.RetrieveUpdateDestroyAPIView):
    """
    Questa view restituisce l'annuncio avente ID passato tramite URL
    e ne permette la modifica
    """
    permission_classes = [IsAnnuncioPossessorOrReadOnly]
    serializer_class = AnnuncioConServizi
    def get_object(self):
        """
        Questa view restituisce i flag dell'annuncio avente ID passato tramite URL
        """
        oid = self.kwargs['pk']
        return Servizio.objects.get(annuncio=oid)


class elencoAnnunciUtente(generics.ListAPIView):
    '''restituisce tutti gli annunci fatti da un utente'''
    serializer_class = AnnuncioConServizi

    def get_queryset(self):
        """
        Questa view restituisce l'annuncio avente ID passato tramite URL
        """
        oid = self.kwargs['pk']
        return Servizio.objects.filter(annuncio__user=oid, annuncio__user_accetta = None)


class inserisciAnnuncio(generics.CreateAPIView):
    '''crea un nuovo annuncio'''
    serializer_class = AnnuncioConServizi
    permission_classes = [IsUserLogged]


class accettaAnnuncio(generics.RetrieveUpdateAPIView):
    permission_classes = [IsCompatibleUser,IsUserLogged]
    serializer_class = AnnuncioConServizi
    def get_object(self):
        """
        Questa view restituisce l'annuncio avente ID passato tramite URL
        """
        oid = self.kwargs['pk']
        return Servizio.objects.get(annuncio=oid)


class calendarioUtente(generics.ListAPIView):
    permission_classes = [IsUserLogged]
    serializer_class = AnnuncioSerializer
    def get_queryset(self):
        user_request = self.request.user
        queryset = Annuncio.objects.filter(user_accetta=user_request)

        return queryset

class cercaUtente(generics.ListAPIView):
    serializer_class = DatiUtenteCompleti
    def get_queryset(self):
        name = self.kwargs['name']
        profili = []
        try :
            username_cercato = User.objects.get(username__exact=name)
            profilo = Profile.objects.get(user=username_cercato)
            profilo.user.password=""
            profili.append(profilo)
            return profili
        except Exception:
            username_trovati = User.objects.filter(username__startswith=name)
            if len(username_trovati) == 0:
                username_trovati = User.objects.filter(username__contains=name)
            for user in username_trovati:
                p = Profile.objects.get(user=user)
                p.user.password = ""
                profili.append(p)
            return profili


class classificaUtenti(generics.ListAPIView):
    '''
    API per la classifica utente :

    tipo_utente : < petsitter > ,  < normale >, < * >

    criterio : < voti > , < recensioni >

    PER SELEZIONARE TUTTI GLI UTENTI INSERIRE ' * '

    NON È AMMESSO IGNORARE IL CRITERIO DI ORDINAMENTO

    '''
    serializer_class = DatiUtenteCompleti
    def get_queryset(self):
        criterio = self.kwargs['criterio']
        tipo_utente = self.kwargs['tipo_utente']

        # viene fatto sempre se si ignora il criterio di ricerca
        profili = Profile.objects.all()

        if tipo_utente == 'petsitter':
            profili = Profile.objects.filter(pet_sitter=True)

        if tipo_utente == 'normale':
            profili = Profile.objects.filter(pet_sitter=False)

        if criterio == 'voti':
            lista = list()
            for p in profili:
                voti = Recensione.objects.filter(user_recensito= p.user)
                somma = 0
                for v in voti:
                    somma += v.voto
                if len(voti) > 0:
                    media = somma / len(voti)
                else:
                    media = 0
                tupla = (p, media)
                lista.append(tupla)
            lista = sorted(lista, key=lambda tup: tup[1], reverse=True)
            profili = []
            for i in lista:
                profili.append(i[0])
            return profili

        if criterio == 'recensioni':
            lista = list()
            for p in profili:
                voti = Recensione.objects.filter(user_recensito= p.user)
                tupla = (p, len(voti))
                lista.append(tupla)
            lista = sorted(lista, key=lambda tup: tup[1], reverse=True)
            profili = []
            for i in lista:
                profili.append(i[0])
            return profili


class recensisciUtente(generics.CreateAPIView):
    serializer_class = RecensioniSerializer
    permission_classes = [IsUserLogged]

    def perform_create(self, serializer):
        nickname_recensore = self.request.user.username
        nickname_recensito = self.kwargs['utente_recensito']
        try:
            recensore = User.objects.get(username=nickname_recensore)
        except Exception:
            raise Exception("Utente recensore non trovato")
        try:
            recensito = User.objects.get(username=nickname_recensito)
        except Exception:
            raise Exception("Utente recensito non trovato")
        serializer.save(user_recensore=recensore, user_recensito=recensito)


class recensioniRicevute(generics.ListAPIView):
    serializer_class = RecensioniSerializer
    def get_queryset(self):
        # lista_recensioni = []
        nickname_cercato = self.kwargs['utente']
        try:
            recensito = User.objects.get(username=nickname_cercato)
        except Exception:
            raise Exception("Utente recensito non trovato")
        recensioni = Recensione.objects.filter(user_recensito=recensito)
        return list(recensioni)


class modificaRecensione(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RecensioniSerializer
    permission_classes = [IsUserLogged, IsRecensionePossessorOrReadOnly]

    def get_object(self):
        nickname_recensore = self.request.user.username
        nickname_recensito = self.kwargs['utente']
        try:
            recensore = User.objects.get(username=nickname_recensore)
        except Exception:
            raise Exception("Utente recensore non trovato")
        try:
            recensito = User.objects.get(username=nickname_recensito)
        except Exception:
            raise Exception("Utente recensito non trovato")

        try:
            recensione = Recensione.objects.get(user_recensore=recensore, user_recensito=recensito)
            return recensione
        except Exception:
            raise Exception("Recensione non trovata." +
                            " \nrecensore : " + nickname_recensore +
                            " \nrecensito : " + nickname_recensito)


class modificaPetCoins(generics.RetrieveUpdateAPIView):
    serializer_class = AnagraficaSerializer
    permission_classes = [IsUserLogged]

    def get_object(self):
        return Profile.objects.get(user=self.request.user)

    def perform_update(self, serializer):
        num = int(self.kwargs['num'])
        valori_ammessi = [ 50, 100, 200, -50, -100, -200]
        if num not in valori_ammessi:
            raise Exception("Valore non ammesso")
        val = serializer.validated_data['pet_coins']
        val = val + num
        serializer.save(pet_coins=val)


class contattaciInPrivato(generics.CreateAPIView):
    serializer_class = ContattaciSerializer
    permission_classes = [IsUserLogged]

    def perform_create(self, serializer):
        print("titolo", serializer.validated_data['titolo'])
        print("messaggio", serializer.validated_data['messaggio'])
        email = EmailMessage(serializer.validated_data['titolo'],
                             'Messaggio dall\'utente: ' + self.request.user.username + "\n" +
                             serializer.validated_data['messaggio'], to=[settings.EMAIL_HOST_USER])
        email.send()

# #################################################
#                          DA CANCELLARE
# #################################################



class elencoservizi(APIView):
    '''
    in questa classe prendo la lista di tutti gli utenti registrati sul sito.
    solo per scopi di debug
    DA CANCELLARE
    '''

    def get(self, request):
        data = Servizio.objects.all()
        serializer = ServizioOffertoSerializer(data, many=True)
        return Response(serializer.data)

class ListaUtentiRegistrati(APIView):
    '''
    in questa classe prendo la lista di tutti gli utenti registrati sul sito.
    solo per scopi di debug
    DA CANCELLARE
    '''

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class ListaAnagraficheRegistrate(APIView):
    '''
    in questa classe prendo la lista di tutti gli utenti registrati sul sito.
    solo per scopi di debug
    DA CANCELLARE
    '''

    def get(self, request):
        profili = Profile.objects.all()
        serializer = AnagraficaSerializer(profili, many=True)
        return Response(serializer.data)

