import http.client
import requests
import json
from tkinter import * 
from tkinter import messagebox
import customtkinter
from tkinter import ttk
import ttkbootstrap as tb
from datetime import datetime
import os
import os.path
import base64 

werb = False

uzd_dictionary = {}
proj_dictionary = {}
user_list = {}

conn = "https://demo.redmineup.com"
dir = ".RedmTime/bin"
file = "authToken.txt"
user = os.getlogin()
folder_path = f"C:/Users/{user}/{dir}"
file_path = f"{folder_path}/{file}"

def read_token(file_path):
    token = open(file_path).readlines()
    token = token[0]
    return token

def issue_selection_count():
    selected_items = my_tree.selection() # curselection()
    return len(selected_items)

def update_selection_count():
    #selected_items = my_tree.selection() # curselection()
    count = issue_selection_count() #len(selected_items)
    if count == 1:
        galotne = 's'
    else:
        galotne = 'i'
    selection_count_label.config(text=f"Izvēlēt{galotne}: {count} uzdevum{galotne}")

uzd_veidi = {9: 'Uzdevumu izpilde', 12: "Sapulce", 23: "Mācības", 15: "1:1 Saruna", 26: "Virsstundas", 81: "Izstrāde", 18: "Testēšana", 82: "Konsultācijas"}
def field_validation():
    # Get the selected value.
    search_key = combo.get()
    combo_res = [key for key, val in uzd_veidi.items() if search_key in val]
    note_res = note_entry.get()
    hour_res = hour_entry.get()
    date_res = date_entry.entry.get()
    if len(combo_res) > 1:
        e1 = 1
        e1_text = "Lūdzu izvēlaties aktivitātes veidu"
    else:
        e1 = 0
        e1_text = ""
    if len(note_res) == 0:
        e2 = 1
        e2_text  = "Lūdzu ievadiet komentāru"
    else:
        e2 = 0
        e2_text = ""
    if len(hour_res) > 0 and hour_res != "0":
        try:
            hour_res = float(hour_res)
            e3 = 0
            e3_text = ""
        except ValueError:
            try:
                hour_res = hour_res.replace(",",".")
                hour_res = float(hour_res)
                e3 = 0
                e3_text = ""
            except ValueError:
                e3 = 1
                e3_text = "Ievadītās stundas nav skaitlis"
    else:
        e3 = 1
        e3_text = "Ievadiet nostrādāto stundu skaitu, kas ir lielāks par 0"
    try:
        date_format = '%d.%m.%Y'
        date_res = datetime.strptime(date_res, date_format).strftime("%Y-%m-%d")
        e4 = 0
        e4_text = ""
    except ValueError:
        e4 = 1
        e4_text = "Nepareizs datuma formāts!"
    if (e1+e2+e3+e4)>0:
        messagebox.showinfo(title=None, message=("\n".join(["- " + e1_text, "- " + e2_text, "- " + e3_text, "- " + e4_text])))
    else:
        selection_validation()

def selection_validation():
    counter = 0
    if int(issue_selection_count()) == 0:
        messagebox.showinfo(title=None, message=("Izvēlaties vismaz vienu uzdevumu"))
    else:
        for item in my_tree.selection():
                item_values = my_tree.item(item, "values")
                if len(str(item_values[1])) == 0:
                    counter += 1
        if counter > 0:
            messagebox.showinfo(title=None, message=(f"Jūs esat izvēlējies {counter} projektus, bet atļauti tikai uzdevumui"))
        else:
            register_hour_in_Redmine()

def send_post_request(conn, url, payload, headers):
    conn.request("POST", url, payload, headers)
    response = conn.getresponse()
    status_code = response.status
    response.read()  # Read the response to ensure the connection can be reused
    return status_code

