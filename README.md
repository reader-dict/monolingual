# reader.dict Monolingual Dictionaries

🚀 Features, **downloads**, and installation details on [reader.dict](https://www.reader-dict.com).

🎇 Want to know what is being cooked, and what was done in past releases? Have a look at our [discussions](https://github.com/reader-dict/monolingual/discussions).

---

## Usage

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

Download the dictionary for your LOCALE:

```
python -m wikidict.__main__ LOCALE
```

Where `LOCALE` is a [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Officially_assigned_code_elements).

Example:

```
python -m wikidict.__main__ en
```

## Development

Before submitting a PR, run tests:

```bash
# All tests, must be run in two steps to prevent database issues
python -m pytest --doctest-modules wikidict
python -m pytest tests

# Skip those requiring a working internet connection
python -m pytest tests -m "not webtest"
```

and linters as well as quality checkers:

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
