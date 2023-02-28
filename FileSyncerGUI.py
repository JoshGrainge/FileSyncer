import PySimpleGUI as sg
from FileSyncerTest import * 

global login
login = False

savedLoginEmail = ""
savedLoginPass = ""

savedTheme = ""

currentDirectories = []

# values to be kept after main window refreshes
global uploadCombo
uploadCombo = ""
global downloadCombo
downloadCombo = ""


def load_login_info():
    # Check if profile details file exists and if so load email and password
    global savedLoginEmail
    global savedLoginPass
    savedLoginEmail = "Saved Email"
    savedLoginPass = "Saved Password"

def open_login_modal():
    loginLayout = [
        [sg.Text("pCloud Email:")],
        [sg.Input("josh.grainge@hotmail.com")],
        [sg.Text("pCloud Password:")],
        [sg.Input("ThisIsASecretPasswordForMeAndMyStinkyFriendsOnly!")],
        [sg.Text("Remember login:"),sg.Checkbox('')],
        [sg.Button("Login")]
    ]

    loginWindow = sg.Window("File Syncer", loginLayout, modal=True, element_justification='c')
    while True:
        event, values = loginWindow.read()

        # Check if login is correct
        if event == "Login":
            global login
            login = True

            if attempt_login(values[0], values[1]):
                # Save login info when login was successful
                if values[2] == True:
                    print("Should remember login")

                break

        if event == "Exit" or event == sg.WIN_CLOSED:
            break

    loginWindow.close()

while login == False:
        open_login_modal()

# Load current directories
currentDirectories = print_save_sub_directories()

def create_main_window():
    global uploadCombo
    global downloadCombo

    mainLayout = [
    [sg.Text("File Syncer")],
    
    [sg.TabGroup([[sg.Tab('Upload',[[sg.Text("Cloud Directories:"),sg.Combo(values=['Create New Directory'] + currentDirectories, default_value=uploadCombo, readonly=True, enable_events=True, k='CLOUD_DIR_UPLOAD'), sg.Button("Upload Files")], 
                                    [sg.Text("Enter new game directory", k="NEW_DIR_TITLE"), sg.Input("", disabled=True, k="ADD_DIR_INPUT")]]), 
                   sg.Tab('Download', [[sg.Text("Cloud Directories:"),sg.Combo(values=currentDirectories, default_value=downloadCombo, readonly=True, enable_events=True, k='CLOUD_DIR_DOWNLOAD'),sg.Button("Download Files")]])
                ]])
    ],
    [sg.Text("")],
    [sg.Text("")],
    [sg.Text("Theme:"), sg.Combo(values=sg.theme_list(), default_value=sg.theme(), readonly=True, enable_events=True, k='THEME')]
    ]
    return sg.Window("FileSyncer", mainLayout, element_justification='c')

mainWindow = create_main_window()


while True:
    event, values = mainWindow.read()
    mainWindow['ADD_DIR_INPUT'].update(disabled=values['CLOUD_DIR_UPLOAD'] != "Create New Directory")

    uploadCombo = values['CLOUD_DIR_UPLOAD']
    downloadCombo = values['CLOUD_DIR_DOWNLOAD']

    if event == "Upload Files":
        result = combine_paths(values['CLOUD_DIR_UPLOAD'], values['ADD_DIR_INPUT'])
        upload_save_game_files(result)
        # Update directories when new directory is added
        if values['CLOUD_DIR_UPLOAD'] == "Create New Directory":
            currentDirectories = print_save_sub_directories()
            mainWindow.close()
            mainWindow = create_main_window()

    if event == "Download Files":
        download_save_game_files(values['CLOUD_DIR_DOWNLOAD'])

    if event == sg.WIN_CLOSED or event == "My simple app.":
        break

    # Reload window
    if(event == "THEME"):
        sg.theme(values['THEME'])
        mainWindow.close()
        mainWindow = create_main_window()

mainWindow.close()