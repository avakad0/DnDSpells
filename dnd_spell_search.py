import requests
import json
import customtkinter as ctk

# Function to fetch spell data from the D&D 5e API
def fetch_spells(spell_name):
    url = f"http://www.dnd5eapi.co/api/spells?name={spell_name}"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data
    else:
        print(f"Failed to get data: {response.status_code}")
        return None
    
spell_details = {}

# Function to search for a spell using the GUI
def search_spell():
    global spell_details
    spell_name = spell_name_entry.get()
    spell_data = fetch_spells(spell_name)  
    print(spell_data)  # Add the print statement here
    # Clear previous search results
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    
    spell_data = fetch_spells(spell_name)
    
    if spell_data and 'results' in spell_data:
        for spell in spell_data['results']:
            label = ctk.CTkLabel(scrollable_frame, text=spell['name'], cursor="hand2")
            label.pack(pady=5)
            label.bind("<Button-1>", lambda e, s=spell: display_spell_details(s))
            spell_details[spell['name']] = spell
    else:
        label = ctk.CTkLabel(scrollable_frame, text="No spell found.")
        label.pack(pady=5)

def display_spell_details(spell):
    # Clear existing details
    for widget in details_frame.winfo_children():
        widget.destroy()

    # Spell name
    name_label = ctk.CTkLabel(details_frame, text=spell['name'], font=("Arial", 18))
    name_label.pack(pady=10)

    # Spell description
    description = spell.get('desc', ["Description not available."])[0]  # Default to "Description not available."
    desc_label = ctk.CTkLabel(details_frame, text=spell['desc'][0])  # Displaying the first line of description
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

    # Schedule the new search
    search_after_id = spell_name_entry.after(300, search_spell)

# customTkinter GUI setup
app = ctk.CTk()
app.title("D&D 5e Spell Search")
app.geometry("600x400")
app.resizable(True, True)

frame = ctk.CTkFrame(app)
frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)

spell_name_entry = ctk.CTkEntry(frame, width=400)
spell_name_entry.grid(row=0, column=0, sticky="w", pady=20)
spell_name_entry.bind("<Return>", on_enter_key)  # Bind Enter key
spell_name_entry.bind("<KeyRelease>", lambda event: delayed_search())  # Bind to KeyRelease

search_button = ctk.CTkButton(frame, text="Search", command=search_spell)
search_button.grid(row=0, column=1, pady=20)

# Using CTkScrollableFrame for results
scrollable_frame = ctk.CTkScrollableFrame(frame)
scrollable_frame.grid(row=1, columnspan=2, pady=20, sticky="w")

# Create a frame for displaying spell details
details_frame = ctk.CTkFrame(app)
details_frame.place(relx=0.6, rely=0.5, anchor="center", relwidth=0.35, relheight=0.5)

app.mainloop()
