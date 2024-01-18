print("Hello World!")

# This assigns 23 to a variable
someVar = 23

# print("someVar's value is", someVar)

someVar = "This is someVar"

# print("someVar's value is:", someVar)

myVar = int(7.0)
myVar = float(7)
myVar += 1

# print(myVar ** 3)
# print(7 / 2)
# Demo escape sequences
my_string = "This is a string"
my_string = 'This is a\t string\nAnd that\'s cool!'
# print(my_string)

new_string = f'my_string: "{my_string}". someVar: {someVar}'
# print{new_string}

print(f'new_string is {len(new_string)} characters long')

print (new_string.index("fasldshfaflsdh"))

fox = 'The quick brown fox jumped over the lazy dog'

my_list = [1, 2, 3, 4, 5, 6]
print(my_list[0:6:2])
print(my_list[-1])

# main difference between strings and lists -- strings are
# immuatable (unchangable) and can't be modified
# There is no 'append' function on strings.
#fox.append('----------')

mylist.append(20)
print(myList)


# Get user input and store it in the variable 'user_input':
user_input = input("Enter a number: ")
user_input_as_int = int(user_input)

# Define a function named 'sort_list' that takes one parameter:  
def sort_list(unsorted_list):
    print(unsorted_list)
    print("This is another line of the function")

def another_fn():
    return None
