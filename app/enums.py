from enum import Enum

class ItemTypesPluralSingular(str, Enum):
    trusouri = "trusou"
    lumanari = "lumanare"
    cutii = "cutie"
    accesorii = "accesoriu"
    cadouri = "cadou"
    tricouri = "tricou"
    tavite = "tava"
    haine = "haina"
    prosoape = "prosop"
    perii = "perie"
    oglinda = "oglinzi"

class ItemTypesEnum(str, Enum):
    trusou = "trusou"
    lumanare = "lumanare"
    cutie = "cutie"
    accesoriu = "accesoriu"
    cadou = "cadou"
    tricou = "tricou"
    tava = "tava"
    haina = "haina"
    prosop = "prosop"
    perie = "perie"
    oglinda = "oglinda"

class ItemCategoriesEnum(str, Enum):
    botez = "botez"
    prima_baie = "prima_baie"
    prima_aniversare = "prima_aniversare"
    imprimate = "imprimate"
    brodate = "brodate"
    craciun = "craciun"
    paste = "paste"

class GenderEnum(str, Enum):
    M = "M"
    F = "F"
    U = "U"

class RolesEnum(str, Enum):
    admin = "admin"
    regular = "regular"

class FamilyEnum(str, Enum):
    bunic = "bunic"
    bunica = "bunica"
    frate = "frate"
    mama = "mama"
    matusa = "matusa"
    nasa = "nasa"
    nasul = "nasul"
    sarbatorit = "sarbatorit"
    sora = "sora"
    tata = "tata"
    unchi = "unchi"
    verisoara = "verisoara"
    verisor = "verisor"

class SizesEnum(str, Enum):
    unu_trei = "1-3"
    trei_sase = "3-6"
    sase_noua = "6-9"
    noua_doisprezece = "9-12"
    doisprezece_optsprezece = "12-18"