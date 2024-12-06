import os
import subprocess
import argparse


def get_commit_dependencies(repo_path, file_name):
    """
    Получает список зависимостей (родительские коммиты) для каждого коммита,
    включая дату, время и автора.
    :param repo_path: Путь к репозиторию.
    :param file_name: Имя файла, для которого строится граф зависимостей.
    :return: Список кортежей (commit_info, [parent_info]).
    """
    try:
        # Получаем лог изменений для файла с данными: хеш, родители, автор, дата
        result = subprocess.run(
            [
                "git", "-C", repo_path, "log", 
                "--pretty=format:%H|%P|%an|%ad",
                "--date=short", "--", file_name
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            raise Exception(f"Ошибка выполнения команды git: {result.stderr}")

        dependencies = []
        for line in result.stdout.strip().split("\n"):
            parts = line.split("|")
            commit_hash = parts[0]
            parents_hashes = parts[1].split() if parts[1] else []
            author = parts[2]
            date_time = parts[3]
            commit_info = f"{date_time} - {author}"
            parents_info = [
                f"{date_time} - {author}" for parent in parents_hashes
            ]  # Заменяем на реальный формат, если у родителей есть отдельные метаданные
            dependencies.append((commit_info, parents_info))

        return dependencies

    except Exception as e:
        raise RuntimeError(f"Не удалось получить зависимости: {e}")


def generate_mermaid_code(dependencies):
    """
    Генерирует код Mermaid для визуализации зависимостей коммитов.
    :param dependencies: Список зависимостей в формате (commit_info, [parent_info]).
    :return: Строка с кодом Mermaid.
    """
    mermaid_code = "graph TD\n"
    for commit, parents in dependencies:
        for parent in parents:
            mermaid_code += f'    "{parent}" --> "{commit}"\n'  # Указываем зависимость от родителя к коммиту
    return mermaid_code


def main():
    # Парсим аргументы командной строки
    parser = argparse.ArgumentParser(description="Визуализатор графа зависимостей коммитов.")
    parser.add_argument("--repo_path", required=True, help="Путь к анализируемому репозиторию.")
    parser.add_argument("--output_file", required=True, help="Путь к выходному файлу для сохранения графа.")
    parser.add_argument("--file_name", required=True, help="Имя файла для анализа зависимостей.")

    args = parser.parse_args()

    # Проверяем, что репозиторий существует
    if not os.path.exists(args.repo_path):
        raise FileNotFoundError(f"Репозиторий не найден: {args.repo_path}")

    # Получаем зависимости для указанного файла
    dependencies = get_commit_dependencies(args.repo_path, args.file_name)

    # Генерация Mermaid кода
    mermaid_code = generate_mermaid_code(dependencies)

    # Сохраняем Mermaid код в файл
    with open(args.output_file, 'w') as f:
        f.write(mermaid_code)

    print(f"Граф зависимостей сохранён в файл: {args.output_file}")
    print("\nСодержимое графа Mermaid:\n")
    print(mermaid_code)


if __name__ == "__main__":
    main()
