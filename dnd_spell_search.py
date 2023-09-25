import sys
sys.path.append("/CTKScrollableDropdown/")


import requests
import json
from tkinter import *
import tkinter as tk
import customtkinter as ctk
from CTkScrollableDropdown import *
from cachetools import TTLCache
from PIL import Image, ImageTk



#
# PNG Images
#
#

def get_dice_icon(dice_type, size=(40, 40)):
    image = Image.open(f"img/{dice_type}.png")
    image_resized = image.resize(size)
    return ImageTk.PhotoImage(image_resized)

#
# GUI SET UP
#
#

app = ctk.CTk()
app.title("D&D 5e Spell Search")
app.geometry("1000x800")

cache = TTLCache(maxsize=100, ttl=3600)

BASE_URL = "http://www.dnd5eapi.co"

search_after_id = None

#
# API-Related Functions
#
#
#

def fetch_spells(spell_name=None, url=None):
    try:
        # Check if the response is in the cache
        cache_key = url if url else f"{BASE_URL}/api/spells?name={spell_name}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return cached_response

        target_url = BASE_URL + url if url else f"{BASE_URL}/api/spells?name={spell_name}"
        response = requests.get(target_url)

        print("Request URL:", target_url)  # Print the request URL for debugging

        response.raise_for_status()  # Raise an exception for 4xx and 5xx HTTP status codes

        if response.status_code == 200:
            data = response.json()

            # Cache the response for future use
            cache[cache_key] = data

            return data
        else:
            print(f"Failed to get data: {response.status_code}")
            print("Response Content:", response.content)  # Print the response content for debugging
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_spell_names():
    """
    Fetch all spells names to populate the dropdown.
    """
    response = requests.get(f"{BASE_URL}/api/spells")
    if response.status_code == 200:
        data = response.json()
        if "results" in data:
            # Return a list of dictionaries containing name and URL
            return [{"name": spell['name'], "url": spell['url']} for spell in data['results']]
    return []



#
# Live search function
#
#

spell_data = {spell['name']: spell['url'] for spell in get_spell_names()}

entry = ctk.CTkEntry (app, width=400, placeholder_text="Search")
entry.pack(padx=10, pady=10)

def on_spell_selected(spell_name):
    spell_url = spell_data.get(spell_name)
    if spell_url:
        entry.delete(0, 'end')
        entry.insert(0, spell_name)
        display_spell_details({"name": spell_name, "url": spell_url}, details_frame)

CTkScrollableDropdown(entry, values=list(spell_data.keys()), command=on_spell_selected, autocomplete=True)

def delayed_search(event=None):
    """
    Delay search results
    """
    global search_after_id

    # If there's an existing scheduled search, cancel it
    if search_after_id:
        app.after_cancel(search_after_id)

    # Schedule the update_dropdown function after a short delay (e.g., 500ms)
    search_after_id = app.after(500, update_dropdown)

    def update_dropdown():
        current_input = entry.get().lower()
        updated_values = [spell for spell in get_spell_names() if current_input in spell.lower()]

    entry.bind("<KeyRelease>", delayed_search)

#
# Display details of the selected spell
#
#

