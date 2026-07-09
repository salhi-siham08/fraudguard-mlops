import subprocess
import webbrowser
import time

commands = [
    ["dbt", "debug"],
    ["dbt", "run"],
    ["dbt", "test"],
    ["dbt", "docs", "generate"]
]

for command in commands:
    subprocess.run(command, check=True)

print("Ouverture de la documentation...")

subprocess.Popen(["dbt", "docs", "serve"])

time.sleep(3)

webbrowser.open("http://localhost:8080")
