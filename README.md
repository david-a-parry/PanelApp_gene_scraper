# PanelApp_gene_scraper
Quickly scrape summary information from all gene entities from PanelApp

## Usage:

Requires Python 3.

The following will download this repository to your current working directory and then write a tab-separated list of genes from [PanelApp](https://panelapp.genomicsengland.co.uk). 

    
    $ git clone https://github.com/david-a-parry/PanelApp_gene_scraper.git
    $ python3 PanelApp_gene_scraper/get_genes.py > panel_app_genes.tsv
