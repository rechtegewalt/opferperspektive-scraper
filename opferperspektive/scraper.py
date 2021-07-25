import datetime
import os

import lxml.html

os.environ["SCRAPERWIKI_DATABASE_NAME"] = "sqlite:///data.sqlite"

import scraperwiki

# morph does not support setting locale in python, so we have to do it like this
months = [
    "Januar",
    "Februar",
    "März",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Dezember",
]
monts_num = [[m, str(i + 1).rjust(2, "0")] for i, m in enumerate(months)]

DEBUG = False


def process_page(doc):
    for entry in doc.xpath("//article"):
        uri = entry.xpath("./header/h2/a/@href")[0]
        # print(uri)

        sources = entry.xpath(".//li[@class='quelle']/a/text()")
        if len(sources) > 0:
            sources = sources[0]
            sources = sources.split(",")
            sources = [s.strip() for s in sources]
        else:
            sources = None

        city = entry.xpath(".//li[@class='stadt']/a/text()")

        # sometimes, there is no city in the field
        if len(city) == 0:
            city = entry.xpath("./header/h2/a/text()")[0]
        else:
            city = city[0]

        city = city.strip()
        county = entry.xpath(".//li[@class='landkreis']/a/text()")
        # Avoid `Landkreis` for `Kreisfreie Städte`
        if len(county) > 0 and city != county[0].strip():
            county = county[0].strip()
        else:
            county = None

        date_raw = entry.xpath(".//span[@class='posted-on']/a/text()")[0].strip()

        for m, i in monts_num:
            date_raw = date_raw.replace(m, i)

        date = datetime.datetime.strptime(date_raw, "%d. %m %Y")

        text = " ".join(entry.xpath(".//div[@class='entry-content']/p/text()"))

        scraperwiki.sqlite.save(
            unique_keys=["rg_id"],
            data={
                "description": text,
                "date": date,
                "url": uri,
                "rg_id": uri,
                "city": city,
                "county": county,
                "chronicler_name": "Opferperspektive",
            },
            table_name="incidents",
        )

        if not sources is None:
            for s in sources:
                scraperwiki.sqlite.save(
                    unique_keys=["rg_id"],
                    data={"name": s, "rg_id": uri},
                    table_name="sources",
                )

        # force commit to prevent duplicates
        # https://github.com/sensiblecodeio/scraperwiki-python/issues/107
        scraperwiki.sqlite.commit_transactions()


base_url = "http://www.opferperspektive.de/category/rechte-angriffe/chronologie-rechter-angriffe/page/%s"
urls = [base_url % i for i in range(1, 1000)]
for url in urls:
    DEBUG and print(urls)
    try:
        html = scraperwiki.scrape(url)
    except:
        # break on 404 because we reached the end
        break
    doc = lxml.html.fromstring(html)
    process_page(doc)

# save meta data

scraperwiki.sqlite.save(
    unique_keys=["chronicler_name"],
    data={
        "iso3166_1": "DE",
        "iso3166_2": "DE-BB",
        "chronicler_name": "Opferperspektive",
        "chronicler_description": "Die Opferperspektive bietet seit 1998 im Land Brandenburg eine professionelle Beratung für Betroffene rechter Gewalt und rassistischer Diskriminierung, deren Freundinnen, Angehörige und Zeuginnen an. Die Beratung ist kostenlos, vertraulich, parteilich und unabhängig von staatlichen Behörden.",
        "chronicler_url": "https://www.opferperspektive.de/",
        "chronicle_source": "https://www.opferperspektive.de/category/rechte-angriffe/chronologie-rechter-angriffe",
    },
    table_name="chronicle",
)

scraperwiki.sqlite.commit_transactions()
