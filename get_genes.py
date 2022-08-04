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
                      mode_of_inheritance=None,
                      mode_of_pathogenicity=None,
                      phenotypes=None,
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


def get_ensembl_information(result):
    grch37_ver = 0
    grch37_id = '-'
    grch38_ver = 0
    grch38_id = '-'
    if 'ensembl_genes' in result['gene_data']:
        edict = result['gene_data']['ensembl_genes']
        if 'GRch37' in edict:
            for k, v in edict['GRch37'].items():
                ver = int(k)
                if ver >= grch37_ver:
                    grch37_ver = ver
                    grch37_id = v['ensembl_id']
        if 'GRch38' in edict:
            for k, v in edict['GRch38'].items():
                ver = int(k)
                if ver >= grch38_ver:
                    grch38_ver = ver
                    grch38_id = v['ensembl_id']
    return [grch37_ver, grch38_ver, grch37_id, grch38_id]


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
        row.extend(get_ensembl_information(res))
        print("\t".join(str(x).replace('\t', ';') for x in row))
    return n


def main():
    url = 'https://panelapp.genomicsengland.co.uk/api/v1/genes/?format=json'
    header = []
    for k, v in results_fields.items():
        if v is None:
            header.append(k)
        else:
            header.extend(v)
    header.extend(['Ensembl_GRCh37_version', 'Ensembl_GRCh38_version',
                   'Ensembl_GRCh37_ID', 'Ensembl_GRCh38_ID'])
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

