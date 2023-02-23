import PySimpleGUI as sg

global login
login = False

savedLoginEmail = ""
savedLoginPass = ""

savedTheme = ""

# Load current directories
currentDirectories = ['Create New Directory', 'Combo 2', 'Combo 3']


def load_login_info():
    # Check if profile details file exists and if so load email and password
    global savedLoginEmail
    global savedLoginPass
    savedLoginEmail = "Saved Email"
    savedLoginPass = "Saved Password"


def open_login_modal():
    loginLayout = [
        [sg.Text("pCloud Email:")],
        [sg.Input()],
        [sg.Text("pCloud Password:")],
        [sg.Input()],
        [sg.Text("Remember login:"),sg.Checkbox('')],
        [sg.Button("Login")]
    ]

    loginWindow = sg.Window("File Syncer", loginLayout, modal=True, element_justification='c')
    while True:
        event, values = loginWindow.read()
        print(event, values)

        # Check if login is correct
        if event == "Login":
            global login
            login = True

            # Save login info when login was successful
            if values[2] == True:
                print("Should remember login")

            break

        if event == "Exit" or event == sg.WIN_CLOSED:
            break

    loginWindow.close()

def create_main_window():
    mainLayout = [
    [sg.Text("File Syncer")],
    
    [sg.TabGroup([[sg.Tab('Upload',[[sg.Text("Cloud Directories:"),sg.Combo(values=currentDirectories, readonly=True, enable_events=True, k='CLOUD_DIR'), sg.Button("Upload Files")], 
                                    [sg.Text("Enter new game directory", k="NEW_DIR_TITLE"), sg.Input("", disabled=True, k="ADD_DIR_INPUT")]]), 
                   sg.Tab('Download', [[sg.Button("Download Files")]])
                ]])
    ],
    [sg.Text("")],
    [sg.Text("")],
    [sg.Text("Theme:"), sg.Combo(values=sg.theme_list(), readonly=True, enable_events=True, k='THEME')]
    ]
    return sg.Window("FileSyncer", mainLayout, element_justification='c')

mainWindow = create_main_window()

while login == False:
        open_login_modal()


while True:
    event, values = mainWindow.read()
    print(event, values)

    if event == "Upload Files":
        print("Upload Files Stuff")

    mainWindow['ADD_DIR_INPUT'].update(disabled=values['CLOUD_DIR'] != "Create New Directory")

    if event == "Download Files":
        print("Download Files Stuff")

    if event == sg.WIN_CLOSED or event == "My simple app.":
        break

    # Reload window
    if(event == "THEME"):
        sg.theme(values['THEME'])
        mainWindow.close()
        mainWindow = create_main_window()

mainWindow.close()