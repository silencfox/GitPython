import git
from git import RemoteProgress
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
import subprocess
import shlex


os.system('cls')
# Create an instance of the ConfigParser class
config = configparser.RawConfigParser()
config.read('config.ini')

# Access values from the configuration file:
repository = config.get('DEFAULT', 'REPOSITORY')
mainbranch = config.get('DEFAULT', 'RAMAPRINCIPAL')
user_name = config.get('DEFAULT', 'USER_NAME')
urlRepo = config.get('DEFAULT', 'URLREPOSITORY')
pat = config.get('DEFAULT', 'PAT')
outpath = config.get('DEFAULT', 'OUTPATH')
local_repo_directory = config.get('DEFAULT', 'REPOPATH')
LOG_PATH = os.path.join(os.getcwd(), "no-conflict.log")

if os.path.isdir(local_repo_directory):
    repo = Repo(local_repo_directory)
    #local_repo_directory = os.path.join(os.getcwd(), repository)

class CloneProgress(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        if message:
            print(message)
            
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
                        local_repo_directory, branch=mainbranch, progress=CloneProgress())


def chdirectory(path):
    os.chdir(path)


def create_branch(repo, branch_name):
    print("Creating a new branch with id name " + branch_name)
    current = repo.create_head(branch_name)
    current.checkout()

def update_branch(branch_name):
    print("updating Branch {}".format(branch_name))
    repo.git.checkout(branch_name)
    repo.git.pull()
    repo.remotes.origin.pull()    
    input("Press Enter to continue...")
    
def branch_diff(repo, branch_name, mainbranch,outpath):
    print("Branch {} vs {}".format(mainbranch, branch_name))
    case=branch_name[branch_name.rindex('/')+1:]
    repo.git.checkout(mainbranch)
    repo.git.pull()
    repo.git.checkout(branch_name)
    repo.git.pull()
    repo.remotes.origin.pull()
    #diff = repo.git.diff("{}..{}".format(branch_name, mainbranch), name_only=True)
    diff = repo.git.diff("{}...{}".format(mainbranch, branch_name), name_status=True)

    diffarr = []

    diffarray = diff.split('\n')
    #print(type(diffarray))
    for diffobj in diffarray:
        estado=diffobj[0]
        objeto=diffobj[1:].strip()
        objarr=[estado,objeto]
        diffarr +=objarr
        print("{}, Objeto: {}".format(estado, objeto))
        diffobj=diffobj.replace("/", "\\")
        src_file=local_repo_directory +objeto
        copy_file(src_file, outpath+case+'\\'+objeto)
    
    #download_branch(src_file, outpath+objeto, diffarr,mainbranch, branch_name)
    #print(diffarr)
    """
    new_files = []
    deleted_files = []
    modified_files = []

    # Your last commit of the current branch
    commit_feature = repo.head.commit.tree
    # Your last commit of the dev branch
    commit_origin_dev = repo.commit("dev")
    # Comparing 
    diff_index = commit_origin_dev.diff(branch_name)

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

def download_branch(src_file, outpath, diffarr,mainbranch, branch_name):
    ## subprocess
    print("Destino:{}:".format(outpath))
    if os.path.isfile(src_file):
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        shutil.copy2(src_file, outpath)

def copy_file(src_file, outpath):
    ## subprocess
    print("Destino:{}:".format(outpath))
    if os.path.isfile(src_file):
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        shutil.copy2(src_file, outpath)

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



def gitdefault(repo):
    git = repo.git
    git.checkout("HEAD", b="my_new_branch")  # Create a new branch.
    git.branch("another-new-one")
    git.branch("-D", "another-new-one")  # Pass strings for full control over argument order.
    git.for_each_ref()  # '-' becomes '_' when calling it.

def run(command: str) -> int:
    """Runs a command, logs the output, and returns the return code."""
    chdirectory(local_repo_directory)
    with open(LOG_PATH, "a") as file:
        process = subprocess.run(
            shlex.split(command, posix=False), stderr=file, stdout=file
        )
    return process.returncode
    
def current_branch_name() -> str:
    """Returns the name of the current git branch."""
    process = subprocess.Popen(
        ["git", "branch", "--show-current"], stdout=subprocess.PIPE
    )
    stdout, _ = process.communicate()
    return stdout.decode().strip()
    
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
def arraytest():
    print("Hola mundo")
    diffarr = []
    arradd=[1,2]
    diffarr += [arradd]
    my_2Dlist = [[1, 2], [3, 4], [5, 6]]
    print(my_2Dlist)
    print(diffarr)

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
    
    #run("black .")
    while True:
        print("***************************************")
        print("*****   AZURE BRANCH MANAGEMENT   *****")
        print("***************************************")
        print("¿Qué desea hacer?")
        print("1. Clonar repositorio")
        print("2. Descargar Ramas")
        print("3. Array Test")
        print("4. Actualizar Rama")
        print("5. Checkout Branch")
        print("x. Salir")
        
        opcion = input("Ingrese su opción: ")
        
        if opcion == "1":
            os.system('cls')
            clone_repo(urlRepo)
            #repo = Repo.init(local_repo_directory)
            #repo = Repo(local_repo_directory)
            chdirectory(local_repo_directory)
        elif opcion == "2":
            os.system('cls')
            rama = input("Introduzca la rama a comparar: ")
            branch_diff(repo, rama, mainbranch,outpath)
        elif opcion == "3":
            os.system('cls')
            arraytest()
            update_branch(branch_name)
        elif opcion == "4":
            os.system('cls')
            branch_name = input("Introduzca la rama a actualizar: ")
            update_branch(branch_name)
        elif opcion == "5":
            os.system('cls')
            branch_name = input("Introduzca la rama a actualizar: ")
            run(f"git checkout {branch_name}")
        elif opcion == "x":
            os.system('cls')
            salir()
        else:
            print("Opción inválida. Intente nuevamente.")
