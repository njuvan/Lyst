import scrapy
from scrapy.spiders import CrawlSpider, Rule
from oxygendemo.items import OxygendemoItem
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from pyquery import PyQuery
import re


# EXCHANGE RATES -----------------------

# eur_gbp
exchange_rates = PyQuery('https://www.ecb.europa.eu/stats/exchange/eurofxref/html/index.en.html')
global eur_gbp
eur_gbp = exchange_rates('td#GBP ~ td.spot.number > span.rate').text()
eur_gbp = float(eur_gbp)


# eur_usd
exchange_rates = PyQuery('https://www.ecb.europa.eu/stats/exchange/eurofxref/html/index.en.html')
global eur_usd
eur_usd = exchange_rates('td#USD ~ td.spot.number > span.rate').text()
eur_usd = float(eur_usd)
# --------------------------------------


# SPIDER
class OxygenSpider(CrawlSpider):
	name = "oxygen"
	allowed_domains = ["oxygenboutique.com"]
	start_urls = ["http://www.oxygenboutique.com"]

	rules = [
		Rule(LxmlLinkExtractor(restrict_css=('.topnav'))),
		Rule(LxmlLinkExtractor(restrict_css=('.pages'), allow=('ViewAll=1$'))),
		Rule(LxmlLinkExtractor(restrict_css=('.itm'), deny=('.tame')), callback='parse_item'),
	]

	def parse_item(self, response):
		def code():
			code = response.css('#aspnetForm::attr(action)').extract()[0].strip('/').strip('.aspx').lower()
			return code

		def name():
			name = response.css('.right h2::text').extract()[0].strip()
			return name

		def description():

			# DESC_1
			description1 = response.css('.right #accordion div::text').extract()[0].strip().encode('utf-8').strip('\xa3')
			description1_split = re.findall(r"[\w']+", str(description1.lower()))

			# DESC_2
			description2 = response.css('.right #accordion div span::text').extract()[0].strip().encode('utf-8').strip('\xa3')
			description2_split = re.findall(r"[\w']+", str(description2.lower()))

			# DESC_3
			try:
				description3 = response.css('.right #accordion div pre::text').extract()[0].strip().encode('utf-8').strip('\xa3')
				description3_split = re.findall(r"[\w']+", str(description3.lower()))
			except:
				description3 = ''

			# DESC_4
			try:
				description4 = response.css('.right #accordion div div::text').extract()[0].strip().encode('utf-8').strip('\xa3')
				description4_split = re.findall(r"[\w']+", str(description4.lower()))
			except:
				description4 = ''

			# DESC_5
			try:
				description5 = response.css('.right #accordion div span:nth-child(2)::text').extract()[0].strip().encode('utf-8').strip('\xa3')
				description5_split = re.findall(r"[\w']+", str(description5.lower()))
			except:
				description5 = ''

			# DESC_6
			try:
				description6 = response.css('.right #accordion div p:nth-child(2)::text').extract()[0].strip().encode('utf-8').strip('\xa3')
				description6_split = re.findall(r"[\w']+", str(description6.lower()))
			except:
				description6 = ''

			# DESC_7
			try:
				description7 = response.css('.right #accordion div div + div + div::text').extract()[0].strip().encode('utf-8').strip('\xa3')
				description7_split = re.findall(r"[\w']+", str(description7.lower()))
			except:
				description7 = ''

			# DESC_8
			try:
				description8 = response.css('.right #accordion div p::text').extract()[0].strip().encode('utf-8').strip('\xa3')
				description8_split = re.findall(r"[\w']+", str(description8.lower()))
			except:
				description8 = ''

			# DESC_SELECT
			description = None
			len_limit = 30
			if (len(description1) > len_limit) and ('delivery' not in description1_split):
				description = description1
			elif (len(description2) > len_limit) and ('delivery' not in description2_split):
				description = description2
			elif (len(description3) > len_limit) and ('delivery' not in description3_split):
				description = description3
			elif (len(description4) > len_limit) and ('delivery' not in description4_split):
				description = description4
			elif (len(description5) > len_limit) and ('delivery' not in description5_split):
				description = description5
			elif (len(description6) > len_limit) and ('delivery' not in description6_split):
				description = description6
			elif (len(description7) > len_limit) and ('delivery' not in description7_split):
				description = description7
			elif (len(description8) > len_limit) and ('delivery' not in description8_split):
				description = description8

			if description:
				return description
			else:
				return item['name']


		def designer():
			designer = response.css('.right .brand_name a::text').extract()[0].strip()
			return designer


		def gender():
			gender = 'F'
			return gender


		def images():
			images = [response.urljoin(href) for href in response.css('.left td a::attr(href)').extract()]
			return images


		def link():
			link = response.url
			return link


		def gbp_price():
			def sale_check():
				sale_check = response.css('#container > div.right > span > span.mark > span::text').extract()[0]
				if sale_check.strip():
					return True
				else:
					return False

			if sale_check() == True:
			 	gbp_price = float(response.css('.price span::text').extract()[0].strip())
			else:
				gbp_price = response.css('.price::text').extract()[0].encode('utf-8')
				gbp_sym = '\xc2\xa3'
				try:
					gbp_price = float(gbp_price.strip().strip(gbp_sym))
				except:
					gbp_price = None

			return gbp_price


		def color():
			color_list = ['red', 'orange', 'yellow', 'green', 'blue', 'violet', 'purple', 'pink', 'grey', 'brown', 'black', 'white', 'beige', 'silver', 'gold', 'golden']
			try:
				item_description = description().lower().split(' ')
				for color in color_list:
					if color in item_description:
						return color
						break
			except:
				return None


		def sale_discount():
			def sale_check():
				sale_check = response.css('#container > div.right > span > span.mark > span::text').extract()[0]
				if sale_check.strip():
					return True
				else:
					return False

			if item['gbp_price'] == None:
				return None
			else:
				if sale_check() == True:
					gbp_price = float(response.css('.price span::text').extract()[0].strip())
					gbp_price_disc = float(response.css('.price span::text').extract()[1].strip())
					discount = (gbp_price - gbp_price_disc) / gbp_price
					return discount
				else:
					return None


		def stock_status():
			stock = response.css('#ctl00_ContentPlaceHolder1_ddlSize option::text')[1:].extract()
			stock = [item.split(' - ') for item in stock]
			stock_status = {}
			for i in stock:
				if len(i) > 1 and i[1].lower() == ('sold out'):
					stock_status[i[0]] = 1
				else:
					stock_status[i[0]] = 3
			return stock_status


		def type():
			description = item['description']
			description = re.findall(r"[\w']+", str(description.lower()))

			# APPAREL - "A"
			A = open('apparel.txt', 'r')
			apparel = A.read().strip().split("\n")
			for i in apparel:
				if i in description:
					return "A"
					break
			A.close()
			
			# SHOES - "S"
			S = open('shoes.txt', 'r')
			shoes = S.read().strip().split("\n")
			for i in shoes:
				if i in description:
					return "S"
					break
			S.close()

			# BAGS - "B"
			B = open('bags.txt', 'r')
			bags = B.read().strip().split("\n")
			for i in bags:
				if i in description:
					return "B"
					break
			B.close()

			# JEWELRY - "J"
			J = open('jewelry.txt', 'r')
			jewelry = J.read().strip().split("\n")
			for i in jewelry:
				if i in description:
					return "J"
					break
			J.close()

			# ACCESSORIES - "R"
			R = open('accessories.txt', 'r')
			accessories = R.read().strip().split("\n")
			for i in accessories:
				if i in description:
					return "R"
					break
			R.close()

			
		def eur_price():
			if item['gbp_price']:
				eur_price = round(item['gbp_price']/eur_gbp, 2)
				return eur_price
			else:
				return None


		def usd_price():
			if item['eur_price']:
				usd_price = round(item['eur_price']*eur_usd, 2)
				return usd_price
			else:
				return None


		item = OxygendemoItem()
		print '------------'
		item['code'] = code()
		item['name'] = name()
		item['description'] = description()
		item['designer'] = designer()
		item['gender'] = gender()
		item['images'] = images()
		item['link'] = link()
		item['gbp_price'] = gbp_price()
		item['raw_color'] = color()
		item['sale_discount'] = sale_discount()
		item['stock_status'] = stock_status()
		item['type'] = type()
		item['eur_price'] = eur_price()
		item['usd_price'] = usd_price()
		yield item