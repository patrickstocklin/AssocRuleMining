import sys
import time
import numpy as np
import os

'''''''''''''''''''''

ASSOCIATION RULE MINING

Files: 
	small_basket.dat - holds our transactions, 4000 in total
	products - holds our product names, prices, 100 in total

Support and Confidence Values: (0.20, 0.75), (0.40, 0.75), (0.50, 0.75),
	(0.20, 0.60), (0.40, 0.60), (0.50, 0.60)

The Plan of Attack:
	[x] Find the Support of Single Items
	Return this as a list of K = 1 items, that we are able to combines as a List of N Products
		When we combine, what we do is generate a lot of combinations for our list to hold
		We self join this N size List with itself
		We then select from this list where
		Pruning:
			If join of all itmes in Candidate List C(K = length of itemset items) do not contain subsets S
				such that all elements in subset exist in self-joined list(K - 1), then remove them
				we do not need to remove or expel any items
			If however we find an element who has an item in its subset that does not exist
				then we must remove it from C_K.
	
	Run through a list of itemsets and calculate their support metric for a given dataset
		If they have a support that is below the threshold, then remove that sonavabitch

	Repeat This Process of Self Joining, Pruning, and Elimination until we cannot produce any new items, ie,
		all generated candidates in C_K do not contain a subset that exists in the list        

	It might be useful to use vertically store a list of transaction ids for each item so we can
		quickly calculate the support of each newly created itemset:
			For each new candidate list, we should join AB with C of transaction ids
				and calculate the new support

	
	Once we have our exhausted list of itemsets that are most frequent, we need to generate candidate rules as 
	efficiently as possible, checking for the confidence of each ruleset generated, and saving them
	
	Generating the rulesets requires a level wise approach starting with only one item in the consequent of the rule
		We do this because all further rulesets would move one determinant to the RHS side would decrease confidence

'''''''''''''''''''''

class Transaction:
	def __init__ (self):
		self.data = {}
		self.items = []

	#Constructor that takes in data in form of string/line from input file
	def __init__(self, itemsarr, prods):
		self.data = {}
		self.items = itemsarr
		print itemsarr
		#Assigns Product Name as Key with Number of Items as value
		for i in range(len(itemsarr)):
			if itemsarr[i] is not '0':
				self.data[prods[i]] = i	

	def printData(self):
		print self.items
		for key, val in sorted(self.data.iteritems(), key=lambda (k,v):(v,k)):
			print key, val

def loadTransactions(Transactions, Products):
	with open('small_basket.dat', 'r') as f:
		j = 1
		for line in f:
			arr = line.strip('\r\n').split(', ')[1:]
			print "appending %d transaction" %j
			j += 1
			Transactions.append(Transaction(arr, Products))
	f.close()
	return Transactions

def loadProducts(Products):
	with open('products', 'r') as f:
		for product in f:
			Products.append(product.split(',')[0])
	f.close()
	return Products

def printTransactions(transactionsArray):
	for transaction in transactionsArray:
		transaction.printData()

#creates a vertical table of Product:[Transaction IDs] to quickly calculate supports of intersections of itemsets
def constructVerticalProducts(Transactions, Products):
	verticalTable = {}
	for product in Products:
	 	verticalTable[product] = []

	for prod in verticalTable.keys():
		transNo = 1
		for transaction in Transactions:
			if prod in transaction.data.keys():
				verticalTable[prod].append(transNo)
			transNo += 1 
	
	return verticalTable

def printVerticalProducts(ProductTransactions):
	i = 0
	for k,v in ProductTransactions.iteritems():
		print str(k) + ": " + str(len(v))
		print str(k) + ": " + repr(v)
		i += 1
		if i > 3:
			break

#Calculates the Initial Frequent Itemset with each element K = 1 given Transactions and Products
def constructInitialFrequentItemset(Transactions, Products, minSupport):
	print ("Constructing Initial Frequent Itemset with minSupport")
	frequentItemset = {}

	for product in Products:
		supp, cnt = calculateProductSupport(product, Transactions)
		if supp > minSupport:
			frequentItemset[product] = supp
		#else:
		#	print("Item %s has support %f which is < than %f" %(product, supp, minSupport))
	print ("Printing Frequent Itemset with support > than %f" %minSupport)

	for key, val in frequentItemset.iteritems():
		print key, val

	return frequentItemset

#Uses Apriori Principle to Generate the Most Frequent Itemsets such that > minSupport Value)
'''
Generate next list of items with size = k+1
Check if any subsets do not exist in previous list
	if not, remove from dictionary
Cull the list for items that do not have enough support

Repeat until we do not generate any more rules with sufficient confidence
'''
def generateFrequentItemsets(Transactions, Products, minSupport):
	frequentItemset = []

	initFreqItems = constructInitialFrequentItemset(Transactions, Products, minSupport)

	for item in initFreqItems.keys():
		frequentItemset.append(item)

	return frequentItemset

#Given a single product, find the support parameter given our Transactions Array
def calculateProductSupport(Product, Transactions):
	count = 0
	for transaction in Transactions:
		if Product in transaction.data.keys():
			count += 1
	support = float(count)/len(Transactions)
	return support, count

if __name__ == '__main__':
	#Arrays to hold our Transaction Objects and Products Array for Product Strings
	Transactions = []
	Products = []
	#Dictionary with Product Name:[Transaction1, Transaction2...] is a list
	ProductTransactions = {}
	#Support and Confidence Parameters
	MINING_PARAMS = [(0.20, 0.75), (0.40, 0.75), (0.50, 0.75),
	(0.20, 0.60), (0.40, 0.60), (0.50, 0.60)]
	
	print ("Ingesting")
	Products = loadProducts(Products)
	Transactions = loadTransactions(Transactions, Products)
	ProductTransactions = constructVerticalProducts(Transactions, Products)
	

	for case in MINING_PARAMS:
		minSup = case[0]
		minCon = case[1]
		frequentItemset = generateFrequentItemsets(Transactions, Products, minSup)
	
	# printTransactions(Transactions)
	# printVerticalProducts(ProductTransactions)

	print ("Association Rule Mining is done! Writing Rulesets to text file")
