from covidnpi.utils.dictionaries import reverse_dictionary

POSTAL_TO_ISOPROV = {
    "01": "VI",
    "02": "AB",
    "03": "A",
    "04": "AL",
    "05": "AV",
    "06": "BA",
    "07": "PM",
    "08": "B",
    "09": "BU",
    "10": "CC",
    "11": "CA",
    "12": "CS",
    "13": "CR",
    "14": "CO",
    "15": "C",
    "16": "CU",
    "17": "GI",
    "18": "GR",
    "19": "GU",
    "20": "SS",
    "21": "H",
    "22": "HU",
    "23": "J",
    "24": "LE",
    "25": "L",
    "26": "LO",
    "27": "LU",
    "28": "M",
    "29": "MA",
    "30": "MU",
    "31": "NA",
    "32": "OR",
    "33": "O",
    "34": "P",
    "35": "GC",
    "36": "PO",
    "37": "SA",
    "38": "TF",
    "39": "S",
    "40": "SG",
    "41": "SE",
    "42": "SO",
    "43": "T",
    "44": "TE",
    "45": "TO",
    "46": "V",
    "47": "VA",
    "48": "BI",
    "49": "ZA",
    "50": "Z",
    "51": "CE",
    "52": "ML",
}

ISOPROV_TO_POSTAL = reverse_dictionary(POSTAL_TO_ISOPROV)

ISOPROV_TO_PROVINCIA = {
    "A": "Alacant",
    "AB": "Albacete",
    "AL": "Almería",
    "AV": "Ávila",
    "B": "Barcelona",
    "BA": "Badajoz",
    "BI": "Bizkaia",
    "BU": "Burgos",
    "C": "A Coruña",
    "CA": "Cádiz",
    "CC": "Cáceres",
    "CE": "Ceuta",
    "CO": "Córdoba",
    "CR": "Ciudad Real",
    "CS": "Castelló",
    "CU": "Cuenca",
    "GC": "Las Palmas",
    "GI": "Girona",
    "GR": "Granada",
    "GU": "Guadalajara",
    "H": "Huelva",
    "HU": "Huesca",
    "J": "Jaén",
    "L": "Lleida",
    "LE": "León",
    "LO": "La Rioja",
    "LU": "Lugo",
    "M": "Madrid",
    "MA": "Málaga",
    "ML": "Melilla",
    "MU": "Murcia",
    "NA": "Nafarroa",
    "OR": "Ourense",
    "O": "Asturias",
    "P": "Palencia",
    "PM": "Illes Balears",
    "PO": "Pontevedra",
    "SA": "Salamanca",
    "TF": "Sta. Cruz de Tenerife",
    "S": "Cantabria",
    "SG": "Segovia",
    "SE": "Sevilla",
    "SO": "Soria",
    "SS": "Gipuzkoa",
    "T": "Tarragona",
    "TE": "Teruel",
    "TO": "Toledo",
    "V": "Valéncia",
    "VA": "Valladolid",
    "VI": "Álava",
    "ZA": "Zamora",
    "Z": "Zaragoza",
}

# Reassing ISO of CCAA to ISO of province
# For CCAA with only one province
ISOPROV_REASSIGN = {
    "AS": "O",
    "CB": "S",
    "IB": "PM",
    "MD": "M",
    "ME": "ML",
    "MC": "MU",
    "NC": "NA",
}

