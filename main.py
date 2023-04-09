from random import choice, randint
import tkinter as tk
from tkinter import scrolledtext
import tkinter.simpledialog as sd


# открываем новый файл для записи
with open('tasks.txt', 'w') as file:
    # записываем в файл
    file.write("1 #%# Матан #%# Найти f'(2) для f(x) = x #%# 1$$$")
    file.write('2 #%# Матан #%# Разложите f(x) = sin(x) в ряд Маклорена до o(x) #%# sin(x) = x + o(x^2)$$$')


number_of_tasks = 2
paused = False
new_timer = False
time_left = None
current_category = None
current_task = None
upper_step = 0.05
left_step = 0.05
width_btn1 = 0.40
height_btn1 = 0.10
width_btn2 = 0.60
height_btn2 = 0.20
font_size = 16
text_width = 0.90
text_height = 0.30
timer_width = 0.45
timer_height = 0.40
start_btn_width=0.20
window_size = "600x400"
categories = []
tasks = dict()

with open("tasks.txt", "r") as f:
    text = f.read()
    lst = text.split("$$$")
    lst.pop(-1)
    for i in lst:
        category, problem, answer = i.split(" #%# ")[1], i.split(" #%# ")[2], i.split(" #%# ")[3]
        if category not in categories:
            categories.append(category)
            tasks[category] = [(problem, answer)]
        tasks[category].append((problem, answer))


def show_answer(current_category, current_task):
    if answer_btn['text'] == 'ответ':
        answer_btn['text'] = tasks[current_category][current_task][1]
        return
    answer_btn['text'] = 'ответ'


def new():
    global current_task, current_category
    current_category = choice(categories)
    current_task = randint(0, len(tasks[current_category]) - 1)
    # Изменить текст задачи
    text_widget.delete(1.0, tk.END)
    text_widget.insert(tk.END, tasks[current_category][current_task][0])


def add_new_problem():
    global number_of_tasks
    # создаем диалоговое окно с полем ввода текста
    category = sd.askstring("Enter text", "Тема задачи")
    problem = sd.askstring("Enter text", "Текст задачи")
    answer = sd.askstring("Enter text", "Ответ на задачу")

    # если пользователь ввел текст, то выводим его в консоль
    if category is not None and problem is not None and answer is not None:
        number_of_tasks += 1
        with open('tasks.txt', 'w') as file:
            file.write(f'{number_of_tasks} #%# {category} #%# {problem} #%# {answer}$$$')
        if category not in categories:
            categories.append(category)
            tasks[category] = [(problem, answer)]
        else:
            tasks[category].append((problem, answer))


# обновляем значение в Label с каждой секундой
def update_label():
    global time_left
    time_label.config(text=f"Time remaining: {time_left} s")
    time_left -= 1
    if time_left >= 0 and not paused:
        window.after(1000, update_label)
    elif time_left < 0:
        time_label.config(text="Time's up!")
        pause_resume_button.config(state='disabled')


# функция, которая начинает отсчет времени
def start_timer():
    global new_timer, paused, time_left
    pause_resume_button.config(state='normal')
    pause_resume_button.config(text='Pause')
    # получаем время из виджета Entry и преобразуем его в целое число
    if not new_timer or paused or time_left < 0:
        time_left = int(time_entry.get())
        paused = False
        update_label()
    new_timer = True


# функция, которая останавливает и запускает таймер
def pause_resume_timer():
    global paused
    paused = not paused
    if paused:
        pause_resume_button.config(text='Resume')
    else:
        pause_resume_button.config(text='Pause')
        update_label()


# Создаем новое окно
window = tk.Tk()
window.title("Math Trainer")
window.geometry(window_size)
window.resizable(width=False, height=False)


# Создаем текстовое поле, в котором будет текст задачи
text_widget = scrolledtext.ScrolledText(window, wrap=tk.WORD, font=("Courier", font_size))
text_widget.place(relx=left_step, rely=upper_step, relwidth=text_width, relheight=text_height)


# Вводим приветственное сообщение
text_widget.insert(tk.END, "Привет, это тренажер для решения математических задач. Чтобы получить новую задачу"
                           " нажми кнопку \"новая задача\"")


# Создаем кнопку для просмотра ответа
answer_btn = tk.Button(window, text="ответ", command=lambda: show_answer(current_category, current_task))
answer_btn.place(relx=left_step, rely=(text_height + 2 * upper_step), relwidth=width_btn1, relheight=height_btn1)


# Создаем кнопку для получения новой задачи
new_btn = tk.Button(window, text="Новая задача", command=new)
new_btn.place(relx=left_step, rely=(text_height + height_btn1 + 3 * upper_step), relwidth=width_btn1, relheight=height_btn1)


# Создаем кнопку для добавления новой задачи
add_btn = tk.Button(window, text="Добавить задачу", command=add_new_problem)
add_btn.place(relx=left_step, rely=(text_height + 2 * height_btn1 + 4 * upper_step), relwidth=width_btn1, relheight=height_btn1)


# создаем фрейм для таймера
timer_frame = tk.Frame(window, bg='white', bd=5)
timer_frame.place(relx=(2 * left_step + width_btn1), rely=(text_height + 2 * upper_step), relwidth=timer_width, relheight=timer_height)


# создаем виджет Entry для ввода времени
time_entry = tk.Entry(timer_frame, font=("Helvetica", font_size))
time_entry.place(relx=left_step, rely=upper_step, relwidth=width_btn2, relheight=height_btn2)


# создаем кнопку Start
start_button = tk.Button(timer_frame, text="Start", command=start_timer, font=("Helvetica", font_size))
start_button.place(relx=(2 * left_step + width_btn2), rely=upper_step, relwidth=start_btn_width, relheight=height_btn2)


# создаем кнопку Pause
pause_resume_button = tk.Button(timer_frame, text="Pause", command=pause_resume_timer, font=("Helvetica", font_size), state='disabled')
pause_resume_button.place(relx=left_step, rely=(height_btn2 + 2 * upper_step), relwidth=width_btn2, relheight=height_btn2)


# создаем Label для отображения времени
time_label = tk.Label(timer_frame, text="Time remaining: ", font=("Helvetica", font_size))
time_label.place(relx=left_step, rely=(2 * height_btn2 + 3 * upper_step), relwidth=width_btn2, relheight=height_btn2)


# Запускаем окно
window.mainloop()

