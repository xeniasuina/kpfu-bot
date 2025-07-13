import os
import docling
from bs4 import BeautifulSoup
import html2text
import logging
from pathlib import Path
import json
from docling.document_converter import DocumentConverter as DocConverter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
pdfConverter = DocConverter()

class DocumentConverter:
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.body_width = 0  # Отключаем перенос строк
        
    def convert_pdf_to_markdown(self, pdf_path: str) -> str:
        """Конвертация PDF в markdown с помощью docling"""
        try:            
            # Конвертируем PDF в markdown
            path = Path(pdf_path)
            path.chmod(0o700)
            result = pdfConverter.convert(pdf_path)
                        
            return result.document.export_to_markdown()
        except Exception as e:
            logger.error(f"Ошибка при конвертации PDF {pdf_path}: {str(e)}")
            return ""
            
    def convert_html_to_markdown(self, html_path: str) -> str:
        """Конвертация HTML в markdown с фильтрацией"""
        try:
            # Читаем HTML файл
            with open(html_path, 'r', encoding='windows-1251') as f:
                html_content = f.read()
                
            # Парсим HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Удаляем ненужные элементы
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
                
            # Конвертируем в markdown
            markdown_content = self.h2t.handle(str(soup))
            
            return markdown_content
        except Exception as e:
            logger.error(f"Ошибка при конвертации HTML {html_path}: {str(e)}")
            return ""

    def convert_json_to_markdown(self, json_path: str) -> str:
        """Конвертация JSON файла в markdown"""
        try:
            # Читаем JSON файл
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Формируем markdown
            markdown_content = []
            
            # Добавляем заголовок
            if 'filename' in data:
                markdown_content.append(f"# {data['filename']}\n")
            
            # Обрабатываем страницы
            if 'pages' in data:
                for page in data['pages']:
                    if page.get('has_text', False):
                        # Добавляем номер страницы
                        markdown_content.append(f"\n## Страница {page.get('page_number', 'N/A')}\n")
                        # Добавляем текст страницы
                        markdown_content.append(page.get('text', '').strip())
                        markdown_content.append("\n---\n")
            
            return "\n".join(markdown_content)
        except Exception as e:
            logger.error(f"Ошибка при конвертации JSON {json_path}: {str(e)}")
            return ""
            
    def process_files(self):
        """Обработка всех файлов в директории"""
        # Создаем выходную директорию если её нет
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Получаем список всех файлов
        files = []
        for ext in ['.pdf', '.html', '.json']:
            files.extend(list(Path(self.input_dir).rglob(f'*{ext}')))
            
        total_files = len(files)
        logger.info(f"Найдено {total_files} файлов для конвертации")
        
        for i, file_path in enumerate(files, 1):
            try:
                # Определяем тип файла
                if file_path.suffix.lower() == '.pdf':
                    content = self.convert_pdf_to_markdown(str(file_path))
                elif file_path.suffix.lower() == '.html':
                    content = self.convert_html_to_markdown(str(file_path))
                elif file_path.suffix.lower() == '.json':
                    content = self.convert_json_to_markdown(str(file_path))
                    
                if content:
                    # Создаем путь для markdown файла
                    rel_path = file_path.relative_to(self.input_dir)
                    md_path = Path(self.output_dir) / rel_path.with_suffix('.md')
                    
                    # Создаем директории если нужно
                    md_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Сохраняем markdown
                    with open(md_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                        
                    logger.info(f"[{i}/{total_files}] Успешно конвертирован {file_path.name}")
                else:
                    logger.warning(f"[{i}/{total_files}] Пропущен {file_path.name} (пустой результат)")
                    
            except Exception as e:
                logger.error(f"[{i}/{total_files}] Ошибка при обработке {file_path.name}: {str(e)}")
                
        logger.info("Конвертация завершена")

if __name__ == "__main__":
    # Пути к директориям
    INPUT_DIR = "dataset"  # Директория с исходными файлами
    OUTPUT_DIR = "markdown_docs"  # Директория для markdown файлов
    
    # Создаем конвертер и запускаем обработку
    converter = DocumentConverter(INPUT_DIR, OUTPUT_DIR)
    converter.process_files() 