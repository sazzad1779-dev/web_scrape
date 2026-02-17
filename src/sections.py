# -------------------- IMPORTS -------------------- #
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from src.config import button_skip_list
def get_sections(driver, wait):
    data = []
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "section.mb-12")))
        sections = driver.find_elements(By.CSS_SELECTOR, "section.mb-12")
        
        for section in sections:
            h2_text = get_h2_heading(section)
            section_data = {}
            
            # Route to appropriate handler based on section type
            
            # 
            if has_accordions(section):
                process_accordions(section, h2_text, section_data,driver, wait)
            elif has_tabs(section):
                process_tabs(section, h2_text, section_data, driver, wait)
            elif has_table(section):
                process_table(section, h2_text, section_data)
            elif has_numbered_steps(section):
                process_numbered_steps(section, h2_text, section_data)
            elif has_checkmark_list(section):
                process_checkmark_list(section, h2_text, section_data)
            elif has_bullet_list(section):
                process_bullet_list(section, h2_text, section_data)
            else:
                process_static_content(section, h2_text, section_data)
            
            if section_data:
                data.append(section_data)
                
    except TimeoutException:
        pass
    return data


# ============= UTILITY FUNCTIONS =============

def get_h2_heading(section):
    """Extract h2 heading and normalize it"""
    h2_elements = section.find_elements(By.XPATH, ".//h2")
    if h2_elements:
        text = h2_elements[0].text.strip()
        return text.lower().replace(" ", "_").replace("&", "and")
    return "unknown"


def has_tabs(section):
    return bool(section.find_elements(
        By.CSS_SELECTOR,
        "div.rounded-xl div.border-b div.flex.gap-6 > button"
    ))




def has_accordions(section):
    return bool(section.find_elements(By.CSS_SELECTOR, "button[data-state]"))


def has_table(section):
    return bool(section.find_elements(By.TAG_NAME, "table"))


def has_numbered_steps(section):
    """Check for numbered steps (How to Reconstitute pattern)"""
    steps = section.find_elements(By.XPATH, ".//div[contains(@class, 'rounded-full')]")
    if steps:
        first_text = steps[0].text.strip()
        return first_text.isdigit()
    return False


def has_checkmark_list(section):
    """Check for checkmark/warning list (Quality Indicators pattern)"""
    items = section.find_elements(By.XPATH, ".//div[contains(@class, 'rounded-full')]")
    if items:
        first_text = items[0].text.strip()
        return first_text in ["✓", "!", "✗"]
    return False


def has_bullet_list(section):
    """Check for bullet point list (What to Expect pattern)"""
    return bool(section.find_elements(By.XPATH, ".//li"))


# ============= SECTION HANDLERS =============
def process_tabs(section, h2_text, section_data, driver, wait):
    """Handle tabbed content (Side Effects & Safety, References)"""

    # Find tab buttons once
    tab_buttons = section.find_elements(By.XPATH, ".//div[contains(@class, 'border-b')]//button")
    if not tab_buttons:
        return

    for tab_btn in tab_buttons:
        try:
            # --- tab name ---
            tab_name = tab_btn.find_element(By.CSS_SELECTOR, "span.font-medium")\
                              .text.strip().lower().replace(" ", "_").replace("&", "and")

            # --- click tab ---
            safe_click(driver, wait, tab_btn)

            # wait until tab becomes active instead of sleep
            wait.until(lambda d: "border" in tab_btn.get_attribute("class"))

            # --- parent tab container (cache once per button) ---
            tab_parent = tab_btn.find_element(By.XPATH, "./ancestor::div[contains(@class, 'border-b')]")

            # --- SAME LOGIC as yours, just safer sibling selection ---
            content_area = tab_parent.find_element(By.XPATH, "./following-sibling::div[1]")

            # ---------- REFERENCES TYPE ----------
            h4_elements = content_area.find_elements(By.TAG_NAME, "h4")
            citation_cards = content_area.find_elements(By.CSS_SELECTOR, "div.p-6 > p")


            if h4_elements :
                for idx, h4 in enumerate(h4_elements, 1):
                    parent_div = h4.find_element(By.XPATH, "./parent::div")

                    content_parts = []

                    elems = parent_div.find_elements(By.XPATH, "./*[self::div or self::p or self::a]")
                    
                    for elem in elems:
                        text = elem.text.strip()
                        if text and text not in content_parts :
                            content_parts.append(text)

                    column_name = f"{h2_text}_{tab_name}_({h4.text.strip().replace("-","").replace(" ","_")})"
                    section_data[column_name] = " ".join(content_parts)
                
            elif citation_cards and tab_name=="citations":
                cards = content_area.find_elements(By.CSS_SELECTOR, "div.p-6")
                for idx, card in enumerate(cards, 1):
                    content_parts = []

                    for elem in card.find_elements(By.XPATH, ".//*"):
                        text = elem.text.strip()
                        if text and text not in content_parts:
                            content_parts.append(text)

                    column_name = f"{h2_text}_{tab_name}_{idx}"
                    section_data[column_name] = " ".join(content_parts)


            # ---------- SIDE EFFECTS TYPE ----------
            else:
                list_items = content_area.find_elements(By.XPATH, ".//li")

                if list_items:
                    for idx, li in enumerate(list_items, 1):
                        column_name = f"{h2_text}_{tab_name}_{idx}"
                        section_data[column_name] = li.text.strip()
                else:
                    column_name = f"{h2_text}_{tab_name}"
                    section_data[column_name] = content_area.text.strip()

        except Exception as e:
            print(f"Tab processing error: {e}")
            continue



