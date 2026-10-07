# =========================================================
# data_Edokk.py
# EDOC DATA COLLECTOR
# =========================================================

import csv
import logging
import time
from datetime import datetime
from pathlib import Path

import undetected_chromedriver as uc

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    WebDriverException,
)


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("edoc_collector")


# =========================================================
# PROJECT PATH
# =========================================================

# ไฟล์นี้อยู่ที่:
#
# Edokk_rtarf-v2/
# ├── drivers/
# ├── Scrap_data/
# │   └── data_Edokk.py
# └── sdc_env/

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent


# =========================================================
# CONFIG
# =========================================================

UNIT_CODE = "J6"


# ---------------------------------------------------------
# ใส่ URL จริง
# ---------------------------------------------------------

EDOC_LOGIN_URL = "https://edocument.rtarf.mi.th/edoc/login.xhtml"

EDOC_INBOX_URL = "https://edocument.rtarf.mi.th/edoc/inbox.xhtml"


# ---------------------------------------------------------
# Account
# ---------------------------------------------------------

USERNAME = "SDC_AI_J6"

PASSWORD = "d0&Y5$n6T#DW"


# =========================================================
# CHROME
# =========================================================

CHROME_VERSION_MAIN = 145


CHROME_BINARY = str(
    PROJECT_DIR
    / "drivers"
    / "chrome-win64"
    / "chrome.exe"
)


CHROMEDRIVER_PATH = str(
    PROJECT_DIR
    / "drivers"
    / "chromedriver-win64"
    / "chromedriver.exe"
)


# =========================================================
# OUTPUT
# =========================================================