PROVINCIA_TO_ISOPROV = {
    "alava": "VI",
    "albacete": "AB",
    "alicante": "A",
    "almeria": "AL",
    "avila": "AV",
    "badajoz": "BA",
    # "mallorca": "PM",
    "islas_baleares": "PM",
    "barcelona": "B",
    "burgos": "BU",
    "caceres": "CC",
    "cadiz": "CA",
    "castellon": "CS",
    "ceuta": "CE",
    "ciudad_real": "CR",
    "cordoba": "CO",
    "coruna_la": "C",
    "cuenca": "CU",
    "girona": "GI",
    "granada": "GR",
    "guadalajara": "GU",
    "guipuzcoa": "SS",
    "huelva": "H",
    "huesca": "HU",
    "jaen": "J",
    "leon": "LE",
    "lleida": "L",
    "rioja_la": "LO",
    "lugo": "LU",
    "madrid": "M",
    "malaga": "MA",
    "melilla": "ML",
    "murcia": "MU",
    "navarra": "NA",
    "orense": "OR",
    "asturias": "O",
    "palencia": "P",
    "gran_canaria": "GC",
    "pontevedra": "PO",
    "salamanca": "SA",
    "santa_cruz_de_tenerife": "TF",
    "cantabria": "S",
    "segovia": "SG",
    "sevilla": "SE",
    "soria": "SO",
    "tarragona": "T",
    "tenerife": "TF",
    "teruel": "TE",
    "toledo": "TO",
    "valencia": "V",
    "valladolid": "VA",
    "vizcaya": "BI",
    "zamora": "ZA",
    "zaragoza": "Z",
}

ISOPROV_TO_FILENAME = reverse_dictionary(PROVINCIA_TO_ISOPROV)

DICT_PROVINCE_RENAME = {
    "a_coruna": "coruna_la",
    "cyl": "",
    "guipuzkoa": "guipuzcoa",
    "grancanaria": "gran_canaria",
}

DICT_FILL_PROVINCIA = {
    "CTB": "cantabria",
    "CEU": "ceuta",
    "MEL": "melilla",
    "MUR": "murcia",
    "NAV": "navarra",
    "RIO": "rioja_la",
}

ISLA_TO_PROVINCIA = {
    "elhierro": "gran_canaria",
    "formentera": "tenerife",
    "fuerteventura": "gran_canaria",
    "ibiza": "tenerife",
    "lagomera": "gran_canaria",
    "lanzarote": "gran_canaria",
    "menorca": "tenerife",
}

ISOPROV_TO_POBLACION = {
    "AB": 388270,
    "A": 1879888,
    "AL": 727945,
    "VI": 333940,
    "O": 1018784,
    "AV": 157664,
    "BA": 672137,
    "PM": 1171543,
    "B": 5743402,
    "BI": 1159443,
    "BU": 357650,
    "CC": 391850,
    "CA": 1244049,
    "S": 582905,
    "CS": 585590,
    "CR": 495045,
    "CO": 781451,
    "C": 1121815,
    "CU": 196139,
    "SS": 727121,
    "GI": 781788,
    "GR": 919168,
    "GU": 261995,
    "H": 524278,
    "HU": 222687,
    "J": 631381,
    "LE": 456439,
    "L": 438517,
    "LU": 327946,
    "M": 6779888,
    "MA": 1685920,
    "MU": 1511251,
    "NA": 661197,
    "OR": 306650,
    "P": 160321,
    "GC": 1131065,
    "PO": 945408,
    "LO": 319914,
    "SA": 329245,
    "TF": 1044887,
    "SG": 153478,
    "SE": 1950219,
    "SO": 88884,
    "T": 816772,
    "TE": 134176,
    "TO": 703772,
    "V": 2591875,
    "VA": 520649,
    "ZA": 170588,
    "Z": 972528,
    "CE": 84202,
    "ML": 87076,
}

ISLA_TO_PERCENTAGE = {
    "islas_baleares": {
        "mallorca": 0.778,
        "menorca": 0.081,
        "ibiza": 0.130,
        "formentera": 0.011,
    },
    "santa_cruz_de_tenerife": {
        "tenerife": 0.77,
        "lanzarote": 0.13,
        "fuerteventura": 0.10,
    },
    "gran_canaria": {
        "gran_canaria": 0.88,
        "lapalma": 0.09,
        "lagomera": 0.02,
        "elhierro": 0.01,
    },
}