def process_accordions(section, h2_text, section_data, driver, wait):
    """Handle accordion sections (Research Indications, Peptide Interactions)"""
    accordion_buttons = section.find_elements(By.CSS_SELECTOR, "button[data-state]")
    
    for btn in accordion_buttons:
        try:
            btn_text = btn.text.strip().lower()

            if any(skip in btn_text for skip in button_skip_list):
                continue


            # Get accordion title from the span inside the button
            # title_elem = btn.find_element(By.XPATH, ".//span[contains(@class, 'text-zinc-900') or contains(@class, 'text-zinc-900')]")
            # title = title_elem.text.strip().lower().replace(" ", "_").replace("/", "_")
            title=btn.text.strip().lower().replace(" ", "_").replace("/", "_").replace("\n","_")
            
            # Get the data-state
            data_state = btn.get_attribute("data-state")
            
            # Click to open if closed
            if data_state == "closed":
                safe_click(driver, wait, btn)
                time.sleep(0.5)
            
            # Get panel ID and find panel
            panel_id = btn.get_attribute("aria-controls")
            
            try:
                panel = wait.until(EC.presence_of_element_located((By.ID, panel_id)))
            except:
                panel = section.find_element(By.ID, panel_id)
            
            # Check for h4 elements within the panel
            h4_elements = panel.find_elements(By.TAG_NAME, "h4")
            
            if h4_elements:
                # Research Indications pattern: h2_h3_h4
                for h4 in h4_elements:
                    h4_text = h4.text.strip().lower().replace(" ", "_").replace("/", "_")
                    
                    # Get the p tag that follows the h4
                    try:
                        p_elem = h4.find_element(By.XPATH, "./following-sibling::p")
                        content = p_elem.text.strip()
                    except:
                        # If no following p, get parent div text
                        parent_div = h4.find_element(By.XPATH, "./parent::div")
                        content = parent_div.text.strip()
                    
                    column_name = f"{h2_text}_{title}_({h4_text})"
                    section_data[column_name] = content
            else:
                # Peptide Interactions pattern: just h2_h3
                # Get all the content text
                content_text = panel.text.strip()
                
                # Remove the h3 title if it's in the content
                if title in content_text.lower():
                    # Get only the p tags
                    p_elements = panel.find_elements(By.TAG_NAME, "p")
                    if p_elements:
                        content_text = " ".join([p.text.strip() for p in p_elements])
                
                column_name = f"{h2_text}_{title}"
                section_data[column_name] = content_text
                
        except Exception as e:
            print(f"Accordion processing error for {h2_text}: {e}")
            continue


def safe_click(driver, wait, element):
    """Safely click an element with multiple fallback methods"""
    try:
        # Method 1: Scroll into view and click
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.2)
        element.click()
    except:
        try:
            # Method 2: Wait for clickable and click
            wait.until(EC.element_to_be_clickable(element))
            element.click()
        except:
            try:
                # Method 3: JavaScript click
                driver.execute_script("arguments[0].click();", element)
            except Exception as e:
                print(f"Click failed: {e}")


def process_table(section, h2_text, section_data):
    """Handle table sections (Research Protocols)"""
    # Check for disclaimer
    disclaimer = section.find_elements(By.XPATH, ".//div[contains(@class, 'amber-50')]//p")
    if disclaimer:
        section_data[f"{h2_text}_info"] = disclaimer[0].text.strip()
    
    # Process table
    table = section.find_element(By.TAG_NAME, "table")
    headers = [th.text.strip().lower().replace(" ", "_") for th in table.find_elements(By.TAG_NAME, "th")]
    rows = table.find_elements(By.TAG_NAME, "tbody")[0].find_elements(By.TAG_NAME, "tr")
    
    for row_idx, row in enumerate(rows, 1):
        cells = row.find_elements(By.TAG_NAME, "td")
        for col_idx, cell in enumerate(cells):
            if col_idx < len(headers):
                column_name = f"{h2_text}_{headers[col_idx]}_{row_idx}"
                section_data[column_name] = cell.text.strip()
    
    # Check for timing note
    timing_note = section.find_elements(By.XPATH, ".//div[contains(@class, 'blue-50')]//p")
    if timing_note:
        section_data[f"{h2_text}_timing"] = timing_note[0].text.strip()


