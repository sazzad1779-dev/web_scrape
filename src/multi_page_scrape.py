# -------------------- IMPORTS -------------------- #
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from src.csv_save import append_to_csv
from src.config import create_driver
from src.sections import get_sections
# -------------------- UTILITIES -------------------- #
def safe_click(driver, wait, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        wait.until(EC.element_to_be_clickable(element)).click()
    except:
        driver.execute_script("arguments[0].click();", element)

def get_categories(driver, wait):
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.flex.gap-2.bg-white\\/10")))
    buttons = driver.find_elements(By.CSS_SELECTOR, "div.flex.gap-2.bg-white\\/10 button")
    return [b.text.strip() for b in buttons if b.text.strip()]

def get_hero_data(driver, wait):
    hero = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.peptide-hero-gradient")))
    name = hero.find_element(By.TAG_NAME, "h1").text.strip()
    subtitle = hero.find_element(By.TAG_NAME, "p").text.strip()
    facts = []
    cards = hero.find_elements(By.XPATH, ".//div[contains(@class,'rounded-2xl')]")
    for card in cards:
        lines = [l.strip() for l in card.text.split("\n") if l.strip()]
        if len(lines) >= 2:
            facts.append({
                "label": lines[0],
                "value": lines[1],
                "extra": lines[2] if len(lines) > 2 else ""
            })
    return {"name": name, "subtitle": subtitle, "facts": facts}

def get_quick_guide(driver, wait):
    # Quick check — returns immediately if section not found
    if not driver.find_elements(By.XPATH, "//h3[contains(text(),'Quick Start Guide')]"):
        return {}

    try:
        guide = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//h3[contains(text(),'Quick Start Guide')]/ancestor::div[contains(@class,'rounded-xl')]")
        ))

        rows = guide.find_elements(By.CSS_SELECTOR, "div.flex.gap-3")

        return {
            r.find_element(By.CSS_SELECTOR, ".text-label-sm").text.strip():
            r.find_element(By.CSS_SELECTOR, ".text-body-sm").text.strip()
            for r in rows
        }

    except TimeoutException:
        return {}


def get_community_insights(driver, wait):
    # Quick existence check (no delay)
    if not driver.find_elements(By.XPATH, "//h3[contains(.,'Community Insights')]"):
        return {}

    try:
        card = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//h3[contains(.,'Community Insights')]/ancestor::div[contains(@class,'rounded-xl')]")
        ))

        heading = card.find_element(By.TAG_NAME, "h3").text.strip()

        responses = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//h3[contains(.,'Community Insights')]/ancestor::div[contains(@class,'rounded-xl')]//p[contains(.,'responses')]")
        )).text

        rows = card.find_elements(By.CSS_SELECTOR, "div.flex.gap-3.items-start")

        insights = {heading: responses}
        insights.update({
            f"{heading}_{r.find_element(By.CSS_SELECTOR, '.text-label-sm').text.strip()}":
            r.find_element(By.CSS_SELECTOR, ".text-body-sm").text.strip()
            for r in rows
        })

        return insights

    except TimeoutException:
        return {}

def get_poll_results(driver, wait):
    if not driver.find_elements(By.XPATH, "//h3[contains(.,'Poll Results')]"):
        return {}
    
    try:
        card = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//h3[contains(text(),'Poll Results')]/ancestor::div[contains(@class,'rounded-xl')]")
        ))
        
        # RESET: Click first pagination dot to ensure we start at slide 1
        first_dot = card.find_element(By.CSS_SELECTOR, "button[aria-label='Go to question 1']")
        driver.execute_script("arguments[0].click();", first_dot)
        time.sleep(0.3)
        
        heading = card.find_element(By.TAG_NAME, "h3").text.strip()
        responses = card.find_element(By.XPATH, ".//p[contains(.,'responses')]").text.strip()
        poll_results = {heading: responses}
        
        slides = card.find_elements(By.CSS_SELECTOR, "div[role='group'][aria-roledescription='slide']")
        total_slides = len(slides)
        
        for i in range(total_slides):
            current_slide = slides[i]
            question = current_slide.find_element(By.TAG_NAME, "h4").text.strip()
            
            options = current_slide.find_elements(By.CSS_SELECTOR, "div.relative")
            for option in options:
                try:
                    label = option.find_element(By.CSS_SELECTOR, "span.truncate").text.strip()
                    value = option.find_element(By.CSS_SELECTOR, "span.whitespace-nowrap").text.strip()
                    poll_results[f"poll_{question}_{label}"] = value
                except:
                    continue
            
            if i < total_slides - 1:
                next_btn = card.find_element(By.CSS_SELECTOR, "button[aria-label='Next question']")
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(0.3)
                slides = card.find_elements(By.CSS_SELECTOR, "div[role='group'][aria-roledescription='slide']")
        
        return poll_results
        
    except Exception as e:
        print(f"Error in get_poll_results: {e}")
        return {}


