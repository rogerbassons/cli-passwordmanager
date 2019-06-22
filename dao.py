def getPasswords():
    passwords = []

    for x in range(0,100):
        i = str(x)
        passwords.append({"group": "G" + i, "name": "Site" + i, "user": "user" + i, "password": "pass" + i, "info": "Bla bla bla... " + i, "project": "Proj" + i})

    return passwords
