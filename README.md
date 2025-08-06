# reader.dict Monolingual Dictionaries

[![Word of the day](https://github.com/reader-dict/monolingual/actions/workflows/daily.yml/badge.svg)](https://github.com/reader-dict/monolingual/actions/workflows/daily.yml)

🎇 Want to know what is being cooked, and what was done in past releases? Have a look at our [dicsussions](https://github.com/reader-dict/monolingual/discussions).

## Features

- **Part of speech** support.
- When selecting a plural word, **its singular form** will be displayed.
- When selecting a conjugated verb, **its infinitive version** will be displayed.
- When a word is the plural form of another, and also a form of a verb, **all versions** are displayed.
- If a word contains **several pronunciations, or genders**, all are available.
- **Chemical formulas** are beautifuly rendered.
- **Mathematic formulas** are beautifuly rendered.
- **Hieroglyphs** are supported.
- **Tables** are supported.

## Special

Find **bilingual, and universal** dictionaries with more than 180 langs at the next-level project: [reader.dict Multilingual Dictionaries](https://www.reader-dict.com).

## Downloads

1. <small>`[CA]`</small> [Catalan](https://www.reader-dict.com/ca/download/ca)
1. <small>`[DA]`</small> [Danish](https://www.reader-dict.com/da/download/da)
1. <small>`[DE]`</small> [German](https://www.reader-dict.com/de/download/de)
1. <small>`[EL]`</small> [Greek](https://www.reader-dict.com/el/download/el)
1. <small>`[EN]`</small> [English](https://www.reader-dict.com/en/download/en)
1. <small>`[EO]`</small> [Esperanto](https://www.reader-dict.com/eo/download/eo)
1. <small>`[ES]`</small> [Spanish](https://www.reader-dict.com/es/download/es)
1. <small>`[FR]`</small> [French](https://www.reader-dict.com/fr/download/fr) ([news](https://www.mobileread.com/forums/showthread.php?t=330223&page=2))
1. <small>`[IT]`</small> [Italian](https://www.reader-dict.com/it/download/it)
1. <small>`[NO]`</small> [Norway](https://www.reader-dict.com/no/download/no)
1. <small>`[PT]`</small> [Portuguese](https://www.reader-dict.com/pt/download/pt)
1. <small>`[RO]`</small> [Romanian](https://www.reader-dict.com/ro/download/ro)
1. <small>`[RU]`</small> [Russian](https://www.reader-dict.com/ru/download/ru)
1. <small>`[SV]`</small> [Swedish](https://www.reader-dict.com/sv/download/sv)

## Installation

### Kindle

Copy the dictionary inside the `documents/dictionaries/` folder on your eBook reader.

### Kobo

Copy the dictionary inside the `.kobo/custom-dict/` folder on your eBook reader.

### KOReader

Download a dictionary in StarDict format, unzip it into the `koreader/data/dict/` folder on your eBook reader. If you want multiple dictionaries you have to create directories in `koreader/data/dict/` for all your dictionaries and unzip the dictionaries into this folders.

---

## Development

Set up a virtual environment:

```bash
python3.13 -m venv venv

# For Linux and Mac users
. venv/bin/activate

# For Windows users
. venv/Scripts/activate
```

Install, or update, dependencies:

```bash
python -m pip install -U pip
python -m pip install -r requirements-tests.txt
```

Run tests:

```bash
# All tests
python -m pytest --doctest-modules wikidict tests

# Skip those requiring a working internet connection
python -m pytest --doctest-modules wikidict tests -m "not webtest"
```

Run linters, and quality checkers, before submitting a pull-request:

```bash
./check.sh
```

## Contributors 💖

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-17-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

Thanks go to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="16.66%"><a href="https://www.tiger-222.fr"><img src="https://avatars.githubusercontent.com/u/2033598?v=4?s=100" width="100px;" alt="Mickaël Schoentgen"/><br /><sub><b>Mickaël Schoentgen</b></sub></a><br /><a href="https://github.com/reader-dict/monolingual/issues?q=author%3ABoboTiG" title="Bug reports">🐛</a> <a href="https://github.com/reader-dict/monolingual/commits?author=BoboTiG" title="Code">💻</a> <a href="https://github.com/reader-dict/monolingual/commits?author=BoboTiG" title="Documentation">📖</a> <a href="#projectManagement-BoboTiG" title="Project Management">📆</a></td>
      <td align="center" valign="top" width="16.66%"><a href="http://lasconic.com"><img src="https://avatars0.githubusercontent.com/u/234271?v=4?s=100" width="100px;" alt="Nicolas Froment"/><br /><sub><b>Nicolas Froment</b></sub></a><br /><a href="https://github.com/reader-dict/monolingual/issues?q=author%3Alasconic" title="Bug reports">🐛</a> <a href="https://github.com/reader-dict/monolingual/commits?author=lasconic" title="Code">💻</a> <a href="https://github.com/reader-dict/monolingual/commits?author=lasconic" title="Documentation">📖</a> <a href="#projectManagement-lasconic" title="Project Management">📆</a></td>
      <td align="center" valign="top" width="16.66%"><a href="https://github.com/atti84it"><img src="https://avatars.githubusercontent.com/u/817905?v=4?s=100" width="100px;" alt="Attilio"/><br /><sub><b>Attilio</b></sub></a><br /><a href="https://github.com/reader-dict/monolingual/commits?author=atti84it" title="Code">💻</a></td>
      <td align="center" valign="top" width="16.66%"><a href="https://github.com/chopinesque"><img src="https://avatars.githubusercontent.com/u/10416842?v=4?s=100" width="100px;" alt="chopinesque"/><br /><sub><b>chopinesque</b></sub></a><br /><a href="https://github.com/reader-dict/monolingual/commits?author=chopinesque" title="Code">💻</a></td>
      <td align="center" valign="top" width="16.66%"><a href="https://github.com/ilius"><img src="https://avatars.githubusercontent.com/u/197648?v=4?s=100" width="100px;" alt="Saeed Rasooli"/><br /><sub><b>Saeed Rasooli</b></sub></a><br /><a href="#infra-ilius" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a></td>
      <td align="center" valign="top" width="16.66%"><a href="https://github.com/Moonbase59"><img src="https://avatars.githubusercontent.com/u/3706922?v=4?s=100" width="100px;" alt="Matthias C. Hormann"/><br /><sub><b>Matthias C. Hormann</b></sub></a><br /><a href="https://github.com/reader-dict/monolingual/commits?author=Moonbase59" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="16.66%"><a href="https://github.com/tjaderxyz"><img src="https://avatars.githubusercontent.com/u/81907?v=4?s=100" width="100px;" alt="tjader"/><br /><sub><b>tjader</b></sub></a><br /><a href="https://github.com/reader-dict/monolingual/commits?author=tjaderxyz" title="Code">💻</a></td>
      <td align="center" valign="top" width="16.66%"><a href="https://github.com/victornove"><img src="https://avatars.githubusercontent.com/u/10910369?v=4?s=100" width="100px;" alt="Victor"/><br /><sub><b>Victor</b></sub></a><br /><a href="https://github.com/reader-dict/monolingual/commits?author=victornove" title="Code">💻</a></td>
      <td align="center" valign="top" width="16.66%"><a href="https://github.com/drkoll"><img src="https://avatars.githubusercontent.com/u/128939759?v=4?s=100" width="100px;" alt="John Koll"/><br /><sub><b>John Koll</b></sub></a><br /><a href="#translation-drkoll" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="16.66%"><a href="http://www.linkedin.com/in/martamalberti/"><img src="https://avatars.githubusercontent.com/u/129286939?v=4?s=100" width="100px;" alt="Marta Malberti"/><br /><sub><b>Marta Malberti</b></sub></a><br /><a href="#translation-MartaMalb" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="16.66%"><a href="https://github.com/g1r0"><img src="https://avatars.githubusercontent.com/u/17737200?v=4?s=100" width="100px;" alt="Arsenii Chaplinskii"/><br /><sub><b>Arsenii Chaplinskii</b></sub></a><br /><a href="#translation-g1r0" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="16.66%"><a href="http://and4po.github.io"><img src="https://avatars.githubusercontent.com/u/94716615?v=4?s=100" width="100px;" alt="Ander Romero"/><br /><sub><b>Ander Romero</b></sub></a><br /><a href="#translation-and4po" title="Translation">🌍</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="16.66%"><a href="http://blog.yue-dongchen.xyz"><img src="https://avatars.githubusercontent.com/u/38829129?v=4?s=100" width="100px;" alt="Dongchen Yue &#124; 岳东辰"/><br /><sub><b>Dongchen Yue &#124; 岳东辰</b></sub></a><br /><a href="#translation-yue-dongchen" title="Translation">🌍</a></td>
      <td align="center" valign="top" width="16.66%"><a href="https://larssonjohan.com"><img src="https://avatars.githubusercontent.com/u/13087841?v=4?s=100" width="100px;" alt="Johan Larsson"/><br /><sub><b>Johan Larsson</b></sub></a><br /><a href="https://github.com/reader-dict/monolingual/commits?author=jolars" title="Code">💻</a></td>
      <td align="center" valign="top" width="16.66%"><a href="https://github.com/kyxap"><img src="https://avatars.githubusercontent.com/u/3080529?v=4?s=100" width="100px;" alt="kyxap"/><br /><sub><b>kyxap</b></sub></a><br /><a href="https://github.com/reader-dict/monolingual/commits?author=kyxap" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="16.66%"><a href="https://github.com/Baitur5"><img src="https://avatars.githubusercontent.com/u/73650784?v=4?s=100" width="100px;" alt="Baitur Ulukbekov"/><br /><sub><b>Baitur Ulukbekov</b></sub></a><br /><a href="https://github.com/reader-dict/monolingual/commits?author=Baitur5" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="16.66%"><a href="https://github.com/StillerHarpo"><img src="https://avatars.githubusercontent.com/u/25526706?v=4?s=100" width="100px;" alt="Florian Engel"/><br /><sub><b>Florian Engel</b></sub></a><br /><a href="https://github.com/reader-dict/monolingual/commits?author=StillerHarpo" title="Documentation">📖</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## Stars ✨

<a href="https://star-history.com/#reader-dict/monolingual&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=reader-dict/monolingual&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=reader-dict/monolingual&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=reader-dict/monolingual&type=Date" />
  </picture>
</a>