OUTPUT_DIR = (
    SCRIPT_DIR
    / "data"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


TODAY = datetime.now().strftime(
    "%Y%m%d"
)


CSV_FILE = (
    OUTPUT_DIR
    / f"edoc_{UNIT_CODE.lower()}_{TODAY}.csv"
)


CSV_COLUMNS = [
    "unit_code",
    "row_no",
    "subject",
    "real_subject",
    "document_owner",
    "detail_url",
    "collected_at",
]


# =========================================================
# CHROME OPTIONS
# =========================================================

def build_options():

    options = uc.ChromeOptions()

    options.binary_location = CHROME_BINARY

    options.add_argument(
        "--start-maximized"
    )

    options.add_argument(
        "--no-first-run"
    )

    options.add_argument(
        "--no-default-browser-check"
    )

    options.add_argument(
        "--disable-popup-blocking"
    )

    options.add_argument(
        "--disable-notifications"
    )

    options.add_argument(
        "--disable-extensions"
    )

    options.add_argument(
        "--disable-dev-shm-usage"
    )

    options.add_argument(
        "--no-sandbox"
    )

    return options


# =========================================================
# CHECK FILES
# =========================================================

def validate_files():

    if not Path(
        CHROME_BINARY
    ).exists():

        raise FileNotFoundError(
            f"ไม่พบ Chrome: {CHROME_BINARY}"
        )

    if not Path(
        CHROMEDRIVER_PATH
    ).exists():

        raise FileNotFoundError(
            f"ไม่พบ ChromeDriver: {CHROMEDRIVER_PATH}"
        )

    logger.info(
        "Chrome = %s",
        CHROME_BINARY,
    )

    logger.info(
        "ChromeDriver = %s",
        CHROMEDRIVER_PATH,
    )


# =========================================================
# CREATE DRIVER
# =========================================================

def create_driver():

    validate_files()

    logger.info(
        "กำลังเปิด Chrome..."
    )

    driver = uc.Chrome(
        options=build_options(),

        browser_executable_path=CHROME_BINARY,

        driver_executable_path=CHROMEDRIVER_PATH,

        version_main=CHROME_VERSION_MAIN,

        use_subprocess=True,
    )

    driver.set_page_load_timeout(
        90
    )

    return driver


# =========================================================
# LOGIN
# =========================================================

def login(driver):

    logger.info(
        "กำลังเข้า EDOC..."
    )

    logger.info(
        "LOGIN URL = %s",
        EDOC_LOGIN_URL,
    )

    # -----------------------------------------------------
    # เปิดหน้า Login
    # -----------------------------------------------------

    driver.get(
        EDOC_LOGIN_URL
    )

    wait = WebDriverWait(
        driver,
        30,
    )

    logger.info(
        "CURRENT URL = %s",
        driver.current_url,
    )

    logger.info(
        "PAGE TITLE = %s",
        driver.title,
    )


    # =====================================================
    # USERNAME
    # =====================================================

    logger.info(
        "กำลังกรอก Username..."
    )

    username = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//*[@id="wrapper"]/div/div/div/div/div/div[1]/div/div/input'
            )
        )
    )

    driver.execute_script(
        """
        arguments[0].scrollIntoView({
            block: 'center'
        });
        """,
        username,
    )

    time.sleep(
        0.3
    )

    try:

        username.click()

        username.send_keys(
            Keys.CONTROL,
            "a",
        )

        username.send_keys(
            Keys.DELETE
        )

        username.send_keys(
            USERNAME
        )

        logger.info(
            "กรอก Username สำเร็จ"
        )

    except Exception as e:

        logger.warning(
            "send_keys Username ไม่สำเร็จ: %s",
            e,
        )

        username = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//*[@id="wrapper"]/div/div/div/div/div/div[1]/div/div/input'
                )
            )
        )

        driver.execute_script(
            """
            const el = arguments[0];
            const value = arguments[1];

            el.focus();
            el.value = value;

            el.dispatchEvent(
                new Event('input', {
                    bubbles: true
                })
            );

            el.dispatchEvent(
                new Event('change', {
                    bubbles: true
                })
            );
            """,
            username,
            USERNAME,
        )

        logger.info(
            "กรอก Username ผ่าน JavaScript สำเร็จ"
        )


    # =====================================================
    # PASSWORD
    # =====================================================

    logger.info(
        "กำลังกรอก Password..."
    )

    password = wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "input#password",
            )
        )
    )

    driver.execute_script(
        """
        arguments[0].scrollIntoView({
            block: 'center'
        });
        """,
        password,
    )

    time.sleep(
        0.3
    )

    try:

        password = wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "input#password",
                )
            )
        )

        password.click()

        password.send_keys(
            Keys.CONTROL,
            "a",
        )

        password.send_keys(
            Keys.DELETE
        )

        password.send_keys(
            PASSWORD
        )

        logger.info(
            "กรอก Password สำเร็จ"
        )

    except Exception as e:

        logger.warning(
            "send_keys Password ไม่สำเร็จ: %s",
            e,
        )

        logger.info(
            "กำลังใช้ JavaScript กรอก Password..."
        )

        password = wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "input#password",
                )
            )
        )

        driver.execute_script(
            """
            const el = arguments[0];
            const value = arguments[1];

            el.focus();
            el.value = value;

            el.dispatchEvent(
                new Event('input', {
                    bubbles: true
                })
            );

            el.dispatchEvent(
                new Event('change', {
                    bubbles: true
                })
            );

            el.dispatchEvent(
                new Event('blur', {
                    bubbles: true
                })
            );
            """,
            password,
            PASSWORD,
        )

        logger.info(
            "กรอก Password ผ่าน JavaScript สำเร็จ"
        )


    # =====================================================
    # LOGIN BUTTON
    # =====================================================

    logger.info(
        "กำลังค้นหาปุ่มเข้าสู่ระบบ..."
    )

    # HTML จริง:
    #
    # <input
    #   id="j_idt34"
    #   value="เข้าสู่ระบบ"
    #   type="submit"
    # >

    login_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                '//input[@type="submit" and @value="เข้าสู่ระบบ"]'
            )
        )
    )

    driver.execute_script(
        """
        arguments[0].scrollIntoView({
            block: 'center'
        });
        """,
        login_button,
    )

    time.sleep(
        0.3
    )

    try:

        login_button.click()

        logger.info(
            "กดปุ่มเข้าสู่ระบบสำเร็จ"
        )

    except Exception as e:

        logger.warning(
            "click Login ปกติไม่ได้: %s",
            e,
        )

        login_button = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//input[@type="submit" and @value="เข้าสู่ระบบ"]'
                )
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            login_button,
        )

        logger.info(
            "กด Login ผ่าน JavaScript สำเร็จ"
        )


    # =====================================================
    # WAIT LOGIN
    # =====================================================

    logger.info(
        "กำลังรอระบบ Login..."
    )

    time.sleep(
        5
    )

    logger.info(
        "URL หลัง Login = %s",
        driver.current_url,
    )

    logger.info(
        "PAGE TITLE หลัง Login = %s",
        driver.title,
    )


