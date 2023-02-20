from tkinter.filedialog import askopenfilenames
from tkinter.filedialog import askdirectory
from pcloud import PyCloud
import os


def print_save_sub_directories():
    meta = pc.listfolder(folderid=0)
    saveDir = pc.listfolder(path=meta['metadata']['contents'][0]['path'])
    print("Current game save directories are: ")
    # List all current sub directories (AKA current games with save files)
    # Removes the directory slash because non programmers are using this mainly
    for dir in saveDir['metadata']['contents']:
        trimmedDirectory = dir['path'].replace(saveDir['metadata']["path"]+"/", '')
        print(trimmedDirectory)

def save_game_files(gameDirectory):
    _files = askopenfilenames()

    print(_files)
    pc.createfolderifnotexists(path='/Saves/' + gameDirectory)

    for _file in _files:
        pc.uploadfile(files=[_file], path='/Saves/' + gameDirectory)

    print_finish_message("Finished uploading files")

def load_game_files(gameDirectory):
    _savefilesDestination = askdirectory()

    meta = pc.listfolder(folderid=0)
    saveDir = pc.listfolder(path=meta['metadata']['contents'][0]['path'])
    # List all current sub directories (AKA current games with save files)
    # Removes the directory slash because non programmers are using this mainly
    folderId = False
    savedFolderPath = ""

    for dir in saveDir['metadata']['contents']:
        if dir['path'] == '/Saves/'+ gameDirectory:
            savedFolderPath = dir['path']
            folderId = dir['folderid']


    # Game folder does not exist
    if folderId == False: 
        print("Game directory " + gameDirectory + " does not exist")
        return

    # TODO can recursively call this function if its a folder to load all files in the folder (would be a good 
    # thing to call it open all files or something where the root dir would be the passed as the folders name)
    files = pc.listfolder(folderid=folderId)
    load_all_files_in_directory(files, savedFolderPath, _savefilesDestination)
    print_finish_message("Finished Downloading files")
   

# Recursive function to load all files in a folder
# Loads all files in folder (does this recursively for all sub directories as well)
def load_all_files_in_directory(files, cloudFolderPath, localPath):
    for file in files['metadata']['contents']:
        # Create folder with folder name and load all files in folder into newly created folder
        if(file['isfolder']):
            # if folder in local directory already exists, populate that instead
            newCloudPath = cloudFolderPath + '/' + file['name']
            newFolderPath = localPath + '/' + file['name']
            if os.path.exists(newFolderPath) == False:
                os.mkdir(newFolderPath)
            folderFiles = pc.listfolder(folderid=file['folderid'])
            load_all_files_in_directory(folderFiles, newCloudPath, newFolderPath)
            continue
            
        _fd = pc.file_open(path=cloudFolderPath + "/" + file['name'], flags=0)
        stats = pc.stat(fileid=file['fileid'])
        size = stats['metadata']['size']
        bytes = pc.file_read(fd=_fd['fd'], count=size)

        binaryFile = open(localPath+"/"+file['name'], 'wb')
        binaryFile.write(bytes)
        binaryFile.close()

        print(file['name'] + " was downloaded to: " + localPath)

        pc.file_close(fd=_fd['fd'])

def print_finish_message(message):
    print(message)
    input("Press enter to return to menu...")

# TODO make this a user input to login with a checkbox of remember me to have them only have to do that once
email = input("Please enter email:\n")
password = input("Please enter email:\n")

pc = PyCloud(email, password)
pc.listfolder(folderid=0)

# Ask if user wants to save or load files
uploadingFiles = input("Would you like to download or upload files?(Type: upload or download)\n")

print_save_sub_directories()

gameName = input("Enter game directory you would like to use (Without the slash)\n")

# TODO make both these branches button functions instead that will be called when the user
# clicks the button it will open proper dialogue box with proper action
if uploadingFiles == "upload":
    save_game_files(gameName)
else:
    load_game_files(gameName)