def create_payload(Debug = werb):
    issues_post = []
    selected_items = my_tree.selection()
    user_hour_for = combo4.get()
    user_hour_for = user_list[user_hour_for]
    comment = note_entry.get().encode('utf-8')
    comment = comment.decode('utf-8')
    # print(f"Izvēlētie uzd: {selected_items}")
    for item in selected_items:
        item_values = my_tree.item(item, "values")
        hour_payload = ('<?xml version="1.0" encoding="UTF-8"?>'
                            '<time_entry>'
                            '<project_id>' + str(item_values[0]) + '</project_id>'
                            '<issue_id>' + str(item_values[1]) + '</issue_id>'
                            '<user_id>' + str(user_hour_for) + '</user_id>'
                            '<activity_id>' + str([key for key, val in uzd_veidi.items() if combo.get() in val][0]) + '</activity_id>'
                            '<hours>' + str(round(float(hour_entry.get())/int(issue_selection_count()),2)) + '</hours>'
                            '<comments>' + str(comment)  + '</comments>'
                            '<spent_on>' + str(datetime.strptime(date_entry.entry.get(), '%d.%m.%Y').strftime("%Y-%m-%d")) + '</spent_on>'
                        '</time_entry>')
        issues_post.append(hour_payload) 
    if Debug == True:
        print(f"saformēti uzd: {issues_post}")
    return issues_post


def register_hour_in_Redmine(Debug = werb):
    reg_counter = 0
    issues_post = create_payload()
    if Debug == True:
        print(f"Pirms sūtīšanas dati: {issues_post}")
    token_post = read_token(file_path)
    headers_post = {'Content-Type': 'application/xml', 'Authorization': 'Basic ' + token_post}
    url = conn + "/time_entries.xml"
    for data in issues_post:
        response = requests.post(url=url, headers=headers_post, data=data.encode('utf-8'), verify=False)
        if Debug == True:
            print(f"Sūtījuma statusa kods: {response.status_code}") 
        if response.status_code == 201:
            reg_counter += 1
    messagebox.showinfo(title=None, message=(f"Redmine reģistrētas nostrādātās stundas {reg_counter} uzdevumiem"))

def get_redmine_data(url):
    redmine_url = conn + url
    response = requests.get(url=redmine_url, headers=headers, verify=False)
    return response.json()

isExist_folder = os.path.exists(folder_path)
if not isExist_folder:
   # Create a new directory because it does not exist
   os.makedirs(folder_path)
#    print("The new directory is created!")
  
if not os.path.exists(file_path):
    root = customtkinter.CTk()
    root.withdraw()
    input_dialog = customtkinter.CTkInputDialog(text=f"Ievadiet Redmine Token \n \n Šis Token tiks saglabāts šeit: {file_path}", title="Autorizācijas forma")
    input_value = input_dialog.get_input()
    root.destroy()
    input_value = input_value.encode("ascii")
    base64_bytes = base64.b64encode(input_value)
    base64_string = base64_bytes.decode("ascii")
    with open(file_path, 'w') as file: 
        file.write(base64_string)
    token = base64_string
else:
    token = read_token(file_path)


payload = ''
headers = {'Content-Type': 'application/xml', 'Authorization': 'Basic ' + token}

# Paņemam projekta datus
proj_data = get_redmine_data("/projects.json?limit=1000")
for element in proj_data['projects']:
    proj_dictionary.update({element['id']: element['name']})

# Paņemam aktuālo lietotāju
u_data = get_redmine_data("/users/current.json")
u_ID = u_data['user']['id']
u_name = u_data['user']['firstname'] + ' ' + u_data['user']['lastname'] 

# Paņemam visus lietotājus
r_data = get_redmine_data("/users.json?limit=100000")
for element in r_data['users']:
    usr_name = element['firstname'] + ' ' + element['lastname']
    user_list[usr_name] = element['id']

for key, value in proj_dictionary.items():
    user_issues_url = conn + f"/issues.json?project_id={key}&limit=200"
    try:
        res_issue = requests.get(url=user_issues_url, headers=headers, verify=False)
        res_issue.raise_for_status()  # Iegūstam Error, ja neveiksmīgs pieprasījums
        data_issue = res_issue.json()
        
        for element in data_issue['issues']:
            uzd_dictionary.update({element['id']: [element['subject'], key]})
    
    except requests.exceptions.HTTPError as http_err:
        if res_issue.status_code == 403:
            print(f"403 Forbidden error for project ID {key}. Possible causes: invalid credentials, IP restriction, insufficient permissions.")
        else:
            print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")




window = Tk() 
window.title('Multiple selection') 

# Create left and right frames
left_frame  =  Frame(window,  width=80,  height=400,  bg='grey')
left_frame.pack(side='left',  fill='both',  padx=10,  pady=5,  expand=True)

