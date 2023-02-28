from tkinter.filedialog import askdirectory
from pcloud import PyCloud
import os
import json
import _thread

global pc

fileName = "FileSyncerSaveData.json"

def attempt_login(_email, _password):
    global pc

    # Login details not specified
    if len(_email) == 0 or len(_password) == 0:
        return False
    
    try:
        pc = PyCloud(_email, _password)
        pc.listfolder(folderid=0)
        return True
    except:
        return False
    

def get_current_directories():
    global pc
    # Create /Saves folder if there is not one already, this is for 
    # organization if you still want to use pCloud for other reasons
    pc.createfolderifnotexists(path='/Saves')
    meta = pc.listfolder(folderid=0)
    saveDir = pc.listfolder(path=meta['metadata']['contents'][0]['path'])

    directories = []

    # List all current sub directories (AKA current games with save files)
    # Removes the directory slash because non programmers are using this mainly
    for dir in saveDir['metadata']['contents']:
        trimmedDirectory = dir['path'].replace(saveDir['metadata']["path"] + "/", '')
        directories.append(trimmedDirectory)

    return directories
        
def combine_paths(cloudDir, addDirInput):
    if(cloudDir == "Create New Directory"):
        result = addDirInput
    else:
        result = cloudDir

    return result

def upload_save_game_files(gameDirectory):
    global pc

    # Don't do multiple file upload sequences at once
    if _thread._count() != 0: return

    localDir = askdirectory()

    # When cancel was pressed just return out of function
    if not localDir:
        return

    # Create folder in cloud if none exists
    cloudDir = '/Saves/' + gameDirectory
    pc.createfolderifnotexists(path=cloudDir)

    _thread.start_new_thread(_upload_all_files_in_local_dir, (localDir, cloudDir))



# Uploads all files recursively to the cloud
def _upload_all_files_in_local_dir(localDir, cloudDir):
    global pc

    files = os.listdir(localDir)
    for file in files:
        filePath = os.path.join(localDir, file)
        if os.path.isdir(filePath):
            print("Creating folder: " + file + " in cloud at dir: " + cloudDir)
            newCloudDir = cloudDir + '/' + file
            pc.createfolderifnotexists(path=newCloudDir)
            _upload_all_files_in_local_dir(filePath, newCloudDir)
            continue
        print("Creating file: " + file + " in cloud at: " + cloudDir)
        pc.uploadfile(files=[os.path.join(localDir, file)], path=cloudDir)

    # print finish message
    if _thread._count() <= 1:
        print_finish_message("=====Finished uploading files=====")


def download_save_game_files(gameDirectory):
    global pc

    # Don't do multiple file download sequences at once
    if _thread._count() != 0: return

    _savefilesDestination = askdirectory()

    # When cancel was pressed just return out of function
    if not _savefilesDestination:
        return

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
    _thread.start_new_thread(_download_all_files_in_directory, (files, savedFolderPath, _savefilesDestination))

   

# Recursive function to load all files in a folder
# Loads all files in folder (does this recursively for all sub directories as well)
def _download_all_files_in_directory(files, cloudFolderPath, localPath):
    global pc

    for file in files['metadata']['contents']:
        # Create folder with folder name and load all files in folder into newly created folder
        if(file['isfolder']):
            # if folder in local directory already exists, populate that instead
            newCloudPath = cloudFolderPath + '/' + file['name']
            newFolderPath = os.path.join(localPath, file['name'])
            if os.path.exists(newFolderPath) == False:
                os.mkdir(newFolderPath)
            folderFiles = pc.listfolder(folderid=file['folderid'])
            _download_all_files_in_directory(folderFiles, newCloudPath, newFolderPath)
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

    if _thread._count() == 1:
        print_finish_message("=====Finished Downloading files=====")


def create_savedata_file():
    global fileName
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    filePath = dir_path + os.sep + fileName
    if(os.path.exists(filePath)):
        return

    baseData = {
                "email": "",
                "password": "",
                "theme": "DarkAmber"
               }
    
    dataObject = json.dumps(baseData, indent=4)
    _write_data(dataObject)
        

def load_savedata():
    global fileName

    dir_path = os.path.dirname(os.path.realpath(__file__))

    filePath = dir_path + os.sep + fileName
    if os.path.exists(filePath) == False:
        return
    
    with open(filePath, 'r') as file:
        jsonObject = json.load(file)
        file.close()
        return jsonObject


def set_savedata(email, password, theme):
    data =  {
                "email": email,
                "password": password,
                "theme": theme
            }
    dataObject = json.dumps(data, indent=4)
    _write_data(dataObject)
    

def _write_data(data):
    global fileName

    dir_path = os.path.dirname(os.path.realpath(__file__))

    filePath = dir_path + os.sep + fileName
    
    with open(filePath, "w") as file:
        file.write(data)
        file.close()



def print_finish_message(message):
    print(message)