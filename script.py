import pexpect
from getpass import getpass
import string


def main():
    # pegar o user e senha
    user = input("Usuário: ")
    senha = getpass(prompt="Senha: ")

    # diretórios e arquivos utilizados
    entradasDir = "entradas"
    #filtrosFile = entradasDir  +"/" + "filtros"
    ipFile = entradasDir + "/" + "ips"
    promptsFile = entradasDir + "/" + "prompts"
    commandsFile = entradasDir + "/" + "comandos"
    commandsCisco = entradasDir + "/" + "comandosCisco"
    commands2530 = entradasDir + "/" + "comandos2530"
    
    # iterando no arquivo que contém os ips dos switches
    ips = open(ipFile, "r")
    #saida = ""
    for ip in ips.read().split("\n"):
        print(f"Iterando em {ip}")
        try:
            tabTemp = iteraSwitches(ip, user, senha, promptsFile, commandsFile, commandsCisco, commands2530)
            #hostname = getHostname(tabTemp)
            #tabTemp = filtraTexto(tabTemp, filtrosFile)
            #saida += f"{hostname} - {ip}\n"
            #for x in tabTemp.split("\n"):
            #    print(x)
            #    for y in x:
            #        saida += y[:-1] + "\n"
                    #print(y)
            logFile = open(f"log/{ip}.log", 'w')
            #logFile.write(f"{ip}\n" + str(tabTemp))
            logFile.write(tabTemp)
            logFile.close()
        except:
            print(f"Ip {ip} não acessado")
    ips.close()
    #print(saida)
    #print(tabTemp)
    #outputFile = open("portasBixadas.txt", 'w')
    #outputFile.write(saida)
    #outputFile.close()
    return


def getHostname(texto):
    temp = ""
    for linha in texto.split("\n"):
        if linha[0] == "<":
            for letra in linha:
                if letra not in (string.ascii_uppercase + string.punctuation + string.digits):
                    return temp[1:]
                temp += letra
    return temp


def filtraTexto(entrada, filtrosFile):
    tabTemp = entrada.split("\n")
    saida = []
    k = 0 # contador de condições, se chegar a 2 o input não entra na tabela
    print("Filtrando o texto")
    for i in range(len(tabTemp)):
        if "GigabitEthernet" in tabTemp[i] and "Administratively" not in tabTemp[i] and 'Description' not in tabTemp[i]: 
            temp = [tabTemp[i]]
            for j in range(i+1, len(tabTemp)):
                if "GigabitEthernet" in tabTemp[j] and 'Description' not in tabTemp[j]:
                    break
                if validaLinha(filtrosFile, tabTemp[j]): 
                    temp.append(tabTemp[j])
                if ' 0 input errors'  in tabTemp[j] or ' 0 output errors' in tabTemp[j]:
                    k+=1
                i+=1
            if k < 2:
                saida.append(temp)
            k = 0
            '''tá salvando temporário as strings filtradas de uma interface à outra, agora é só verificar se tem tudo zerado pra não gravar'''
    return saida


def loginSpecial(arquivo, child):
    f = open(arquivo, 'r')
    comandos = f.read()
    comandos = comandos.split("\n")
    i = 0
    while i < len(comandos):
        child.sendline(comandos[i])
        child.expect(comandos[i+1])
        i += 2


def iteraSwitches(ip, user, senha, promptsFile, commandsFile, commandsCisco, commands2530):
    child = pexpect.spawn(f"ssh {user}@{ip}", echo=True)
    child.expect("assword:")
    child.sendline(senha)
    print("Mandou o password!")
    promptsList = getPrompts(promptsFile)
    prompt = child.expect(promptsList)
    temp = ""

    for i in range(len(promptsList)):
        if prompt == i:
            print(f"Detectou o {promptsList[i][4:-4]}")
            if i == 0: # comandos especiais do 1910, o resto segue igual
                loginSpecial("entradas/login1910", child)
            if i == 2: # se for switch da cisco
                temp = mandaComandos(commandsCisco, "(?i)#", child)
                print("Mandou os comandos!")
                child.sendline("exit\r")
            elif i == 5: # 2530, os poe
                child.expect("(?i)continue")
                child.sendline("\r")
                temp = mandaComandos(commands2530, "(?i)#", child)
                print("Mandou os comandos!")
                child.sendline("quit\r")
                child.expect("(?i)>")
                child.expect("(?i)?")
                child.sendline("quit\r")
                child.sendline("y\r")
            else:
                temp = mandaComandos(commandsFile, "(?i)>", child)
                print("Mandou os comandos!")
                child.sendline("quit\r")
            child.expect(pexpect.EOF)
    return temp


def validaLinha(filtrosFile, linha):
    f = open(filtrosFile, 'r')
    filtros = f.read().split('\n')[:-1]
    print(filtros)
    f.close()
    for x in filtros:
        if x in linha and "Description" not in linha:
            return True
    return False


def getPrompts(file):
    f = open(file, 'r')
    lista = []
    for prompt in f.readlines():
        lista.append(prompt[:-1])
    return lista


def mandaComandos(file, prompt, child):
    f = open(file, 'r')
    comandos = f.read().split("\n")
    text = ""
    for comando in comandos:
        child.expect(prompt)
        child.send(comando+"\r")
        text += str(child.before, "utf-8")
    return text


main()
