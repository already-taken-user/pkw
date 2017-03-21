from jinja2 import Environment, PackageLoader
from jinja2 import select_autoescape
import csv
import collections


env = Environment(
        loader = PackageLoader('nowy', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
)


wyniki_wybory = {}
statystyki_wybory = {}
kluczeKandydaci = []
kluczeDane = []

# powiatDane = {}
# powiatWyniki = {}

okregiDane = {}
okregiWyniki = {}
wojewodztwoDane = {}
wojewodztwoWyniki = {}

kodGminyNazwa = {}

ltrPL = "ŻÓŁĆĘŚĄŹŃżółćęśąźń"
ltrnoPL = "ZOLCESAZNzolcesazn"
trantab = str.maketrans(ltrPL, ltrnoPL)




def percentage(part, whole):
  return 100 * float(part)/float(whole)

def generujKlucze(fieldnames):
    for i in range(11, 23):
        kluczeKandydaci.append(fieldnames[i])
    for i in range(6, 11):
        if i == 8: continue;
        kluczeDane.append(fieldnames[i])

def sumujGlosy(kandydaciWyniki):
    suma = 0
    for kandydat in kandydaciWyniki:
        suma += kandydaciWyniki[kandydat]
    if suma == 0: return 1
    else: return suma

def generujKandydaciProcenty(kandydaciWyniki):
    kandydaciProcenty = {}
    glosy = sumujGlosy(kandydaciWyniki)
    for key in kandydaciWyniki:
        kandydaciProcenty[key] = round(percentage(kandydaciWyniki[key],
                                            glosy), 2)
    return kandydaciProcenty

def obliczFrekwencje(dane):
    return round(percentage(int(dane['Głosy ważne']) + int(dane['Głosy nieważne']),
                            int(dane['Uprawnieni'])), 2)


def generujNazwyHTML(dane):
    noweNazwy = {}
    for key in dane:
        noweNazwy[key] = key.translate(trantab).lower()
    return noweNazwy


# def sumujDaneWyniki(tab1, tab2):
#     for klucz in kluczeDane:
#         tab1[klucz] += tab2[klucz]
#     for klucz in kluczeKandydaci:
#         tab1[klucz] += tab2[klucz]

def utworzKlucze(wojewodztwo, okrag, kodGminy):
    if wojewodztwo not in statystyki_wybory:
        wyniki_wybory[wojewodztwo] = {}
        statystyki_wybory[wojewodztwo] = {}
    if okrag not in statystyki_wybory[wojewodztwo]:
        wyniki_wybory[wojewodztwo][okrag] = {}
        statystyki_wybory[wojewodztwo][okrag] = {}
    if kodGminy not in statystyki_wybory[wojewodztwo][okrag]:
        wyniki_wybory[wojewodztwo][okrag][kodGminy] = {}
        statystyki_wybory[wojewodztwo][okrag][kodGminy] = {}
    wyniki_wybory[wojewodztwo][okrag][kodGminy] = dict.fromkeys(kluczeKandydaci, 0)
    statystyki_wybory[wojewodztwo][okrag][kodGminy] = dict.fromkeys(kluczeDane, 0)



# def parsujDane():
#     with open('../../pkw2000.csv') as csvfile:
#         reader_csv = csv.DictReader(csvfile)
#         generujKlucze(reader_csv.fieldnames)
#         for row in reader_csv:
#             wojewodztwo = row['Województwo']
#             okrag = row['Nr okręgu']
#             powiat = row['Powiat']
#             kodGminy = row['Kod gminy']
#             utworzKlucze(wojewodztwo, okrag, powiat, kodGminy)
#             wynikDlaGminy = wyniki_wybory[wojewodztwo][okrag][powiat][kodGminy]
#             daneDlaGminy = statystyki_wybory[wojewodztwo][okrag][powiat][kodGminy]
#             for kandydat in wynikDlaGminy:
#                 wynikDlaGminy[kandydat] = int(row[kandydat])
#             for dane in daneDlaGminy:
#                 daneDlaGminy[dane] = int(row[dane])

def parsujDane():
    with open('../../pkw2000.csv') as csvfile:
        reader_csv = csv.DictReader(csvfile)
        generujKlucze(reader_csv.fieldnames)
        for row in reader_csv:
            wojewodztwo = row['Województwo']
            okrag = row['Nr okręgu']
            kodGminy = row['Kod gminy']
            gmina = row['Gmina']
            utworzKlucze(wojewodztwo, okrag, kodGminy)
            wynikDlaGminy = wyniki_wybory[wojewodztwo][okrag][kodGminy]
            daneDlaGminy = statystyki_wybory[wojewodztwo][okrag][kodGminy]
            kodGminyNazwa[kodGminy] = gmina
            for kandydat in wynikDlaGminy:
                wynikDlaGminy[kandydat] = int(row[kandydat])
            for dane in daneDlaGminy:
                daneDlaGminy[dane] = int(row[dane])

def generujGminy():

    template = env.get_template("gmina2.html")

    for wojewodztwo in statystyki_wybory:
        for okrag in statystyki_wybory[wojewodztwo]:
            for nrGminy in statystyki_wybory[wojewodztwo][okrag]:

                wyniki = wyniki_wybory[wojewodztwo][okrag][nrGminy]
                statystyki = statystyki_wybory[wojewodztwo][okrag][nrGminy]

                kandydaciProcenty = generujKandydaciProcenty(wyniki)
                statystyki['Frekwencja'] = obliczFrekwencje(statystyki)

                with open("generowane/" + nrGminy + ".html", "w") as out:
                    out.write(template.render(
                        gmina = kodGminyNazwa[nrGminy],
                        dane = statystyki,
                        kandydaci_glosy = collections.OrderedDict(sorted(wyniki.items(), key=lambda t: t[0])),
                        kandydaci_procenty = kandydaciProcenty
                    ))

# def generujGminy():
#     gminaKandydaciProcenty = {}
#
#     template = env.get_template("gmina2.html")
#     i = 0
#     for wojewodztwo in statystyki_wybory:
#         for okrag in statystyki_wybory[wojewodztwo]:
#             for powiat in statystyki_wybory[wojewodztwo][okrag]:
#                 for nrGminy in statystyki_wybory[wojewodztwo][okrag][powiat]:
#                     i += 1
#
#                     wyniki = wyniki_wybory[wojewodztwo][okrag][powiat][nrGminy]
#                     statystyki = statystyki_wybory[wojewodztwo][okrag][powiat][nrGminy]
#                     kandydaciProcenty = generujKandydaciProcenty(wyniki)
#
#                     with open("generowane/" + nrGminy + ".html", "w") as out:
#                         out.write(template.render(
#                             gmina = nrGminy,
#                             dane = statystyki,
#                             kandydaci_glosy = collections.OrderedDict(sorted(wyniki.items(), key=lambda t: t[0])),
#                             kandydaci_procenty = kandydaciProcenty
#                         ))

# def generujPowiaty():
#     for wojewodztwo in statystyki_wybory:
#         for okrag in statystyki_wybory[wojewodztwo]:
#             for powiat in statystyki_wybory[wojewodztwo][okrag]:
#                 #To nie musi tak wygladac \/
#                 print(powiat)
#                 if powiat not in powiatDane:
#                     # okregiDane[okrag] = {}
#                     # okregiWyniki[okrag] = {}
#                     powiatDane[powiat] = dict.fromkeys(kluczeDane, 0)
#                     powiatWyniki[powiat] = dict.fromkeys(kluczeKandydaci, 0)
#                 for gmina in statystyki_wybory[wojewodztwo][okrag][powiat]:
#                     wynikiPowiat = wyniki_wybory[wojewodztwo][okrag][powiat][gmina]
#                     danePowiat = statystyki_wybory[wojewodztwo][okrag][powiat][gmina]
#                     for klucz in kluczeDane:
#                         powiatDane[powiat][klucz] += danePowiat[klucz]
#                     for klucz in kluczeKandydaci:
#                         powiatWyniki[powiat][klucz] += wynikiPowiat[klucz]
#             kandydaciProcenty = generujKandydaciProcenty(powiatWyniki[powiat])
#             # print(okregiWyniki[okrag])
#             template = env.get_template("okrag.html")
#             with open("generowane/" + powiat + ".html", "w") as out:
#                 out.write(template.render(
#                     okrag = powiat,
#                     dane = powiatDane[powiat],
#                     gminy = statystyki_wybory[wojewodztwo][okrag][powiat],
#                     kandydaci_glosy = collections.OrderedDict(sorted(powiatWyniki[powiat].items(),
#                                             key=lambda t: t[0])),
#                     kandydaci_procenty = kandydaciProcenty
#                 ))


def dodajKlucze(mapaDane, mapaWyniki, region):
    mapaDane[region] = dict.fromkeys(kluczeDane, 0)
    mapaWyniki[region] = dict.fromkeys(kluczeKandydaci, 0)

def sumujWartosciPoKluczu(wynik, dane, regionyDane, klucze):
    for region in regionyDane:
        for klucz in klucze:
            wynik[klucz] += dane[region][klucz]


def generujOkregi():
    for wojewodztwo in statystyki_wybory:
        for okrag in statystyki_wybory[wojewodztwo]:

            if okrag not in okregiDane:
                dodajKlucze(okregiDane, okregiWyniki, okrag)

            okragDane = okregiDane[okrag]
            okragWyniki = okregiWyniki[okrag]

            sumujWartosciPoKluczu(okragDane, statystyki_wybory[wojewodztwo][okrag],
                                statystyki_wybory[wojewodztwo][okrag].keys(), kluczeDane)
            sumujWartosciPoKluczu(okragWyniki, wyniki_wybory[wojewodztwo][okrag],
                                wyniki_wybory[wojewodztwo][okrag].keys(), kluczeKandydaci)

            kandydaciProcenty = generujKandydaciProcenty(okragWyniki)
            okragDane['Frekwencja'] = obliczFrekwencje(okragDane)

            template = env.get_template("okrag2.html")
            with open("generowane/" + okrag + ".html", "w") as out:
                out.write(template.render(
                    okrag = okrag,
                    dane = okregiDane[okrag],
                    gminy = statystyki_wybory[wojewodztwo][okrag],
                    gminyNazwa = kodGminyNazwa,
                    kandydaci_glosy = okregiWyniki[okrag],
                    kandydaci_procenty = kandydaciProcenty
                ))

def generujWojewodztwa():
    for wojewodztwo in statystyki_wybory:

        if wojewodztwo not in wojewodztwoDane:
            dodajKlucze(wojewodztwoDane, wojewodztwoWyniki, wojewodztwo)

        wojDane = wojewodztwoDane[wojewodztwo]
        wojWyniki = wojewodztwoWyniki[wojewodztwo]

        sumujWartosciPoKluczu(wojDane, okregiDane,
                                statystyki_wybory[wojewodztwo].keys(), kluczeDane)
        sumujWartosciPoKluczu(wojWyniki, okregiWyniki,
                                wyniki_wybory[wojewodztwo].keys(), kluczeKandydaci)

        kandydaciProcenty = generujKandydaciProcenty(wojWyniki)
        wojDane['Frekwencja'] = obliczFrekwencje(wojDane)
        wojewodztwoHTML = wojewodztwo.translate(trantab).lower()
        # print(okregiWyniki[okrag])
        template = env.get_template("wojewodztwo.html")
        with open("generowane/" + wojewodztwoHTML + ".html", "w") as out:
            out.write(template.render(
                wojewodztwo = wojewodztwo,
                dane = wojDane,
                okregi = statystyki_wybory[wojewodztwo],
                okregiDane = okregiDane,
                kandydaci_glosy = wojWyniki,
                kandydaci_procenty = kandydaciProcenty
            ))

def generujPolska():
    wynikiPolska = dict.fromkeys(kluczeKandydaci, 0)
    danePolska = dict.fromkeys(kluczeDane, 0)

    sumujWartosciPoKluczu(danePolska, wojewodztwoDane,
                            statystyki_wybory.keys(), kluczeDane)
    sumujWartosciPoKluczu(wynikiPolska, wojewodztwoWyniki,
                            wyniki_wybory.keys(), kluczeKandydaci)


    kandydaciProcenty = generujKandydaciProcenty(wynikiPolska)
    danePolska['Frekwencja'] = obliczFrekwencje(danePolska)
    nazwaHTML = generujNazwyHTML(statystyki_wybory)
    template = env.get_template("polska.html")

    with open("generowane/index.html", "w") as out:
        out.write(template.render(
            dane = danePolska,
            wojewodztwa = statystyki_wybory,
            wojewodztwoHTML = nazwaHTML,
            wojewodztwoDane = wojewodztwoDane,
            kandydaci_glosy = wynikiPolska,
            kandydaci_procenty = kandydaciProcenty
        ))




    # for gmina in gminaDane:
    #     i += 1
    #     with open("generowane/" + str(i) + ".html", "w") as out:
    #         out.write(template.render(
    #             gmina = gmina,
    #             dane = gminaDane[gmina],
    #             kandydaci_glosy = collections.OrderedDict(sorted(gminaKandydaci[gmina].items(), key=lambda t: t[0])),
    #             kandydaci_procenty = gminaKandydaciProcenty[gmina]
    #         ))

parsujDane()
generujGminy()
generujOkregi()
generujWojewodztwa()
generujPolska()
# print(len(statystyki_wybory))
