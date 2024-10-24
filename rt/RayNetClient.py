import subprocess
import platform
import os


def startup():
    try:
        cwd = os.path.dirname(__file__)
        print(cwd)
        os.chdir(os.path.join(cwd, 'bin'))
        

    except:
        print('failed to set current directory')
    
    bin = os.path.join(os.getcwd(), 'TracerModule')

    binaryTag = '.exe' if platform.system() == 'Windows' else ''
    print(bin + binaryTag)
    startupTask = subprocess.run([bin + binaryTag], shell=True, capture_output=True, text=True)
    

if __name__ == '__main__':
    startup()