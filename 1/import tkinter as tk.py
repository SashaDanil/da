import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
from typing import List, Dict

class SimpleEventManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Сервис организации мероприятий - Упрощенная версия")
        self.root.geometry("1000x700")
        
        self.db_name = "events_simple.db"
        self.init_database()
        self.create_widgets()
        self.load_events()
    
    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                location TEXT NOT NULL,
                max_participants INTEGER,
                current_participants INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Создание вкладок
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка мероприятий
        events_frame = ttk.Frame(notebook)
        notebook.add(events_frame, text="Мероприятия")
        
        # Вкладка регистрации
        registration_frame = ttk.Frame(notebook)
        notebook.add(registration_frame, text="Регистрация")
        
        # Вкладка статистики
        stats_frame = ttk.Frame(notebook)
        notebook.add(stats_frame, text="Статистика")
        
        self.setup_events_tab(events_frame)
        self.setup_registration_tab(registration_frame)
        self.setup_stats_tab(stats_frame)
    
    def setup_events_tab(self, parent):
        """Настройка вкладки мероприятий"""
        # Форма создания мероприятия
        form_frame = ttk.LabelFrame(parent, text="Создать новое мероприятие")
        form_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(form_frame, text="Название:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.title_entry = ttk.Entry(form_frame, width=40)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Описание:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.desc_entry = ttk.Entry(form_frame, width=40)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.date_entry = ttk.Entry(form_frame, width=40)
        self.date_entry.grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Место:").grid(row=3, column=0, sticky='w', padx=5, pady=2)
        self.location_entry = ttk.Entry(form_frame, width=40)
        self.location_entry.grid(row=3, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Макс. участников:").grid(row=4, column=0, sticky='w', padx=5, pady=2)
        self.max_participants_entry = ttk.Entry(form_frame, width=40)
        self.max_participants_entry.grid(row=4, column=1, padx=5, pady=2)
        
        ttk.Button(form_frame, text="Создать мероприятие", 
                  command=self.create_event).grid(row=5, column=1, sticky='e', padx=5, pady=5)
        
        # Список мероприятий
        list_frame = ttk.LabelFrame(parent, text="Существующие мероприятия")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('ID', 'Название', 'Дата', 'Место', 'Макс.', 'Текущ.')
        self.events_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.events_tree.heading(col, text=col)
            self.events_tree.column(col, width=100)
        
        self.events_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Кнопки управления
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Обновить список", 
                  command=self.load_events).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Удалить выбранное", 
                  command=self.delete_event).pack(side='left', padx=5)
    
    def setup_registration_tab(self, parent):
        """Настройка вкладки регистрации"""
        form_frame = ttk.LabelFrame(parent, text="Регистрация участника")
        form_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(form_frame, text="Мероприятие:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        self.event_combobox = ttk.Combobox(form_frame, state='readonly', width=37)
        self.event_combobox.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Имя:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        self.participant_name_entry = ttk.Entry(form_frame, width=40)
        self.participant_name_entry.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
        self.participant_email_entry = ttk.Entry(form_frame, width=40)
        self.participant_email_entry.grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Button(form_frame, text="Зарегистрировать", 
                  command=self.register_participant).grid(row=3, column=1, sticky='e', padx=5, pady=5)
        
        # Список участников
        participants_frame = ttk.LabelFrame(parent, text="Зарегистрированные участники")
        participants_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ('ID', 'Мероприятие', 'Имя', 'Email', 'Дата регистрации')
        self.participants_tree = ttk.Treeview(participants_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.participants_tree.heading(col, text=col)
        
        self.participants_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        ttk.Button(participants_frame, text="Обновить список участников", 
                  command=self.load_participants).pack(padx=5, pady=5)
    
    def setup_stats_tab(self, parent):
        """Настройка вкладки статистики"""
        # Выбор мероприятия для статистики
        selection_frame = ttk.Frame(parent)
        selection_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(selection_frame, text="Выберите мероприятие:").pack(side='left', padx=5)
        self.stats_event_combobox = ttk.Combobox(selection_frame, state='readonly', width=50)
        self.stats_event_combobox.pack(side='left', padx=5)
        ttk.Button(selection_frame, text="Показать статистику", 
                  command=self.show_statistics).pack(side='left', padx=5)
        
        # Статистика
        stats_frame = ttk.LabelFrame(parent, text="Статистика мероприятия")
        stats_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=15, width=80)
        scrollbar = ttk.Scrollbar(stats_frame, orient='vertical', command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=scrollbar.set)
        
        self.stats_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', padx=5, pady=5)
    
    def create_event(self):
        """Создание нового мероприятия"""
        try:
            title = self.title_entry.get()
            description = self.desc_entry.get()
            date = self.date_entry.get()
            location = self.location_entry.get()
            max_participants = int(self.max_participants_entry.get())
            
            if not all([title, date, location]):
                messagebox.showerror("Ошибка", "Заполните все обязательные поля")
                return
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO events (title, description, date, location, max_participants)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, description, date, location, max_participants))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", "Мероприятие успешно создано!")
            self.clear_event_form()
            self.load_events()
            self.update_event_comboboxes()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное значение для количества участников")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при создании мероприятия: {e}")
    
    def clear_event_form(self):
        """Очистка формы создания мероприятия"""
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.location_entry.delete(0, tk.END)
        self.max_participants_entry.delete(0, tk.END)
    
    def load_events(self):
        """Загрузка списка мероприятий"""
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, date, location, max_participants, current_participants
            FROM events ORDER BY date DESC
        ''')
        
        for row in cursor.fetchall():
            self.events_tree.insert('', 'end', values=row)
        
        conn.close()
        self.update_event_comboboxes()
    
    def update_event_comboboxes(self):
        """Обновление комбобоксов с мероприятиями"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, title FROM events ORDER BY date DESC')
        events = cursor.fetchall()
        conn.close()
        
        event_list = [f"{event[0]}: {event[1]}" for event in events]
        
        self.event_combobox['values'] = event_list
        self.stats_event_combobox['values'] = event_list
        
        if event_list:
            self.event_combobox.set(event_list[0])
            self.stats_event_combobox.set(event_list[0])
    
    def delete_event(self):
        """Удаление выбранного мероприятия"""
        selected = self.events_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите мероприятие для удаления")
            return
        
        event_id = self.events_tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранное мероприятие?"):
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            try:
                # Удаляем связанных участников
                cursor.execute('DELETE FROM participants WHERE event_id = ?', (event_id,))
                # Удаляем мероприятие
                cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
                
                conn.commit()
                messagebox.showinfo("Успех", "Мероприятие удалено")
                self.load_events()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении: {e}")
            finally:
                conn.close()
    
    def register_participant(self):
        """Регистрация участника на мероприятие"""
        try:
            event_str = self.event_combobox.get()
            if not event_str:
                messagebox.showerror("Ошибка", "Выберите мероприятие")
                return
            
            event_id = int(event_str.split(':')[0])
            name = self.participant_name_entry.get()
            email = self.participant_email_entry.get()
            
            if not all([name, email]):
                messagebox.showerror("Ошибка", "Заполните имя и email")
                return
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Проверяем доступность мест
            cursor.execute('SELECT max_participants, current_participants FROM events WHERE id = ?', (event_id,))
            result = cursor.fetchone()
            
            if not result:
                messagebox.showerror("Ошибка", "Мероприятие не найдено")
                return
            
            max_participants, current_participants = result
            
            if current_participants >= max_participants:
                messagebox.showerror("Ошибка", "Нет свободных мест на мероприятии")
                return
            
            # Регистрируем участника
            cursor.execute('''
                INSERT INTO participants (event_id, name, email)
                VALUES (?, ?, ?)
            ''', (event_id, name, email))
            
            # Обновляем счетчик
            cursor.execute('''
                UPDATE events 
                SET current_participants = current_participants + 1 
                WHERE id = ?
            ''', (event_id,))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", "Участник успешно зарегистрирован!")
            self.participant_name_entry.delete(0, tk.END)
            self.participant_email_entry.delete(0, tk.END)
            self.load_events()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при регистрации: {e}")
    
    def load_participants(self):
        """Загрузка списка участников"""
        for item in self.participants_tree.get_children():
            self.participants_tree.delete(item)
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.id, e.title, p.name, p.email, p.registered_at
            FROM participants p
            JOIN events e ON p.event_id = e.id
            ORDER BY p.registered_at DESC
        ''')
        
        for row in cursor.fetchall():
            self.participants_tree.insert('', 'end', values=row)
        
        conn.close()
    
    def show_statistics(self):
        """Показать статистику выбранного мероприятия"""
        event_str = self.stats_event_combobox.get()
        if not event_str:
            messagebox.showwarning("Предупреждение", "Выберите мероприятие")
            return
        
        event_id = int(event_str.split(':')[0])
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Получаем статистику
        cursor.execute('''
            SELECT e.*, COUNT(p.id) as registered_count
            FROM events e
            LEFT JOIN participants p ON e.id = p.event_id
            WHERE e.id = ?
            GROUP BY e.id
        ''', (event_id,))
        
        event_data = cursor.fetchone()
        conn.close()
        
        if not event_data:
            messagebox.showerror("Ошибка", "Данные мероприятия не найдены")
            return
        
        # Формируем отчет
        occupancy_rate = (event_data[6] / event_data[5]) * 100 if event_data[5] > 0 else 0
        
        stats_text = f"""
СТАТИСТИКА МЕРОПРИЯТИЯ

Название: {event_data[1]}
Описание: {event_data[2]}
Дата: {event_data[3]}
Место: {event_data[4]}

УЧАСТНИКИ:
Максимальное количество: {event_data[5]}
Зарегистрировано: {event_data[6]}
Свободных мест: {event_data[5] - event_data[6]}
Заполняемость: {occupancy_rate:.1f}%

ДЕТАЛИ:
Создано: {event_data[7]}
ID мероприятия: {event_data[0]}
        """
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)

def main():
    root = tk.Tk()
    app = SimpleEventManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()