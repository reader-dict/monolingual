from ...user_functions import extract_keywords_from


def template_etymologie_graphique_chinoise(args: tuple[str, ...]) -> str:
    """
    >>> template_etymologie_graphique_chinoise(("Étymologie graphique chinoise", "racine=羊", "sens=Attaquer en force, porter un coup (敦) / Vase rituel pour offrir les viandes (錞)"))
    'Attaquer en force, porter un coup (敦) / Vase rituel pour offrir les viandes (錞)'
    """
    data = extract_keywords_from(list(args[1:]))
    return data["sens"] or data["composition"] or data["explication"]


def template_sinogram_noimg(args: tuple[str, ...]) -> str:
    """
    >>> template_sinogram_noimg(("sinogram-noimg", "它", "clefhz1=宀", "clefhz2=2", "nbthz1=1-5", "nbthz2=5", "m4chz1=3", "m4chz2=3071<sub>1</sub>", "unihz=5B83", "gbhz1= ", "gbhz2=-", "b5hz1=A1", "b5hz2=A5A6", "cjhz1=J", "cjhz2=十心", "cjhz3=JP"))
    'Codage informatique : <b>Unicode</b> : U+5B83 - <b>Big5</b> : A5A6 - <b>Cangjie</b> : 十心 (JP) - <b>Quatre coins</b> : 3071<sub>1</sub>'
    """
    data = extract_keywords_from(list(args[1:]))
    text = "Codage informatique :"
    codages = []

    if unihz := data["unihz"]:
        codages.append(f"<b>Unicode</b> : U+{unihz}")

    if b5hz2 := data["b5hz2"]:
        codage = f"<b>Big5</b> : {b5hz2}"
        if b5hz3 := data["b5hz3"]:
            codage += f" ({b5hz3})"
        codages.append(codage)

    if cjhz2 := data["cjhz2"]:
        codage = f"<b>Cangjie</b> : {cjhz2}"
        if cjhz3 := data["cjhz3"]:
            codage += f" ({cjhz3})"
        codages.append(codage)

    if m4chz2 := data["m4chz2"]:
        codage = f"<b>Quatre coins</b> : {m4chz2}"
        if m4chz3 := data["m4chz3"]:
            codage += f" ({m4chz3})"
        codages.append(codage)

    return f"{text} {' - '.join(codages)}"


overrides = {
    **dict.fromkeys(
        {"Étymologie graphique chinoise", "Etymologie graphique chinoise"},
        template_etymologie_graphique_chinoise,
    ),
    **dict.fromkeys({"sinogramme-sans-image", "sinogram-noimg"}, template_sinogram_noimg),
}
