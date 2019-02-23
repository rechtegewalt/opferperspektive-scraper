import datetime
import locale
import re
import os

import lxml.html

os.environ["SCRAPERWIKI_DATABASE_NAME"] = "sqlite:///data.sqlite"

import scraperwiki

# for date parsing
locale.setlocale(locale.LC_ALL, "de_De")


def process_page(doc):
    for entry in doc.xpath("//article"):
        # TODO: sources is not clean, occasionally, there are multiple sources in one field
        sources = entry.xpath("//li[@class='quelle']/a/text()")
        county = entry.xpath("//li[@class='landkreis']/a/text()")[0]
        city = entry.xpath("//li[@class='stadt']/a/text()")[0]

        location = ", ".join([city, county, "Brandenburg", "Germany"])

        uri = entry.xpath("./header/h2/a/@href")[0]

        date_raw = entry.xpath(".//span[@class='posted-on']/a/text()")[0].strip()

        date = datetime.datetime.strptime(date_raw, "%d. %B %Y").isoformat()
        text = " ".join(entry.xpath("//div[@class='entry-content']/p/text()"))

        # print(location)
        # print(sources)
        # print(date)
        # print(text)

        scraperwiki.sqlite.save(
            unique_keys=["uri"],
            data={
                "description": text,
                "startDate": date,
                "iso3166_2": "DE-BB",
                "uri": uri,
            },
            table_name="data",
        )

        scraperwiki.sqlite.save(
            unique_keys=["reportURI"],
            data={"subdivisions": location, "reportURI": uri},
            table_name="location",
        )

        for s in sources:
            scraperwiki.sqlite.save(
                unique_keys=["reportURI"],
                data={"name": s, "reportURI": uri},
                table_name="source",
            )


base_url = "http://www.opferperspektive.de/category/rechte-angriffe/chronologie-rechter-angriffe/page/%s"
urls = [base_url % i for i in range(1, 1000)]
for url in urls:
    try:
        html = scraperwiki.scrape(url)
    except:
        # break on 404 because we reached the end
        break
    doc = lxml.html.fromstring(html)
    process_page(doc)
