# *************************************************************************
## CREATO DA ORTU prof. DANIELE
## daniele.ortu@itisgrassi.edu.it

# from danieleRSINK import tbk
import os
# import ast
import subprocess
from datetime import datetime
import shutil

DEBUG = False


class bkFile():
    def __init__(self, bks, altro, cdir):
        self._bks, self._altro = bks, altro
        self.__currDIR = cdir
    def __isnumeric(self,s):
        try:
            n = int(s)
            return n
        except:
            return 0
    def __get_spazio(self, ltdir, da, a,mnta):
        if ltdir:
            rsync = ["rsync","-navh","--link-dest",ltdir, da, a]
        else:
            rsync = ["rsync", "-navh", da, a]
        r = subprocess.run(rsync, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if r.stderr:
            return True, r.stderr

        s = str(r.stdout)
        i = s.find("total size is ")
        if i == -1:
            return True, "Non trovo total size"
        s = s[i + len("total size is "):]
        print(s)
        tot = ""
        for c in s:
            if c == " ":
                break;
            elif c == ',':
                tot += "."
            else:
                tot += c
        m = 1
        if tot[-1] == 'K':
            m = 2 ** 10
        elif tot[-1] == 'M':
            m = 2 ** 20
        elif tot[-1] == 'G':
            m = 2 ** 30
        elif tot[-1] == 'T':
            m = 2 ** 40

        tot = int(float(tot[:-1])) * m

        total, used, free = shutil.disk_usage(mnta)
        '''
        print("Total: %d GiB" % (total//2**30))
        print("Used: %d GiB" % (used//2**30))
        print("Free: %d GiB" % (free))	
        '''
        # spazio = tot - free
        if tot  > free:
            return True, "spazio disco insufficiente\n"+ \
                    "backup:  "+ str(tot)+"\n" + \
                    "libero: " + str(free) + "\n"
        return False, f'Verrano backuppati: {tot//2**20}MB\n' + f'libero: {free//2**20}MB'
    def __lista_file(self, rootdir, nome):
        d = []
        for file in os.listdir(rootdir):
            di = os.path.join(rootdir, file)
            if os.path.isdir(di):
                if di[len(di)-len(nome):] == nome:
                    d.append(di)
        return d

    def __rimuovi(self, root_dir, nome, max_bk):
        if max_bk == 0:
            return
        lst_bk = self.__lista_file(root_dir, nome)
        print(lst_bk)
        i = len(lst_bk)-max_bk
        if i > 0:
            for i in range(0, i):
                os.system("rm -rf " + lst_bk[i])
    def __getLatest(self, rootdir, nome):
        #s = "gigi"
        #rootdir = '/home/daniele/Scrivania/repository-git/test'
        '''
        d = []
        for file in os.listdir(rootdir):
           di = os.path.join(rootdir, file)
           if os.path.isdir(di):
              if di[len(di)-len(nome):] == nome:
                 d.append(di)
        '''
        d = self.__lista_file(rootdir, nome)
        if len(d) == 0:
          # return rootdir
            return ""
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
        self.__numeroBK = data['numeroBK']
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
                    r = subprocess.run(self.__protocolloDA,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if r.stderr:
                        flog.write("\nERRORE: " + r.stderr.decode("utf-8"))
                        # self.__send_log(True)
                        self.initOK = False
                        return False
                    flog.write("\nDirectory montata")
                else:
                    flog.write("\nDirectory GIA montata")
                # self._dirDA = mntDA
            if self.__remotoTO:
                flog.write("\nMonto directory dei backup\n\t" +
                           str(self.__protocolloTO)) #+ " " + self.__dirBK + " " + self.__mntTO)
                # mntTO = self._dirBASE + "/" + self.__mntTO
                if not self.__isMount(self.__mntTO):
                    r = subprocess.run(self.__protocolloTO,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if r.stderr:
                        flog.write("\nERRORE: " + r.stderr.decode("utf-8"))
                        # self.__send_log(True)
                        self.initOK = False
                        return False
                    flog.write("\nDirectory montata")
                else:
                    flog.write("\nDirectory GIA montata")

            flog.write("\nFine inizializzazione processo")
            return True
    def __backuppa(self):
        print("Inizio backup")
        with open(self.__path_flog, "a") as flog:
            flog.write("\n*********Inizio il processo di backup************")
            #latestDIR = self.__mntTO + "/" + self.__latestDIR_nome
            latestDIR = self.__getLatest(self.__mntTO, self.__nome)
            flog.write("\nUso come base: " + latestDIR)
            # attr = '-auv --link-dest "' + latestDIR + '" --exclude=".cache" '
            attr = '-rltu --link-dest "' + latestDIR + '" --exclude=".cache" '
            # dirBK = self.__dirBK + "/" + self.__do + "-" + self.__nome
            da = self.__mntDA
            bk = self.__mntTO + "/" + self.__do + "-" + self.__nome

            err, msg = self.__get_spazio(latestDIR, da, bk,self.__mntTO)
            if err:
                flog.write("\nERRORE __getspazio: " + str(msg))
                # self.__send_log(True)
                self.initOK = False
                return False

            flog.write("\n" + msg)
            # rsync = "rsync " + attr + " " + da + "/ " + bk + "  >> " + self.__path_flog
            rsync = "rsync " + attr + " " + da + "/ " + bk
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
                    # self.__send_log(True)
                    self.initOK = False
                    ros = 1
                flog.write("\nDirectory " + self.__mntDA + " smontata")
            if self.__isMount(self.__mntTO):
                r = subprocess.run(["umount", self.__mntTO],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if r.stderr:
                    flog.write("\nERRORE: " + r.stderr.decode("utf-8"))
                    # self.__send_log(True)
                    self.initOK = False
                    ros = 1
                flog.write("\nDirectory " + self.__mntTO + " smontata")

            if ros != 0:
                flog.write("\nPROCESSO ESEGUITO CON ERRORI\n\n")
            else:
                self.__rimuovi(self.__mntTO, self.__nome, self.__isnumeric(self.__numeroBK))
                flog.write("\nPROCESSO ESEGUITO CON SUCCESSO\n\n")

        print("Finito backup")
    def _esegui(self, ch):
        self.__inizializza_backup(ch)
        print("********************** Inizia thread: " + ch)
        if self.__inizializza_paths():
            self.__backuppa()
        #else:
        #    print("Errore nell'inizializzazione")
        self.__send_log(True)
        print("********************** fine thread")

# c = bkFile()
# c._esegui()
