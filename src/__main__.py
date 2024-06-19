import time
from getpass import getpass

from cryptography.hazmat.primitives.asymmetric import rsa

from serialize import Key, File


def key_gen() -> None:
    passwd = getpass("Enter password for your key: \n")
    passwd_match = getpass("Enter it again to confirm: \n")
    passwd_succ, passwd_err = Key.pkey_password_match(passwd, passwd_match)
    if not passwd_succ:
        print(passwd_err)
        time.sleep(0.5)
        exit()
    file = input("Enter file name where to store key: ex. priv.key\n")
    print("Generating private_key...")
    time.sleep(0.5)
    priv = Key.generate_pkey(passwd_succ)
    print("Saving key file...")
    time.sleep(0.5)
    File().save_keyfile(file, priv)


def store_password(pubkey: rsa.RSAPublicKey) -> None:
    service = input("Enter service name: ")
    username = input("Enter username: ")
    password = getpass("Enter password: ")
    file_data = Key().encrypt_message(
        service,
        username,
        password,
        pubkey
    )
    File().write_storefile(file_data)
    return file_data


def search_password(privkey: rsa.RSAPrivateKey) -> None:
    data = File().read_storefile()
    passwords = Key().decrypt_message(data, privkey)
    service = input("Enter the service of the password that you would to find:\n")
    passwd_found = None
    print("Searching...")
    time.sleep(0.5)
    for passwd in passwords:
        if service != passwd['service']:
            continue
        else:
            passwd_found = passwd['password']
            username = passwd['username']
    if passwd_found is None:
        print("There is not a stored password for this service\nExit...")
        time.sleep(0.5)
        return None
    print(f"Username and password for service {service} are:\nusername: {username}\npassword: {passwd_found}")


def update_password(privkey: rsa.RSAPrivateKey, pubkey: rsa.RSAPublicKey) -> None:
    data = File().read_storefile()
    passwords = Key().decrypt_message(data, privkey)
    service = input("Enter the service of the password that you would to update:\n")
    service_found = None
    print("Searching...")
    time.sleep(0.5)
    for passwd in passwords:
        if service != passwd['service']:
            continue
        else:
            service_index = passwords.index(passwd)
            service_found = passwd
    if service_found is None:
        print("No service found.\nExit...")
        time.sleep(0.5)
        return None
    new_username = input("Enter the new username: ")
    new_password = getpass("Enter the new password: ")
    service_found["username"] = new_username
    service_found["password"] = new_password
    passwords[service_index] = service_found
    print("Updating...")
    time.sleep(0.5)
    print("Writing on file...")
    time.sleep(0.5)
    File().update_password_file(passwords, pubkey)
    print("Successfuly updated.")
    time.sleep(0.5)


def list_passwords(privkey: rsa.RSAPrivateKey) -> None:
    data = File().read_storefile()
    print(Key().decrypt_message(data, privkey))


def main():
        try:
            starter_choice = input("Do you already have a key to access? type y/n\n").upper()
            match starter_choice:
                case "N":
                    key_gen()
                case "Y":
                    print("Going next...")
                case _:
                    print("Invalid choice, exit...")
                    time.sleep(0.5)
                    exit()
            time.sleep(0.3)
            key_file = input("Enter key file name: ")
            key_passwd = getpass("Enter key password: ")
            pkey = Key().load_key(key_file, key_passwd)
            pubkey = pkey.public_key()
            time.sleep(0.3)
            while True:
                choice = int(input("What do you want do?\n1. Search a password.\n2. Store a password\n3. Change a password\n4. List all passwords\n5. Exit\n"))
                match choice:
                    case 1:
                        search_password(pkey)
                    case 2:
                        store_password(pubkey)
                    case 3:
                        update_password(pkey, pubkey)
                    case 4:
                        list_passwords(pkey)
                    case 5:
                        print("Exit...")
                        time.sleep(0.5)
                        exit()
                    case _:
                        print("Invalid choice, exit...")
                        time.sleep(0.5)
                        exit()
        except KeyboardInterrupt:
            print("Exit...")
            time.sleep(0.5)
            exit()
    
            

if __name__ == "__main__":
    main()