def display_spell_details(spell, details_frame):
    dice_type = None

    # Fetch complete spell details
    full_spell_data = fetch_spells(url=spell['url'])

    # Clear existing details
    for widget in details_frame.winfo_children():
        widget.destroy()

    # Spell name
    name_label = ctk.CTkLabel(details_frame, text=spell['name'], font=("Nodesto Caps Condensed", 32))
    name_label.pack(pady=0)

    # Separator
    separator_width = 200
    separator = Frame(details_frame, width=separator_width, height=2, bg="grey")
    separator.pack(padx=0, pady=0)

    # Classes
    classes_list = full_spell_data.get('classes', [])
    class_names = ', '.join([cls['name'] for cls in classes_list])
    classes_label = ctk.CTkLabel(details_frame, font=("Bookinsanity", 12, "italic"), text=f"Classes: {class_names}")
    classes_label.pack(pady=0, ipady=0)

    # Level and School of magic
    level = full_spell_data.get('level', 0)
    
    # If level is 0, it's a cantrip
    if level == 0:
        level_display = ""
    else:
        level_display = f"Level {level}"

    school = full_spell_data.get('school', {}).get('name', '')
    school_label = ctk.CTkLabel(details_frame, text=f"{level_display} {school} Spell")
    school_label.pack(pady=5)

    # Damage type color mapping // CHANGE COLORS
    damage_color_map = {
        "acid": "#A6E22E",  # Bright Green
        "bludgeoning": "#FD971F",  # Orange
        "cold": "#66D9EF",  # Cyan
        "fire": "#F92672",  # Red
        "force": "#AE81FF",  # Purple
        "lightning": "#FD971F",  # Orange
        "necrotic": "#676E79",  # Dark Gray
        "piercing": "#FFE792",  # Yellow
        "poison": "#529B2F",  # Dark Green
        "psychic": "#AE81FF",  # Purple
        "radiant": "#E6DB74",  # Light Yellow
        "slashing": "#FFE792",  # Yellow
        "thunder": "#FD971F"  # Orange
    }

    # Damage calculations
    def calculate_damage_range(damage_formula):
        try:
            num_dice, dice_type = map(int, damage_formula.split('d'))
            return num_dice, num_dice * dice_type, f"d{dice_type}"
        except ValueError:
            return None, None, None

    damage_data = full_spell_data.get('damage', {})
    damage_at_slot_level = damage_data.get('damage_at_slot_level', {})
    damage_at_character_level = damage_data.get('damage_at_character_level', {})
    damage_type = damage_data.get('damage_type', {}).get('name', "")
    
    damage_formula = None

    # Check for damage at character level
    if damage_at_character_level:
        damage_formula = damage_at_character_level.get("1")
        if not damage_formula:
            damage_formula = list(damage_at_character_level.values())[0]  # Get first available value if "1" is missing

    elif damage_at_slot_level:  # If not character level based, then slot based
        lowest_slot_level = min(map(int, damage_at_slot_level.keys())) if damage_at_slot_level else None
        if lowest_slot_level:
            damage_formula = damage_at_slot_level[str(lowest_slot_level)]

    # Min-Max Damage formula display
    if damage_formula:
        min_damage, max_damage, dice_type = calculate_damage_range(damage_formula)
        damage_text_min_max = ctk.CTkLabel(details_frame, text=f"{min_damage} - {max_damage} Damage", font=("Bookinsanity", 14))
        damage_text_min_max.pack(pady=5)

    # Only proceed if dice_type has been assigned
    if dice_type:
        dice_icon = get_dice_icon(dice_type)
        damage_text_formula = f" {damage_formula} {damage_type}"
        damage_color = damage_color_map.get(damage_type, "#FFFFFF")
        print("Damage Color:", damage_color)
        formula_label = ctk.CTkLabel(details_frame, 
                                 text=damage_text_formula, 
                                 text_color=(damage_color),
                                 image=dice_icon, 
                                 compound=LEFT)
        formula_label.image = dice_icon  # Keep a reference to the image
        formula_label.pack()


    # Spell description
    description = "\n\n".join(full_spell_data.get('desc', ["Description not available."]))
    desc_label = ctk.CTkLabel(details_frame, text=description, font=("Bookinsanity", 14), wraplength=400)
    desc_label.pack(pady=5)

    # Higher level description (if available)
    higher_level_desc = full_spell_data.get('higher_level')
    if higher_level_desc:
        higher_description = "\n\n".join(higher_level_desc)
        higher_level_label = ctk.CTkLabel(details_frame, text=higher_description, font=("Bookinsanity", 14), wraplength=400)
        higher_level_label.pack(pady=5)

    # Area of Effect
    area_of_effect_type = full_spell_data.get('area_of_effect', {}).get('type')
    area_of_effect_size = full_spell_data.get('area_of_effect', {}).get('size')
    if area_of_effect_type and area_of_effect_size:
        area_of_effect_text = f"{area_of_effect_type} ({area_of_effect_size})"
    elif area_of_effect_type:
        area_of_effect_text = area_of_effect_type
    else:
        area_of_effect_text = ""

    # Extracting the DC type data
    dc_data = full_spell_data.get('dc', {})
    dc_type = dc_data.get('dc_type', {}).get('name', '')

    # Range, DC Save, Area of Effect, and Concentration
    range_text = f"Range: {full_spell_data.get('range', 'N/A')}"
    concentration_text = f"Concentration: {'Yes' if full_spell_data.get('concentration', False) else 'No'}"
    details_text = f"{range_text}  |  Area: {area_of_effect_text}  |  {dc_type}  |  {concentration_text}"
    details_label = ctk.CTkLabel(details_frame, text=details_text, wraplength=450)
    details_label.pack(pady=5)

    # Casting Time and Spell Slot Level
    casting_time = full_spell_data.get('casting_time', '')
    # Update the text depending on the spell level
    if level == 0:
        level_display = "Cantrip"
    else:
        level_display = f"Level {level} Spell Slot"
    casting_time_label = ctk.CTkLabel(details_frame, text=f"{casting_time} | {level_display}")
    casting_time_label.pack(pady=5)

    # Components and Materials
    components_text = f"Components: {''.join(full_spell_data.get('components', []))}"
    material_text = full_spell_data.get('material', '')
    comp_material_text = f"{components_text}  |  {material_text}"
    comp_material_label = ctk.CTkLabel(details_frame, text=comp_material_text, wraplength=450)
    comp_material_label.pack(pady=5)


# GUI Configuration
#
#
#

# Details frame
details_frame = ctk.CTkScrollableFrame(app)
details_frame.pack(side = LEFT, fill = BOTH, expand= TRUE, padx=20, pady=20)


app.mainloop()