# def get_sections(driver, wait):
#     data = []
#     try:
#         wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "section.mb-12")))
#         for section in driver.find_elements(By.CSS_SELECTOR, "section.mb-12"):
#             section_data = {}
#             has_interactive = False
#             current_heading = None
#             heading_counter = {}
#             # Get h2 headings
#             for el in section.find_elements(By.XPATH, ".//h2"):
#                 text = el.text.strip()
#                 if text:
#                     current_heading = text
                    
#             # ---- CHECK FOR TAB BUTTONS ----
#             tab_container = section.find_elements(By.CSS_SELECTOR, "div.flex.gap-6")
#             if tab_container:
#                 tab_buttons = tab_container[0].find_elements(By.TAG_NAME, "button")
#                 if tab_buttons:
#                     has_interactive = True
#                     content_wrapper = tab_container[0].find_element(By.XPATH, "./ancestor::div[contains(@class, 'rounded-xl')]")
                    
#                     for tab_btn in tab_buttons:
#                         try:
#                             tab_title = tab_btn.find_element(By.CSS_SELECTOR, "span.font-medium").text.strip()
#                             safe_click(driver, wait, tab_btn)
#                             time.sleep(0.3)
                            
#                             content_area = content_wrapper.find_element(By.XPATH, ".//div[contains(@class, 'border-b')]/following-sibling::div")
#                             content = content_area.text.strip()
                            
#                             if current_heading:
#                                 if current_heading not in section_data:
#                                     section_data[current_heading] = []
#                                 section_data[current_heading].append({"tab": tab_title, "content": content})
#                         except Exception as e:
#                             print(f"Tab error: {e}")
#                             continue
            
#             # ---- CHECK FOR ACCORDION BUTTONS ----
#             accordion_buttons = section.find_elements(By.CSS_SELECTOR, "button[data-state]")
#             if accordion_buttons:
#                 has_interactive = True
#                 for btn in accordion_buttons:
#                     if btn.accessible_name in button_skip_list:
#                         continue
                    
#                     try:
#                         title = btn.text.strip()
#                         panel_id = btn.get_attribute("aria-controls")

#                         if btn.get_attribute("data-state") == "closed":
#                             safe_click(driver, wait, btn)

#                         panel = wait.until(EC.visibility_of_element_located((By.ID, panel_id)))
#                         for el in panel.find_elements(By.XPATH, ".//h3|.//h4|.//p"):
#                             if el.tag_name in ['h3', 'h4']:
#                                 text = el.text.strip()
#                                 current_heading = f"{current_heading}_{title}_{text}"
#                             if el.tag_name in ['p']:
#                                 content = el.text.strip()
#                         if current_heading:
#                             if current_heading not in section_data:
#                                 section_data[current_heading] = ""
#                             section_data[current_heading].append({"dropdown": f"{current_heading}", "content": content})
#                     except:
#                         continue

#             # ---- STATIC CONTENT (only if no interactive elements found) ----
#             if not has_interactive:
#                 heading = None
                
#                 for el in section.find_elements(By.XPATH, ".//h3|.//h4|.//p|.//table|.//li|.//pre|.//ol"):
#                     text = el.text.strip()
#                     if text:
#                         # Check if this element is inside the check-card layout
#                         try:
#                             parent_card = el.find_element(
#                                 By.XPATH,
#                                 "./ancestor::div[contains(@class,'gap-4') and contains(@class,'items-start')]"
#                             )
#                             check_el = parent_card.find_elements(By.CSS_SELECTOR, "div.rounded-full")
#                             if check_el:
#                                 check = check_el[0].text.strip()
#                                 text = f"{check}"
#                         except:
#                             pass
                        
#                         # If it's a heading (h3/h4), set it as heading
#                         if el.tag_name in ['h3', 'h4']:

#                             base_heading = f"{current_heading}" if current_heading else text

#                             # only when checkmark row
#                             if "✓" in text:
#                                 count = heading_counter.get(base_heading, 0) + 1
#                                 heading_counter[base_heading] = count
#                                 heading = f"{base_heading}_{count}(✓)"
#                             else:
#                                 heading = f"{base_heading}_{text}"

#                             section_data[heading] = ""

#                         elif heading or current_heading:
#                             if heading:
#                                 section_data[heading] += text + " "
#                             else:
#                                 section_data[current_heading]=""
#                                 section_data[current_heading] += text + " "

                            
#             data.append(section_data)
#     except TimeoutException:
#         pass
#     return data

