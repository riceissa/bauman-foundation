#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import csv
import sys

def main():
    with open("data.csv", "w", newline="") as f:
        fieldnames = ["grantee", "grantee_url", "amount", "fiscal_year",
                      "grant_type", "grant_description"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        go(writer)


def go(writer):
    # This is a map: int -> fiscal_year -> float
    fy_sums = {}

    response = requests.get("https://www.baumanfoundation.org/grants/search?amount=All&fiscal_year=&name=&items_per_page=All")
    soup = BeautifulSoup(response.content, "lxml")
    rows = soup.find_all("tr")[1:]  # Skip the header row of the table
    for row in rows:
        cols = row.find_all("td")
        grantee = cols[0].text.strip()
        grantee_path = cols[0].find("a")["href"]
        grantee_num = int(grantee_path.split('/')[-1])
        grantee_url = ("https://www.baumanfoundation.org" +
                            grantee_path)
        fiscal_year = cols[2].text.strip()

        # This is the total for this (grantee, fiscal_year) combination, so
        # it's different from a single grant. We store it to check against our
        # per-grant sums (stored in fy_sums) to check our understanding of the
        # site.
        amount = cols[1].text.strip()
        assert amount.startswith("$"), amount
        amount = float(amount.replace("$", "").replace(",", ""))

        # Now we go to the grantee page to get information about each individual
        # grant. We only need to do this once for each grantee.
        if grantee_num not in fy_sums:
            fy_sums[grantee_num] = {}
            response_g = requests.get(grantee_url)
            soup_g = BeautifulSoup(response_g.content, "lxml")
            rows_g = soup_g.find_all("tr")[1:]  # Skip the header row of the table
            for row_g in rows_g:
                cols_g = row_g.find_all("td")

                d = {}
                d['grantee'] = grantee
                d['grantee_url'] = grantee_url
                d['fiscal_year'] = cols_g[0].text.strip()
                d['amount'] = cols_g[1].text.strip()
                d['grant_type'] = cols_g[2].text.strip()
                d['grant_description'] = cols_g[3].text.strip()
                writer.writerow(d)

                amount_g = d['amount']
                assert amount_g.startswith("$")
                amount_g = float(amount_g.replace("$", "").replace(",", ""))
                if d['fiscal_year'] not in fy_sums[grantee_num]:
                    fy_sums[grantee_num][d['fiscal_year']] = amount_g
                else:
                    fy_sums[grantee_num][d['fiscal_year']] += amount_g

        assert fy_sums[grantee_num][fiscal_year] == amount, \
               (grantee, fiscal_year, fy_sums[grantee_num][fiscal_year], amount)


if __name__ == "__main__":
    main()
