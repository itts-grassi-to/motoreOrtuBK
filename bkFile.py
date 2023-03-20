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

    def __init__(self, bks, altro, cdir):
        self._bks, self._altro = bks, altro
        self.__currDIR = cdir

    def __getLatest(self, rootdir, nome):
        #s = "gigi"
        #rootdir = '/home/daniele/Scrivania/repository-git/test'
        d = []
        for file in os.listdir(rootdir):
           di = os.path.join(rootdir, file)
           if os.path.isdir(di):
              if di[len(di)-len(nome):] == nome:
                 d.append(di)
        if len(d) == 0:
          return rootdir
        d.sort(reverse=True)
        return d[0]

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

    def __protoSSH(self, d):
        '''
        return d["protocollo"], \
            d['utente'] + '@' + \
            d["host"] + ":" + \
            d["rem_path"]
        '''
        dir =  d['utente'] + '@' + \
            d["host"] + ":" + \
            d["rem_path"]
        mnt = self.__currDIR + "/" + d["mnt"]
        r =["sshfs"]
        r.append(dir)
        r.append(mnt)
        return r, dir, mnt
    def __protoSMB(self, d):
        # mount -t cifs -o username=uffici,password=****** //172.16.200.100/Volume_1 /mnt/NAS
        '''
        return "mount -t cifs -o username=" + d['utente'] + \
               ",password=" + d['passwd'], \
               "//" + d['host'] + "/" + d['rem_path']
        '''
        opt = "username=" + d['utente'] + \
               ",password=" + d['passwd']+",vers=1.0"
        dir = "//" +  d['host'] + "/" + d['rem_path']
        mnt = self.__currDIR + "/" + d["mnt"]
        r =["mount", "-t", "cifs", "-o"]
        r.append(opt)
        r.append(dir)
        r.append(mnt)
        return r, dir, mnt
    def __inizializza_backup(self, ch):
        data = self._bks[ch]
        if DEBUG:
            self._printa(data)
        self.__remotoDA = data['dirDA']["remoto"]
        self.__remotoTO = data['dirTO']["remoto"]
        # self._dirBASE = self.__currDIR
        # ************************************** directory backup da e verso
        if self.__remotoDA:
            #self.__mntDA = self.__currDIR + "/" + data['dirDA']["mnt"]
            if data['dirDA']['protocollo'] == "smb":
                self.__protocolloDA, self.__dirDA, self.__mntDA = self.__protoSMB(data['dirDA'])
            elif data['dirDA']['protocollo'] == "sshfs":
                self.__protocolloDA, self.__dirDA, self.__mntDA = self.__protoSSH(data['dirDA'])
            os.system("mkdir -p " + self.__mntDA)
        else:
            self.__mntDA=self.__dirDA = data['dirDA']["loc_path"]
            #self.__mntDA = ""
        # ****
        if self.__remotoTO:
            #self.__mntTO = self.__currDIR + "/" + data['dirTO']["mnt"]
            if data['dirTO']['protocollo'] == "smb":
                self.__protocolloTO, self.__dirBK, self.__mntTO = self.__protoSMB(data['dirTO'])
            elif data['dirTO']['protocollo'] == "sshfs":
                self.__protocolloTO, self.__dirBK, self.__mntTO = self.__protoSSH(data['dirTO'])
            os.system("mkdir -p " + self.__mntTO)
        else:
            self.__mntTO=self.__dirBK = data['dirTO']["loc_path"]
            #self.__mntTO = ""
        # self.__mntDA = self.__currDIR + "/" + data['dirDA']["mnt"]
        # self.__mntTO = self.__currDIR + "/" + data['dirTO']["mnt"]


        self.__nome = ch
        self.__titolo =  data['titolo']
        # self._path_flog = CURRDIR + "/" + self._nome + ".log"
        self.__path_flog = self.__currDIR + "/" + self.__nome + ".log"
        # self.__flog = open(self._path_flog, "w")
        self.__do = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
        self.__latestDIR_nome = "latestDIR" + ch
        self.__nomeStatoFile = "stf.bin"
        self.__nomeTAR = self.__do + "-" + self.__nome + ".tar.gz"
        with open(self.__path_flog, "w") as flog:
            flog.write("*************** Variabili inizializzate *************\n")

    def __isMount(self, sub):
        r = subprocess.run(["df", "-a"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return sub in str(r.stdout)

    def __send_log(self, invia):
        # print("****** send_log")
        if invia and not DEBUG:
            #vmail = "mail -s  '"+self.__titolo+" - " + self.__nome + "' server.backup@itisgrassi.edu.it < " + self.__path_flog
            vmail = "echo backup | mail -r noreplay@itisgrassi.edu.it  -s  '"+self.__titolo+" - " + self.__nome + "' server.backup@itisgrassi.edu.it -A " + self.__path_flog
            os.system(vmail)
            print("MAIL INVIATA: " + vmail)

    def __monta(self,comando):
        try:
            os.system(comando)
            return ""
        except:
            return "Errore nel montaggio"


    def __inizializza_paths(self):
        with open(self.__path_flog, "a") as flog:
            if self.__remotoDA:
                flog.write("\nMonto directory da backuppare:\n\t " +
                           str(self.__protocolloDA)) # + " " + self.__dirDA + " " + self.__mntDA)
                # mntDA = self._dirBASE + "/" + self._mntDA
                if not self.__isMount(self.__mntDA):
                    '''
                    r = subprocess.run([self.__protocolloDA, self.__dirDA, self.__mntDA],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    '''
                    r = subprocess.run(self.__protocolloDA,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if r.stderr:
                        flog.write("\nERRORE: " + r.stderr.decode("utf-8"))
                        self.__send_log(True)
                        self.initOK = False
                        return False
                    '''
                    r=self.__monta(self.__protocolloDA + " " + self.__dirDA + " " + self.__mntDA)
                    if r=="":
                        flog.write("\nDirectory montata")
                    else:
                        flog.write("\n"+r)
                    '''
                else:
                    flog.write("\nDirectory GIA montata")
                # self._dirDA = mntDA
            if self.__remotoTO:
                flog.write("\nMonto directory dei backup\n\t" +
                           str(self.__protocolloTO)) #+ " " + self.__dirBK + " " + self.__mntTO)
                # mntTO = self._dirBASE + "/" + self.__mntTO
                if not self.__isMount(self.__mntTO):
                    '''
                    r = subprocess.run([self.__protocolloTO, self.__dirBK, self.__mntTO],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    '''

                    r = subprocess.run(self.__protocolloTO,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if r.stderr:
                        flog.write("\nERRORE: " + r.stderr.decode("utf-8"))
                        self.__send_log(True)
                        self.initOK = False
                        return False
                    '''
                    r=os.system(self.__protocolloTO + " " + self.__dirBK + " " + self.__mntTO)
                    if r == "":
                        flog.write("\nDirectory montata")
                    else:
                        flog.write("\n" + r)
                    '''
                else:
                    flog.write("\nDirectory GIA montata")
                # self._dirBK = mntTO

                # self._latestDIR = self.currDIR + "/" +self._dirBK+ "/latestDIR" + self._mntTO
            flog.write("\nFine inizializzazione processo")
            return True

    def __backuppa(self):
        print("Inizio backup")
        with open(self.__path_flog, "a") as flog:
            flog.write("\n*********Inizio il processo di backup************")
            #latestDIR = self.__mntTO + "/" + self.__latestDIR_nome
            latestDIR = self.__getLatest(self.__mntTO,self.__nome)
            flog.write("\nUso come base: " + latestDIR)
            # attr = '-auv --link-dest "' + latestDIR + '" --exclude=".cache" '
            attr = '-rltuv --link-dest "' + latestDIR + '" --exclude=".cache" '
            # dirBK = self.__dirBK + "/" + self.__do + "-" + self.__nome
            da = self.__mntDA
            bk = self.__mntTO + "/" + self.__do + "-" + self.__nome
            rsync = "rsync " + attr + " " + da + "/ " + bk + "  >> " + self.__path_flog
            flog.write("\n" + rsync + "\n")
        r = os.system(rsync)

        with open(self.__path_flog, "a") as flog:
            #flog.write("\nRimuovuo: " + latestDIR)
            #r = os.system("rm -rf " + latestDIR)
            # flog.write("\nNuova base: " + dirBK)
            #ln = "ln -s " + self.__do + "-" + self.__nome + " " + latestDIR
            #flog.write("\nCreo link: " + ln)
            #ros = os.system(ln)
            #flog.write("\n" + str(ros))
            #if ros != 0:
            #    flog.write("\nLink nuova base errore\n\n")
            ros = 0
            if self.__isMount(self.__mntDA):
                r = subprocess.run(["umount", self.__mntDA],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if r.stderr:
                    flog.write("\nERRORE: " + r.stderr.decode("utf-8"))
                    self.__send_log(True)
                    self.initOK = False
                    ros = 1
                flog.write("\nDirectory " + self.__mntDA + " smontata")
            if self.__isMount(self.__mntTO):
                r = subprocess.run(["umount", self.__mntTO],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if r.stderr:
                    flog.write("\nERRORE: " + r.stderr.decode("utf-8"))
                    self.__send_log(True)
                    self.initOK = False
                    ros = 1
                flog.write("\nDirectory " + self.__mntTO + " smontata")

            if ros != 0:
                flog.write("\nPROCESSO ESEGUITO CON ERRORI\n\n")
            else:
                flog.write("\nPROCESSO ESEGUITO CON SUCCESSO\n\n")

        print("Finito backup")

    def _esegui(self, ch):
        self.__inizializza_backup(ch)
        print("********************** Inizia thread: " + ch)
        if self.__inizializza_paths():
            self.__backuppa()
        self.__send_log(True)
        print("********************** fine thread")

# c = bkFile()
# c._esegui()
