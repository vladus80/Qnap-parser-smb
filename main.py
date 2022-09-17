# re2
import re, os
from progress.bar import IncrementalBar


def print_main():
    parserQnap = ParserQnapSmb()
    parserQnap.printMatrix()


class ParserQnapSmb:
    def __init__(self, filePathSmb='smb.conf', filePathPasswd='passwd', filePathShadow='shadow'):

        if os.path.exists(filePathSmb) & os.path.exists(filePathPasswd):
            self.filePathSmb = filePathSmb
            self.filePathPasswd = filePathPasswd
            self.filePathShadow = filePathShadow

            self.fSmbRead = open(self.filePathSmb, 'r', encoding="UTF-8").read()
            self.fShadowLines = open(self.filePathShadow, 'r', encoding="UTF-8").readlines()
            self.fPasswdLines = open(self.filePathPasswd, 'r', encoding='UTF-8').readlines()

        else:
            print('Файлы ', 'не обнаружены')
            exit(0)

    # Возвращает список пользователей из smbpasswd
    def getUsers(self):

        fPasswd = self.filePathPasswd
        linesPasswd = self.fPasswdLines # Читаем файл с пользователями
        usrDict = {} # Словарь куда будем записывать данные о пользователе
                     # структура - petrov{['Петров, Блок']}

        for line in linesPasswd:
            if int(line.split(':')[2]) > 1000: # Если > 1000 то поль-тель  не системный
                if line.split(':')[4] != 'guest':  # и если он не гость
                    userName = line.split(':')[0] # Логин -ключ словаря
                    userFIO = line.split(':')[4].split(',')[2] # ФИО пользователя
                    userStatus = self.isBlockUser(userName) # Статус блокировки
                    usrDict[userName] = [userFIO, userStatus] # Добавляем в словарь список с данными (ФИО, Статус)
                                                              # Сам ключ представляет данные Логин
        return usrDict

    # Возвращает статус (Блок или пустая строка), не заблокирован ли пользователь
    def isBlockUser(self, user):

        res = ''
        #fShadow = self.filePathShadow
        linesShadow = self.fShadowLines
        for ln in linesShadow:
            listData = ln.split(':')
            if listData[0] == user:
                if listData[1][0] == '!':
                    res = 'Блок'
                else:
                    res = ''
        return res

    # Печатает в файл матрицу
    def printMatrix(self):

        file = open('usersAccs.csv', 'w', encoding='windows-1251')
        folders = self.getFolders()
        users = self.getUsers()
        strRes = ''
        topStr = 'Логин;ФИО;Статус;' + str(folders).replace(', ', ';').replace("'", "").replace('[', '').replace(']',
                                                                                                  '') + '\n'  # заголовок
        file.write(topStr)
        print('Начинаем, ожидайте..')
        bar = IncrementalBar('Работаю', max=len(users), suffix='%(percent)d%%', color='green') # Запускаем прогресс бар
        for usr in users.keys():
            for folder in folders:
                acc = self.__isAccesUserToFolder(usr, folder)
                strRes += ';' + str(acc)
            #print(usr, ';', users[usr][0], ';', users[usr][1], strRes)
            file.write(usr + ';' + users[usr][0] + ';' + users[usr][1] + strRes + '\n')
            bar.next()
            strRes = ''
        file.close()
        bar.finish()
        print('Готово')

    # Возвращает статус пользователя к папке (Чтение, Запись, Нет доступа)
    def __isAccesUserToFolder(self, user, folder):

        # acces: 0 - нет доступа к папке; -1 доступ запрещен; 1 - только чтение; 2 - запись
        acces = 'Нет доступа'

        userData = self.getAllDataUser(user)
        writeList = userData['write list']
        readList = userData['read list']
        validUser = userData['valid users']
        invalidUser = userData['invalid users']

        if folder in writeList:
            acces = 'Запись'
        else:
            if folder in readList:
                acces = 'Только чтение'
            else:
                if folder in invalidUser:
                    acces = 'Доступ запрещен'
        return acces

    # Возвращает  все данные  по пользователю
    def getAllDataUser(self, user):
        res = dict()
        res['user'] = user
        res['write list'] = self.__getDataUser(user, 'write list')
        res['read list'] = self.__getDataUser(user, 'read list')
        res['valid users'] = self.__getDataUser(user, 'valid users')
        res['invalid users'] = self.__getDataUser(user, 'invalid users')
        return res

    # Возвращает запрашиваемые данные по имени пользователя
    # user - Имя пользователя
    # typeData - Тип запрашиваемых данных: write list, read list, valid users, invalid users
    def __getDataUser(self, user, typeData='write list'):
        typeClear = typeData
        if typeData == 'write list':
            typeData = 3
        elif typeData == 'read list':
            typeData = 2
        elif typeData == 'valid users':
            typeData = 4
        elif typeData == 'invalid users':
            typeData = 1

        sections = self.__getSections()
        userFolder = []
        i = 1
        while i < len(sections):
            section = self.__getDataSection(sections, i)
            if section[0] != '[share_geo]':
                if user in self.__getClearData(section[typeData], typeClear):
                    userFolder.append(self.__getShareFolder(section[0]))
            i += 1
        return userFolder

    #  Возвращает данные по имени общей папки, например: '[Public]'
    def getDataByFolder(self, folderName):

        sections = self.__getSections()
        i = 1
        while i < len(sections):
            section = self.__getDataSection(sections, i)
            i += 1
            if section[0] == '[' + folderName + ']':
                # print(folders)
                return section
                break

    # Возвращает общие папки из smb.conf
    def getFolders(self):
        data = re.findall(r'\[(.*)\]', self.fSmbRead, flags=re.MULTILINE)
        return data[1:]


    # Возвращает секцию со строками [название папки]-0, write list-1, read list-2, valid users-3
    # listSections - список секций
    # iter - номер в списке
    def __getDataSection(self, listSections, iter):
        data = re.findall(r'(\[.*\]|write list = .*|read list = .*|\bvalid users = .*|invalid users = .*)',
                          listSections[iter], flags=re.MULTILINE)
        return data

    # Возвращает список секций из файла
    def __getSections(self):
        fileText = self.fSmbRead
        sections = fileText.split('\n\n')
        return sections

    # Возвращает название общей папки без скобок
    def __getShareFolder(self, string):
        return str(string).rstrip(']').lstrip('[')

    # Возвращает список пользователей в строке getReadList
    def __getReadList(self, string):
        stringRemoveName = string[12:]
        stringRemoveCov = str(stringRemoveName).replace('"', '')
        return stringRemoveCov.split(',')

    # Возвращает список пользователей в строке getWriteList
    def __getWriteList(self, string):
        stringRemoveName = string[13:]
        stringRemoveCov = str(stringRemoveName).replace('"', '')
        return stringRemoveCov.split(',')

    # Возвращает список пользователей в строке getValidUsers
    def __getValidUsers(self, string):
        stringRemoveName = string[14:]
        stringRemoveCov = str(stringRemoveName).replace('"', '')
        return stringRemoveCov.split(',')

    def __getInvalidUsers(self, string):
        stringRemoveName = string[16:]
        stringRemoveCov = str(stringRemoveName).replace('"', '')
        return stringRemoveCov.split(',')

    def __getClearData(self, string, typeClear):
        if typeClear == 'write list':
            return self.__getWriteList(string)
        elif typeClear == 'read list':
            return self.__getReadList(string)
        elif typeClear == 'valid users':
            return self.__getValidUsers(string)
        elif typeClear == 'invalid users':
            return self.__getInvalidUsers(string)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/