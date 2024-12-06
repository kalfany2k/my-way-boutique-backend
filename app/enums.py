from enum import Enum

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
    aniversare = "aniversare"
    imprimate = "imprimate"
    brodate = "brodate"
    craciun = "craciun"
    paste = "paste"
    economic = "economic"

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