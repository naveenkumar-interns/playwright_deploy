from flask import Flask, jsonify
from playwright.sync_api import sync_playwright

app = Flask(__name__)

@app.route('/scrape_jobs', methods=['GET'])
def scrape_jobs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        base_url = "https://www.freelancer.com"
        page.goto(f"{base_url}/jobs")
        page.fill("input[name=search_keyword]", "django")
        page.click("button[id=search-submit]")
        
        job_elements = page.query_selector_all("a.JobSearchCard-primary-heading-link")
        jobs = []
        if job_elements:
            for job_element in job_elements:
                title = job_element.inner_text().strip()
                link = base_url + job_element.get_attribute("href")
                description_element = job_element.evaluate_handle("element => element.closest('.JobSearchCard-primary').querySelector('.JobSearchCard-primary-description')")
                description = description_element.inner_text().strip() if description_element else "No description available"
                time_left = job_element.evaluate("element => element.closest('.JobSearchCard-primary').querySelector('.JobSearchCard-primary-heading-days').innerText")
                time_left = time_left.strip() if time_left else "No time left"
                jobs.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "time_left": time_left
                })

        browser.close()
        return jsonify(jobs)

if __name__ == '__main__':
    app.run(debug=True)
