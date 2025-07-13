import os
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
import logging
from typing import List, Dict, Tuple
import json
import sys

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Пути к внешним зависимостям
POPPLER_PATH = r"C:\\Program Files\\poppler-24.08.0\\Library\\bin"
TESSERACT_PATH = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

class PDFProcessor:
    def __init__(self, output_dir: str = "processed_pdfs"):
        """
        Инициализация процессора PDF
        :param output_dir: Директория для сохранения обработанных файлов
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Проверка наличия Poppler
        if not os.path.exists(POPPLER_PATH):
            logger.error(f"Poppler не найден по пути: {POPPLER_PATH}")
            logger.info("Скачайте Poppler с https://github.com/oschwartz10612/poppler-windows/releases/")
            logger.info("Распакуйте в C:\\Program Files\\poppler-23.11.0")
            sys.exit(1)
            
        # Проверка наличия Tesseract
        if not os.path.exists(TESSERACT_PATH):
            logger.error(f"Tesseract не найден по пути: {TESSERACT_PATH}")
            logger.info("Скачайте Tesseract с https://github.com/UB-Mannheim/tesseract/wiki")
            logger.info("Установите в C:\\Program Files\\Tesseract-OCR")
            sys.exit(1)
        
        # Настройка Tesseract
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Предобработка изображения для улучшения OCR
        """
        # Конвертация в оттенки серого
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Увеличение контраста
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Шумоподавление
        denoised = cv2.fastNlMeansDenoising(enhanced)
        
        # Бинаризация
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary

    def extract_images_from_pdf(self, pdf_path: str) -> List[Tuple[np.ndarray, int]]:
        """
        Извлечение изображений из PDF
        :return: Список кортежей (изображение, номер страницы)
        """
        images = []
        try:
            # Конвертация PDF в изображения с явным указанием пути к Poppler
            pdf_images = convert_from_path(
                pdf_path,
                poppler_path=POPPLER_PATH,
                dpi=300,  # Увеличиваем DPI для лучшего качества
                thread_count=4  # Используем многопоточность
            )
            
            for i, img in enumerate(pdf_images):
                # Конвертация PIL Image в numpy array
                img_array = np.array(img)
                # Конвертация RGB в BGR для OpenCV
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                images.append((img_array, i + 1))
                
        except Exception as e:
            logger.error(f"Ошибка при извлечении изображений из {pdf_path}: {str(e)}")
            if "poppler" in str(e).lower():
                logger.error("Проверьте установку Poppler и путь к нему")
            
        return images

    def process_image(self, image: np.ndarray) -> str:
        """
        Обработка одного изображения через OCR
        """
        # Предобработка
        processed = self.preprocess_image(image)
        
        # OCR с русским языком
        text = pytesseract.image_to_string(processed, lang='rus+eng')
        
        return text.strip()

    def process_pdf(self, pdf_path: str) -> Dict:
        """
        Обработка PDF файла
        :return: Словарь с результатами обработки
        """
        results = {
            "filename": os.path.basename(pdf_path),
            "pages": [],
            "total_pages": 0,
            "success": False
        }
        
        try:
            # Извлечение изображений
            images = self.extract_images_from_pdf(pdf_path)
            results["total_pages"] = len(images)
            
            # Обработка каждой страницы
            for image, page_num in images:
                page_text = self.process_image(image)
                
                results["pages"].append({
                    "page_number": page_num,
                    "text": page_text,
                    "has_text": bool(page_text.strip())
                })
            
            results["success"] = True
            
            # Сохранение результатов
            output_path = os.path.join(
                self.output_dir, 
                f"{os.path.splitext(os.path.basename(pdf_path))[0]}_processed.json"
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
            logger.info(f"PDF обработан и сохранен: {output_path}")
            
        except Exception as e:
            logger.error(f"Ошибка при обработке {pdf_path}: {str(e)}")
            
        return results

def process_directory(input_dir: str, output_dir: str = "processed_pdfs"):
    """
    Обработка всех PDF файлов в директории
    """
    processor = PDFProcessor(output_dir)
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_dir, filename)
            logger.info(f"Обработка файла: {filename}")
            processor.process_pdf(pdf_path)

if __name__ == "__main__":
    # Пример использования
    input_directory = "img_pdfs"
    output_directory = "processed_pdfs"
    
    process_directory(input_directory, output_directory) 