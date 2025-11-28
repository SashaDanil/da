import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
from typing import List, Dict
import random

class AdvancedEventManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎭 Advanced Event Manager - Расширенная версия")
        self.root.geometry("1200x800")
        
        self.db_name = "events_advanced.db"
        self.current_user = "Администратор"
        self.init_database()
        self.create_widgets()
        self.load_events()
    
    def init_database(self):
        """Инициализация расширенной базы данных"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Таблица мероприятий с расширенными полями
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL,
                location TEXT NOT NULL,
                category TEXT NOT NULL,
                max_participants INTEGER,
                price REAL DEFAULT 0,
                organizer TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица участников с демографическими данными
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                age INTEGER,
                registration_type TEXT,
                company TEXT,
                position TEXT,
                registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events (id)
            )
        ''')
        
        # Таблица аналитики
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                metric_name TEXT,
                metric_value REAL,
                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
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
        notebook.add(events_frame, text="📋 Мероприятия")
        
        # Вкладка регистрации
        registration_frame = ttk.Frame(notebook)
        notebook.add(registration_frame, text="👥 Регистрация")
        
        # Вкладка аналитики
        analytics_frame = ttk.Frame(notebook)
        notebook.add(analytics_frame, text="📊 Аналитика")
        
        # Вкладка эксперимента
        experiment_frame = ttk.Frame(notebook)
        notebook.add(experiment_frame, text="🎯 Эксперимент")
        
        self.setup_events_tab(events_frame)
        self.setup_registration_tab(registration_frame)
        self.setup_analytics_tab(analytics_frame)
        self.setup_experiment_tab(experiment_frame)
    
    def setup_events_tab(self, parent):
        """Настройка вкладки мероприятий"""
        # Панель быстрых действий
        quick_actions = ttk.LabelFrame(parent, text="Быстрые действия")
        quick_actions.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(quick_actions, text="➕ Новое мероприятие", 
                  command=self.show_create_event_dialog, width=20).pack(side='left', padx=5, pady=5)
        ttk.Button(quick_actions, text="🔄 Обновить", 
                  command=self.load_events, width=15).pack(side='left', padx=5, pady=5)
        ttk.Button(quick_actions, text="📊 Статистика", 
                  command=self.show_quick_stats, width=15).pack(side='left', padx=5, pady=5)
        
        # Список мероприятий
        list_frame = ttk.LabelFrame(parent, text="Список мероприятий")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview для мероприятий
        columns = ('ID', 'Название', 'Дата', 'Категория', 'Место', 'Участники', 'Статус', 'Цена')
        self.events_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Настраиваем колонки
        column_widths = [50, 200, 100, 100, 150, 100, 80, 80]
        for col, width in zip(columns, column_widths):
            self.events_tree.heading(col, text=col)
            self.events_tree.column(col, width=width, anchor='center')
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.events_tree.yview)
        self.events_tree.configure(yscrollcommand=scrollbar.set)
        
        self.events_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', padx=5, pady=5)
        
        # Кнопки управления
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="🗑️ Удалить выбранное", 
                  command=self.delete_event, width=20).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="📊 Детали", 
                  command=self.show_event_details, width=15).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="✏️ Редактировать", 
                  command=self.edit_event, width=15).pack(side='left', padx=5)
    
    def setup_registration_tab(self, parent):
        """Настройка вкладки регистрации"""
        # Форма регистрации
        form_frame = ttk.LabelFrame(parent, text="Регистрация участника")
        form_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(form_frame, text="Мероприятие:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=10, pady=5)
        self.reg_event_combo = ttk.Combobox(form_frame, state="readonly", width=50)
        self.reg_event_combo.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Имя участника:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
        self.reg_name_entry = ttk.Entry(form_frame, width=50)
        self.reg_name_entry.grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky='w', padx=10, pady=5)
        self.reg_email_entry = ttk.Entry(form_frame, width=50)
        self.reg_email_entry.grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Возраст:").grid(row=3, column=0, sticky='w', padx=10, pady=5)
        self.reg_age_entry = ttk.Entry(form_frame, width=50)
        self.reg_age_entry.grid(row=3, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Тип регистрации:").grid(row=4, column=0, sticky='w', padx=10, pady=5)
        self.reg_type_combo = ttk.Combobox(form_frame, 
                                          values=["Обычная", "Ранняя", "VIP", "Спонсор"], 
                                          state="readonly", width=50)
        self.reg_type_combo.set("Обычная")
        self.reg_type_combo.grid(row=4, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Компания:").grid(row=5, column=0, sticky='w', padx=10, pady=5)
        self.reg_company_entry = ttk.Entry(form_frame, width=50)
        self.reg_company_entry.grid(row=5, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Должность:").grid(row=6, column=0, sticky='w', padx=10, pady=5)
        self.reg_position_entry = ttk.Entry(form_frame, width=50)
        self.reg_position_entry.grid(row=6, column=1, padx=10, pady=5)
        
        ttk.Button(form_frame, text="✅ Зарегистрировать участника", 
                  command=self.register_participant_advanced, width=25).grid(row=7, column=1, pady=10)
        
        # Список участников
        list_frame = ttk.LabelFrame(parent, text="Зарегистрированные участники")
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview для участников
        columns = ('ID', 'Мероприятие', 'Имя', 'Email', 'Возраст', 'Тип', 'Компания', 'Дата')
        self.participants_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        column_widths = [50, 150, 120, 150, 60, 80, 120, 100]
        for col, width in zip(columns, column_widths):
            self.participants_tree.heading(col, text=col)
            self.participants_tree.column(col, width=width, anchor='center')
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.participants_tree.yview)
        self.participants_tree.configure(yscrollcommand=scrollbar.set)
        
        self.participants_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', padx=5, pady=5)
        
        ttk.Button(list_frame, text="🔄 Обновить список", 
                  command=self.load_participants).pack(pady=5)
    
    def setup_analytics_tab(self, parent):
        """Настройка вкладки аналитики"""
        # Выбор мероприятия
        selection_frame = ttk.LabelFrame(parent, text="Выбор мероприятия для анализа")
        selection_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(selection_frame, text="Мероприятие:").pack(side='left', padx=10, pady=10)
        self.analytics_event_combo = ttk.Combobox(selection_frame, state="readonly", width=60)
        self.analytics_event_combo.pack(side='left', padx=10, pady=10)
        ttk.Button(selection_frame, text="📈 Показать аналитику", 
                  command=self.show_advanced_analytics, width=20).pack(side='left', padx=10, pady=10)
        
        # Отображение аналитики
        analytics_frame = ttk.LabelFrame(parent, text="Расширенная аналитика")
        analytics_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Текстовое поле для аналитики
        self.analytics_text = tk.Text(analytics_frame, font=('Arial', 10), wrap='word', height=20)
        scrollbar = ttk.Scrollbar(analytics_frame, orient="vertical", command=self.analytics_text.yview)
        self.analytics_text.configure(yscrollcommand=scrollbar.set)
        
        self.analytics_text.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', padx=5, pady=5)
    
    def setup_experiment_tab(self, parent):
        """Настройка вкладки эксперимента"""
        # Описание
        desc_frame = ttk.LabelFrame(parent, text="Вычислительный эксперимент")
        desc_frame.pack(fill='x', padx=5, pady=5)
        
        desc_text = """🎯 ВЫЧИСЛИТЕЛЬНЫЙ ЭКСПЕРИМЕНТ

