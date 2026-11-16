adapters = {
    # The `{{#if:` of the past forms lost its closing braces when "Он/она/оно (прош.)" was split into one parameter
    # per gender, so the table is never rendered
    'Шаблон:гл ru 5b/c"-ся': lambda body: body.replace(
        "|Он (прош.) ={{#if:{{{безличный|1}}}||{{{основа}}}а́лся\n|Она (прош.)={{{основа}}}ала́сь\n",
        "|Он (прош.) ={{#if:{{{безличный|1}}}||{{{основа}}}а́лся}}\n"
        "|Она (прош.)={{#if:{{{безличный|1}}}||{{{основа}}}ала́сь}}\n",
        1,
    ),
}
