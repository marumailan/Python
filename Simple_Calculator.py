#Simple Calculator

#Addtion
def addition(x, y):
	return x + y

#Subtract
def subtract(x, y):
	return x - y

#Multiply
def multiply(x, y):
	return x * y


#Divide
def divide(x, y):
	return x / y


#user input
print("Select Operation.")
print("1. Add")
print("2. Subtract")
print("3. Multiply")
print("4. Divide")

choice = input("Enter Choice 1, 2, 3, 4: ")

num1 = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))

#Operation

if choice == '1':
	print(num1, "+", num2, "=", addition(num1, num2))


elif choice == '2':
	print(num1, "-", num2, "=", subtract(num1, num2))


elif choice == '3':
	print(num1, "*", num2, "=", multiply(num1, num2))

elif choice == '4':
	print(num1, "/", num2, "=", divide(num1, num2))

else:
	print("Invalid input")	

