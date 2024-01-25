
f = open("/home/lennaert/Thesis-Lennaert-Feijtes-Safe-PDF-Redaction-Tool/src/test_cases/res.txt", "r")
lines = f.readlines()

res = {}

for lin in lines:
    splitted = lin.split("\n")[0].split(" ")
    for i in range(0, len(splitted)):
        if i == 0:
            if splitted[i] not in res:
                res[splitted[0]] = {"mani": [], "redact": []}
        elif i == 1:
            res[splitted[0]]["mani"].append(splitted[i])
        elif i == 2:
            res[splitted[0]]["redact"].append(splitted[i])


for i in res:
    print(i, res[i])