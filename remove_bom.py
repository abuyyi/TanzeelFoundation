import codecs

with codecs.open("data_backup_clean.json", "r", encoding="utf-8-sig") as f:
    content = f.read()

with open("data_backup_final.json", "w", encoding="utf-8") as f:
    f.write(content)

print("BOM removed successfully")
