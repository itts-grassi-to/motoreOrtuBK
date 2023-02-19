# *************************************************************************
## CREATO DA ORTU prof. DANIELE
## daniele.ortu@itisgrassi.edu.it

# from danieleRSINK import tbk
import os
import ast
import subprocess
from datetime import datetime

DEBUG = False

class bkFile():
    # def __init__(self, ch, bks, cd):
    def _printa(self, s):
        if DEBUG:
            print(s)

    def __init__(self,bks, altro):
        self._bks, self._altro = bks, altro
        # self.__path_fconf = path_fconf
        #self._path_fpar = NOME_FPAR
        #self._bks, self._altro = self._get_impostazioni()

    def _is_running(self, ps):
        r = subprocess.run(["ps", "-e"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if r.stderr:
            print("\nERRORE: " + r.stderr.decode("utf-8"))
            return False
        l = r.stdout.decode("utf-8").split("\n")

        for ch in l:
            print(ch)
            if ps in ch:
                return True
        return False
        # print(ch)

    def _esegui(self, ch):
        self._printa("********************** Inizia thread: "+ch)
        self.__inizializza_backup(ch)
        self._flog.write("Variabili inizializzate")
        if self.__inizializza_paths():
            self.__backuppa()
        self._printa("********************** fine thread")

    def __inizializza_backup(self, ch):
        data = self._bks[ch]
        if DEBUG:
            self._printa(data)
        self._remotoDA = data['dirDA']["remoto"]
        self._remotoTO = data['dirTO']["remoto"]
        self._dirBASE = "."
        if self._remotoDA:
            self._dirDA = data['dirDA']['utente'] +'@' + \
                data['dirDA']["host"] + ":" + \
                data['dirDA']["rem_path"]
            self._protocolloDA = data['dirDA']["protocollo"]
        else:
            self._dirDA = data['dirDA']["loc_path"]
        if self._remotoTO:
            self._dirBK = data['dirTO']['utente'] + '@' + \
                data['dirTO']["host"] + ":" + \
                data['dirTO']["rem_path"]
            self._protocolloTO = data['dirDA']["protocollo"]
        else:
            self._dirBK = data['dirTO']["loc_path"]
        self._mntDA = data['dirDA']["mnt"]
        self._mntTO = data['dirTO']["mnt"]
        self._nome = ch
        #self._path_flog = CURRDIR + "/" + self._nome + ".log"
        self._path_flog = "./" + self._nome + ".log"
        self._flog = open(self._path_flog, "w")
        self._do = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
        self._latestDIR = self._dirBK + "/" + "latestDIR"
        self._nomeStatoFile = "stf.bin"
        self.__nomeTAR = self._do + "-" + self._nome + ".tar.gz"

    def __inizializza_paths(self):
        if self._remotoDA:
            self._flog.write("\nMonto directory da backuppare: " + self._dirDA)
            mntDA = self._dirBASE + "/" + self._mntDA
            if not self.__isMount(self._dirDA):
                r = subprocess.run([self._protocolloDA, self._dirDA, mntDA],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if r.stderr:
                    self.__log("\nERRORE: " + r.stderr.decode("utf-8"), True)
                    self.initOK = False
                    return False
                self._flog.write("\nDirectory montata")
            else:
                self._flog.write("\nDirectory GIA montata")
            self._dirDA = mntDA
        if self._remotoTO:
            self._flog.write("\nMonto directory dei backup: " + self._dirBK)
            mntTO = self._dirBASE + "/" + self._mntTO
            if not self.__isMount(self._dirBK):
                r = subprocess.run([self._protocolloTO, self._dirBK, mntTO], stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
                if r.stderr:
                    self.__log("\nERRORE: " + r.stderr.decode("utf-8"), True)
                    self.initOK = False
                    return False
                self._flog.write("\nDirectory montata")
            else:
                self._flog.write("\nDirectory GIA montata")
            self._dirBK = mntTO

            self._latestDIR = self._dirBK + "/" + "latestDIR" + self._mntTO
        self._flog.write("\nFine inizializzazione processo")
        return True


    def __isMount(self, sub):
        r = subprocess.run(["df"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return sub in str(r.stdout)

    def __log(self, msg, mail):
        self._flog.write(msg)
        self._flog.close()
        if mail and not DEBUG:
            dummy = 0
            os.system("mail -s  '" + self._nome + "' server.backup@itisgrassi.edu.it < " + self._path_flog)
        self._printa("MAIL INVIATA: mail -s  '" + self._nome + "' server.backup@itisgrassi.edu.it < " + self._path_flog)

    def __backuppa(self):
        print("Inizio backup")
        self._flog.write("\n*********Inizio il processo di backup************")
        self._flog.write("\nUso come base: " + self._latestDIR)
        attr = '-auv --link-dest "' + self._latestDIR + '" --exclude=".cache" '
        dirBK = self._dirBK + "/" + self._do + "-" + self._nome
        rsync = "rsync " + attr + "\n\t" + self._dirDA + "/\n\t" + dirBK + "\n\t > " + self._path_flog
        self._flog.write("\n" + rsync)
        r = os.system("rsync " + attr + self._dirDA + "/ " + dirBK + " > " + self._path_flog)
        self._flog.close()
        self._flog = f = open(self._path_flog, "a")
        self._flog.write("\nRimuovuo: " + self._latestDIR)
        r = os.system("rm -rf " + self._latestDIR)
        self._flog.write("\nNuova base: " + self._dirBK + "/" + self._do + "-" + self._nome)
        self._flog.write(
            "\nCreo link: ln -s " + self._dirBK + "/" + self._do + "-" + self._nome + " " + self._latestDIR)
        r = os.system("ln -s " + self._dirBK + "/" + self._do + "-" + self._nome + " " + self._latestDIR)

        self.__log("\nPROCESSO ESEGUITO CON SUCESSO\n\n", True)
        print("Finito backup")
        self._flog.close()


 # c = bkFile()
# c._esegui()
