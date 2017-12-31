#!/usr/bin/env python3
# License: CC0 https://creativecommons.org/publicdomain/zero/1.0/

import csv
import re


def mysql_quote(x):
    '''
    Quote the string x using MySQL quoting rules. If x is the empty string,
    return "NULL". Probably not safe against maliciously formed strings, but
    whatever; our input is fixed and from a basically trustable source..
    '''
    if not x:
        return "NULL"
    x = x.replace("\\", "\\\\")
    x = x.replace("'", "''")
    x = x.replace("\n", "\\n")
    return "'{}'".format(x)


def main():
    with open("data.csv", "r") as f:
        reader = csv.DictReader(f)
        first = True

        print("""insert into donations (donor, donee, amount, donation_date,
        donation_date_precision, donation_date_basis, cause_area, url,
        donor_cause_area_url, notes, affected_countries,
        affected_regions) values""")

        for row in reader:
            amount = row['amount']
            assert amount.startswith("$")
            amount = float(amount.replace("$", "").replace(",", ""))

            # FIXME: convert fiscal years?
            donation_date = ""

            notes = "; ".join(filter(bool,
                                [row['grant_type'], row['grant_description']]))

            print(("    " if first else "    ,") + "(" + ",".join([
                mysql_quote("Bauman Foundation"),  # donor
                mysql_quote(row['grantee']),  # donee
                str(amount),  # amount
                mysql_quote(donation_date),  # donation_date
                mysql_quote("year"),  # donation_date_precision
                mysql_quote("donation log"),  # donation_date_basis
                mysql_quote("FIXME"),  # cause_area
                mysql_quote(row['grantee_url']),  # url
                mysql_quote("FIXME"),  # donor_cause_area_url
                mysql_quote(notes),  # notes
                mysql_quote("FIXME"),  # affected_countries
                mysql_quote("FIXME"),  # affected_regions
            ]) + ")")
            first = False
        print(";")


if __name__ == "__main__":
    main()