# =========================================================
# OPEN INBOX
# =========================================================

def open_inbox(driver):

    logger.info("กำลังเปิดหน้ารายการหนังสือ...")

    wait = WebDriverWait(
        driver,
        30
    )

    logger.info(
        "URL ปัจจุบัน = %s",
        driver.current_url
    )

    logger.info(
        "PAGE TITLE = %s",
        driver.title
    )

    # =====================================================
    # หาเมนูรูป message_green.png
    # =====================================================

    logger.info(
        "กำลังค้นหาเมนูหนังสือ..."
    )

    inbox_button = wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                '//div[contains(@class,"el-card-avatar")]'
                '//a[.//img[contains(@src,"message_green.png")]]'
            )
        )
    )

    # =====================================================
    # Scroll
    # =====================================================

    driver.execute_script(
        """
        arguments[0].scrollIntoView({
            block: 'center'
        });
        """,
        inbox_button
    )

    time.sleep(0.5)

    # =====================================================
    # Click
    # =====================================================

    try:

        inbox_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//div[contains(@class,"el-card-avatar")]'
                    '//a[.//img[contains(@src,"message_green.png")]]'
                )
            )
        )

        inbox_button.click()

        logger.info(
            "กดเมนูหนังสือสำเร็จ"
        )

    except Exception as e:

        logger.warning(
            "click ปกติไม่ได้: %s",
            e
        )

        logger.info(
            "ลอง click ผ่าน JavaScript..."
        )

        inbox_button = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//div[contains(@class,"el-card-avatar")]'
                    '//a[.//img[contains(@src,"message_green.png")]]'
                )
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            inbox_button
        )

        logger.info(
            "กดเมนูหนังสือผ่าน JavaScript สำเร็จ"
        )

    # =====================================================
    # รอระบบเปลี่ยนหน้า
    # =====================================================

    logger.info(
        "กำลังรอหน้ารายการหนังสือ..."
    )

    time.sleep(3)

    logger.info(
        "URL หลังเปิดเมนู = %s",
        driver.current_url
    )

    logger.info(
        "TITLE หลังเปิดเมนู = %s",
        driver.title
    )

    # =====================================================
    # รอให้มี table
    # =====================================================

    try:

        wait.until(
            EC.presence_of_element_located(
                (
                    By.TAG_NAME,
                    "table"
                )
            )
        )

        logger.info(
            "พบ Table ในหน้ารายการหนังสือ"
        )

    except TimeoutException:

        logger.warning(
            "ยังไม่พบ Table หลังเปิดเมนูหนังสือ"
        )

        # Debug จำนวน table
        tables = driver.find_elements(
            By.TAG_NAME,
            "table"
        )

        logger.info(
            "จำนวน Table = %s",
            len(tables)
        )

        raise


# =========================================================
# GET ELEMENT VALUE
# =========================================================

def get_value(
    driver,
    by,
    selector,
    timeout=5,
):

    try:

        element = WebDriverWait(
            driver,
            timeout,
        ).until(
            EC.presence_of_element_located(
                (
                    by,
                    selector,
                )
            )
        )

        # -------------------------------------------------
        # input value
        # -------------------------------------------------

        value = element.get_attribute(
            "value"
        )

        if value:

            return value.strip()

        # -------------------------------------------------
        # normal text
        # -------------------------------------------------

        value = (
            element.text
            or ""
        ).strip()

        return value

    except Exception:

        return ""


# =========================================================
# SAVE CSV
# =========================================================

def save_csv(data):

    file_exists = (
        CSV_FILE.exists()
    )

    with open(
        CSV_FILE,
        "a",
        encoding="utf-8-sig",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=CSV_COLUMNS,
        )

        if not file_exists:

            writer.writeheader()

        writer.writerow(
            data
        )


