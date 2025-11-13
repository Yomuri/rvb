#!/bin/python3
import sys, pexpect

ANSI_GREEN = '\033[32m'
ANSI_RED = '\033[31m'
ANSI_END = '\033[0m'

def change_password(host, user, passwd, new_passwd):
	# Spawn SSH + passwd command
	child = pexpect.spawn(f"ssh {user}@{host} passwd")
	child.timeout=3
	print(f'{host}:{user} attempting ssh')
	# First, SSH login prompt
	i = child.expect([r"user@.*'s password:", pexpect.EOF, pexpect.TIMEOUT])
	child.sendline(passwd)
	print(f'{host}:{user} sent password \'{passwd}\'')

	# Expect current password prompt
	child.expect(r"[Cc]urrent.*password:")
	child.sendline(passwd)
	print(f'{host}:{user} sent password \'{passwd}\' for passwd')

	# Expect new password prompt
	child.expect("New password:")
	child.sendline(new_passwd)
	print(f'{host}:{user} sent new password \'{new_passwd}\' for passwd')

	# Expect confirmation prompt
	child.expect("Retype new password:")
	child.sendline(new_passwd)
	print(f'{host}:{user} retyped new password \'{new_passwd}\' for passwd')

	# Wait for command to finish
	child.expect(pexpect.EOF)
	output = child.before.decode()
	return output

def run(data, passwords):
	log = []
	for entry in data:
		host = entry[0]
		user = entry[1]
		passwd = entry[2] if len(entry) > 2 else None
		passwd_index = 0
		while passwords[passwd_index] == passwd and len(passwords) > passwd_index + 1:
			passwd_index += 1
		new_passwd = passwords[passwd_index]
		try:
			result = change_password(host, user, passwd, new_passwd)
			if 'success' in result:
				log.append((host, user, new_passwd, f'{ANSI_GREEN}{host}:{user}:{new_passwd}{ANSI_END}'))
				passwords.remove(new_passwd)
			else:
				log.append((host, user, passwd, f'{ANSI_RED}{host}:{user}:{passwd}{ANSI_END}'))
		except:
			print('SSH session ended unexpectedly')
			log.append((host, user, passwd, f'{ANSI_RED}{host}:{user}:{passwd}{ANSI_END}'))

	return log

def get_data(path):
	content = []
	with open(path, 'r') as file:
		for line in file:
			content.append(line.strip().split(' '))
	return content

def get_passwords(path):
	content = []
	with open(path, 'r') as file:
		for line in file:
			content.append(line.strip())
	return content

def write_data(data_path, data):
	with open(data_path, 'w') as file:
		for host, user, passwd, info in data:
			content = f'{host} {user} {passwd}\n'
			file.write(content)
			print(info)

def main():
	data_path = sys.argv[1]
	data = get_data(data_path)
	passwords = get_passwords(sys.argv[2])
	data = run(data, passwords)
	write_data(data_path, data)

if __name__ == '__main__':
	main()
