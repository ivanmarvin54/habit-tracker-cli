import json
from datetime import date, timedelta
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

DATA_FILE = Path(__file__).parent / "data.json"


def load_data() -> dict:
    if not DATA_FILE.exists():
        return {}
    content = DATA_FILE.read_text(encoding="utf-8").strip()
    if not content:
        return {}
    return json.loads(content)


def save_data(data: dict) -> None:
    DATA_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def add_habit(data: dict, name: str) -> None:
    if name in data:
        print(f"Привычка '{name}' уже есть")
        return
    data[name] = {"created": str(date.today()), "done_dates": []}
    print(f"Добавлено: {name}")


def mark_done(data: dict, name: str) -> None:
    if name not in data:
        print(f"Привычки '{name}' нет в списке")
        return
    today = str(date.today())
    if today in data[name]["done_dates"]:
        print("Уже отмечено сегодня")
        return
    data[name]["done_dates"].append(today)
    print(f"Отмечено: {name} ({today})")


def delete_habit(data: dict, name: str) -> None:
    if name not in data:
        print(f"Привычки '{name}' нет в списке")
        return
    del data[name]
    print(f"Удалено: {name}")


def list_habits(data: dict) -> None:
    """Показывает все привычки в виде красивой таблицы."""
    if not data:
        console.print("[yellow]Список пуст[/yellow]")
        return
    table = Table(titile="Твои привычки", show_header=True, header_style="bold magenta")
    table.add_column("№", style="dim")
    table.add_column("Название")
    table.add_column("Выполнено", justify="right")
    for i, (name, info) in enumerate(data.items(), 1):
        count = len(info["done_dates"])
        table.add_row(str(i), name, f"{count} раз")
        console.print(table)


def calculate_streak(done_dates: list[str]) -> int:
    """Считает, сколько дней подряд выполнялась привычка (включая сегодня)."""
    if not done_dates:
        return 0
    
    # Превращаем строки в объекты дат и сортируем по убыванию (сначала свежие)
    dates = sorted([date.fromisoformat(d) for d in done_dates], reverse=True)
    
    today = date.today()
    
    # Если последнее выполнение было не сегодня и не вчера, то серия прервалась (0)
    if dates[0] != today and dates[0] != today - timedelta(days=1):
        return 0
        
    streak = 1
    for i in range(len(dates) - 1):
        # Если разница между соседними датами ровно 1 день — серия продолжается
        if (dates[i] - dates[i+1]).days == 1:
            streak += 1
        else:
            break
    return streak


def show_stats(data: dict) -> None:
    if not data:
        print("Нет привычек для статистики.")
        return
    
    print("\n--- СТАТИСТИКА ---")
    for name, info in data.items():
        total = len(info["done_dates"])
        streak = calculate_streak(info["done_dates"])
        
        # Считаем процент выполнения
        created_date = date.fromisoformat(info["created"])
        total_days = (date.today() - created_date).days + 1
        percent = int((total / total_days) * 100)
        
        print(f"\n{name}")
        print(f"  Всего выполнений: {total}")
        print(f"  Текущая серия: {streak} дн.")
        print(f"  Выполнено: {percent}% с {info['created']}")


def main() -> None:
    data = load_data()

    while True:
        console.print(Panel.fit(
            "[bold cyan]ТРЕКЕР ПРИВЫЧЕК[/bold cyan]\n\n"
            "[green]1.[/green] Показать привычки\n"
            "[green]2.[/green] Добавить привычку\n"
            "[green]3.[/green] Отметить выполнение\n"
            "[green]4.[/green] Удалить\n"
            "[green]5.[/green] Выход\n"
            "[green]6.[/green] Статистика",
            title="Меню",
            border_style="blue"
        ))
       

        choice = input("Твой выбор: ").strip()

        if choice == "1":
            list_habits(data)
            
        elif choice == "2":
            name = input("Название привычки: ").strip()
            if name:
                add_habit(data, name)
                save_data(data)
                
        elif choice == "3":
            if not data:
                print("Список пуст, сначала добавь привычку")
                continue
            name = input("Какую привычку отметить? ").strip()
            if name:
                mark_done(data, name)
                save_data(data)
                
        elif choice == "4":
            if not data:
                print("Список пуст, нечего удалять")
                continue
            list_habits(data) # Показываем список перед удалением
            num_str = input("Введи номер привычки для удаления: ").strip()
            
            if not num_str.isdigit():
                print("Нужно ввести число!")
                continue
                
            num = int(num_str)
            if num < 1 or num > len(data):
                print("Неверный номер")
                continue
                
            # Достаем имя по номеру и удаляем
            name = list(data.keys())[num - 1]
            delete_habit(data, name)
            save_data(data)
            
        elif choice == "5":
            save_data(data)
            console.print("[bold red]Пока![/bold red]")
            break
            
        elif choice == "6":
            show_stats(data)
            
        else:
            print("Не понял, попробуй снова")


if __name__ == "__main__":
    main()