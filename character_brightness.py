from PIL import Image, ImageDraw, ImageFont
import numpy as np
import json
import math 

# Function to render a character and calculate its grayscale/brightness
def calculate_brightness(char, font_path='Anonymous Pro.ttf', font_size=16):
    # Create a blank image with white background
    img_size = (math.ceil(font_size*0.6), math.ceil(font_size*1.2))  # Image size (width, height)
    img = Image.new('L', img_size, color=255)  # 'L' mode for grayscale
    draw = ImageDraw.Draw(img)
    
    # Load the font and draw the character on the image
    font = ImageFont.truetype(font_path, font_size)
    draw.text((0, 0), char, font=font, fill=0)  # Fill with black text
    
    img.save(f"./character_img/{ord(char)}.png")   
    
    # Convert image to numpy array and calculate average brightness
    img_array = np.array(img)
    brightness = np.mean(img_array)  # Average pixel value
    
    return brightness

# Function to generat brightness dictionary
def generate_brightness(font_path='Anonymous Pro.ttf'):    
    # Calculate and print the brightness for a range of ASCII characters
    brightness_dict={}
    brightness_list=[]
    for ascii_code in range(32, 127):  # Printable ASCII characters
        char = chr(ascii_code)
        brightness = calculate_brightness(char, font_size=30)
        brightness_dict[char]=brightness
        brightness_list.append(brightness)
    
    bmin=np.min(brightness_list)
    bmax=np.max(brightness_list)
    norm_brightness_list=[]
    
    for ascii_code in range(32, 127):
        char = chr(ascii_code)
        brightness_dict[char]=(brightness_dict[char]-bmin)/(bmax-bmin)
        norm_brightness_list.append(brightness_dict[char])
        print(f"Character: {char}, ASCII Code: {ascii_code}, Brightness: {brightness_dict[char]}")
    
    # Conver to Gray Scale from 0 to 255
    new_list=[(idx+32, int(gs*255)) for idx, gs in enumerate(norm_brightness_list)]
    
    # Select only the first instance of each grayscale value
    selected = []
    seen_grayscale = set()  # A set to track seen grayscale values
    
    for ascii_code, gs_value in new_list:
        if gs_value not in seen_grayscale:  # If it's the first occurrence of this grayscale value
            selected.append((ascii_code, gs_value))
            seen_grayscale.add(gs_value)  # Mark this grayscale value as seen
    
    # Prepare Decoding Scheme
    brightness_decode = {}
    # Sort the selected list by grayscale value for easier lookup
    selected_sorted = sorted(selected, key=lambda x: x[1])  # Sort by grayscale value (gs)
    
    # Add Values to Decoding Scheme
    for gs in range(256):
        if gs in brightness_decode.keys():
            continue
        
        # Exact Brightness Match
        match_flag = False
        for ascii_code, gs1 in selected_sorted:
            if gs1 == gs:
                match_flag = True
                brightness_decode[gs] = [chr(ascii_code)]  # Exact match found
                break
        
        # Interpolation
        if not match_flag:
            # Find the two closest grayscale values in selected_sorted
            lower = None
            upper = None
            for i in range(len(selected_sorted)):
                if selected_sorted[i][1] < gs:
                    lower = selected_sorted[i]  # Store the lower grayscale value
                if selected_sorted[i][1] > gs:
                    upper = selected_sorted[i]  # Store the upper grayscale value
                    break
            
            if lower and upper:
                # Linear interpolation based on distances
                lower_ascii, lower_gs = lower
                upper_ascii, upper_gs = upper
                
                lower_weight = upper_gs - gs
                upper_weight = gs - lower_gs
                
                brightness_decode[gs] = [chr(lower_ascii)] * lower_weight + [chr(upper_ascii)] * upper_weight
        
    with open('brightness_data.json', 'w') as json_file:
        json.dump(brightness_dict, json_file, indent=4)
    
    with open('brightness_decoder.json', 'w') as json_file:
        json.dump(brightness_decode, json_file, indent=4)


if __name__=='__main__':
    generate_brightness('cour.ttf')
    generate_brightness('Anonymous Pro.ttf')