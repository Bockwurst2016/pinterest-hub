import os
from src.core.config_loader import CONFIG
from typing import Dict

class WebHubGenerator:
    def __init__(self):
        self.output_dir = "data/web"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Basic CSS for an "Aesthetic & Cozy" vibe
        self.css = """
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background-color: #fdfaf6;
            color: #4a4a4a;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        header {
            padding: 50px;
            text-align: center;
            background-color: #fff;
            width: 100%;
            border-bottom: 1px solid #eee;
        }
        .container {
            max-width: 900px;
            padding: 40px;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 30px;
        }
        .product-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
            padding: 20px;
            max-width: 400px;
            transition: transform 0.3s;
        }
        .product-card:hover {
            transform: translateY(-5px);
        }
        .product-card img {
            width: 100%;
            border-radius: 10px;
        }
        .product-card h2 {
            margin: 20px 0 10px;
            font-size: 1.5rem;
        }
        .product-card p {
            font-size: 1rem;
            line-height: 1.6;
            color: #666;
            margin-bottom: 20px;
        }
        .btn {
            display: inline-block;
            background-color: #d4a373;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            transition: background 0.3s;
        }
        .btn:hover {
            background-color: #bc8a5f;
        }
        footer {
            padding: 40px;
            font-size: 0.8rem;
            color: #aaa;
        }
        """

    def generate_page(self, products: List[Dict]) -> str:
        """
        Generates a static HTML page with all products currently in the queue.
        
        :param products: List of product dictionaries (title, description, image_path, amazon_link)
        :return: The path to the generated HTML file.
        """
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Curated Finds | Aesthetic Home & Tech</title>
            <style>{self.css}</style>
        </head>
        <body>
            <header>
                <h1>Curated Finds</h1>
                <p>Handpicked essentials for a cozy lifestyle.</p>
            </header>
            <div class="container">
        """

        for p in products:
            html_content += f"""
                <div class="product-card">
                    <img src="{p['image_path']}" alt="{p['title']}">
                    <h2>{p['title']}</h2>
                    <p>{p['description']}</p>
                    <a href="{p['amazon_link']}" target="_blank" class="btn">View on Amazon</a>
                </div>
            """

        html_content += """
            </div>
            <footer>
                &copy; 2024 Curated Finds. All rights reserved.
            </footer>
        </body>
        </html>
        """

        filename = "index.html"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        logger.info(f"WebHub page updated at {filepath}")
        return filepath
