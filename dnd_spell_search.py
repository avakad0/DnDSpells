import requests
import json
import customtkinter as ctk

BASE_URL = "http://www.dnd5eapi.co"

# Function to fetch spell data from the D&D 5e API
def fetch_spells(spell_name=None, url=None):
    if url:
        # Prepend the BASE_URL to the provided relative URL
        response = requests.get(BASE_URL + url)
    else:
        response = requests.get(f"{BASE_URL}/api/spells?name={spell_name}")

    if response.status_code == 200:
        data = json.loads(response.text)
        return data
    else:
        print(f"Failed to get data: {response.status_code}")
        return None


    
spell_details = {}

# Function to search for a spells using the GUI
def search_spell():
    global spell_details

    spell_name = spell_name_entry.get() 
    spell_data = fetch_spells(spell_name)

    # Clear existing spell names from the scrollable frame
    for widget in scrollable_frame.winfo_children():
        widget.destroy()

    if spell_data and 'results' in spell_data:
        for spell in spell_data['results']:
            label = ctk.CTkLabel(scrollable_frame, text=spell['name'])
            label.bind("<Button-1>", lambda e, s=spell: display_spell_details(s))
            label.pack(fill="x", pady=2)
    else:
        label = ctk.CTkLabel(scrollable_frame, text="No spell found.")
        label.pack(pady=10)

def display_spell_details(spell):
    # Fetch full details of the spell
    full_spell_data = fetch_spells(url=spell['url'])
    # PRINT
    print(full_spell_data)  

    # Clear existing details
    for widget in details_frame.winfo_children():
        widget.destroy()

    # Spell name
    name_label = ctk.CTkLabel(details_frame, text=spell['name'], font=("Arial", 18))
    name_label.pack(pady=10)

    # Casting Time and Level/Cantrip
    casting_time = full_spell_data.get('casting_time', 'Unknown Casting Time')
    level = full_spell_data.get('level', 0)
    level_display = "Cantrip" if level == 0 else f"Level {level}"
    casting_level_label = ctk.CTkLabel(details_frame, text=f"{level_display} | Casting Time: {casting_time}")
    casting_level_label.pack(pady=10)

    # Spell damage (if available) and area of effect
    damage = full_spell_data.get('damage', {}).get('damage_type', {}).get('name', 'No Damage Info')

    # Extract the area of effect type and size
    area_of_effect_type = full_spell_data.get('area_of_effect', {}).get('type', 'Unknown Area')
    area_of_effect_size = full_spell_data.get('area_of_effect', {}).get('size', '')

    # Combine type and size for display
    area_of_effect_display = f"{area_of_effect_type} ({area_of_effect_size})" if area_of_effect_size else area_of_effect_type

    # Create the label
    damage_area_label = ctk.CTkLabel(details_frame, text=f"Damage: {damage} | Area of Effect: {area_of_effect_display}")
    damage_area_label.pack(pady=10)



    # School of magic
    school = full_spell_data.get('school', {}).get('name', 'Unknown School')
    school_label = ctk.CTkLabel(details_frame, text=f"School: {school}")
    school_label.pack(pady=10)

    # Displaying the range, components, material, duration, and concentration
    range_text = f"Range: {full_spell_data.get('range', 'N/A')}"
    components_text = f"Components: {''.join(full_spell_data.get('components', []))}"
    material_text = full_spell_data.get('material', '')
    duration_text = f"Duration: {full_spell_data.get('duration', 'N/A')}"
    concentration_text = f"Concentration: {'Yes' if full_spell_data.get('concentration', 'no') == 'yes' else 'No'}"
    details_text = f"{range_text}  |  {components_text}  |  {material_text}  |  {duration_text}  |  {concentration_text}"
    details_label = ctk.CTkLabel(details_frame, text=details_text, wraplength=450)  # Adjust 450 to your frame's width
    details_label.pack(pady=10)

    # Spell description
    description = "\n\n".join(full_spell_data.get('desc', ["Description not available."]))

    # Higher level description (if available)
    higher_level_desc = full_spell_data.get('higher_level')
    if higher_level_desc:
        description += "\n\n" + "\n\n".join(higher_level_desc)

    desc_label = ctk.CTkLabel(details_frame, text=full_spell_data.get('desc', ["Description not available."])[0])
    desc_label = ctk.CTkLabel(details_frame, text=description, wraplength=400)

    desc_label.pack(pady=10)

# Function to handle Enter key press
def on_enter_key(event):
    search_spell()

search_after_id = None

def delayed_search():
    global search_after_id

    # If there's an existing scheduled search, cancel it
    if search_after_id:
        spell_name_entry.after_cancel(search_after_id)

    # Schedule the new search .after(ms)
    search_after_id = spell_name_entry.after(200, search_spell)


# customTkinter GUI setup
app = ctk.CTk()
app.title("D&D 5e Spell Search")
app.geometry("1200x800")
app.resizable(True, True)

frame = ctk.CTkFrame(app)
frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)

spell_name_entry = ctk.CTkEntry(frame)
spell_name_entry.grid(row=0, column=0, sticky="nsew")
spell_name_entry.bind("<Return>", on_enter_key)
spell_name_entry.bind("<KeyRelease>", lambda event: delayed_search())

search_button = ctk.CTkButton(frame, text="Search", command=search_spell)
search_button.grid(row=0, column=1, padx=(10, 50))

scrollable_frame = ctk.CTkScrollableFrame(frame)
scrollable_frame.grid(row=1, columnspan=2, pady=20, sticky="nsew")

# Adjust the relative width and height
details_frame = ctk.CTkScrollableFrame(app)
details_frame.place(relx=0.6, rely=0.5, anchor="center", relwidth=0.4, relheight=0.6)

app.mainloop()