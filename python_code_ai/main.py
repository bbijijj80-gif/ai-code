#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ИИ для написания кода на языке Python
Генератор кода с использованием эвристических правил и шаблонов
"""

import re
import json
from typing import Optional, List, Dict, Any


class PythonCodeGenerator:
    """
    Генератор кода на Python с поддержкой русского языка
    Использует набор шаблонов и правил для генерации кода
    """
    
    def __init__(self):
        # Шаблоны распространённых конструкций
        self.templates = {
            'hello_world': 'print("Привет, мир!")',
            'function_simple': '''def {name}({params}):
    """{docstring}"""
    {body}
    return {return_value}''',
            
            'class_simple': '''class {name}:
    """{docstring}"""
    
    def __init__(self, {init_params}):
        {init_body}
    
    {methods}''',
            
            'loop_for': '''for {item} in {collection}:
    {body}''',
            
            'loop_while': '''while {condition}:
    {body}''',
            
            'if_statement': '''if {condition}:
    {if_body}
{else_part}''',
            
            'try_except': '''try:
    {try_body}
except {exception} as e:
    {except_body}''',
            
            'list_comprehension': '[{expression} for {item} in {collection}{condition}]',
            
            'dict_comprehension': '{{{key}: {value} for {item} in {collection}}}',
            
            'import_statement': 'import {module}',
            
            'from_import': 'from {module} import {names}',
        }
        
        # Словарь русских терминов и их соответствий в Python
        self.russian_terms = {
            'привет': 'hello',
            'мир': 'world',
            'функция': 'function',
            'класс': 'class',
            'цикл': 'loop',
            'условие': 'condition',
            'список': 'list',
            'словарь': 'dict',
            'кортеж': 'tuple',
            'множество': 'set',
            'строка': 'str',
            'число': 'int',
            'плавающее': 'float',
            'истина': 'True',
            'ложь': 'False',
            'ничто': 'None',
            'для': 'for',
            'в': 'in',
            'пока': 'while',
            'если': 'if',
            'иначе': 'else',
            'elif': 'elif',
            'попытка': 'try',
            'исключение': 'except',
            'наконец': 'finally',
            'вернуть': 'return',
            'импорт': 'import',
            'из': 'from',
        }
        
        # Примеры кода для обучения
        self.code_examples = self._load_code_examples()
    
    def _load_code_examples(self) -> List[Dict[str, str]]:
        """Загружает примеры кода для генерации"""
        return [
            {
                'description': 'Функция умножения двух чисел',
                'code': '''def multiply(a, b):
    """Умножает два числа"""
    return a * b'''
            },
            {
                'description': 'Функция сложения двух чисел',
                'code': '''def add(a, b):
    """Складывает два числа"""
    return a + b'''
            },
            {
                'description': 'Класс человека',
                'code': '''class Person:
    """Класс представляющий человека"""
    
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        """Приветствует человека"""
        return f"Привет, меня зовут {self.name}"'''
            },
            {
                'description': 'Чтение файла',
                'code': '''def read_file(filename):
    """Читает содержимое файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Файл {filename} не найден")
        return None'''
            },
            {
                'description': 'Фильтрация списка',
                'code': '''def filter_even(numbers):
    """Фильтрует чётные числа из списка"""
    return [num for num in numbers if num % 2 == 0]'''
            },
            {
                'description': 'Работа со словарём',
                'code': '''def create_user_dict(name, age, email):
    """Создаёт словарь пользователя"""
    return {
        'name': name,
        'age': age,
        'email': email
    }'''
            },
            {
                'description': 'Рекурсивный факториал',
                'code': '''def factorial(n):
    """Вычисляет факториал числа рекурсивно"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)'''
            },
            {
                'description': 'Парсинг JSON',
                'code': '''import json

def parse_json(json_string):
    """Парсит JSON строку в словарь"""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        print(f"Ошибка парсинга JSON: {e}")
        return None'''
            },
            {
                'description': 'Генератор случайных чисел',
                'code': '''import random

def generate_random_numbers(count, min_val=0, max_val=100):
    """Генерирует список случайных чисел"""
    return [random.randint(min_val, max_val) for _ in range(count)]'''
            },
            {
                'description': 'HTTP запрос',
                'code': '''import requests

def fetch_url(url):
    """Делает GET запрос к URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        return None'''
            },
            {
                'description': 'База данных SQLite',
                'code': '''import sqlite3

