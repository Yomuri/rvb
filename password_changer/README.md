Sean Ham

# passtool.py
This python script connects to servers using provided login info and changes passwords using a provided password list.

How to use:

python's pexpect module must be installed on the control device
The file can be run with:
passtool.py inventory password_list

inventory is expected to be in the format:
{host} {user} {password (optional)}
