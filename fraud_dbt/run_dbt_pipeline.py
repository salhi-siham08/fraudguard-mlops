import subprocess
import sys

commands = [
    ["dbt", "debug"],
    ["dbt", "run"],
    ["dbt", "test"],
    ["dbt", "docs", "generate"]
]

for command in commands:
    print("\n" + "=" * 60)
    print("Exécution :", " ".join(command))
    print("=" * 60)

    result = subprocess.run(command)

    if result.returncode != 0:
        print(f"\nErreur lors de l'exécution de : {' '.join(command)}")
        sys.exit(result.returncode)

print("\nToutes les étapes dbt ont été exécutées avec succès !")
print("Pour consulter la documentation, exécute ensuite :")
print("dbt docs serve")