def process_numbered_steps(section, h2_text, section_data):
    """Handle numbered step sections (How to Reconstitute)"""
    # Check for disclaimer/note at top
    disclaimer = section.find_elements(By.XPATH, ".//div[contains(@class, 'amber-50')]//p")
    if disclaimer:
        section_data[f"{h2_text}_info"] = disclaimer[0].text.strip()
    
    # Process numbered steps
    step_containers = section.find_elements(By.XPATH, ".//div[contains(@class, 'flex gap-4 items-start')]")
    
    for container in step_containers:
        try:
            # Get step number
            number_elem = container.find_element(By.XPATH, ".//div[contains(@class, 'rounded-full')]")
            step_num = number_elem.text.strip()
            
            # Get step content
            content_elem = container.find_element(By.TAG_NAME, "p")
            content = content_elem.text.strip()
            
            column_name = f"{h2_text}_{step_num}"
            section_data[column_name] = content
            
        except:
            continue

def process_checkmark_list(section, h2_text, section_data):
    """Handle checkmark/warning list sections (Quality Indicators)"""
    list_containers = section.find_elements(By.XPATH, ".//div[contains(@class, 'flex gap-4 items-start')]")
    
    # Counter for each icon type
    icon_counters = {}
    
    for container in list_containers:
        try:
            # Get icon
            icon_elem = container.find_element(By.XPATH, ".//div[contains(@class, 'rounded-full')]")
            icon = icon_elem.text.strip()
            
            # Get content
            content_div = container.find_element(By.XPATH, ".//div[not(contains(@class, 'rounded-full'))]")
            h3_elem = content_div.find_element(By.TAG_NAME, "h3")
            p_elem = content_div.find_element(By.TAG_NAME, "p")
            
            content = f"{p_elem.text.strip()}"
            
            # Increment counter for this icon type
            if icon not in icon_counters:
                icon_counters[icon] = 0
            icon_counters[icon] += 1
            
            # Build column name with checkmark symbol
            column_name = f"{h2_text}_{h3_elem.text.strip()}({icon})"
            section_data[column_name] = content
            
        except:
            continue


def process_bullet_list(section, h2_text, section_data):
    """Handle bullet point list sections (What to Expect)"""
    list_items = section.find_elements(By.XPATH, ".//ul/li")
    
    for idx, li in enumerate(list_items, 1):
        column_name = f"{h2_text}_{idx}"
        section_data[column_name] = li.text.strip()


def process_static_content(section, h2_text, section_data):
    """Handle static content sections (Overview, Molecular Information, Pharmacokinetics)"""
    # Process h3 sections with content
    h3_elements = section.find_elements(By.TAG_NAME, "h3")
    
    if h3_elements:
        for h3 in h3_elements:
            try:
                h3_text = h3.text.strip().lower().replace(" ", "_").replace("?", "")
                
                # Get following p tag
                p_elem = h3.find_element(By.XPATH, "./following-sibling::p")
                content = p_elem.text.strip()
                
                column_name = f"{h2_text}_{h3_text}"
                section_data[column_name] = content
            except:
                continue
    
    # Check for grid pattern (Molecular Information - Weight, Length, Type)
    grid_divs = section.find_elements(By.XPATH, ".//div[contains(@class, 'grid')]//div/p[@class and contains(@class, 'text-xs')]")
    
    if grid_divs:
        for div in grid_divs:
            try:
                label = div.text.strip().lower().replace(" ", "_")
                value_elem = div.find_element(By.XPATH, "./following-sibling::p")
                value = value_elem.text.strip()
                
                column_name = f"{h2_text}_{label}"
                section_data[column_name] = value
            except:
                continue
    
    # Check for code blocks (amino acid sequence)
    code_blocks = section.find_elements(By.XPATH, ".//div/p[contains(@class, 'font-mono')]")
    if code_blocks:
        section_data[f"{h2_text}_amino_acid_sequence"] = code_blocks[0].text.strip()
    
    # If no specific structure found, get all text
    if not section_data:
        section_data[f"{h2_text}_others"] = section.text.strip()


def safe_click(driver, wait, element):
    """Safely click an element"""
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        wait.until(EC.element_to_be_clickable(element))
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)