def create_database(db_name):
    """Создаёт подключение к базе данных"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    return conn, cursor'''
            }
        ]
    
    def analyze_request(self, request: str) -> Dict[str, Any]:
        """Анализирует запрос пользователя на русском языке"""
        request_lower = request.lower()
        
        analysis = {
            'type': 'unknown',
            'keywords': [],
            'complexity': 'simple',
            'suggested_templates': []
        }
        
        # Определение типа запрошенного кода
        if any(word in request_lower for word in ['функция', 'деф', 'определить']):
            analysis['type'] = 'function'
            analysis['suggested_templates'].append('function_simple')
        
        if any(word in request_lower for word in ['класс']):
            analysis['type'] = 'class'
            analysis['suggested_templates'].append('class_simple')
        
        if any(word in request_lower for word in ['цикл', 'для', 'пока']) and 'функция' not in request_lower:
            analysis['type'] = 'loop'
            if 'для' in request_lower:
                analysis['suggested_templates'].append('loop_for')
            else:
                analysis['suggested_templates'].append('loop_while')
        
        if any(word in request_lower for word in ['если', 'условие', 'проверк']):
            analysis['type'] = 'conditional'
            analysis['suggested_templates'].append('if_statement')
        
        if any(word in request_lower for word in ['список', 'массив', 'фильтр']):
            analysis['type'] = 'list_operation'
            analysis['suggested_templates'].append('list_comprehension')
        
        if any(word in request_lower for word in ['файл', 'чтен', 'запис']):
            analysis['type'] = 'file_operation'
            analysis['suggested_templates'].append('try_except')
        
        if any(word in request_lower for word in ['ошибк', 'исклю', 'попытк']):
            analysis['type'] = 'error_handling'
            analysis['suggested_templates'].append('try_except')
        
        if any(word in request_lower for word in ['импорт', 'подключ', 'библиотек']):
            analysis['type'] = 'import'
            analysis['suggested_templates'].append('import_statement')
        
        # Извлечение ключевых слов
        keywords = []
        for word in request_lower.split():
            clean_word = re.sub(r'[^\wа-яё]', '', word)
            if len(clean_word) > 2 and clean_word not in ['что', 'как', 'сделать', 'напиши', 'создай']:
                keywords.append(clean_word)
        
        analysis['keywords'] = keywords
        
        # Оценка сложности
        if len(analysis['suggested_templates']) > 2 or len(keywords) > 5:
            analysis['complexity'] = 'complex'
        elif len(analysis['suggested_templates']) > 0:
            analysis['complexity'] = 'medium'
        
        return analysis
    
    def find_similar_examples(self, request: str, limit: int = 3) -> List[Dict[str, str]]:
        """Находит похожие примеры кода"""
        request_lower = request.lower()
        scored_examples = []
        
        # Ключевые слова для каждого типа операций
        type_keywords = {
            'file': ['файл', 'читать', 'запис', 'open', 'read', 'write'],
            'function_add': ['сложени', 'add', 'плюс', 'сумм'],
            'function_mult': ['умнож', 'multiply', 'произвед'],
            'class': ['класс', 'person', 'человек'],
            'list': ['список', 'фильтр', 'list'],
            'json': ['json', 'парс', 'json'],
            'random': ['случайн', 'random', 'генератор'],
            'factorial': ['факториал', 'factorial'],
            'database': ['база', 'данных', 'sqlite', 'database'],
            'http': ['http', 'запрос', 'request', 'url'],
            'dict': ['словар', 'dict', 'user']
        }
        
        for example in self.code_examples:
            score = 0
            desc_lower = example['description'].lower()
            code_lower = example['code'].lower()
            
            # Подсчёт совпадений слов в описании
            for word in request_lower.split():
                clean_word = re.sub(r'[^\wа-яё]', '', word)
                if len(clean_word) > 2:
                    if clean_word in desc_lower:
                        score += 3
                    if clean_word in code_lower:
                        score += 1
            
            # Проверка по типам операций
            for op_type, keywords in type_keywords.items():
                if any(kw in request_lower for kw in keywords):
                    if any(kw in desc_lower for kw in keywords):
                        score += 5
                    if any(kw in code_lower for kw in keywords):
                        score += 2
            
            # Специальная обработка для функций
            if 'функция' in request_lower and 'def ' in code_lower:
                if 'function' not in op_type:
                    score += 3
            
            # Специальная обработка для циклов
            if 'цикл' in request_lower or ('для' in request_lower and 'перебор' in request_lower):
                if 'list' in op_type and 'for' in code_lower:
                    score += 2
            
            if score > 0:
                scored_examples.append((score, example))
        
        # Сортировка по релевантности
        scored_examples.sort(reverse=True, key=lambda x: x[0])
        
        return [example for _, example in scored_examples[:limit]]
    
    def generate_code(self, request: str) -> str:
        """Генерирует код на основе запроса пользователя"""
        analysis = self.analyze_request(request)
        similar_examples = self.find_similar_examples(request)
        
        result = "# " + "=" * 60 + "\n"
        result += "# Сгенерированный код на Python\n"
        result += "# Запрос: " + request + "\n"
        result += "# " + "=" * 60 + "\n\n"
        
        # Добавляем анализ запроса
        result += f"# Тип кода: {analysis['type']}\n"
        result += f"# Сложность: {analysis['complexity']}\n"
        result += f"# Ключевые слова: {', '.join(analysis['keywords'])}\n\n"
        
        # Если найдены похожие примеры, используем их как основу
        if similar_examples:
            result += "# Найдены похожие примеры:\n"
            for i, example in enumerate(similar_examples, 1):
                result += f"# {i}. {example['description']}\n"
            result += "\n"
            
            # Используем лучший пример как основу
            best_example = similar_examples[0]
            result += best_example['code'] + "\n\n"
        else:
            # Генерируем код на основе шаблонов
            if analysis['type'] == 'function':
                result += self._generate_function_template(analysis, request)
            elif analysis['type'] == 'class':
                result += self._generate_class_template(analysis, request)
            elif analysis['type'] == 'loop':
                result += self._generate_loop_template(analysis, request)
            elif analysis['type'] == 'conditional':
                result += self._generate_conditional_template(analysis, request)
            elif analysis['type'] == 'list_operation':
                result += self._generate_list_comprehension(analysis, request)
            elif analysis['type'] == 'file_operation':
                result += self._generate_file_operation(analysis, request)
            elif analysis['type'] == 'error_handling':
                result += self._generate_error_handling(analysis, request)
            elif analysis['type'] == 'import':
                result += self._generate_import_statement(analysis, request)
            else:
                result += self._generate_generic_code(analysis, request)
        
        result += "\n# " + "=" * 60 + "\n"
        result += "# Код готов к использованию!\n"
        result += "# " + "=" * 60 + "\n"
        
        return result
    
    def _generate_function_template(self, analysis: Dict, request: str) -> str:
        """Генерирует шаблон функции"""
        func_name = self._extract_name(request, 'my_function')
        params = self._extract_params(request)
        
        template = self.templates['function_simple'].format(
            name=func_name,
            params=params,
            docstring=f"Функция для: {request}",
            body="# TODO: Реализуйте логику функции",
            return_value="result"
        )
        
        return template + "\n\n"
    
    def _generate_class_template(self, analysis: Dict, request: str) -> str:
        """Генерирует шаблон класса"""
        class_name = self._extract_name(request, 'MyClass').title()
        
        template = self.templates['class_simple'].format(
            name=class_name,
            docstring=f"Класс для: {request}",
            init_params="self",
            init_body="# Инициализация атрибутов",
            methods="def __str__(self):\n        return f'{class_name}()'"
        )
        
        return template + "\n\n"
    
    def _generate_loop_template(self, analysis: Dict, request: str) -> str:
        """Генерирует шаблон цикла"""
        if 'loop_for' in analysis['suggested_templates']:
            template = self.templates['loop_for'].format(
                item="item",
                collection="collection",
                body="# Обработка элемента"
            )
        else:
            template = self.templates['loop_while'].format(
                condition="condition",
                body="# Тело цикла"
            )
        
        return template + "\n\n"
    
    def _generate_conditional_template(self, analysis: Dict, request: str) -> str:
        """Генерирует шаблон условия"""
        template = self.templates['if_statement'].format(
            condition="condition",
            if_body="    # Код если условие истинно",
            else_part="else:\n    # Код если условие ложно"
        )
        
        return template + "\n\n"
    
    def _generate_list_comprehension(self, analysis: Dict, request: str) -> str:
        """Генерирует списковое включение"""
        template = self.templates['list_comprehension'].format(
            expression="item",
            item="item",
            collection="collection",
            condition=""
        )
        
        return template + "\n\n"
    
    def _generate_file_operation(self, analysis: Dict, request: str) -> str:
        """Генерирует код работы с файлами"""
        code = '''def process_file(filename):
    """Обрабатывает файл"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            # Обработка содержимого
            return content
    except FileNotFoundError:
        print(f"Файл {filename} не найден")
        return None
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None
'''
        return code + "\n"
    
    def _generate_error_handling(self, analysis: Dict, request: str) -> str:
        """Генерирует обработку исключений"""
        template = self.templates['try_except'].format(
            try_body="# Код который может вызвать исключение",
            exception="Exception",
            except_body="print(f'Произошла ошибка: {e}')"
        )
        
        return template + "\n\n"
    
    def _generate_import_statement(self, analysis: Dict, request: str) -> str:
        """Генерирует импорты"""
        imports = []
        
        # Распространённые библиотеки
        library_map = {
            'json': 'json',
            'регулярн': 're',
            'дата': 'datetime',
            'время': 'time',
            'случайн': 'random',
            'математик': 'math',
            'систем': 'os',
            'путь': 'os.path',
            'запрос': 'requests',
            'beautifulsoup': 'bs4',
            'pandas': 'pandas',
            'numpy': 'numpy',
            'flask': 'flask',
            'django': 'django',
        }
        
        request_lower = request.lower()
        for keyword, module in library_map.items():
            if keyword in request_lower:
                imports.append(f"import {module}")
        
        if not imports:
            imports.append("# import module_name  # Добавьте нужный модуль")
        
        return "\n".join(imports) + "\n\n"
    
    def _generate_generic_code(self, analysis: Dict, request: str) -> str:
        """Генерирует универсальный код"""
        code = '''# Универсальный шаблон кода
