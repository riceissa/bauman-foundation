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
    # This is a map:
    # int -> [{fiscal_year, amount, grant_type, grant_description} -> values]
    grantee_dict = {}

    all_grants_url = "https://www.baumanfoundation.org/grants/search?amount=All&fiscal_year=&name=&items_per_page=All"
    response = requests.get(all_grants_url)
    soup = BeautifulSoup(response.content, "lxml")
    rows = soup.find_all("tr")[1:]  # Skip the header row of the table
    for row in rows:
        d = {}
        cols = row.find_all("td")
        d['grantee'] = cols[0].text.strip()
        grantee_path = cols[0].find("a")["href"]
        grantee_num = int(grantee_path.split('/')[-1])
        d['grantee_url'] = ("https://www.baumanfoundation.org" +
                            grantee_path)
        d['amount'] = cols[1].text.strip()
        d['fiscal_year'] = cols[2].text.strip()

        # Now we go to the grantee page to get more information about the
        # grant, if we haven't done so already (the grantees are repeated in
        # the main grants page, so it is possible we have already stored the
        # grantee info, in which case we don't want to download the grantee
        # page all over again)
        if grantee_num not in grantee_dict:
            grantee_dict[grantee_num] = []
            response_g = requests.get(d['grantee_url'])
            soup_g = BeautifulSoup(response_g.content, "lxml")
            rows_g = soup_g.find_all("tr")[1:]  # Skip the header row of the table
            for row_g in rows_g:
                d_g = {}
                cols_g = row_g.find_all("td")
                d_g['fiscal_year'] = cols_g[0].text.strip()
                d_g['amount'] = cols_g[1].text.strip()
                d_g['grant_type'] = cols_g[2].text.strip()
                d_g['grant_description'] = cols_g[3].text.strip()
                grantee_dict[grantee_num].append(d_g)

        # Now, find the grant we are on among the grants on the grantee page
        l_g = [x for x in grantee_dict[grantee_num]
               if x['fiscal_year'] == d['fiscal_year'] and
                  x['amount'] == d['amount']]
        # There should be only one grant matching this
        assert len(l_g) == 1, (d, grantee_dict[grantee_num], grantee_num, l_g)
        d['grant_type'] = l_g[0]['grant_type']
        d['grant_description'] = l_g[0]['grant_description']
        writer.writerow(d)


if __name__ == "__main__":
    main()
