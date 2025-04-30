import json

# Criar um json apartir de uma lista, e salvar em um arquivo .json
# with open("cache.json", "w") as f:
#     json.dump(files,f,indent=4)

# Retorna uma lista com o nome dos principais projetos
# Isso criar na gui um pre preenchimento ao digitar
def return_list_projects():
    try:
        with open("cache.json", "r") as projects:
            list_json = json.load(projects)
            return list_json
    except FileNotFoundError:
        print()
        return None
    except json.JSONDecodeError:
        print()
        return None