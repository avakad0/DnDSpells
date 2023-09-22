import requests
import json
import tkinter as tk
from tkinter import ttk

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

# Function to search for a spell using the GUI
def search_spell():
    spell_name = spell_name_entry.get()
    spell_listbox.delete(0, tk.END)  # Clear previous search results
    spell_data = fetch_spells(spell_name)
    
    if spell_data and 'results' in spell_data:
        for spell in spell_data['results']:
            spell_listbox.insert(tk.END, spell['name'])
    else:
        spell_listbox.insert(tk.END, "No spell found.")

# Tkinter GUI setup
app = tk.Tk()
app.title("D&D 5e Spell Search")

frame = ttk.Frame(app, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

spell_name_entry = ttk.Entry(frame, width=30)
spell_name_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))

search_button = ttk.Button(frame, text="Search", command=search_spell)
search_button.grid(row=0, column=1)

spell_listbox = tk.Listbox(frame, width=50, height=15)
spell_listbox.grid(row=1, columnspan=2, sticky=(tk.W, tk.E))

frame.columnconfigure(0, weight=1)
frame.rowconfigure(1, weight=1)

app.mainloop()
