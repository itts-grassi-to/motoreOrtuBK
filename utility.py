# ## CREATO DA ORTU prof. DANIELE
# ## daniele.ortu@itisgrassi.edu.it
import os
import subprocess

class Utility_bk:
    def __init__(self, currdir):
        self.__currdir = currdir
    def __isMount(self, sub):
        r = subprocess.run(["df"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return sub in str(r.stdout)
    def mount(self,proto, da,to):
        if not self.__isMount(da):
            #*********** cambio directory in currdir
            r = os.system("cd "+ self.__currdir)
            if r != 0:
                return self.__currdir+" non esistente"
            #*************** creo directory di mount
            os.system("mkdir -p " + to)
            #************* monto la directory
            r = subprocess.run([proto, da, to],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if r.stderr:
                return r.stderr

        return ""

