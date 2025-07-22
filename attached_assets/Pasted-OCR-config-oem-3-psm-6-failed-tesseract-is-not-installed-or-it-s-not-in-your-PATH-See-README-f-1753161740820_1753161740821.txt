OCR config --oem 3 --psm 6 failed: tesseract is not installed or it's not in your PATH. See README file for more information.
OCR config --oem 3 --psm 8 failed: tesseract is not installed or it's not in your PATH. See README file for more information.
OCR config --oem 3 --psm 13 failed: tesseract is not installed or it's not in your PATH. See README file for more information.
OCR config --oem 3 --psm 11 failed: tesseract is not installed or it's not in your PATH. See README file for more information.
OCR config --oem 3 --psm 12 failed: tesseract is not installed or it's not in your PATH. See README file for more information.
[22/Jul/2025 08:15:48] "POST /customer/prescription-validation/3/ HTTP/1.1" 200 12038
[22/Jul/2025 08:15:52] "POST /customer/update-location/ HTTP/1.1" 200 61
[22/Jul/2025 08:16:19] "GET /customer/prescription-validation/3/ HTTP/1.1" 200 12626
[22/Jul/2025 08:16:20] "POST /customer/update-location/ HTTP/1.1" 200 61
[22/Jul/2025 08:16:26] "POST /customer/cart/add/3/ HTTP/1.1" 302 0
[22/Jul/2025 08:16:27] "GET /customer/cart/ HTTP/1.1" 200 16130
[22/Jul/2025 08:16:30] "GET /customer/cart/bulk-ocr/ HTTP/1.1" 200 12080
[22/Jul/2025 08:16:31] "POST /customer/update-location/ HTTP/1.1" 200 61
OCR config --oem 3 --psm 6 failed: tesseract is not installed or it's not in your PATH. See README file for more information.
OCR config --oem 3 --psm 8 failed: tesseract is not installed or it's not in your PATH. See README file for more information.
OCR config --oem 3 --psm 13 failed: tesseract is not installed or it's not in your PATH. See README file for more information.
OCR config --oem 3 --psm 11 failed: tesseract is not installed or it's not in your PATH. See README file for more information.
OCR config --oem 3 --psm 12 failed: tesseract is not installed or it's not in your PATH. See README file for more information.
[22/Jul/2025 08:16:57] "POST /customer/cart/bulk-ocr/ HTTP/1.1" 302 0
[22/Jul/2025 08:16:57] "GET /customer/cart/ HTTP/1.1" 200 17841
[22/Jul/2025 08:16:57] "GET /media/medicines/images_oDAU2Tt.jpg HTTP/1.1" 304 0
[22/Jul/2025 08:16:57] "GET /media/cart_prescriptions/ChatGPT_Image_Jul_9_2025_11_13_17_AM_lFD51IN.png HTTP/1.1" 200 2666517
[22/Jul/2025 08:17:01] "POST /customer/update-location/ HTTP/1.1" 200 61
C:\Users\HP\Desktop\ff\pharmacy_finder\settings.py changed, reloading.
Traceback (most recent call last):
  File "C:\Users\HP\Desktop\ff\manage.py", line 22, in <module>
    main()
  File "C:\Users\HP\Desktop\ff\manage.py", line 18, in main
    execute_from_command_line(sys.argv)
  File "C:\Users\HP\Desktop\ff\venv\Lib\site-packages\django\core\management\__init__.py", line 442, in execute_from_command_line
    utility.execute()
  File "C:\Users\HP\Desktop\ff\venv\Lib\site-packages\django\core\management\__init__.py", line 382, in execute
    settings.INSTALLED_APPS
  File "C:\Users\HP\Desktop\ff\venv\Lib\site-packages\django\conf\__init__.py", line 81, in __getattr__
    self._setup(name)
  File "C:\Users\HP\Desktop\ff\venv\Lib\site-packages\django\conf\__init__.py", line 68, in _setup
    self._wrapped = Settings(settings_module)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\HP\Desktop\ff\venv\Lib\site-packages\django\conf\__init__.py", line 166, in __init__
    mod = importlib.import_module(self.SETTINGS_MODULE)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\HP\AppData\Local\Programs\Python\Python312\Lib\importlib\__init__.py", line 90, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import      
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load   
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked    
  File "<frozen importlib._bootstrap_external>", line 995, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "C:\Users\HP\Desktop\ff\pharmacy_finder\settings.py", line 220, in <module>
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    ^^^^^^^^^^^
NameError: name 'pytesseract' is not defined