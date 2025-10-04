adapters = {
    "Predefinição:etimo2": lambda body: body.replace(":{{#seigual", "{{#seigual", count=1).replace(
        '{{#se:{{codlingua-codwmf|{{{1}}}}}|<small><sup> ([[:{{codlingua-codwmf|{{{1}}}}}:{{{2}}}|<span title="ver no Wikcionário em {{nome língua|{{{1}}}}}">{{codlingua-codwmf|{{{1}}}}}</span>]])</sup></small>}}',
        "",
    ),
    "Predefinição:étimo junção": lambda body: body.replace(":De", "De", count=1),
}
