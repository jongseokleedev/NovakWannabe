# The NovakWannabe: Hobby Helper

### Environment

- python 3.9.6

### How To Start

1. start chrome debug

   - **mac**: `/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="~/Desktop/temp_chrome"`
   - **window**: `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:/Chrome_debug_temp"`

2. Check chrom version

   - `chrome://settings/help`

3. Download chrome driver

   - [ChromeDriver - WebDriver for Chrome](https://chromedriver.chromium.org/)

4. `yangjae/main.py` Setting

   - set chromedriver path

     `chrome_driver = "/Users/kangsujin/Desktop/chromedriver"`

     `chrome_driver = "/chromedriver_win32/chromedriver"`

   - set url

     `url = "https://booking.naver.com/booking/10/bizes/210031/items/*"`

   - set execution period

     `schedule.every(10).seconds.do(main)`

5. execute `python3 main.py` in `yangjae` path

install is necessary only for first try

- `pip install selenium`

- `pip install schedule`
