# Steganography Utility
# Nathan Lenzini
# 01/05/2022

import os
from PIL import Image, ImageOps


# Core Functions
def main():

    # Handles main menu user input

    while True:
        choice = get_choice(["Hide a message in an image", "Read a hidden message from an image", "Quit"], "What would you like to do?")
        if choice == 0:
            encode()
        elif choice == 1:
            decode()
        else:
            print("Thank you for using the Steganograpy Utility.")
            break


def encode():

    # Takes text input from user, encodes it to binary, and changes image pixels to match binary digits

    cwd = os.getcwd()

    filename = False # A string variable containing the name of the image to hide the message in
    while not filename:
        print("Please drag the image you would like to hide a message in to the same folder as this program: " + cwd)
        input("Press Enter when you are ready.")
        filename = get_file(["png", "jpg", "jpeg"])

    image = Image.open(filename)           # Image object which takes the user-provided filename as its input
    image = ImageOps.exif_transpose(image) # Preserves some image metadata
    width, height = image.size             # Integer variables storing the width and height of the image in pixels
    pixels = image.load()                  # Object allowing the pixels of the image to be accessed like a data structure
    
    char_limit = (width * height * 3) // 8                                   # Integer variable indicating the images maximum capacity for text
    message = False                                                          # String variable with the message the user would like to hide
    while not message:                                                       # Keeps trying until get_string() returns an acceptable value
        message = get_string("Please enter the message you would like to hide in the image. It cannot exceed " + str(char_limit) + " characters.") + "STOP"
        if not check_string(message):
            message = False
    message = message[:char_limit] if len(message) > char_limit else message # Cuts off message if it is too long

    binary_message = string_to_binary(message)                    # List containing the message in binary digits
    for y in range(height):
        for x in range(width):
            pixel = list(pixels[x, y])                            # List containing the red, green, and blue values of the current pixel
            for i in range(3):
                try:
                    bit = binary_message[3 * (y * width + x) + i] # Integer indicating the number of pixels looked at so far
                except IndexError:
                    break
                color_bit = pixel[i] % 2                          # Integer, either 1 or 0, indicating an even or odd number for the color value

                delta = 0                       # Integer, either 1, 0, or -1, indicating how much the color value should be changed by to make it even or odd (even = 0, odd = 1)
                if bit == 1 and color_bit == 0: # Makes the oddness/evenness of the color value match the current binary digit
                    delta = 1
                elif bit == 0 and color_bit == 1:
                    delta = -1

                pixel[i] += delta

            pixels[x, y] = tuple(pixel)

    image.save(filename[:filename.index(".")] + "_2.png") # The image must be saved as a .png. Other types do not preserve pixel values exactly
    print("Message successfully hidden!")


def decode():

    # Finds text hidden in the pixels of an image, decodes it from binary, and displays it

    cwd = os.getcwd() # String containing the filepath to the folder in which the program is being executed

    filename = False # String indicating the name of the file being searched for encoded text
    while not filename:
        print("Please drag the image you would like to find a message in to the same folder as this program: " + cwd)
        input("Press Enter when you are ready.")
        filename = get_file(["png", "jpg", "jpeg"])

    image = Image.open(filename) # Image object which takes the user-provided filename as its input
    width, height = image.size   # Integer variables storing the width and height of the image in pixels
    pixels = image.load()        # Object allowing the pixels of the image to be accessed like a data structure

    binary_message = []                   # List containing the message in binary digits
    for y in range(height):
        for x in range(width):
            for i in range(3):
                bit = pixels[x, y][i] % 2 # Integer, either 1 or 0, indicating an even or odd number for the color value
                binary_message.append(bit)
    
    message = binary_to_string(binary_message)                                  # String containing the decoded message
    message = message[:message.index("STOP")] if "STOP" in message else message # Does not display nonsensical text representing the rest of the image

    print("Message successfully found!")
    print(message)


# Conversion Functions
def check_string(str):

    # Takes a string as input, returns a boolean indicating whether all characters are ASCII

    for char in str:
        if ord(char) >= 256:
            print("This text contains characters that cannot be encoded.")
            return False
    
    return True


def string_to_binary(str):

    # Takes a string as input, returns a list containing the representation of each character of the string as 8 binary digits

    binary = []                                # List containing the string as binary
    for char in str:
        char_binary = [0, 0, 0, 0, 0, 0, 0, 0] # List containing the current character as binary
        ascii = ord(char)                      # Integer indicating the ASCII value of the current character
        for i in range(8):
            if ascii >= 2 ** (7 - i):          # Binary digits represent power of 2 values, so raise 2 to incrementall smaller powers
                char_binary[i] = 1
                ascii -= 2 ** (7 - i)
        binary.extend(char_binary)
    
    return binary


def binary_to_string(binary):

    # Takes a list containing the representation of characters as 8 binary digits, returns them as a string

    str = ""                          # String containing the decoded binary as text
    for i in range(0, len(binary), 8):
        ascii = 0                     # Integer indicating the ASCII value of the current character
        for j in range(8):
            if binary[i + j]:
                ascii += 2 ** (7 - j) # Binary digits represent power of 2 values, so raise 2 to incrementall smaller powers
        char = chr(ascii)             # Character containing the string representation of the current ASCII value
        str += char

    return str


# User Interface Functions
def get_file(extensions):

    # Takes a list of file extensions as strings as input, finds all files in the current directory that match, gets user choice, and returns the chosen filename as a string

    files = [file for file in os.listdir() if file.split(".")[-1].lower() in extensions] # A list containing filenames as strings

    if len(files) == 0:   # If no files can be found...
        print("No files of the correct type can be found.")
        return False
    elif len(files) == 1: # If only one file is found...
        return files[0]

    return files[get_choice(files, "Please select a file.")]


def get_choice(options, prompt):

    # Takes a list of options as strings and a string prompt as input, displays the prompt and the options, and returns an integer indicating the user's choice

    while True:
        print('\n' + prompt + " (1 - " + str(len(options)) + "):")
        for i, option in enumerate(options):
            print(str(i + 1) + '. ' + option)
        choice = input('>>> ') # String containing an integer representing the user's choice

        try:
            choice = int(choice)
            if(choice > 0 and choice <= len(options)):
                return choice - 1
            else:          # If the user entered a number outside the range of choices...
                print("That's not one of the choices.")
        except ValueError: # If the user didn't enter a number...
            print("Please enter a number.")


def get_number(prompt, bound=0, require_positive=True, use_float=False):

    # Takes a prompt as input and returns an integer (or optionally a float) of the user's choosing. Optional arguments can limit the range of available choices, allow negative inputs, or allow decimal values

    while True:
        print('\n' + prompt)
        choice = input('>>> ')

        try:
            if use_float:
                choice = float(choice)
            else:
                choice = int(choice)
            if bound != 0 and choice > bound:     # If the value is too high...
                print("That value is too high.")
            elif require_positive and choice < 0: # If the value is negative and it oughtn't to be...
                print("Your input must be positive.")
            else:
                return choice
        except ValueError:
            print("Please enter a number.")       # If the value isn't even a number!


def get_string(prompt):

    # Takes a string prompt as input, shows it to the user, and returns a user-inputted string

    print('\n' + prompt)
    choice = input('>>> ') # String containing the user's input
    return choice


if __name__ == "__main__":

    # Executes the main function when the program is started

    main()