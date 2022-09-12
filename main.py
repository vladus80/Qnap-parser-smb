#git 1
import re
def print_hi():

    #print(getValidUsers(cont[3]))
    #print (getDataByFolder('[Проектно-Строительные работы]'))
    #print (getDataByUser('andreishmelev', 'read list'))
    #print(getDataSection(getSections(),1))
    #print(getUserSmb())
    # for user in getUserSmb():
    #     if len(getDataByUser(user, 'write list'))>0:
    #         print (user, getDataByUser(user, 'write list'))
    #print(getAllDataUserByTypeData())
    userData = getAllDataUserByTypeData('admin')
    #print(userData)

    for user in getUsersSmb():
        userData = getAllDataUserByTypeData(user)
        if len(userData['read list'])!=0:
            print(userData['user'], userData['read list'])

# Возвращает  все данные  по пользователю
def getAllDataUserByTypeData(user):

    res = dict()
    res['user'] = user
    res['write list'] = getDataByUser(user, 'write list')
    res['read list'] = getDataByUser(user, 'read list')
    res['valid users'] = getDataByUser(user, 'valid users')
    res['invalid users'] = getDataByUser(user, 'invalid users')

    return res

# Возвращает запрашиваемые данные по имени пользователя
# user - Имя пользователя
# typeData - Тип запрашиваемых данных: write list, read list, valid users, invalid users
def getDataByUser(user, typeData='write list'):
    typeClear = typeData
    if typeData=='write list':
        typeData = 3
    elif typeData == 'read list':
        typeData = 2
    elif typeData == 'valid users':
        typeData = 4
    elif typeData == 'invalid users':
        typeData = 1

    sections = getSections()
    userFolder=[]
    i = 1
    while i < len(sections):
        section = getDataSection(sections, i)
        if section[0] != '[share_geo]':
            #print(section[0], getWriteList(section[2]))
            if user in getClearData(section[typeData], typeClear):
                userFolder.append(getShareFolder(section[0]))
        i += 1
    return userFolder

#  Возвращает данные по имени общей папки, например: '[Public]'
def getDataByFolder(folderName):
    sections = getSections()
    i = 1
    while i<len(sections):

        section = getDataSection(sections, i)
        i += 1
        if section[0] == folderName:
            #print(folders)
            return section
            break

# Возвращает секцию со строками [название папки]-0, write list-1, read list-2, valid users-3
# listSections - список секций
# iter - номер в списке
def getDataSection(listSections, iter):
    data = re.findall(r'(\[.*\]|write list = .*|read list = .*|\bvalid users = .*|invalid users = .*)',
                                                                listSections[iter], flags=re.MULTILINE)
    return data

# Возвращает список секций из файла
def getSections(fPath = 'smb.conf'):
    fileText = open(fPath, 'r', encoding="UTF-8").read()
    sections = fileText.split('\n\n')
    return sections

# Возвращает список пользователей из smbpasswd
def getUsersSmb(fPath='smbpasswd'):
    lines = open(fPath,'r').readlines()
    userList = []

    for line in lines:
      userList.append(line.split(':')[0])

    return userList

# Возвращает название общей папки без скобок
def getShareFolder(string):
    return str (string).rstrip(']').lstrip('[')

# Возвращает список пользователей в строке getReadList
def getReadList(string):
    stringRemoveName = string[12:]
    stringRemoveCov = str(stringRemoveName).replace('"', '')
    return stringRemoveCov.split(',')

# Возвращает список пользователей в строке getWriteList
def getWriteList(string):
    stringRemoveName = string[13:]
    stringRemoveCov = str (stringRemoveName).replace('"','')
    return stringRemoveCov.split(',')

# Возвращает список пользователей в строке getValidUsers
def getValidUsers(string):
    stringRemoveName = string[14:]
    stringRemoveCov = str(stringRemoveName).replace('"', '')
    return stringRemoveCov.split(',')

def getInvalidUsers(string):
    stringRemoveName = string[16:]
    stringRemoveCov = str(stringRemoveName).replace('"', '')
    return stringRemoveCov.split(',')

def getClearData(string, typeClear):
    if typeClear == 'write list':
        return getWriteList(string)
    elif typeClear == 'read list':
        return getReadList(string)
    elif typeClear == 'valid users':
        return getValidUsers(string)
    elif typeClear == 'invalid users':
        return getInvalidUsers(string)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
