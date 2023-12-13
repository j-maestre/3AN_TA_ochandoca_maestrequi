import importlib.util
import subprocess
import os

def InstallPackage(PackageName: str, Force: bool = False, Verbose: bool = True, Atempts:int = 2) -> bool:
  if Atempts == 0:
    print(f"No more atempts allowed installing {PackageName}!")
    return False

  if importlib.util.find_spec(PackageName) is None:
    if Force == False:
      PermissionGaranted = False
      while not PermissionGaranted:
        reply = str(input("Would you like to install Python package '{0:s}'? [Y/N]: ".format(PackageName))).lower().strip()[:1]
        if reply == 'n':
          return False
        PermissionGaranted = (reply == 'y')
        print(f"Installing {PackageName} module...")

    if Verbose == True:
      subprocess.call(['python', '-m', 'pip', 'install', PackageName])
    else:
      stdout = open(os.devnull, 'w')
      stderr = subprocess.STDOUT
      subprocess.call(['python', '-m', 'pip', 'install', PackageName], stdout=stdout, stderr=stderr)

    return InstallPackage(PackageName, Atempts=(Atempts-1), Force=Force, Verbose=Verbose)
  return True

def UnInstallPackage(PackageName: str, Verbose: bool = True):
  if importlib.util.find_spec(PackageName):
    if Verbose == True:
      subprocess.call(['python', '-m', 'pip', 'uninstall', PackageName])
    else:
      stdout = open(os.devnull, 'w')
      stderr = subprocess.STDOUT
      subprocess.call(['python', '-m', 'pip', 'install', PackageName], stdout=stdout, stderr=stderr)