# def get_sections(driver, wait):
#     data = []
#     try:
#         wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "section.mb-12")))
#         for section in driver.find_elements(By.CSS_SELECTOR, "section.mb-12"):
#             section_data = []
#             has_interactive = False
#             for el in section.find_elements(By.XPATH, ".//h2"):
#                 text = el.text.strip()
#                 if text:
#                     section_data.append({"type": el.tag_name, "text": text})

                    
#             # ---- CHECK FOR TAB BUTTONS ----
#             tab_container = section.find_elements(By.CSS_SELECTOR, "div.flex.gap-6")
#             if tab_container:
#                 tab_buttons = tab_container[0].find_elements(By.TAG_NAME, "button")
#                 if tab_buttons:
#                     has_interactive = True
                    
#                     # Get the content wrapper (parent of the tab container)
#                     content_wrapper = tab_container[0].find_element(By.XPATH, "./ancestor::div[contains(@class, 'rounded-xl')]")
                    
#                     for tab_btn in tab_buttons:
#                         try:
#                             # Get tab title
#                             tab_title = tab_btn.find_element(By.CSS_SELECTOR, "span.font-medium").text.strip()
                            
#                             # Click the tab
#                             safe_click(driver, wait, tab_btn)
#                             time.sleep(0.3)  # Wait for content to load
                            
#                             # Get content from the sibling div (after the border-b div containing tabs)
#                             content_area = content_wrapper.find_element(By.XPATH, ".//div[contains(@class, 'border-b')]/following-sibling::div")
#                             content = content_area.text.strip()
                            
#                             section_data.append({"tab": tab_title, "content": content})
#                         except Exception as e:
#                             print(f"Tab error: {e}")
#                             continue
            
#             # ---- CHECK FOR ACCORDION BUTTONS ----
#             accordion_buttons = section.find_elements(By.CSS_SELECTOR, "button[data-state]")
#             if accordion_buttons:
#                 has_interactive = True
#                 for btn in accordion_buttons:
#                     if btn.accessible_name in button_skip_list:
#                         continue
                    
#                     try:
#                         title = btn.text.strip()
#                         panel_id = btn.get_attribute("aria-controls")

#                         if btn.get_attribute("data-state") == "closed":
#                             safe_click(driver, wait, btn)

#                         panel = wait.until(EC.visibility_of_element_located((By.ID, panel_id)))
#                         content = panel.text.strip()
#                         section_data.append({"dropdown": title, "content": content})
#                     except:
#                         continue

#             # ---- STATIC CONTENT (only if no interactive elements found) ----
#             if not has_interactive:
#                 for el in section.find_elements(By.XPATH, ".//h3|.//h4|.//p|.//table|.//li|.//pre|.//ol"):
#                     text = el.text.strip()
#                     if text:

#                         # 🔹 Check if this element is inside the check-card layout
#                         try:
#                             parent_card = el.find_element(
#                                 By.XPATH,
#                                 "./ancestor::div[contains(@class,'gap-4') and contains(@class,'items-start')]"
#                             )

#                             check_el = parent_card.find_elements(
#                                 By.CSS_SELECTOR,
#                                 "div.rounded-full"
#                             )

#                             if check_el:
#                                 check = check_el[0].text.strip()
#                                 if check in check_list:
#                                     text = f"{check}"
#                                 else:
#                                     text = f"{check}"
                                
#                         except:
#                             pass
#                         section_data.append({"type": el.tag_name, "text": text})
#             data.append(section_data)
#     except TimeoutException:
#         pass
#     return data

def scrape_url(url):
    driver, wait = create_driver()
    start_time = time.time()
    expanded=True # set to False to only take visible text, True to also capture dropdown content in separate columns
    try:
        print(f"[INFO] Processing: {url}")
        driver.get(url)
        time.sleep(2)

        results = {}
        categories = get_categories(driver, wait)

        for cat in categories:
            buttons = driver.find_elements(By.CSS_SELECTOR, "div.flex.gap-2.bg-white\\/10 button")
            for b in buttons:
                if b.text.strip() == cat:
                    safe_click(driver, wait, b)
                    break
            results[cat] = {
                "hero": get_hero_data(driver, wait),
                "quick_guide": get_quick_guide(driver, wait),
                "community_insights": get_community_insights(driver, wait),
                "poll_results": get_poll_results(driver, wait),
                "sections": get_sections(driver, wait),
                "url": driver.current_url
            }
        # print("results: ",results,"\n\n")
        result_rows, error = append_to_csv(results)  # returns rows, error (None if success)
        # print(f"[INFO] Completed: {url} in {time.time() - start_time:.2f}s with {len(result_rows)} rows")
        return result_rows, error  # Return rows and no error

    except Exception as e:
        print(f"[ERROR] {url}: {e}")
        return [], f"{url} - {e}"  # empty rows, log error
    finally:
        driver.quit()