right_frame  =  Frame(window,  width=200,  height=400,  bg='grey')
right_frame.pack(side='right',  fill='both',  padx=10,  pady=5,  expand=True)

# Kreisās puses projektu saraksts


my_tree = ttk.Treeview(left_frame,  selectmode='extended')


yscrollbar = ttk.Scrollbar(left_frame, command=my_tree.yview) 
yscrollbar.pack(side = RIGHT, fill = Y) 

my_tree['columns'] = ("pID", "uID", "pNosaukums")

my_tree.column("#0", width=20, minwidth=20)
my_tree.column("pID", anchor=CENTER, width=50)
my_tree.column("uID", anchor=CENTER, width=50)
my_tree.column("pNosaukums", anchor=W, width=400)

my_tree.heading("#0", text="", anchor=W)
my_tree.heading("pID", text="ID", anchor=CENTER)
my_tree.heading("uID", text="Uzd.", anchor=CENTER)
my_tree.heading("pNosaukums", text="Nosaukums", anchor=CENTER)

for key, value in proj_dictionary.items():
    my_tree.insert(parent='', index='end', iid=key, text="", values=(key, "", value))

for key, value in uzd_dictionary.items():
    my_tree.insert(parent='', index='end', iid=key, text="", values=(value[1], key, value[0]))
    my_tree.move(key, value[1], key)

my_tree.pack(padx = 0, pady = 0, 
          expand = YES, fill = "both")

# # Labās puses lauku izkārtojums un saturs
# Label to display the count of selected projects
selection_count_label = Label(right_frame, text="Izvēlēti: 0 uzdevumu", font=("Times New Roman", 12), width=50)
selection_count_label.pack(pady=10)

# Bind the selection event to update the count
my_tree.bind('<<TreeviewSelect>>', lambda event: update_selection_count())

frame4 = Frame(right_frame, width=200)
frame4.pack(side=TOP, anchor='w')

Label_combo4 = Label(frame4, text="Lietotājs: ", width=10)
Label_combo4.pack(side=LEFT, pady=10)

combo4 = ttk.Combobox(frame4, state="readonly", values=list(user_list.keys()), width=20)
combo4.pack(side = LEFT, padx=25, pady=10)
user_inex = list(user_list).index(u_name)
combo4.current(user_inex)

# Aprasksts par stundām
frame1 = Frame(right_frame, width=200)
frame1.pack(side=TOP, anchor='w')

Label_note = Label(frame1, text="Komentārs: ", width=10)
Label_note.pack(side=LEFT, padx=10)

note_entry = Entry(frame1, font=('Times New Roman',12,'normal'),  width=50)
note_entry.pack(side = LEFT, padx=5, pady=10)


# Aktivitātes izvēle
frame2 = Frame(right_frame, width=200)
frame2.pack(side=TOP, anchor='w')

Label_combo = Label(frame2, text="Aktivitāte: ", width=10)
Label_combo.pack(side=LEFT, pady=10)

combo = ttk.Combobox(frame2, state="readonly", values=["Uzdevumu izpilde", "Sapulce", "Mācības", "1:1 Saruna", "Virsstundas", "Izstrāde", "Testēšana", "Konsultācijas"],width=20)
combo.pack(side = LEFT, padx=25, pady=10)
combo.current(0)

# Stundu ievade
frame3 = Frame(right_frame, width=200)
frame3.pack(side=TOP, anchor='w')

Label_hour = Label(frame3, text="Stundas: ", width=10)
Label_hour.pack(side=LEFT, padx=10)

hour_entry = Entry(frame3, font=('Times New Roman',12,'normal'),  width=10)
hour_entry.pack(side = LEFT, padx=5, pady=10)

# Datuma ievade
frame4 = Frame(right_frame, width=200)
frame4.pack(side=TOP, anchor='w')

Label_hour = Label(frame4, text="Datums: ", width=10)
Label_hour.pack(side=LEFT, padx=10)

date_entry = tb.DateEntry(frame4, width=10, dateformat=r'%d.%m.%Y')
date_entry.pack(side = LEFT, padx=5, pady=10)

bottomframe = Frame(right_frame)
bottomframe.pack( side = BOTTOM )
blackbutton = Button(bottomframe, text='Reģistrēt stundas', command = field_validation) 
blackbutton.pack( side = BOTTOM)

window.mainloop() 
