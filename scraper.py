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

        county = entry.xpath(".//li[@class='landkreis']/a/text()")
        if len(county) > 0:
            county = county[0]
            location = ", ".join([city, county, "Brandenburg", "Deutschland"])
        else:
            location = ", ".join([city, "Brandenburg", "Deutschland"])

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
                "iso3166_2": "DE-BB",
                "url": uri,
                "rg_id": uri,
                "subdivisions": location,
                "aggregator": "Opferperspektive (Brandenburg)",
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
