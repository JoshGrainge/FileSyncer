from tkinter.filedialog import askdirectory
from pcloud import PyCloud
import os

# TODO Auto create Saves folder in root
# TODO Alter print sub directories to return array of directories as strings
# TODO Create function to ensure login was successful

def print_save_sub_directories():
    meta = pc.listfolder(folderid=0)
    saveDir = pc.listfolder(path=meta['metadata']['contents'][0]['path'])
    print("Current game save directories are: ")
    # List all current sub directories (AKA current games with save files)
    # Removes the directory slash because non programmers are using this mainly
    for dir in saveDir['metadata']['contents']:
        trimmedDirectory = dir['path'].replace(saveDir['metadata']["path"] + "/", '')
        print(trimmedDirectory)

def upload_save_game_files(gameDirectory):
    localDir = askdirectory()

    # Create folder in cloud if none exists
    cloudDir = '/Saves/' + gameDirectory
    pc.createfolderifnotexists(path=cloudDir)

    upload_all_files_in_local_dir(localDir, cloudDir)

    print_finish_message("Finished uploading files")


# Uploads all files recursively to the cloud
def upload_all_files_in_local_dir(localDir, cloudDir):
    files = os.listdir(localDir)
    for file in files:
        filePath = os.path.join(localDir, file)
        if os.path.isdir(filePath):
            print("Creating folder: " + file + " in cloud at dir: " + cloudDir)
            newCloudDir = cloudDir + '/' + file
            pc.createfolderifnotexists(path=newCloudDir)
            upload_all_files_in_local_dir(filePath, newCloudDir)
            continue
        print("Creating file: " + file + " in cloud at: " + cloudDir)
        pc.uploadfile(files=[os.path.join(localDir, file)], path=cloudDir)

def download_save_game_files(gameDirectory):
    _savefilesDestination = askdirectory()

    meta = pc.listfolder(folderid=0)
    saveDir = pc.listfolder(path=meta['metadata']['contents'][0]['path'])
    # List all current sub directories (AKA current games with save files)
    # Removes the directory slash because non programmers are using this mainly
    folderId = False
    savedFolderPath = ""

    # Search for directory
    for dir in saveDir['metadata']['contents']:
        if dir['path'] == '/Saves/'+ gameDirectory:
            savedFolderPath = dir['path']
            folderId = dir['folderid']

    # Game folder does not exist
    if folderId == False: 
        print("Game directory " + gameDirectory + " does not exist")
        return

    files = pc.listfolder(folderid=folderId)
    download_all_files_in_directory(files, savedFolderPath, _savefilesDestination)
    print_finish_message("Finished Downloading files")
   

# Recursive function to load all files in a folder
# Loads all files in folder (does this recursively for all sub directories as well)
def download_all_files_in_directory(files, cloudFolderPath, localPath):
    for file in files['metadata']['contents']:
        # Create folder with folder name and load all files in folder into newly created folder
        if(file['isfolder']):
            # if folder in local directory already exists, populate that instead
            newCloudPath = cloudFolderPath + '/' + file['name']
            newFolderPath = os.path.join(localPath, file['name'])
            if os.path.exists(newFolderPath) == False:
                os.mkdir(newFolderPath)
            folderFiles = pc.listfolder(folderid=file['folderid'])
            download_all_files_in_directory(folderFiles, newCloudPath, newFolderPath)
            continue
            
        # Write cloud file to local file
        _fd = pc.file_open(path=cloudFolderPath + "/" + file['name'], flags=0)
        stats = pc.stat(fileid=file['fileid'])
        size = stats['metadata']['size']
        bytes = pc.file_read(fd=_fd['fd'], count=size)
        localFilePath = os.path.join(localPath, file['name'])
        binaryFile = open(localFilePath, 'wb')
        binaryFile.write(bytes)
        binaryFile.close()
        pc.file_close(fd=_fd['fd'])

        print(file['name'] + " was downloaded to: " + localPath)


def print_finish_message(message):
    print(message)
    input("Press enter to return to menu...")

# TODO make this a user input to login with a checkbox of remember me to have them only have to do that once
email = input("Enter pCloud email: \n")
password = input("Enter pCloud password: \n")

pc = PyCloud(email, password)
pc.listfolder(folderid=0)

# Ask if user wants to save or load files
uploadingFiles = input("Would you like to download or upload files?(Type: upload or download)\n")

print_save_sub_directories()

gameName = input("Enter game directory you would like to use (Without the slash)\n")

# TODO make both these branches button functions instead that will be called when the user
# clicks the button it will open proper dialogue box with proper action
if uploadingFiles == "upload":
    upload_save_game_files(gameName)
else:
    download_save_game_files(gameName)
