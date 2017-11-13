import scrapy
from fara.util.model import DataModel
import datetime

class FasaSpider(scrapy.Spider):
    name = "fara"
    allowed_domains = ['fara.gov']
    start_urls = ['https://www.fara.gov/quick-search.html']

    # Clear content of fara_active_principals.json file for new inputs
    # Reason: So we dont have irrelevant/old data
    rm_active_p_data = open("fara_active_principals.json", 'w').close()

    # Intial Parse Method
    def parse(self, response):

        # Pick the source of the iframe and loads it
        for link in response.css('iframe::attr(src)'):
            url = response.urljoin(link.extract())
            yield scrapy.Request(url, callback = self.parse_iframe_content)

    # Parse the content of the Iframe
    def parse_iframe_content(self, response):
        for iframe_url in response.css('ul[id="L80330217189774968"] li:first-child a::attr(href)'):  
            url = response.urljoin(iframe_url.extract())
            yield scrapy.Request(url, callback = self.parse_active_principal)

    # Main Active Principal Parser Method
    def parse_active_principal(self, response):

        # Get Main table that contains our data
        for data_table in response.xpath('//table[@class="apexir_WORKSHEET_DATA"]/tr'):
            country_name = data_table.css('th.apexir_REPEAT_HEADING span.apex_break_headers::text').extract_first()

            # Set Contry name if available
            if country_name:
                country = country_name
            
            # Run if country name is None to check if spider is in the correct tr.
            # Coutry name resolves to None if in the correct tr because the data tr
            # doesn't contain 'apexir_REPEAT_HEADING' class, hence there is no match for it

            if country_name is None and (data_table.css('.even') or data_table.css('.odd')):
                foreign_principal = data_table.css('td[headers*=FP_NAME]::text').extract_first()
                if foreign_principal:

                    # Get Follow URL for Exhibit URL's
                    follow_url = data_table.css('td[headers] a::attr(href)')

                    # Convert URL to clickable link
                    url = data_table.css('td[headers] a::attr(href)').extract_first()
                    patch_url = response.urljoin(url)

                    # Addresses contain some Unicode Characters that needs to remove from address string
                    parsed_address = "".join([raw_address.replace(u'\xa0', u' ') for raw_address in data_table.css('td[headers*=ADDRESS_1]::text').extract()])

                    # Convert Date to ISOFormat
                    registration_date = data_table.css('td[headers*=REG_DATE]::text').extract_first()
                    registration_date = datetime.datetime.strptime(registration_date, '%m/%d/%Y').isoformat()

                    data = DataModel()
                    data['foreign_principal'] = foreign_principal
                    data['state'] = data_table.css('td[headers*=STATE]::text').extract_first()
                    data['url'] = patch_url
                    data['country'] = country
                    data['reg_num'] = data_table.css('td[headers*=REG_NUMBER]::text').extract_first()
                    data['address'] = parsed_address
                    data['date'] = registration_date
                    data['registrant'] = data_table.css('td[headers*=REGISTRANT_NAME]::text').extract_first()
                    for href in data_table.css('td[headers] a::attr(href)'):
                        yield response.follow(href, self.parse_exhibit_url, meta={'data_model' : data})

        NEXT_PAGE_SELECTOR = 'img[title=Next]'
        nextpage = response.css(NEXT_PAGE_SELECTOR).extract_first() is not None

        # Check if the next page button is available
        if nextpage:

            # The Pagination URL is hidden inside an href like so : 
            # javascript:gReport.navigate.paginate('pgR_min_row=16max_rows=15rows_fetched=15')
            # Scrapy can't parse that kind of url, so had to check network request and 
            # an API that accepts a POST HTTP METHOD and returns HTML for the new page
            # URL : https://efile.fara.gov/pls/apex/wwv_flow.show
            # Sample Parameters: 
            # {
            #     p_request:APXWGT
            #     p_instance:11308718744962
            #     p_flow_id:171
            #     p_flow_step_id:130
            #     p_widget_num_return:15
            #     p_widget_name:worksheet
            #     p_widget_mod:ACTION
            #     p_widget_action:PAGE
            #     p_widget_action_mod:pgR_min_row=31max_rows=15rows_fetched=15
            #     x01:80340213897823017
            #     x02:80341508791823021
            # }

            # Check if parameter doesnt already exists in response meta
            if 'parameters' not in response.meta:
                parameters = {
                    'p_request' : 'APXWGT',
                    'p_instance' : response.css('input[id="pInstance"]::attr(value)').extract_first(),
                    'p_flow_id' : response.css('input[id="pFlowId"]::attr(value)').extract_first(),
                    'p_flow_step_id' : response.css('input[id="pFlowStepId"]::attr(value)').extract_first(),
                    'p_widget_num_return' : '15',
                    'p_widget_name' : 'worksheet',
                    'p_widget_mod' : 'ACTION',
                    'p_widget_action' : 'PAGE',
                    'x01': response.css('input[id="apexir_WORKSHEET_ID"]::attr(value)').extract_first(),
                    'x02': response.css('input[id="apexir_REPORT_ID"]::attr(value)').extract_first()
                }
            else:
                parameters = response.meta['parameters']
            
            next_page = "https://efile.fara.gov/pls/apex/wwv_flow.show"
            
            # Get the href content of the pagination link, which is returned similar to
            # javascript:gReport.navigate.paginate('pgR_min_row=16max_rows=15rows_fetched=15')

            path = response.xpath('(//td[@class="pagination"]/span/a/@href)[last()]').extract_first()

            # Using the Example from above, Get the content between the two braces which is returned as
            # pgR_min_row=16max_rows=15rows_fetched=15

            p_widget_action_mod = path[path.find("('") + 2 : path.find("')")]

            # Add our p_widget_action_mod result to the parameter dict
            parameters['p_widget_action_mod'] = p_widget_action_mod

            # Make POST HTTP Request to Pagination URL with parameter dict as POST OBJECT
            request = scrapy.FormRequest(next_page, method="POST", formdata=parameters, callback=self.parse_active_principal)
            request.meta['parameters'] = parameters
        
            yield request

    def parse_exhibit_url(self, response):
        def extract_with_css(query):
            return response.css(query).extract()
        
        response.meta['data_model']['exhibit_url'] = extract_with_css('td[headers=DOCLINK] a::attr(href)')
        yield response.meta['data_model']
