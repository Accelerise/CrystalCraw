import math
import mmh3
from bitarray import bitarray


def ln(number):
	return math.log(number,math.e)

class Bloomfilter:
	# 
	def __init__(self,number,errorRate):
		self.number = number
		size = -(number*ln(errorRate)/(ln(2)*ln(2)))
		self.size = math.ceil(size)
		self.errorRate = errorRate
		self.numHash = int(math.ceil(0.7 * (size / number)))
		self.bitArray = bitarray(int(math.ceil(size)))
		self.bitArray.setall(0)
		self.itemArray =[]
	#
	def displayParameter(self):
		print "Number is : %d" % self.number
		print "Size is : %f  MB" % ((self.size/8)/1024/1024)
		print "errorRate is : %f" % self.errorRate
		print "NumHash is : %d " %self.numHash
	#
	def isContain(self,item):
		for i in range(self.numHash):
			bitIndex = long (mmh3.hash128(item,i) % self.size)
			if self.bitArray[bitIndex] == 0 :
				return False
		return True		
	#
	def add(self,item):
		if self.isContain(item):
			return False
		else :
			for i in range(self.numHash):
				bitIndex = long (mmh3.hash128(item,i) % self.size)
				self.bitArray[bitIndex] = 1
			return True
	
def test():
	bf = Bloomfilter(100000000,0.00001)
	bf.displayParameter()

#show the data
# #test
# animals = ['dog', 'cat', 'giraffe', 'fly', 'mosquito', 
# 'horse', 'eagle','bird', 'bison', 'boar', 'butterfly', 
# 'ant', 'anaconda', 'bear','chicken', 'dolphin', 'donkey', 'crow', 'crocodile']
# otherAnimals = ['badger', 'cow', 'pig', 'sheep', 'bee',
# 'wolf', 'fox','whale', 'shark', 'fish', 'turkey', 'duck',
# 'dove','deer', 'elephant', 'frog', 'falcon', 'goat', 'gorilla','hawk','fly' ]

# for i in range(len(animals)):
# 	if bf.add(animals[i]):
# 		print "sucess push : %s" % animals[i]
# 	else :
# 		print "wrong ! : %s" % animals[i]

# for i in range(len(otherAnimals)):
# 	if bf.isContain(otherAnimals[i]):
# 		print "oh no ,it's wrong :" + otherAnimals[i]
# 	else :
# 		print "sucess,it's right :" + otherAnimals[i]
