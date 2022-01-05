# Steganography Utility
# Nathan Lenzini
# 12/31/2021

import os
from PIL import Image, ImageOps


# Core Functions
def main():

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

    cwd = os.getcwd()

    filename = False
    while not filename:
        print("Please drag the image you would like to hide a message in to the same folder as this program: " + cwd)
        input("Press Enter when you are ready.")
        filename = get_file(["png", "jpg", "jpeg"])

    image = Image.open(filename)
    image = ImageOps.exif_transpose(image)
    width, height = image.size
    pixels = image.load()
    
    char_limit = (width * height * 3) // 8
    message = False
    while not message:
        message = get_string("Please enter the message you would like to hide in the image. It cannot exceed " + str(char_limit) + " characters.") + "STOP"
        if not check_string(message):
            message = False
    message = message[:char_limit] if len(message) > char_limit else message

    binary_message = string_to_binary(message)
    for y in range(height):
        for x in range(width):
            pixel = list(pixels[x, y])
            for i in range(3):
                try:
                    bit = binary_message[3 * (y * width + x) + i]
                except IndexError:
                    break
                color = pixel[i]
                color_bit = color % 2

                delta = 0
                if bit == 1 and color_bit == 0:
                    delta = 1
                elif bit == 0 and color_bit == 1:
                    delta = -1

                pixel[i] += delta

            pixels[x, y] = tuple(pixel)

    image.save(filename[:filename.index(".")] + "_2.png")
    print("Message successfully hidden!")


def decode():

    cwd = os.getcwd()

    filename = False
    while not filename:
        print("Please drag the image you would like to find a message in to the same folder as this program: " + cwd)
        input("Press Enter when you are ready.")
        filename = get_file(["png", "jpg", "jpeg"])

    image = Image.open(filename)
    width, height = image.size
    pixels = image.load()

    binary_message = []
    for y in range(height):
        for x in range(width):
            for i in range(3):
                bit = pixels[x, y][i] % 2
                binary_message.append(bit)
    
    message = binary_to_string(binary_message)
    message = message[:message.index("STOP")] if "STOP" in message else message

    print("Message successfully found!")
    print(message)


# Conversion Functions
def check_string(str):

    for char in str:
        if ord(char) >= 256:
            print("This text contains characters that cannot be encoded.")
            return False
    
    return True


def string_to_binary(str):

    binary = []
    for char in str:
        char_binary = [0, 0, 0, 0, 0, 0, 0, 0]
        ascii = ord(char)
        for i in range(8):
            if ascii >= 2 ** (7 - i):
                char_binary[i] = 1
                ascii -= 2 ** (7 - i)
        binary.extend(char_binary)
    
    return binary


def binary_to_string(binary):

    str = ""
    for i in range(0, len(binary), 8):
        ascii = 0
        for j in range(8):
            if binary[i + j]:
                ascii += 2 ** (7 - j)
        char = chr(ascii)
        str += char

    return str


# User Interface Functions
def get_file(extensions):

    files = [file for file in os.listdir() if file.split(".")[-1].lower() in extensions]

    if len(files) == 0:
        print("No files of the correct type can be found.")
        return False
    elif len(files) == 1:
        return files[0]

    return files[get_choice(files, "Please select a file.")]


def get_choice(options, prompt):

    while True:
        print('\n' + prompt + " (1 - " + str(len(options)) + "):")
        for i, option in enumerate(options):
            print(str(i + 1) + '. ' + option)
        choice = input('>>> ')

        try:
            choice = int(choice)
            if(choice > 0 and choice <= len(options)):
                return choice - 1
            else:
                print("That's not one of the choices.")
        except ValueError:
            print("Please enter a number.")


def get_number(prompt, bound=0, require_positive=True, use_float=False):

    while True:
        print('\n' + prompt)
        choice = input('>>> ')

        try:
            if use_float:
                choice = float(choice)
            else:
                choice = int(choice)
            if bound != 0 and choice > bound:
                print("That value is too high.")
            elif require_positive and choice < 0:
                print("Your input must be positive.")
            else:
                return choice
        except ValueError:
            print("Please enter a number.")


def get_string(prompt):

    print('\n' + prompt)
    choice = input('>>> ')
    return choice


if __name__ == "__main__":

    main()