# =========================================================
# LOAD OLD DATA
# =========================================================

def load_existing_subjects():

    existing = set()

    if not CSV_FILE.exists():

        return existing

    try:

        with open(
            CSV_FILE,
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as f:

            reader = csv.DictReader(
                f
            )

            for row in reader:

                real_subject = (
                    row.get(
                        "real_subject",
                        ""
                    )
                    or ""
                ).strip()

                subject = (
                    row.get(
                        "subject",
                        ""
                    )
                    or ""
                ).strip()

                key = (
                    real_subject
                    or subject
                )

                if key:

                    existing.add(
                        key
                    )

    except Exception:

        logger.exception(
            "อ่านข้อมูล CSV เดิมไม่สำเร็จ"
        )

    return existing


# =========================================================
# READ DOCUMENT DETAIL
# =========================================================

def collect_detail(
    driver,
    row_no,
    subject,
):

    logger.info(
        "กำลังอ่านรายละเอียด ROW %s",
        row_no,
    )


    # =====================================================
    # REAL SUBJECT
    # =====================================================

    real_subject = get_value(
        driver,
        By.CSS_SELECTOR,
        "input[name='j_idt280']",
        timeout=10,
    )


    # =====================================================
    # DOCUMENT OWNER
    # =====================================================

    document_owner = get_value(
        driver,
        By.CSS_SELECTOR,
        "[id$='txtdocto']",
        timeout=5,
    )


    # =====================================================
    # DATA
    # =====================================================

    data = {

        "unit_code": UNIT_CODE,

        "row_no": row_no,

        "subject": subject,

        "real_subject": real_subject,

        "document_owner": document_owner,

        "detail_url": driver.current_url,

        "collected_at": (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ),
    }

    return data


# =========================================================
# WAIT TABLE
# =========================================================

def wait_table(
    driver,
    timeout=30,
):

    WebDriverWait(
        driver,
        timeout,
    ).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//table//tbody",
            )
        )
    )


# =========================================================
# BACK TO LIST
# =========================================================

def back_to_list(driver):

    try:

        driver.back()

        wait_table(
            driver,
            timeout=30,
        )

        logger.info(
            "กลับหน้ารายการสำเร็จ"
        )

        return True

    except Exception:

        logger.exception(
            "กลับหน้ารายการไม่ได้"
        )

        return False


# =========================================================
# COLLECT INBOX
# =========================================================

