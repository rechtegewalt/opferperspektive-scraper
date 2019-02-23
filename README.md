# Opferperspektive Scraper

Scraping right-wing incidents in Brandenburg, Germany as monitored by the NGO [Opferperspektive](https://www.opferperspektive.de/).

Website: https://www.opferperspektive.de/category/rechte-angriffe/chronologie-rechter-angriffe
Data:

## Usage

For local development:

-   Install [Pipenv](https://github.com/pypa/pipenv)
-   `pipenv install`
-   `pipenv run python scraper.py`

For Morph:

-   `pipenv lock --requirements > requirements.txt`
-   commit the `requirements.txt`
-   modify `runtime.txt`

## Morph

This is a scraper that runs on [Morph](https://morph.io). To get started [see the documentation](https://morph.io/documentation)
