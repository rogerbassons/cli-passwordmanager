def getPasswords():
    passwords = []

    for x in range(0,100):
        i = str(x)
        passwords.append({"group": "G" + i, "name": "Site" + i, "user": "user" + i, "password": "pass" + i})

    return passwords