Этот эксперимент позволяет протестировать систему с большим объемом данных:
• Создает тестовые мероприятия разных категорий
• Регистрирует участников с различными характеристиками  
• Анализирует эффективность и заполняемость
• Генерирует статистику и рекомендации"""
        
        desc_label = ttk.Label(desc_frame, text=desc_text, justify='left', font=('Arial', 10))
        desc_label.pack(padx=10, pady=10)
        
        # Параметры эксперимента
        params_frame = ttk.Frame(parent)
        params_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(params_frame, text="Количество мероприятий:").grid(row=0, column=0, padx=10, pady=5)
        self.exp_events_count = ttk.Entry(params_frame, width=10)
        self.exp_events_count.insert(0, "5")
        self.exp_events_count.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(params_frame, text="Макс. участников:").grid(row=0, column=2, padx=10, pady=5)
        self.exp_max_participants = ttk.Entry(params_frame, width=10)
        self.exp_max_participants.insert(0, "100")
        self.exp_max_participants.grid(row=0, column=3, padx=10, pady=5)
        
        ttk.Button(params_frame, text="🚀 Запустить эксперимент", 
                  command=self.run_advanced_experiment, width=20).grid(row=0, column=4, padx=20, pady=5)
        
        ttk.Button(params_frame, text="🧹 Очистить данные", 
                  command=self.clear_experiment_data, width=15).grid(row=0, column=5, padx=10, pady=5)
        
        # Результаты эксперимента
        results_frame = ttk.LabelFrame(parent, text="Результаты эксперимента")
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.experiment_results = tk.Text(results_frame, font=('Arial', 10), wrap='word', height=15)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.experiment_results.yview)
        self.experiment_results.configure(yscrollcommand=scrollbar.set)
        
        self.experiment_results.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', padx=5, pady=5)
    
    def show_create_event_dialog(self):
        """Диалог создания нового мероприятия"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Создание мероприятия")
        dialog.geometry("500x650")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Поля формы
        form_frame = ttk.Frame(dialog)
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(form_frame, text="Создание нового мероприятия", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Название
        ttk.Label(form_frame, text="Название мероприятия:*").pack(anchor='w', pady=(10,5))
        title_entry = ttk.Entry(form_frame, width=60)
        title_entry.pack(fill='x', pady=(0,10))
        
        # Описание
        ttk.Label(form_frame, text="Описание:").pack(anchor='w', pady=(10,5))
        desc_entry = ttk.Entry(form_frame, width=60)
        desc_entry.pack(fill='x', pady=(0,10))
        
        # Дата
        ttk.Label(form_frame, text="Дата (ГГГГ-ММ-ДД):*").pack(anchor='w', pady=(10,5))
        date_entry = ttk.Entry(form_frame, width=60)
        date_entry.pack(fill='x', pady=(0,10))
        
        # Место
        ttk.Label(form_frame, text="Место проведения:*").pack(anchor='w', pady=(10,5))
        location_entry = ttk.Entry(form_frame, width=60)
        location_entry.pack(fill='x', pady=(0,10))
        
        # Категория
        ttk.Label(form_frame, text="Категория:*").pack(anchor='w', pady=(10,5))
        category_combo = ttk.Combobox(form_frame, 
                                    values=["Технологии", "Бизнес", "Образование", "Наука", "Искусство", "Спорт"],
                                    state="readonly", width=57)
        category_combo.set("Технологии")
        category_combo.pack(fill='x', pady=(0,10))
        
        # Макс. участников
        ttk.Label(form_frame, text="Максимальное количество участников:*").pack(anchor='w', pady=(10,5))
        max_participants_entry = ttk.Entry(form_frame, width=60)
        max_participants_entry.pack(fill='x', pady=(0,10))
        
        # Цена
        ttk.Label(form_frame, text="Цена (руб.):").pack(anchor='w', pady=(10,5))
        price_entry = ttk.Entry(form_frame, width=60)
        price_entry.insert(0, "0")
        price_entry.pack(fill='x', pady=(0,10))
        
        # Организатор
        ttk.Label(form_frame, text="Организатор:").pack(anchor='w', pady=(10,5))
        organizer_entry = ttk.Entry(form_frame, width=60)
        organizer_entry.pack(fill='x', pady=(0,20))
        
        def create_event():
            """Создание мероприятия из диалога"""
            try:
                event_data = {
                    'title': title_entry.get(),
                    'description': desc_entry.get(),
                    'date': date_entry.get(),
                    'location': location_entry.get(),
                    'category': category_combo.get(),
                    'max_participants': int(max_participants_entry.get()),
                    'price': float(price_entry.get()),
                    'organizer': organizer_entry.get()
                }
                
                if not all([event_data['title'], event_data['date'], event_data['location']]):
                    messagebox.showerror("Ошибка", "Заполните обязательные поля (отмечены *)")
                    return
                
                self.create_advanced_event(event_data)
                dialog.destroy()
                messagebox.showinfo("Успех", "Мероприятие успешно создано!")
                
            except ValueError as e:
                messagebox.showerror("Ошибка", "Проверьте числовые поля (количество участников и цена)")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при создании: {e}")
        
        ttk.Button(form_frame, text="Создать мероприятие", 
                  command=create_event, width=20).pack(pady=10)
        
        ttk.Label(form_frame, text="* - обязательные поля", 
                 font=('Arial', 8), foreground='gray').pack(pady=5)
    
    def create_advanced_event(self, event_data):
        """Создание мероприятия с расширенными данными"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO events (title, description, date, location, category, max_participants, price, organizer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_data['title'],
            event_data['description'],
            event_data['date'],
            event_data['location'],
            event_data['category'],
            event_data['max_participants'],
            event_data['price'],
            event_data['organizer']
        ))
        
        conn.commit()
        conn.close()
        self.load_events()
    
    def load_events(self):
        """Загрузка списка мероприятий"""
        # Очищаем treeview
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, date, category, location, 
                   (SELECT COUNT(*) FROM participants WHERE event_id = events.id) || '/' || max_participants as participants,
                   status, price
            FROM events 
            ORDER BY date DESC
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
        
        self.reg_event_combo['values'] = event_list
        self.analytics_event_combo['values'] = event_list
        
        if event_list:
            self.reg_event_combo.set(event_list[0])
            self.analytics_event_combo.set(event_list[0])
    
    def delete_event(self):
        """Удаление выбранного мероприятия"""
        selected = self.events_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите мероприятие для удаления")
            return
        
        event_id = self.events_tree.item(selected[0])['values'][0]
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранное мероприятие и всех участников?"):
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            try:
                cursor.execute('DELETE FROM participants WHERE event_id = ?', (event_id,))
                cursor.execute('DELETE FROM events WHERE id = ?', (event_id,))
                cursor.execute('DELETE FROM analytics WHERE event_id = ?', (event_id,))
                
                conn.commit()
                messagebox.showinfo("Успех", "Мероприятие удалено")
                self.load_events()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении: {e}")
            finally:
                conn.close()
    
    def show_event_details(self):
        """Показать детали выбранного мероприятия"""
        selected = self.events_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите мероприятие")
            return
        
        event_id = self.events_tree.item(selected[0])['values'][0]
        self.show_advanced_analytics(event_id)
    
    def edit_event(self):
        """Редактирование выбранного мероприятия"""
        selected = self.events_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите мероприятие для редактирования")
            return
        
        # Здесь можно добавить функционал редактирования
        messagebox.showinfo("Информация", "Функция редактирования в разработке")
    
    def show_quick_stats(self):
        """Показать быструю статистику"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM events')
        total_events = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM participants')
        total_participants = cursor.fetchone()[0]
        
        cursor.execute('''
            SELECT AVG((SELECT COUNT(*) FROM participants WHERE event_id = events.id) * 100.0 / max_participants) 
            FROM events WHERE max_participants > 0
        ''')
        avg_occupancy = cursor.fetchone()[0] or 0
        
        conn.close()
        
        stats_text = f"""
📊 БЫСТРАЯ СТАТИСТИКА СИСТЕМЫ

• Всего мероприятий: {total_events}
• Всего участников: {total_participants}
• Средняя заполняемость: {avg_occupancy:.1f}%

💡 СИСТЕМА РАБОТАЕТ СТАБИЛЬНО
"""
        messagebox.showinfo("Быстрая статистика", stats_text)
    
    def register_participant_advanced(self):
        """Регистрация участника с расширенными данными"""
        try:
            event_str = self.reg_event_combo.get()
            if not event_str:
                messagebox.showerror("Ошибка", "Выберите мероприятие")
                return
            
            event_id = int(event_str.split(':')[0])
            name = self.reg_name_entry.get()
            email = self.reg_email_entry.get()
            age = self.reg_age_entry.get()
            reg_type = self.reg_type_combo.get()
            company = self.reg_company_entry.get()
            position = self.reg_position_entry.get()
            
            if not all([name, email]):
                messagebox.showerror("Ошибка", "Заполните имя и email")
                return
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Проверяем доступность мест
            cursor.execute('''
                SELECT max_participants, 
                       (SELECT COUNT(*) FROM participants WHERE event_id = events.id) as current 
                FROM events WHERE id = ?
            ''', (event_id,))
            
            result = cursor.fetchone()
            
            if not result:
                messagebox.showerror("Ошибка", "Мероприятие не найдено")
                return
            
            max_participants, current = result
            
            if current >= max_participants:
                messagebox.showerror("Ошибка", "Нет свободных мест на мероприятии")
                return
            
            # Регистрируем участника
            cursor.execute('''
                INSERT INTO participants (event_id, name, email, age, registration_type, company, position)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (event_id, name, email, int(age) if age else None, reg_type, company, position))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Успех", "Участник успешно зарегистрирован!")
            self.clear_registration_form()
            self.load_events()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при регистрации: {e}")
    
    def clear_registration_form(self):
        """Очистка формы регистрации"""
        self.reg_name_entry.delete(0, 'end')
        self.reg_email_entry.delete(0, 'end')
        self.reg_age_entry.delete(0, 'end')
        self.reg_company_entry.delete(0, 'end')
        self.reg_position_entry.delete(0, 'end')
        self.reg_type_combo.set("Обычная")
    
    def load_participants(self):
        """Загрузка списка участников"""
        for item in self.participants_tree.get_children():
            self.participants_tree.delete(item)
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.id, e.title, p.name, p.email, p.age, p.registration_type, p.company, p.registered_at
            FROM participants p
            JOIN events e ON p.event_id = e.id
            ORDER BY p.registered_at DESC
        ''')
        
        for row in cursor.fetchall():
            self.participants_tree.insert('', 'end', values=row)
        
        conn.close()
    
    def show_advanced_analytics(self, event_id=None):
        """Показать расширенную аналитику"""
        if not event_id:
            event_str = self.analytics_event_combo.get()
            if not event_str:
                messagebox.showwarning("Предупреждение", "Выберите мероприятие")
                return
            event_id = int(event_str.split(':')[0])
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Основная статистика
        cursor.execute('''
            SELECT e.*, 
                   COUNT(p.id) as registered_count,
                   AVG(p.age) as avg_age,
                   COUNT(DISTINCT p.registration_type) as reg_types_count
            FROM events e
            LEFT JOIN participants p ON e.id = p.event_id
            WHERE e.id = ?
            GROUP BY e.id
        ''', (event_id,))
        
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Ошибка", "Данные мероприятия не найдены")
            return
        
        # Статистика по типам регистрации
        cursor.execute('''
            SELECT registration_type, COUNT(*) as count, AVG(age) as avg_age
            FROM participants 
            WHERE event_id = ?
            GROUP BY registration_type
        ''', (event_id,))
        
        reg_stats = cursor.fetchall()
        
        conn.close()
        
        # Формируем отчет
        max_participants = result[6]
        registered_count = result[16]
        price = result[7]
        
        occupancy_rate = (registered_count / max_participants) * 100 if max_participants > 0 else 0
        estimated_revenue = registered_count * price
        
        analytics_text = f"""
📊 РАСШИРЕННАЯ АНАЛИТИКА МЕРОПРИЯТИЯ

🏷️ Название: {result[1]}
📝 Описание: {result[2]}
📅 Дата: {result[3]}
📍 Место: {result[4]}
🏷️ Категория: {result[5]}
💰 Цена: {price:.2f} руб.
👨‍💼 Организатор: {result[8]}

👥 СТАТИСТИКА УЧАСТНИКОВ:
• Максимальное количество: {max_participants}
• Зарегистрировано: {registered_count}
• Свободных мест: {max_participants - registered_count}
• Заполняемость: {occupancy_rate:.1f}%
• Средний возраст: {result[17] or 0:.1f} лет
• Типов регистрации: {result[18]}

💰 ФИНАНСОВЫЕ ПОКАЗАТЕЛИ:
• Ожидаемый доход: {estimated_revenue:.2f} руб.
• Доход на участника: {price:.2f} руб.

📋 СТАТИСТИКА ПО ТИПАМ РЕГИСТРАЦИИ:
"""
        
        for reg_type, count, avg_age in reg_stats:
            analytics_text += f"• {reg_type}: {count} чел. (ср. возраст: {avg_age or 0:.1f} лет)\n"
        
        # Анализ эффективности
        if occupancy_rate > 90:
            efficiency = "🔴 ВЫСОКАЯ - мероприятие популярно"
            recommendation = "Рекомендуется увеличить цену или организовать повторное мероприятие"
        elif occupancy_rate > 70:
            efficiency = "🟡 СРЕДНЯЯ - хорошая заполняемость"
            recommendation = "Продолжайте текущую стратегию продвижения"
        elif occupancy_rate > 50:
            efficiency = "🟢 УДОВЛЕТВОРИТЕЛЬНАЯ - требуется дополнительное продвижение"
            recommendation = "Рассмотрите скидки или дополнительные промо-акции"
        else:
            efficiency = "⚪ НИЗКАЯ - требуется активное продвижение"
            recommendation = "Рекомендуется пересмотреть маркетинговую стратегию"
        
        analytics_text += f"""
🎯 АНАЛИЗ ЭФФЕКТИВНОСТИ:
• Уровень заполняемости: {efficiency}
• Рекомендация: {recommendation}

🆔 ID мероприятия: {result[0]}
⏰ Создано: {result[10]}
"""
        
        self.analytics_text.delete(1.0, 'end')
        self.analytics_text.insert(1.0, analytics_text)
    
    def run_advanced_experiment(self):
        """Запуск расширенного вычислительного эксперимента"""
        try:
            num_events = int(self.exp_events_count.get())
            max_participants = int(self.exp_max_participants.get())
            
            self.experiment_results.delete(1.0, 'end')
            self.experiment_results.insert('end', "🚀 ЗАПУСК РАСШИРЕННОГО ЭКСПЕРИМЕНТА...\n\n")
            
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Категории мероприятий для эксперимента
            categories = ["Технологии", "Бизнес", "Образование", "Наука", "Искусство"]
            locations = ["Москва", "Санкт-Петербург", "Новосибирск", "Казань", "Екатеринбург"]
            organizers = ["TechEvents Inc", "Business Leaders", "Education Hub", "Science Foundation", "Art Community"]
            
            event_ids = []
            
            # Создаем тестовые мероприятия
            for i in range(num_events):
                event_data = (
                    f'Тестовое мероприятие {i+1} - {categories[i % len(categories)]}',
                    f'Описание тестового мероприятия категории {categories[i % len(categories)]}',
                    f'2024-12-{15 + i}',
                    locations[i % len(locations)],
                    categories[i % len(categories)],
                    max_participants,
                    random.randint(1000, 5000),
                    organizers[i % len(organizers)]
                )
                
                cursor.execute('''
                    INSERT INTO events (title, description, date, location, category, max_participants, price, organizer)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', event_data)
                
                event_id = cursor.lastrowid
                event_ids.append(event_id)
                self.experiment_results.insert('end', f"✅ Создано: {event_data[0]}\n")
            
            # Регистрируем случайных участников
            registration_types = ["Обычная", "Ранняя", "VIP", "Спонсор"]
            
            for event_id in event_ids:
                # Случайное количество участников (50-100% от максимума)
                num_participants = random.randint(max_participants // 2, max_participants)
                registered = 0
                
                for j in range(num_participants):
                    try:
                        participant_data = (
                            event_id,
                            f"Участник_Эксп_{j+1}",
                            f"exp_{event_id}_{j+1}@example.com",
                            random.randint(18, 65),
                            random.choice(registration_types),
                            f"Компания_{random.randint(1, 10)}",
                            f"Должность_{random.randint(1, 5)}"
                        )
                        
                        cursor.execute('''
                            INSERT INTO participants (event_id, name, email, age, registration_type, company, position)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', participant_data)
                        
                        registered += 1
                    except:
                        break
                
                self.experiment_results.insert('end', f"👥 Зарегистрировано на мероприятие {event_id}: {registered} участников\n")
            
            # Анализируем результаты
            self.experiment_results.insert('end', "\n📈 АНАЛИЗ РЕЗУЛЬТАТОВ ЭКСПЕРИМЕНТА:\n")
            
            cursor.execute(f'''
                SELECT e.category, 
                       COUNT(e.id) as event_count,
                       AVG((SELECT COUNT(*) FROM participants WHERE event_id = e.id) * 100.0 / e.max_participants) as avg_occupancy,
                       AVG(e.price) as avg_price,
                       SUM((SELECT COUNT(*) FROM participants WHERE event_id = e.id) * e.price) as total_revenue
                FROM events e 
                WHERE e.id IN ({','.join('?' * len(event_ids))})
                GROUP BY e.category
            ''', event_ids)
            
            category_stats = cursor.fetchall()
            
            total_revenue = 0
            total_events = 0
            
            for category, event_count, avg_occupancy, avg_price, revenue in category_stats:
                total_revenue += revenue if revenue else 0
                total_events += event_count
                
                self.experiment_results.insert('end', 
                    f"\n🏷️ Категория: {category}\n"
                    f"   • Мероприятий: {event_count}\n"
                    f"   • Средняя заполняемость: {avg_occupancy or 0:.1f}%\n"
                    f"   • Средняя цена: {avg_price or 0:.1f} руб.\n"
                    f"   • Общий доход: {revenue or 0:.2f} руб.\n")
            
            # Общая статистика
            if category_stats:
                avg_occupancy_all = sum([stat[2] or 0 for stat in category_stats]) / len(category_stats)
            else:
                avg_occupancy_all = 0
            
            self.experiment_results.insert('end', 
                f"\n📊 ОБЩАЯ СТАТИСТИКА:\n"
                f"• Всего мероприятий: {total_events}\n"
                f"• Средняя заполняемость: {avg_occupancy_all:.1f}%\n"
                f"• Общий ожидаемый доход: {total_revenue:.2f} руб.\n"
                f"• Средний доход на мероприятие: {total_revenue/total_events if total_events > 0 else 0:.2f} руб.\n")
            
            # Рекомендации
            if category_stats:
                best_category = max(category_stats, key=lambda x: x[2] or 0)
                worst_category = min(category_stats, key=lambda x: x[2] or 0)
                
                self.experiment_results.insert('end', 
                    f"\n💡 РЕКОМЕНДАЦИИ:\n"
                    f"• Самая популярная категория: {best_category[0]} ({best_category[2] or 0:.1f}% заполняемости)\n"
                    f"• Наименее популярная категория: {worst_category[0]} ({worst_category[2] or 0:.1f}% заполняемости)\n"
                    f"• Рекомендуется развивать категорию: {best_category[0]}\n")
            
            conn.commit()
            conn.close()
            
            self.experiment_results.insert('end', "\n✅ ЭКСПЕРИМЕНТ УСПЕШНО ЗАВЕРШЕН!\n")
            self.load_events()
            
        except Exception as e:
            self.experiment_results.insert('end', f"\n❌ ОШИБКА: {e}\n")
    
    def clear_experiment_data(self):
        """Очистка данных эксперимента"""
        if messagebox.askyesno("Подтверждение", 
                             "Удалить ВСЕ мероприятия и участников?\nЭто действие нельзя отменить."):
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM participants')
            cursor.execute('DELETE FROM events')
            cursor.execute('DELETE FROM analytics')
            cursor.execute('DELETE FROM sqlite_sequence WHERE name IN ("events", "participants", "analytics")')
            
            conn.commit()
            conn.close()
            
            self.experiment_results.delete(1.0, 'end')
            self.experiment_results.insert('end', "🧹 Данные эксперимента очищены.\n")
            self.load_events()

def main():
    root = tk.Tk()
    app = AdvancedEventManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()