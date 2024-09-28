import numpy as np 
from PIL import Image, ImageDraw, ImageFont
import cv2
import json
import random 
import html
import os 
import base64

def encode_file_to_base64(file_path):
    # Open the file in binary mode
    with open(file_path, "rb") as file:
        # Read the file content and encode it to Base64
        encoded_content = base64.b64encode(file.read())
        
        # Convert the bytes to a string (optional, depending on usage)
        base64_string = encoded_content.decode('utf-8')
        
    return base64_string

def resize_input(img, blur_ksize=(5,5), sigmaX=0):  
    
    # Get original dimensions
    original_height, original_width = img.shape[:2]
    
    # Step 0: Gaussian blurr
    blurred_img = cv2.GaussianBlur(img, blur_ksize, sigmaX)
    
    # Step 1: Shrink the height to 60% of the original height
    new_height = int(original_height * 0.55 / 0.9)
    new_width = original_width  # Keep the width the same for now
    resized_img = cv2.resize(blurred_img, (new_width, new_height), cv2.INTER_CUBIC)
    
    # Step 2: Proportionally resize the image to fit within 200px height and 120px width
    max_height = 300
    max_width = 300
    
    # Calculate the aspect ratio of the resized image
    aspect_ratio = new_width / new_height
    
    # Calculate the new dimensions based on the aspect ratio
    if new_height > max_height or new_width > max_width:
        # If the height is greater than 200 or the width is greater than 120, we scale down
        scale_factor = min(max_width / new_width, max_height / new_height)
        final_width = int(new_width * scale_factor)
        final_height = int(new_height * scale_factor)
    else:
        # If the dimensions are already within the limits, keep the current size
        final_width = new_width
        final_height = new_height
    
    # Resize the image to the final dimensions
    final_resized_img = cv2.resize(resized_img, (final_width, final_height), cv2.INTER_CUBIC)
    
    # Save the final resized image to Grayscale 
    cv_img_gs = cv2.cvtColor(final_resized_img, cv2.COLOR_BGR2GRAY)
    return cv_img_gs

def make_transparent_white(image_path):
    # Step 1: Read the PNG image with the alpha channel (RGBA)
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
    # Check if the image has an alpha channel
    if img.shape[2] == 4:
        # Step 2: Split the image into its channels (B, G, R, A)
        b, g, r, a = cv2.split(img)
        
        # Step 3: Create a mask where the alpha channel is less than 255 (transparent pixels)
        mask = a < 255
        
        # Step 4: Replace transparent areas with white (255, 255, 255) in the B, G, R channels
        b[mask] = 255
        g[mask] = 255
        r[mask] = 255
        
        # Step 5: Merge the B, G, R channels back (drop the alpha channel)
        img_rgb = cv2.merge([b, g, r])
        print(f"Image with transparent areas turned white.")
        return img_rgb
        
    else:
        print("The image does not have an alpha channel!")
        return img
        


# Function to convert grayscale image to ASCII art
def gs_image_to_ascii(img, decode_scheme):
    
    # Step 1: Get the image dimensions
    height, width = img.shape
    
    # Step 2: Initialize an empty string for ASCII art
    ascii_art_array = np.empty((height, width), dtype='<U1')
    
    # Step 3: Loop through each pixel of the grayscale image
    for i in range(height):
        for j in range(width):
            gs_value = str(img[i, j])  # Get the grayscale value of the pixel
            
            # Step 4: Get the corresponding character list from the decode scheme
            if gs_value in decode_scheme:
                char_list = decode_scheme[gs_value]
                # Randomly select a character from the list
                selected_char = random.choice(char_list)
            else:
                selected_char = " "  # Default to space if gs_value is not in decode_scheme
            
            #print(f"GS at ({i}, {j}) is {gs_value} and selected {selected_char}")
            # Add the selected character to the ASCII art array
            ascii_art_array[i, j] = selected_char
    
    return ascii_art_array


def encode_file_to_base64(file_path):
    with open(file_path, "rb") as file:
        encoded_content = base64.b64encode(file.read()).decode('utf-8')
    return encoded_content

