import git
import os
from os import system
from os import scandir
#from os import fopen
import shutil
from subprocess import call
from git import Repo
# Import the configparser module
import configparser
import asyncio
import time
from time import gmtime, strftime
from gidgethub import aiohttp
import sys


os.system('cls')
# Create an instance of the ConfigParser class
config = configparser.ConfigParser()
config.read('config.ini')

# Access values from the configuration file:
repository = config.get('DEFAULT', 'REPOSITORY')
mainbranch = config.get('DEFAULT', 'RAMAPRINCIPAL')
user_name = config.get('DEFAULT', 'USER_NAME')
urlRepo = config.get('DEFAULT', 'URLREPOSITORY')
outpath = config.get('DEFAULT', 'OUTPATH')
local_repo_directory = config.get('DEFAULT', 'REPOPATH')


if os.path.isdir(local_repo_directory):
    repo = Repo(local_repo_directory)
    #local_repo_directory = os.path.join(os.getcwd(), repository)


def clone_repo(urlRepo):
    if os.path.exists(local_repo_directory):
        print("Directory exists, pulling changes from main branch")
        #repo = Repo(local_repo_directory)
        origin = repo.remotes.origin
        origin.pull(mainbranch)
    else:
        print("Directory does not exists, cloning")
        print(urlRepo)
        Repo.clone_from(urlRepo,
                        local_repo_directory, branch=mainbranch)


def chdirectory(path):
    os.chdir(path)


def create_branch(repo, branch_name):
    print("Creating a new branch with id name " + branch_name)
    current = repo.create_head(branch_name)
    current.checkout()

def branch_diff(repo, branch_name, outpath):
    print("Descargando objetos de la rama {}".format(branch_name))
    new_files = []
    deleted_files = []
    modified_files = []
    # Your last commit of the current branch

    repo.git.checkout("main")
    repo.git.pull()
    repo.git.checkout(branch_name)
    
    commit_feature = repo.head.commit.tree
    # Your last commit of the dev branch
    commit_origin_dev = repo.commit("main")
    # Comparing 

    diff_index = commit_origin_dev.diff(branch_name)

    #diff = repo.git.diff('HEAD~1...HEAD', name_only=True)
    diff = repo.git.diff('dev..main', name_only=True)
    #diff = repo.git.diff('main..dev', name_status=True)
    
    #print(diff)
    diffarray = diff.split('\n')
    #print(type(diffarray))
    #print(diffarray)
    for diffobj in diffarray:
        diffobj=diffobj.replace("/", "\\")
        origen=local_repo_directory +diffobj
        print(origen)
        print(outpath)
        #print("Origen:{}:".format(origen)) 
        print("Destino:{}:".format(outpath))
        if os.path.isfile(origen):
            os.makedirs(os.path.dirname(outpath+diffobj), exist_ok=True)
            shutil.copy2(origen, outpath+diffobj)

    # Collection all new files
    for file in diff_index.iter_change_type('A'):
        new_files.append(file)
        #print(file)

    # Collection all deleted files
    for file in diff_index.iter_change_type('D'):
        deleted_files.append(file)
        #print(file)

    # Collection all modified files
    for file in diff_index.iter_change_type('M'):
        modified_files.append(file)
        #print(file)

    """
    """

def update_file():
    print("Modifying the file")
    chdirectory(local_repo_directory)
    opened_file = open("file.txt", 'a')
    opened_file.write("{0} added at {1} \n".format(
        "I am a new string", str(time.time())))


def add_and_commit_changes(repo):
    print("Commiting changes")
    #repo.git.add(update=True)
    #repo.index.add(['.'])
    repo.git.add(all=True)
    repo.git.commit("-m", "Adding a new line to the file.text file")


def push_changes(repo, branch_name):
    print("Push changes")
    repo.git.push("--set-upstream", 'origin', branch_name)

