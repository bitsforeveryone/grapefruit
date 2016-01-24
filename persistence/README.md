# Persistence Tools
#### mothership.py
- serves as a host for backdoor jobs running on pwned clients
- does port hopping on network for obfuscation
- gives python remote code execution

#### backdoor.py
- calls out to mothership on STATIC_PORT
- migrates according to the mothership
- executes python commands