# Адаптируйте под ваши нужды

def main():
    """Основная функция программы"""
    # Инициализация
    data = []
    
    # Обработка данных
    for item in data:
        pass  # Ваша логика здесь
    
    # Вывод результатов
    print("Программа завершена")

if __name__ == "__main__":
    main()
'''
        return code
    
    def _extract_name(self, request: str, default: str) -> str:
        """Извлекает имя из запроса"""
        # Простая эвристика для извлечения имени
        words = re.findall(r'[а-яёa-zA-Z][а-яёa-zA-Z0-9_]*', request)
        
        for word in words:
            if word.lower() not in ['создай', 'напиши', 'сделай', 'функцию', 'класс', 'код', 'для']:
                return word.lower()
        
        return default
    
    def _extract_params(self, request: str) -> str:
        """Извлекает параметры из запроса"""
        # Простая реализация, может быть улучшена
        return "arg1, arg2"
    
    def explain_code(self, code: str) -> str:
        """Объясняет код на русском языке"""
        explanation = "# Объяснение кода:\n\n"
        
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if stripped.startswith('def '):
                func_name = re.search(r'def\s+(\w+)', stripped)
                if func_name:
                    explanation += f"Строка {i}: Определение функции '{func_name.group(1)}'\n"
            
            elif stripped.startswith('class '):
                class_name = re.search(r'class\s+(\w+)', stripped)
                if class_name:
                    explanation += f"Строка {i}: Определение класса '{class_name.group(1)}'\n"
            
            elif stripped.startswith('import '):
                module = re.search(r'import\s+([\w.]+)', stripped)
                if module:
                    explanation += f"Строка {i}: Импорт модуля '{module.group(1)}'\n"
            
            elif stripped.startswith('for ') and ' in ' in stripped:
                explanation += f"Строка {i}: Цикл for для итерации по коллекции\n"
            
            elif stripped.startswith('while '):
                explanation += f"Строка {i}: Цикл while с условием\n"
            
            elif stripped.startswith('if ') and ':' in stripped:
                explanation += f"Строка {i}: Условное выражение if\n"
            
            elif stripped.startswith('try:'):
                explanation += f"Строка {i}: Блок try для обработки исключений\n"
            
            elif stripped.startswith('return '):
                explanation += f"Строка {i}: Возврат значения из функции\n"
        
        return explanation


def main():
    """Основная функция демонстрации ИИ"""
    generator = PythonCodeGenerator()
    
    print("=" * 70)
    print("ИИ для написания кода на Python")
    print("Поддержка русского языка")
    print("=" * 70)
    print()
    
    # Примеры запросов
    examples = [
        "Создай функцию для сложения двух чисел",
        "Напиши класс человека с именем и возрастом",
        "Как прочитать файл и обработать ошибки?",
        "Создай цикл для перебора списка",
        "Нужен код для фильтрации чётных чисел",
        "Импортируй модуль для работы с JSON",
        "Создай функцию для вычисления факториала",
        "Напиши код для работы с базой данных SQLite"
    ]
    
    print("Примеры генерации кода:\n")
    
    for i, example in enumerate(examples, 1):
        print(f"\n{'='*70}")
        print(f"Пример {i}: {example}")
        print('='*70)
        
        code = generator.generate_code(example)
        print(code)
        
        # Объяснение кода
        print("\n# Объяснение:")
        explanation = generator.explain_code(code)
        print(explanation)
    
    print("\n" + "=" * 70)
    print("Интерактивный режим")
    print("=" * 70)
    print("Введите ваш запрос (или 'выход' для завершения):")
    
    while True:
        try:
            user_input = input("\n>>> ").strip()
            
            if user_input.lower() in ['выход', 'exit', 'quit', 'q']:
                print("До свидания!")
                break
            
            if not user_input:
                continue
            
            print("\n" + "-" * 70)
            code = generator.generate_code(user_input)
            print(code)
            
            # Предложить объяснение
            explain_choice = input("\nОбъяснить код? (да/нет): ").strip().lower()
            if explain_choice in ['да', 'yes', 'y']:
                explanation = generator.explain_code(code)
                print("\n" + explanation)
        
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана. До свидания!")
            break
        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")


if __name__ == "__main__":
    main()