def copy_file(src_file):

    ## subprocess
    #subprocess.call(args, *, stdin=None, stdout=None, stderr=None, shell=False)
    # example (WARNING: setting `shell=True` might be a security-risk)
    # In Linux/Unix
    #status = subprocess.call('cp source.txt destination.txt', shell=True) 
    # In Windows
    #status = subprocess.call('copy source.txt destination.txt', shell=True)

    ### shutil
    src_path = r"C:\Repos\tools\profit.txt"
    #dst_path = r"C:\Repos\tools\profit2.txt"
    #shutil.copy2(src_path, dst_path)
    #print('Copied')
    ### subprocess
    #call("cp -p <file> <file>", shell=True)
    # OS Open example
    # In Unix/Linux
    #os.popen('cp source.txt destination.txt') 
    # In Windows
    #os.popen('copy source.txt destination.txt')
    ## OS System
    # In Linux/Unix
    #os.system('cp source.txt destination.txt')  

    # In Windows
    #os.system('copy source.txt destination.txt')

def gitdefault(repo):
    git = repo.git
    git.checkout("HEAD", b="my_new_branch")  # Create a new branch.
    git.branch("another-new-one")
    git.branch("-D", "another-new-one")  # Pass strings for full control over argument order.
    git.for_each_ref()  # '-' becomes '_' when calling it.

def salir():
    print("¡Hasta luego!")
    sys.exit()

async def setup_github(branch_name):
    print("Setup github token")
    api_token = config.get('DEFAULT', 'GH_API_TOKEN')
    print("nombre de usuario")
    print(user_name)
    #api_token = config('GH_API_TOKEN')
    print(api_token)
    async with aiohttp.ClientSession() as session:
        gh = aiohttp.GitHubAPI(session, user_name, oauth_token=api_token)
        
        #create-pull-request
        await create_pull_request(gh, branch_name, api_token)


async def create_pull_request(gh, branch_name, token):
    print("Creating PR from: " + branch_name)
    response = await gh.post('/repos/{owner}/{repo}/pulls', url_vars={'owner': user_name, 'repo': repository}, data = {
        'title': 'Addition of a new line to the file.txt',
        'head': branch_name,
        'body': '\n #What does this PR do? \n Add a new text line to the main text file',
        'base': mainbranch
    }, accept='application/vnd.github.v3+json', oauth_token=token)
    if response:
        print("PR was created at: " + response['html_url'])


async def main():
    clone_repo(urlRepo)
    repo = Repo.init(local_repo_directory)
    #repo = Repo(local_repo_directory)
    chdirectory(local_repo_directory)
    
    #branch_name = "feature/update-txt-file" + str(round(time.time()))
    branch_name = "feature/update-txt-file_" + strftime("%Y_%m_%d")
    #print(strftime("%Y_%m_%d__%H_%M"))
    #create a new branch
    #create_branch(repo, branch_name)
    
    branch_diff(repo, "dev", outpath)
    # update file
    #update_file()

    # add and commit changes
    #add_and_commit_changes(repo)

    # push changes
    #push_changes(repo, branch_name)
    
    #setup github credentials and session
    #await setup_github(branch_name)


if __name__ == "__main__":
    #Only for windows
    #asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    #run main async
    #asyncio.run(main())
    #asyncio.run(main())

    while True:
        print("***************************************")
        print("*****   AZURE BRANCH MANAGEMENT   *****")
        print("***************************************")
        print("¿Qué desea hacer?")
        print("1. Clonar repositorio")
        print("2. Descargar Ramas")
        print("3. Salir")
        
        opcion = input("Ingrese su opción: ")
        
        if opcion == "1":
            os.system('cls')
            clone_repo(urlRepo)
            #repo = Repo.init(local_repo_directory)
            #repo = Repo(local_repo_directory)
            chdirectory(local_repo_directory)
        elif opcion == "2":
            os.system('cls')
            branch_diff(repo, "dev", outpath)
        elif opcion == "3":
            os.system('cls')
            salir()
        else:
            print("Opción inválida. Intente nuevamente.")