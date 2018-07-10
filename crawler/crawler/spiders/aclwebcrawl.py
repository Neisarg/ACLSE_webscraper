# -*- coding: utf-8 -*-
import scrapy
import os
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from crawler.settings import DOC_HOME
from scrapy.http import Request

PDF_HOME = os.path.join(DOC_HOME, "scrapy_data_pdf")
XML_HOME = os.path.join(DOC_HOME, "scrapy_data_xml")
BIB_HOME = os.path.join(DOC_HOME, "scrapy_data_bib")

BASE_URL = "https://aclanthology.coli.uni-saarland.de"

if not os.path.exists(PDF_HOME):
    os.makedirs(PDF_HOME)

if not os.path.exists(XML_HOME):
    os.makedirs(XML_HOME)

if not os.path.exists(BIB_HOME):
    os.makedirs(BIB_HOME)


class AclwebcrawlSpider(CrawlSpider):
    name = 'aclwebcrawl'
    allowed_domains = ['www.aclweb.org','aclweb.org','aclanthology.coli.uni-saarland.de']
    start_urls = ["https://aclanthology.coli.uni-saarland.de/" ]
    rules = (
        Rule(
            LinkExtractor(
                allow = r'https*:\/\/aclanthology\.coli\.uni-saarland\.de\/papers\/[A-Z][0-9][0-9]-[0-9]+\/[a-z][0-9][0-9]-[0-9]+',
                deny = r'https:\/\/aclanthology\.coli\.uni-saarland\.de\/papers\/[A-Z][0-9][0-9]-[0-9]+\/[a-z][0-9][0-9]-[0-9]+\..+'
            ),
            callback = 'parse_paper_page',
            follow = True
        ),
        Rule(
            LinkExtractor(
                allow = [ r'https*:\/\/www\.aclweb\.org\/anthology\/[A-Z][0-9][0-9]-[0-9]+',
                          r'https*:\/\/aclweb\.org\/anthology\/[A-Z][0-9][0-9]-[0-9]+']
            ),
            callback = 'parse_pdf',
            follow = True
        ),
        Rule(
            LinkExtractor(
                allow = r'https:\/\/aclanthology\.coli\.uni-saarland\.de\/papers\/[A-Z][0-9][0-9]-[0-9]+\/[a-z][0-9][0-9]-[0-9]+\.bib',
            ),
            callback = 'parse_bib',
            follow = True
        ),
        Rule(
            LinkExtractor(
                allow = r'https:\/\/aclanthology\.coli\.uni-saarland\.de\/papers\/[A-Z][0-9][0-9]-[0-9]+\/[a-z][0-9][0-9]-[0-9]+\.xml',
            ),
            callback = 'parse_xml',
            follow = True
        ),
        Rule(
            LinkExtractor(),
            callback = 'parse_item',
            follow = True
        )
    )

    def parse_item(self, response):
        yield

    def parse_paper_page(self, response):
        #print(response.url)
        meta = response.xpath('//div[@class="span12 page-header"]/h2/a/@href').extract()
        pdf_url = meta[0]

        #print("dispatch_pdf : ", pdf_url)
        yield scrapy.Request(pdf_url, callback = self.parse_pdf)

        bib_url = BASE_URL + meta[1]
        #print("dispatch_bib : ", bib_url)
        yield scrapy.Request(bib_url, callback = self.parse_bib)

        xml_url = bib_url[:-4] + '.xml'
        #print("dispatch_xml : ", xml_url)
        yield scrapy.Request(xml_url, callback = self.parse_xml)


    def parse_bib(self,response):
        print(response.url)
        path = response.url.split('/')[-1]
        path = os.path.join(BIB_HOME, path)
        with open(path, 'wb') as f:
            f.write(response.body)
        yield

    def parse_pdf(self, response):
        if response.status != 200:
            yield
        print(response.url)
        path = response.url.split('/')[-1] + ".pdf"
        path = os.path.join(PDF_HOME, path)
        with open(path, 'wb') as f:
            f.write(response.body)
        yield

    def parse_xml(self,response):
        print(response.url)
        path = response.url.split('/')[-1]
        path = os.path.join(XML_HOME, path)
        with open(path, 'wb') as f:
            f.write(response.body)
        yield
