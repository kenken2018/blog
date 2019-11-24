import os


BASE_DIR = "./posts"
posts = []


def extract_title(file: str) -> str:
    with open("{}/{}".format(BASE_DIR, file), "r") as f:
        for line in f.readlines():
            posts.append((file, line.strip()))
            break


for _, _, files in os.walk(BASE_DIR):
    for file in files:
        if not file.startswith("."):
            extract_title(file)


pairs = [(post[0], post[1]) for post in posts]
pairs = sorted(pairs, key=lambda x: x[0])


result = []
for pair in pairs:
    filename, title = pair
    result.append("* [{}]({}/{})\n".format(title[2:], BASE_DIR, filename))


readme_content = ""
with open("README.md", "r") as f:
    for line in f.readlines():
        readme_content += line
        if line == "### 文章列表\n":
            readme_content += "\n"
            break


readme_content += "".join(result)
with open("README.md", "w+") as f:
    f.write(readme_content + "\n")
