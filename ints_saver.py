from json import dump

integers: dict[str, int] = {}
print()
file_name = input("file name:  ")
name = input("name:  ")
integer = int(input("int:  "))
integers[name] = integer
print()
while True:
    name = input("name:  ")
    if name == "!":
        break
    integer = int(input("int:  "))
    integers[name] = integer
    print()

with open(f"{file_name}.json", "w") as file:
    dump(integers, file)
