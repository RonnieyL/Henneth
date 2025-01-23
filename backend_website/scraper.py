import asyncio
import logging
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import base64
import requests
import google.generativeai as genai
from utils import WebsiteAnalysisOutput, VisualAnalysis
from PIL import Image
from io import BytesIO
from datetime import datetime
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def launch_browser():
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=True,
            # Remove problematic args
            # Use system default sandbox settings
        )
        return browser, playwright
    except Exception as e:
        logger.error(f"Browser launch detailed error: {e}")
        # Consider printing full traceback
        import traceback
        traceback.print_exc()
        raise

class WebsiteAnalyzer:
    def __init__(self, gemini_api_key: str):
        """Initialize with Gemini API key"""
        self.api_key = gemini_api_key
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.text_model = genai.GenerativeModel("gemini-pro")

    async def capture_screenshots(self, url: str) -> List[Dict[str, str]]:
        """Capture multiple screenshots of the website"""
        screenshots = []
        browser, playwright = None, None
        try:
            browser, playwright = await launch_browser()

            # Additional timeout and context management
            context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = await context.new_page()

            await page.goto(url, timeout=30000, wait_until='networkidle')
            try:
                await page.goto(url, timeout=30000)
            except Exception as nav_error:
                logger.warning(f"Navigation error: {nav_error}")
                return [{
                    "type": "error",
                    "data": base64.b64encode(b"navigation_failed").decode("utf-8")
                }]

            screenshot_types = [
                {"type": "full_page", "full": True},
                {"type": "viewport", "full": False}
            ]

            for shot_config in screenshot_types:
                try:
                    screenshot = await page.screenshot(full_page=shot_config["full"])
                    screenshots.append({
                        "type": shot_config["type"],
                        "data": base64.b64encode(screenshot).decode("utf-8"),
                    })
                except Exception as shot_error:
                    logger.warning(f"Screenshot error for {shot_config['type']}: {shot_error}")
                    screenshots.append({
                        "type": shot_config["type"],
                        "data": base64.b64encode(b"screenshot_failed").decode("utf-8"),
                    })

            return screenshots

        except Exception as e:
            logger.error(f"Unexpected screenshot error: {str(e)}")
            return [{
                "type": "unexpected_error",
                "data": base64.b64encode(b"unexpected_error").decode("utf-8")
            }]

        finally:
            if browser:
                await browser.close()
            if playwright:
                await playwright.stop()

    def _base64_to_image(self, base64_string: str) -> Image.Image:
        """Safely convert base64 to image with error handling"""
        try:
            image_data = base64.b64decode(base64_string)
            return Image.open(BytesIO(image_data))
        except Exception as e:
            logger.warning(f"Image conversion error: {e}")
            return Image.new('RGB', (100, 100), color='white')

    def scrape_content(self, url: str) -> Dict[str, Any]:
        """Scrape textual content from website"""
        try:
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.content, "html.parser")

            return {
                "title": soup.title.string if soup.title else "",
                "meta_description": soup.find("meta", {"name": "description"})["content"]
                if soup.find("meta", {"name": "description"}) else "",
                "headings": [h.text.strip() for h in soup.find_all(["h1", "h2", "h3"])],
                "main_content": " ".join([p.text.strip() for p in soup.find_all("p")])[:2000],
                "links": [a.get("href", "") for a in soup.find_all("a", href=True)],
            }
        except Exception as e:
            logger.error(f"Error scraping content: {str(e)}")
            raise

    async def analyze_website(self, url: str) -> WebsiteAnalysisOutput:
        """Complete website analysis using both content and screenshots"""
        try:
            # Concurrent tasks for screenshots and content
            screenshots_task = self.capture_screenshots(url)
            content_task = asyncio.to_thread(self.scrape_content, url)

            screenshots, content = await asyncio.gather(screenshots_task, content_task)

            # Prepare visual analyses
            visual_analyses = []
            for screenshot in screenshots:
                try:
                    image = self._base64_to_image(screenshot["data"])
                    view_type = screenshot["type"].replace("_", " ").title()

                    # Skip analysis for error screenshots
                    if view_type == "Error":
                        continue

                    prompt = f"This is the {view_type} view of the website. Analyze the design, layout, visual hierarchy, and user experience."
                    response = self.model.generate_content([prompt, image])
                    visual_analyses.append(VisualAnalysis(view_type=view_type, analysis=response.text))
                except Exception as analysis_error:
                    logger.warning(f"Visual analysis error: {analysis_error}")

            # Content analysis
            content_prompt = f"""Analyze this website content:
            URL: {url}
            Title: {content['title']}
            Description: {content['meta_description']}
            Main Headings: {' | '.join(content['headings'])}
            """
            content_analysis = self.text_model.generate_content(content_prompt)

            # Combine analyses
            return WebsiteAnalysisOutput(
                url=url,
                timestamp=datetime.now().isoformat(),
                visual_analyses=visual_analyses,
                content_analysis=content_analysis.text,
            )

        except Exception as e:
            logger.error(f"Error in website analysis: {str(e)}")
            raise