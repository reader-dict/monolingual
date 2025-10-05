adapters = {
    "Plantilla:-etimologia-": lambda body: body.replace(':*<span style="font-weight: bold;">Etimologia</span>: ', ""),
    "Plantilla:etim-comp": lambda body: body.replace(":* '''Etimologia:''' ", ""),
    **dict.fromkeys(
        {"Plantilla:etim-fpref", "Plantilla:etim-fsuf", "Plantilla:etim-lang"},
        lambda body: body.replace(':* <span style="font-weight: bold;">Etimologia</span>: ', ""),
    ),
    "Plantilla:etimologia": lambda body: body.replace(":*'''Etimologia:''' ", ""),
}