def ascii_art_to_svg(ascii_art, font_family="Courier New", font_size=16, output_path='ascii_art.svg'):
    '''
    Convert ASCII art to an SVG file.
    
    ascii_art: NumPy array or list of lists with ASCII characters.
    font_family: CSS font-family for the ASCII art (default: Courier New).
    font_size: Size of the font for each character.
    output_path: Path where the SVG file will be saved.
    '''
    rows, cols = ascii_art.shape
    
    # Calculate width and height of the SVG canvas
    svg_width = cols * font_size * 0.6  # Approximate width per character
    svg_height = rows * font_size * 0.9 # Approximate height per row
    
    # Start building the SVG content
    if font_family == "Courier New":
        svg_content = f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}">
            <style>
                text {{
                    font-family: '{font_family}', monospace;
                    font-size: {font_size}px;
                }}
            </style>
        """
    else:
        font_code = encode_file_to_base64(f"{font_family}.ttf")
        svg_content = f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}">
            <style>
                text {{
                    font-family: '{font_family}', monospace;
                    font-size: {font_size}px;
                    src: url('https://blogs.gwu.edu/qluo/files/2024/09/{font_family}.woff') format('woff');
                }}
            </style>
        """
    
    # Add each row of ASCII characters as a single <text> element
    for i in range(rows):
        y = (i + 1) * font_size * 0.9  # Estimate line height for each row
        row_text = ''.join(html.escape(char) for char in ascii_art[i, :])  # Combine characters in a row
        svg_content += f'<text x="0" y="{y}"  xml:space="preserve">{row_text}</text>\n'  # Render whole row at once
    
    # Close the SVG tag
    svg_content += "</svg>"
    
    # Write the SVG content to the file
    with open(output_path, 'w') as svg_file:
        svg_file.write(svg_content)
    
    print(f"ASCII art saved as SVG to {output_path}")

def ascii_art_to_svg(ascii_art, font_family="Courier New", font_size=16, output_path='ascii_art.svg'):
    '''
    Convert ASCII art to an SVG file.
    
    ascii_art: NumPy array or list of lists with ASCII characters.
    font_family: CSS font-family for the ASCII art (default: Courier New).
    font_size: Size of the font for each character.
    output_path: Path where the SVG file will be saved.
    '''
    rows, cols = ascii_art.shape
    
    # Calculate width and height of the SVG canvas
    svg_width = cols * font_size * 0.6  # Approximate width per character
    svg_height = rows * font_size * 0.9 # Approximate height per character (line height)
    
    # Start building the SVG content
    if font_family=="Courier New":
        svg_content = f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}">
            <style>
                text {{
                    font-family: '{font_family}', monospace;
                    font-size: {font_size}px;
                }}
            </style>
        """
    else:
        font_code=encode_file_to_base64(f"{font_family}.ttf")
        svg_content = f"""
        <svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}">
            <style>
                text {{
                    font-family: '{font_family}', monospace;
                    font-size: {font_size}px;
                    src: url("data:application/font-woff;charset=utf-8;base64,{font_code}")
                }}
            </style>
        """
        
    # Add each ASCII character to the SVG with appropriate coordinates
    for i in range(rows):
        for j in range(cols):
            x = j * font_size * 0.6  # Estimate character width
            y = (i + 1) * font_size * 0.9  # Estimate line height
            char = html.escape(ascii_art[i, j])  
            svg_content += f'<text x="{x}" y="{y}">{char}</text>\n'
    
    # Close the SVG tag
    svg_content += "</svg>"
    
    # Write the SVG content to the file
    with open(output_path, 'w') as svg_file:
        svg_file.write(svg_content)
    
    print(f"ASCII art saved as SVG to {output_path}")



def process_images_in_folder(input_folder, output_folder, gs_decoder, font='Courier New', font_size=10):
    random.seed(1234)
    # Step 1: Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Step 2: Iterate over all files in the input folder
    for fname in os.listdir(input_folder):
        # Step 3: Check if the file is an image (you can adjust the extension list as needed)
        if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif','.webp')):
            # Full path to the input image
            file_path = os.path.join(input_folder, fname)
            
            # Step 4: Load and process the image
            print(f"Processing file: {file_path}")
            cv_img = make_transparent_white(file_path)
            
            # Resize the input image to grayscale
            gs_img = resize_input(cv_img)
            
            # Convert the grayscale image to ASCII
            ascii_img = gs_image_to_ascii(gs_img, gs_decoder)
            
            # Output path for the ASCII art SVG file
            output_svg_path = os.path.join(output_folder, f'{font}-{os.path.splitext(fname)[0]}.svg')
            
            # Step 5: Convert the ASCII array to SVG and save it
            ascii_art_to_svg(ascii_img, font_family=font, font_size=font_size, output_path=output_svg_path)
            
            print(f"Saved ASCII art to {output_svg_path}")



# Decoder
with open('brightness_decoder.json', 'r') as file:
        gs_decoder = json.load(file)

input_folder = "./original/"  # Folder with input images
output_folder = "./ascii_art/"  # Folde

process_images_in_folder(input_folder, output_folder, gs_decoder, font='Courier New', font_size=10)
process_images_in_folder(input_folder, output_folder, gs_decoder, font='Anonymous Pro', font_size=10)
