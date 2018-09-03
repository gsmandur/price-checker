# import libraries
import urllib.request
import csv
import json
import smtplib

from datetime import date
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart


# finds the price for a prouduct on the web
# - track the price changes, and emails me when it does
# - for a new product just change info in the main function

def getPrice(url, html_attribute, attribute_description):
	# query website and get contents
	page = urllib.request.urlopen(url)

	# parse html contents with BeautifulSoup
	soup = BeautifulSoup(page, 'html.parser')

	# get the price on the page
	price_box = soup.find('span', attrs={html_attribute : attribute_description} )
	price = price_box.text
	print(price)
	return price


# store price in csv doc (by appending to it)
def sendToCSV(product, price):

	# append info to csv file
	with open('price_change_log.csv', 'a', newline='') as csv_file:
		writer = csv.writer(csv_file)
		writer.writerow([product, price, date.today()])

	print("entered info to tracker.csv")


# send an email about the current price of the product
def sendEmailAlert(product, price):
	from_addr = 'FROM_EMAIL'
	to_addr = 'TO_EMAIL'
	msg = MIMEMultipart()
	msg['From'] = from_addr
	msg['To'] = to_addr
	msg['Subject'] = product + ': ' + price

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(from_addr, 'PASSWORD')
	text = msg.as_string()
	server.sendmail(from_addr, to_addr, text)
	server.quit()
	print("sent email!")


# compare the current price with the last checked price (hopefully yesterdays)
def priceCompare(product, price):
	# get the last stored price of the item from the json file
	with open('price_history.json') as f:
		data = json.load(f)
	
	# initialize product price info if not already in json file
	if product not in data:
		data[product] = price

	prev_price = data[product]
	cur_price = price
	print("previous price: " + prev_price)
	print("current price:  " + cur_price)

	# compare prices
	if prev_price != cur_price:
		print("price has changed!")

		sendToCSV(product, price)			# save new price in csv file
		sendEmailAlert(product, price)		# send email to notify me

	# update json file price to current price and dump updates into json file
	data[product] = cur_price
	with open('price_history.json', 'w') as f:
		json.dump(data, f)


if __name__ == '__main__':
	product = 'sportchek - nike flyknit shoes'
	url = 'https://www.sportchek.ca/categories/men/footwear/running-shoes/lightweight/product/nike-mens-free-rn-flyknit-motion-2017-running-shoes-black-332258744.html#332258744%5Bcolor%5D=99'
	
	# location of the price html attribute on the webpage (for scraping)
	price_attribute = 'class'
	attribute_description = 'product-detail__price-text'


	price = getPrice(url, price_attribute, attribute_description)
	priceCompare(product, price)
