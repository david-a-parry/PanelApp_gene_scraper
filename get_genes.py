#!/usr/bin/env python3
import sys
import requests
import logging

logger = logging.getLogger("PanelApp Scraper")
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
                '[%(asctime)s] %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logger.level)
ch.setFormatter(formatter)
logger.addHandler(ch)

max_attempts = 3

results_fields = dict(gene_data=['hgnc_symbol', 'gene_name', 'omim_gene',
                                 'hgnc_id', 'biotype'],
                      panel=['id', 'name', 'disease_group'],
                      confidence_level=None,
                      evidence=None)


def get_endpoint(url, attempt=0):
    r = requests.get(url, timeout=5.0)
    if not r.ok:
        if attempt < max_attempts:
            attempt += 1
            logger.warn("Retry {}/{}".format(attempt, max_attempts) +
                        " for {}\n".format(url))
            return get_endpoint(url, attempt=attempt)
        r.raise_for_status()
    return r.json()


def print_results(results, fields):
    n = 0
    for res in results:
        n += 1
        row = []
        for k, v in fields.items():
            if v is None:
                if isinstance(res[k], list):
                    row.append(",".join(res[k]))
                else:
                    row.append(res[k])
            else:
                for j in v:
                    if isinstance(res[k][j], list):
                        row.append(",".join(res[k][j]))
                    else:
                        row.append(res[k][j])
        print("\t".join(str(x) for x in row))
    return n
 

def main():
    url = 'https://panelapp.genomicsengland.co.uk/api/v1/genes/?format=json'
    header = []
    for k, v in results_fields.items():
        if v is None:
            header.append(k)
        else:
            header.extend(v)
    print("\t".join(header))
    n = process_url(url, count=1)
    logger.info("Finished processing {} gene entities".format(n))

def process_url(url, count=1):
    logger.info("Lookup {}".format(count))
    results = get_endpoint(url)
    if 'results' not in results:
        raise LookupError("No results for {}".format(url))
    n = print_results(results['results'], results_fields)
    logger.info("Processed {} gene entities for lookup {}".format(n, count))
    if 'next' in results and results['next'] is not None:
        count += 1
        n += process_url(results['next'], count)
    return n


if __name__ == '__main__':
    main()
    