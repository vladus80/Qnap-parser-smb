#git 1
import re, os

def print_hi():

    parserQnap = ParserQnapSmb()
    print(parserQnap.getFolders())

class ParserQnapSmb:
    def __init__(self, filePathSmb='smb.conf', filePathPasswd='smbpasswd'):

        if os.path.exists(filePathSmb) & os.path.exists(filePathPasswd):
            self.filePathSmb = filePathSmb
            self.filePathPasswd = filePathPasswd
        else:
            print('Файлы ', 'не обнаружены')
            exit(0)

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
        if typeData=='write list':
            typeData = 3
        elif typeData == 'read list':
            typeData = 2
        elif typeData == 'valid users':
            typeData = 4
        elif typeData == 'invalid users':
            typeData = 1

        sections = self.__getSections()
        userFolder=[]
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
        while i<len(sections):
            section = self.__getDataSection(sections, i)
            i += 1
            if section[0] == '['+folderName+']':
                #print(folders)
                return section
                break

    # Возвращает общие папки
    def getFolders(self):
        data = re.findall(r'\[(.*)\]', open(self.filePathSmb, 'r', encoding="UTF-8").read(), flags=re.MULTILINE)
        return data[1:]

    # Возвращает список пользователей из smbpasswd
    def getUsersSmb(self):
        lines = open(self.filePathPasswd, 'r').readlines()
        userList = []

        for line in lines:
            userList.append(line.split(':')[0])
        return userList

    # Возвращает секцию со строками [название папки]-0, write list-1, read list-2, valid users-3
    # listSections - список секций
    # iter - номер в списке
    def __getDataSection(self, listSections, iter):
        data = re.findall(r'(\[.*\]|write list = .*|read list = .*|\bvalid users = .*|invalid users = .*)',
                                                                    listSections[iter], flags=re.MULTILINE)
        return data

    # Возвращает список секций из файла
    def __getSections(self):
        fileText = open(self.filePathSmb, 'r', encoding="UTF-8").read()
        sections = fileText.split('\n\n')
        return sections

    # Возвращает название общей папки без скобок
    def __getShareFolder(self, string):
        return str (string).rstrip(']').lstrip('[')

    # Возвращает список пользователей в строке getReadList
    def __getReadList(self, string):
        stringRemoveName = string[12:]
        stringRemoveCov = str(stringRemoveName).replace('"', '')
        return stringRemoveCov.split(',')

    # Возвращает список пользователей в строке getWriteList
    def __getWriteList(self, string):
        stringRemoveName = string[13:]
        stringRemoveCov = str (stringRemoveName).replace('"','')
        return stringRemoveCov.split(',')

    # Возвращает список пользователей в строке getValidUsers
    def __getValidUsers(self, string):
        stringRemoveName = string[14:]
        stringRemoveCov = str(stringRemoveName).replace('"', '')
        return stringRemoveCov.split(',')

    def __getInvalidUsers(self,string):
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
    print_hi()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