def collect_inbox(driver):

    wait = WebDriverWait(
        driver,
        30,
    )

    existing_subjects = (
        load_existing_subjects()
    )

    processed_subjects = set()

    row_index = 0


    while True:

        try:

            # =================================================
            # READ ROWS
            # =================================================

            rows = wait.until(
                EC.presence_of_all_elements_located(
                    (
                        By.XPATH,
                        "//table//tbody/tr",
                    )
                )
            )

            total_rows = len(
                rows
            )

            logger.info(
                "จำนวนรายการทั้งหมด = %s",
                total_rows,
            )

            if row_index >= total_rows:

                logger.info(
                    "อ่านครบทุกแถวแล้ว"
                )

                break


            # =================================================
            # READ ROW AGAIN
            # =================================================

            rows = driver.find_elements(
                By.XPATH,
                "//table//tbody/tr",
            )

            if row_index >= len(
                rows
            ):

                break


            row = rows[
                row_index
            ]

            current_row_no = (
                row_index + 1
            )

            row_index += 1


            # =================================================
            # ROW TEXT
            # =================================================

            row_text = (
                row.text
                or ""
            ).strip()

            if not row_text:

                logger.warning(
                    "ROW %s ไม่มีข้อความ",
                    current_row_no,
                )

                continue


            logger.info(
                "ROW %s | %s",
                current_row_no,
                row_text.replace(
                    "\n",
                    " | ",
                ),
            )


            # =================================================
            # FIND LINK
            # =================================================

            links = row.find_elements(
                By.XPATH,
                ".//a",
            )

            if not links:

                logger.warning(
                    "ROW %s ไม่พบ Link",
                    current_row_no,
                )

                continue


            detail_link = (
                links[0]
            )


            # =================================================
            # SUBJECT
            # =================================================

            subject = (
                detail_link.text
                or row_text
            ).strip()


            # =================================================
            # DUPLICATE IN CURRENT RUN
            # =================================================

            if subject in processed_subjects:

                logger.warning(
                    "ข้ามรายการซ้ำในรอบ: %s",
                    subject,
                )

                continue


            processed_subjects.add(
                subject
            )


            # =================================================
            # SCROLL
            # =================================================

            driver.execute_script(
                """
                arguments[0].scrollIntoView({
                    block: 'center'
                });
                """,
                detail_link,
            )

            time.sleep(
                0.5
            )


            # =================================================
            # CLICK DETAIL
            # =================================================

            try:

                detail_link.click()

            except Exception:

                driver.execute_script(
                    "arguments[0].click();",
                    detail_link,
                )


            # =================================================
            # WAIT DETAIL PAGE
            # =================================================

            try:

                WebDriverWait(
                    driver,
                    15,
                ).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "input[name='j_idt280']",
                        )
                    )
                )

            except TimeoutException:

                logger.warning(
                    "ROW %s ไม่พบหัวเรื่องจริง",
                    current_row_no,
                )


            # =================================================
            # COLLECT DATA
            # =================================================

            data = collect_detail(
                driver=driver,
                row_no=current_row_no,
                subject=subject,
            )


            real_subject = (
                data.get(
                    "real_subject",
                    ""
                )
                or ""
            ).strip()


            duplicate_key = (
                real_subject
                or subject
            )


            # =================================================
            # CHECK OLD CSV
            # =================================================

            if duplicate_key in existing_subjects:

                logger.warning(
                    "ข้าม เพราะมีข้อมูลอยู่แล้ว: %s",
                    duplicate_key,
                )

            else:

                save_csv(
                    data
                )

                existing_subjects.add(
                    duplicate_key
                )

                logger.info(
                    "บันทึกสำเร็จ: %s",
                    duplicate_key,
                )


            # =================================================
            # BACK
            # =================================================

            if not back_to_list(
                driver
            ):

                break


        # =====================================================
        # STALE
        # =====================================================

        except StaleElementReferenceException:

            logger.warning(
                "DOM เปลี่ยน กำลังโหลดรายการใหม่..."
            )

            try:

                wait_table(
                    driver
                )

            except Exception:

                logger.exception(
                    "โหลดตารางใหม่ไม่ได้"
                )

                break


        # =====================================================
        # ERROR
        # =====================================================

        except Exception:

            logger.exception(
                "เกิดข้อผิดพลาดที่ ROW %s",
                row_index,
            )

            if not back_to_list(
                driver
            ):

                break


# =========================================================
# MAIN
# =========================================================

def main():

    driver = None

    try:

        logger.info(
            "================================"
        )

        logger.info(
            "EDOC DATA COLLECTOR"
        )

        logger.info(
            "UNIT = %s",
            UNIT_CODE,
        )

        logger.info(
            "OUTPUT = %s",
            CSV_FILE,
        )

        logger.info(
            "================================"
        )


        # =================================================
        # DRIVER
        # =================================================

        driver = create_driver()


        # =================================================
        # LOGIN
        # =================================================

        login(
            driver
        )


        # =================================================
        # OPEN INBOX
        # =================================================

        open_inbox(
            driver
        )


        # =================================================
        # COLLECT
        # =================================================

        collect_inbox(
            driver
        )


        # =================================================
        # FINISHED
        # =================================================

        logger.info(
            "================================"
        )

        logger.info(
            "เก็บข้อมูลเสร็จแล้ว"
        )

        logger.info(
            "ไฟล์: %s",
            CSV_FILE,
        )

        logger.info(
            "================================"
        )


    except KeyboardInterrupt:

        logger.warning(
            "ผู้ใช้หยุดโปรแกรม"
        )


    except WebDriverException:

        logger.exception(
            "WebDriver เกิดข้อผิดพลาด"
        )


    except Exception:

        logger.exception(
            "โปรแกรมเกิดข้อผิดพลาด"
        )


    finally:

        if driver is not None:

            logger.info(
                "กำลังปิด Chrome..."
            )

            try:

                driver.quit()

            except Exception:

                pass


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    main()