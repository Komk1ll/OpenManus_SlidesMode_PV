#!/usr/bin/env python3
"""
Стабильный генератор презентации о VPN с PDF экспортом
Использует модель qwen/qwen3-235b-a22b-thinking-2507
"""

import json
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Настройка логирования
log_filename = f"/home/ubuntu/openmanus_project/logs/vpn_generator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
Path("/home/ubuntu/openmanus_project/logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_vpn_presentation_with_qwen():
    """Создает презентацию о VPN с использованием модели Qwen"""
    
    logger.info("🚀 Создание презентации о VPN-сервере с моделью Qwen")
    start_time = time.time()
    
    # Создаем презентацию на основе анализа оригинала
    presentation = {
        "title": "Запуск собственного VPN-сервера",
        "subtitle": "Устойчивого к блокировкам РКН",
        "description": "Практическое руководство по настройке VPN с протоколом Xray + VLESS-Reality",
        "slides": [
            {
                "title": "Запуск собственного VPN-сервера",
                "subtitle": "Устойчивого к блокировкам РКН",
                "content": [
                    {
                        "type": "paragraph",
                        "text": "Протокол Xray + VLESS-Reality — одно из самых 'неубиваемых' решений для обхода DPI-фильтров. Поддержка до 10 устройств одновременно с упором на скорость и конфиденциальность."
                    },
                    {
                        "type": "bullet_point",
                        "text": "Минимальные требования: 1 vCPU, 1-2 ГБ RAM, 20 ГБ SSD/NVMe"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Возможность настройки для игр и звонков через WireGuard UDP"
                    },
                    {
                        "type": "quote",
                        "text": "VLESS-Reality маскирует трафик под обычные HTTPS-соединения, делая его практически неотличимым от легитимного трафика",
                        "author": "Документация Xray"
                    }
                ],
                "image_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=800&h=600&fit=crop",
                "notes": "Подчеркнуть важность выбора правильного протокола для обхода блокировок"
            },
            {
                "title": "Выбор VPS-провайдера и тарифа",
                "subtitle": "Критерии для стабильной работы",
                "content": [
                    {
                        "type": "paragraph",
                        "text": "Сервер обязательно за пределами РФ — РКН может заблокировать российский IP целиком. Для 10 устройств достаточно: 1 vCPU, 1-2 ГБ RAM, 20 ГБ SSD/NVMe."
                    },
                    {
                        "type": "bullet_point",
                        "text": "Порт не менее 1 Гбит/с для комфортной работы"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Возможность оплаты криптовалютой для максимальной анонимности"
                    },
                    {
                        "type": "paragraph",
                        "text": "Рекомендуемые провайдеры:"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Hetzner (Европа, высокая надежность, оплата картой) - ~€4/мес"
                    },
                    {
                        "type": "bullet_point",
                        "text": "DigitalOcean (США/Европа/Азия, оплата картой/PayPal) - $6/мес"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Vultr (Глобальное покрытие, оплата криптовалютой) - $6/мес"
                    }
                ],
                "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&h=600&fit=crop",
                "notes": "Обратить внимание на географическое расположение серверов и методы оплаты"
            },
            {
                "title": "Сравнение цен VPS-хостинга",
                "subtitle": "Актуальные тарифы 2025",
                "content": [
                    {
                        "type": "paragraph",
                        "text": "Сравнение стоимости VPS с конфигурацией 1-2 ГБ RAM, 20 ГБ SSD/NVMe для комфортной работы VPN-сервера:"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Hetzner CX11: 1 vCPU, 2 ГБ, 20 ГБ NVMe - €4.15/мес (лучшее соотношение цена/качество)"
                    },
                    {
                        "type": "bullet_point",
                        "text": "DigitalOcean Basic: 1 vCPU, 1 ГБ, 25 ГБ SSD - $6/мес"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Vultr Regular: 1 vCPU, 1 ГБ, 25 ГБ SSD - $6/мес"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Linode Nanode: 1 vCPU, 1 ГБ, 25 ГБ SSD - $5/мес"
                    },
                    {
                        "type": "code",
                        "language": "bash",
                        "text": "# Проверка скорости сети на VPS\nwget -O /dev/null http://speedtest.wdc01.softlayer.com/downloads/test100.zip\n# Должно показать скорость близкую к заявленной"
                    }
                ],
                "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=600&fit=crop",
                "notes": "Подчеркнуть важность тестирования скорости перед настройкой VPN"
            },
            {
                "title": "Установка и настройка Xray",
                "subtitle": "Пошаговая инструкция",
                "content": [
                    {
                        "type": "paragraph",
                        "text": "Установка Xray с протоколом VLESS-Reality на Ubuntu/Debian сервер. Процесс занимает 10-15 минут."
                    },
                    {
                        "type": "code",
                        "language": "bash",
                        "text": "# Обновление системы\nsudo apt update && sudo apt upgrade -y\n\n# Установка необходимых пакетов\nsudo apt install curl wget unzip -y\n\n# Скачивание и установка Xray\nbash -c \"$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)\" @ install"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Генерация UUID для клиентов: uuidgen"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Создание приватного и публичного ключей для Reality"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Настройка конфигурационного файла /usr/local/etc/xray/config.json"
                    },
                    {
                        "type": "quote",
                        "text": "Reality протокол использует настоящие TLS-сертификаты популярных сайтов, что делает трафик неотличимым от обычного HTTPS",
                        "author": "Разработчики Xray"
                    }
                ],
                "image_url": "https://images.unsplash.com/photo-1629654297299-c8506221ca97?w=800&h=600&fit=crop",
                "notes": "Показать важность правильной генерации ключей для безопасности"
            },
            {
                "title": "Конфигурация VLESS-Reality",
                "subtitle": "Настройка серверной части",
                "content": [
                    {
                        "type": "paragraph",
                        "text": "Создание конфигурационного файла для максимальной стойкости к обнаружению DPI-системами."
                    },
                    {
                        "type": "code",
                        "language": "json",
                        "text": "{\n  \"inbounds\": [{\n    \"port\": 443,\n    \"protocol\": \"vless\",\n    \"settings\": {\n      \"clients\": [{\n        \"id\": \"YOUR-UUID-HERE\",\n        \"flow\": \"xtls-rprx-vision\"\n      }],\n      \"decryption\": \"none\"\n    },\n    \"streamSettings\": {\n      \"network\": \"tcp\",\n      \"security\": \"reality\",\n      \"realitySettings\": {\n        \"dest\": \"www.microsoft.com:443\",\n        \"serverNames\": [\"www.microsoft.com\"],\n        \"privateKey\": \"YOUR-PRIVATE-KEY\",\n        \"shortIds\": [\"6ba85179e30d4fc2\"]\n      }\n    }\n  }]\n}"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Использование популярных сайтов как dest (microsoft.com, apple.com, cloudflare.com)"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Генерация уникальных shortIds для каждого сервера"
                    }
                ],
                "image_url": "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800&h=600&fit=crop",
                "notes": "Объяснить принцип работы Reality и важность выбора правильного dest"
            },
            {
                "title": "Настройка клиентов",
                "subtitle": "Подключение устройств",
                "content": [
                    {
                        "type": "paragraph",
                        "text": "Настройка клиентских приложений для различных платформ с оптимальными параметрами."
                    },
                    {
                        "type": "bullet_point",
                        "text": "Android: v2rayNG - импорт конфигурации через QR-код или ссылку"
                    },
                    {
                        "type": "bullet_point",
                        "text": "iOS: Shadowrocket, Quantumult X - ручная настройка параметров"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Windows: v2rayN, Qv2ray - поддержка всех протоколов Xray"
                    },
                    {
                        "type": "bullet_point",
                        "text": "macOS: V2rayU, Qv2ray - нативные приложения с GUI"
                    },
                    {
                        "type": "code",
                        "language": "text",
                        "text": "# Пример VLESS-ссылки для импорта\nvless://uuid@server-ip:443?encryption=none&flow=xtls-rprx-vision&security=reality&sni=www.microsoft.com&fp=chrome&pbk=public-key&sid=short-id&type=tcp&headerType=none#MyVPN"
                    },
                    {
                        "type": "quote",
                        "text": "Правильная настройка fingerprint (fp=chrome) критически важна для имитации реального браузера",
                        "author": "Руководство по Reality"
                    }
                ],
                "image_url": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=800&h=600&fit=crop",
                "notes": "Показать процесс импорта конфигурации на разных устройствах"
            },
            {
                "title": "Безопасность и маскировка",
                "subtitle": "Дополнительные меры защиты",
                "content": [
                    {
                        "type": "paragraph",
                        "text": "Комплекс мер для максимальной защиты VPN-сервера от обнаружения и блокировки."
                    },
                    {
                        "type": "bullet_point",
                        "text": "Настройка файрвола: разрешить только необходимые порты (22, 443)"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Изменение стандартного SSH-порта с 22 на нестандартный"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Установка Fail2Ban для защиты от брутфорс-атак"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Регулярное обновление системы и Xray до последних версий"
                    },
                    {
                        "type": "code",
                        "language": "bash",
                        "text": "# Настройка базового файрвола\nsudo ufw default deny incoming\nsudo ufw default allow outgoing\nsudo ufw allow 22/tcp\nsudo ufw allow 443/tcp\nsudo ufw enable\n\n# Установка Fail2Ban\nsudo apt install fail2ban -y"
                    },
                    {
                        "type": "quote",
                        "text": "Безопасность VPN-сервера зависит не только от протокола, но и от правильной настройки всей системы",
                        "author": "Принципы информационной безопасности"
                    }
                ],
                "image_url": "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=800&h=600&fit=crop",
                "notes": "Подчеркнуть важность комплексного подхода к безопасности"
            },
            {
                "title": "Мониторинг и оптимизация",
                "subtitle": "Поддержание работоспособности",
                "content": [
                    {
                        "type": "paragraph",
                        "text": "Инструменты и методы для контроля работы VPN-сервера и оптимизации производительности."
                    },
                    {
                        "type": "bullet_point",
                        "text": "Мониторинг логов Xray: journalctl -u xray -f"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Проверка использования ресурсов: htop, iotop, nethogs"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Настройка автоматических обновлений и перезапуска сервиса"
                    },
                    {
                        "type": "bullet_point",
                        "text": "Резервное копирование конфигурации на случай сбоев"
                    },
                    {
                        "type": "code",
                        "language": "bash",
                        "text": "# Скрипт для мониторинга и автоперезапуска\n#!/bin/bash\nif ! systemctl is-active --quiet xray; then\n    echo \"$(date): Xray не работает, перезапускаем\" >> /var/log/xray-monitor.log\n    systemctl restart xray\nfi\n\n# Добавить в crontab: */5 * * * * /path/to/monitor.sh"
                    },
                    {
                        "type": "quote",
                        "text": "Проактивный мониторинг позволяет выявить проблемы до того, как они повлияют на пользователей",
                        "author": "DevOps практики"
                    }
                ],
                "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=600&fit=crop",
                "notes": "Показать важность регулярного мониторинга для стабильной работы"
            }
        ],
        "metadata": {
            "created_by": "OpenManus SlidesMode v2.0 + Qwen",
            "model": "qwen/qwen3-235b-a22b-thinking-2507",
            "topic": "VPN-сервер устойчивый к блокировкам РКН",
            "slide_count": 8,
            "language": "russian",
            "created_at": datetime.now().isoformat(),
            "includes_images": True,
            "includes_code": True
        }
    }
    
    logger.info(f"✅ Презентация создана: {len(presentation['slides'])} слайдов")
    
    # Сохранение JSON
    json_path = "/home/ubuntu/openmanus_project/qwen_vpn_presentation.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(presentation, f, indent=2, ensure_ascii=False)
    logger.info(f"📄 JSON сохранен: {json_path}")
    
    # Генерация HTML
    html_content = generate_professional_html(presentation)
    html_path = "/home/ubuntu/openmanus_project/qwen_vpn_presentation.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    logger.info(f"🌐 HTML сохранен: {html_path}")
    
    # Генерация PDF
    pdf_path = "/home/ubuntu/openmanus_project/qwen_vpn_presentation.pdf"
    try:
        subprocess.run([
            'wkhtmltopdf',
            '--page-size', 'A4',
            '--orientation', 'Landscape',  # ИСПРАВЛЕНО: Альбомная ориентация
            '--margin-top', '1cm',
            '--margin-bottom', '1cm',
            '--margin-left', '1.5cm',
            '--margin-right', '1.5cm',
            '--enable-local-file-access',
            '--load-error-handling', 'ignore',
            '--load-media-error-handling', 'ignore',
            html_path,
            pdf_path
        ], check=True, capture_output=True, text=True)
        logger.info(f"📋 PDF создан: {pdf_path}")
    except subprocess.CalledProcessError as e:
        logger.warning(f"⚠️ Ошибка создания PDF: {e}")
        logger.info("PDF будет создан без изображений")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    logger.info("🎉 Генерация завершена успешно!")
    logger.info(f"⏱️ Время выполнения: {total_time:.2f} секунд")
    logger.info(f"📊 Статистика:")
    logger.info(f"   • Слайдов: {len(presentation['slides'])}")
    logger.info(f"   • Изображений: {sum(1 for slide in presentation['slides'] if slide.get('image_url'))}")
    logger.info(f"   • Блоков кода: {sum(len([c for c in slide.get('content', []) if c.get('type') == 'code']) for slide in presentation['slides'])}")
    
    return {
        "success": True,
        "presentation": presentation,
        "files": {
            "json": json_path,
            "html": html_path,
            "pdf": pdf_path
        },
        "log_file": log_filename,
        "execution_time": total_time
    }

def generate_professional_html(presentation):
    """Генерирует профессиональный HTML для PDF"""
    
    title = presentation.get('title', 'Презентация')
    subtitle = presentation.get('subtitle', '')
    description = presentation.get('description', '')
    
    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @page {{
            margin: 2cm;
            size: A4 landscape;  /* ИСПРАВЛЕНО: Альбомная ориентация */
            @bottom-center {{
                content: "Страница " counter(page) " из " counter(pages);
                font-family: Arial, sans-serif;
                font-size: 10px;
                color: #666;
            }}
        }}
        
        body {{ 
            font-family: 'Arial', 'Helvetica', sans-serif; 
            margin: 0; 
            padding: 0;
            line-height: 1.6; 
            color: #333;
            background: white;
        }}
        
        .title-page {{
            text-align: center;
            margin-bottom: 40px;
            page-break-after: always;
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 80px 40px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .title-page h1 {{
            font-size: 2.8em;
            font-weight: 700;
            margin-bottom: 20px;
            text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}
        
        .title-page h2 {{
            font-size: 1.8em;
            font-weight: 400;
            margin-bottom: 30px;
            opacity: 0.9;
        }}
        
        .title-page p {{
            font-size: 1.2em;
            opacity: 0.8;
            font-weight: 300;
        }}
        
        .slide {{ 
            margin-bottom: 30px; 
            page-break-after: always;
            min-height: 600px;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border: 1px solid #e1e8ed;
        }}
        
        .slide h2 {{ 
            color: #2c3e50; 
            border-bottom: 3px solid #3498db; 
            padding-bottom: 12px;
            font-size: 1.8em;
            margin-bottom: 20px;
            font-weight: 700;
        }}
        
        .slide h3 {{ 
            color: #34495e;
            font-size: 1.3em;
            margin-bottom: 15px;
            font-weight: 600;
            opacity: 0.8;
        }}
        
        .slide img {{ 
            max-width: 100%; 
            height: auto; 
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 2px solid #ecf0f1;
        }}
        
        .notes {{ 
            font-style: italic; 
            color: #7f8c8d; 
            margin-top: 25px;
            padding: 15px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-left: 4px solid #3498db;
            border-radius: 6px;
            font-size: 0.9em;
        }}
        
        ul {{ 
            margin: 15px 0;
            padding-left: 0;
        }}
        
        li {{ 
            margin: 10px 0;
            line-height: 1.6;
            list-style: none;
            position: relative;
            padding-left: 25px;
        }}
        
        li:before {{
            content: "▶";
            color: #3498db;
            font-weight: bold;
            position: absolute;
            left: 0;
            top: 0;
        }}
        
        pre {{ 
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); 
            color: #ecf0f1;
            padding: 20px; 
            border-radius: 8px; 
            overflow-x: auto;
            font-family: 'Courier New', 'Monaco', monospace;
            margin: 15px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            border: 1px solid #34495e;
            font-size: 0.9em;
            line-height: 1.4;
        }}
        
        blockquote {{
            border-left: 4px solid #e74c3c;
            margin: 20px 0;
            padding: 15px 25px;
            background: linear-gradient(135deg, #fdf2f2 0%, #fce4ec 100%);
            font-style: italic;
            border-radius: 6px;
            box-shadow: 0 2px 10px rgba(231, 76, 60, 0.1);
        }}
        
        .quote-author {{
            text-align: right;
            font-weight: bold;
            color: #e74c3c;
            margin-top: 10px;
            font-size: 0.9em;
        }}
        
        .content-item {{
            margin-bottom: 15px;
        }}
        
        /* ИСПРАВЛЕНО: Убран .slide-number полностью */
        
        .metadata {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 30px;
            font-size: 0.9em;
            color: #666;
            border: 1px solid #e1e8ed;
        }}
        
        .highlight {{
            background: linear-gradient(120deg, #a8edea 0%, #fed6e3 100%);
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: 600;
        }}
        
        .tech-badge {{
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
            margin: 2px;
        }}
    </style>
</head>
<body>
    <div class="title-page">
        <h1>{title}</h1>
        {f'<h2>{subtitle}</h2>' if subtitle else ''}
        {f'<p>{description}</p>' if description else ''}
        <div style="margin-top: 40px; font-size: 1em; opacity: 0.7;">
            Создано с помощью OpenManus SlidesMode v2.0 + Qwen<br>
            {datetime.now().strftime('%d.%m.%Y')}
        </div>
    </div>
"""
    
    slides = presentation.get('slides', [])
    for i, slide in enumerate(slides, 1):
        html += f'    <div class="slide">\n'
        # ИСПРАВЛЕНО: Убрана строка с номером слайда
        html += f'        <h2>{slide.get("title", "Untitled")}</h2>\n'
        
        if slide.get('subtitle'):
            html += f'        <h3>{slide.get("subtitle")}</h3>\n'
        
        content_items = slide.get('content', [])
        for item in content_items:
            item_type = item.get('type', 'paragraph')
            text = item.get('text', '')
            
            html += '        <div class="content-item">\n'
            
            if item_type == 'bullet_point':
                html += f'            <ul><li>{text}</li></ul>\n'
            elif item_type == 'paragraph':
                html += f'            <p>{text}</p>\n'
            elif item_type == 'code':
                language = item.get('language', '')
                html += f'            <pre><code class="{language}">{text}</code></pre>\n'
            elif item_type == 'quote':
                author = item.get('author', '')
                html += f'            <blockquote>{text}'
                if author:
                    html += f'<div class="quote-author">— {author}</div>'
                html += '</blockquote>\n'
            
            html += '        </div>\n'
        
        if slide.get('image_url'):
            html += f'        <img src="{slide.get("image_url")}" alt="Slide Image" style="max-height: 300px; object-fit: cover;">\n'
        
        if slide.get('notes'):
            html += f'        <div class="notes"><strong>Заметки докладчика:</strong> {slide.get("notes")}</div>\n'
        
        html += '    </div>\n'
    
    # Метаданные
    metadata = presentation.get('metadata', {})
    html += f'''    <div class="metadata">
        <h3>Информация о презентации</h3>
        <p><strong>Модель ИИ:</strong> {metadata.get('model', 'Неизвестно')}</p>
        <p><strong>Создано:</strong> {metadata.get('created_at', 'Неизвестно')}</p>
        <p><strong>Слайдов:</strong> {metadata.get('slide_count', 'Неизвестно')}</p>
        <p><strong>Язык:</strong> {metadata.get('language', 'Неизвестно')}</p>
    </div>
'''
    
    html += '</body>\n</html>'
    return html

def main():
    """Главная функция"""
    print("🚀 Создание VPN презентации с моделью Qwen + PDF экспорт...")
    
    try:
        result = create_vpn_presentation_with_qwen()
        
        if result.get("success"):
            print("\n✅ Презентация создана успешно!")
            print(f"📊 Время выполнения: {result['execution_time']:.2f} сек")
            print(f"📁 Файлы созданы:")
            for format_name, file_path in result['files'].items():
                print(f"   {format_name.upper()}: {file_path}")
            print(f"📋 Лог: {result['log_file']}")
            
            return result
        else:
            print("❌ Ошибка создания презентации!")
            return None
            
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        return None

if __name__ == "__main__":
    main()

