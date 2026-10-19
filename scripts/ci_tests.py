"""Run the normal suite once, logging failed local browser requests for CI diagnosis."""
from pathlib import Path
import sys,unittest
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from playwright.sync_api import Browser
original=Browser.new_page

def page_with_diagnostics(browser,*args,**kwargs):
    page=original(browser,*args,**kwargs)
    def failed(request):
        parsed=urlsplit(request.url)
        location=request.url if parsed.hostname in {'127.0.0.1','localhost'} else '[nonlocal resource]'
        print('[requestfailed]',request.failure,location,flush=True)
    page.on('requestfailed',failed)
    return page

if __name__=='__main__':
    Browser.new_page=page_with_diagnostics
    suite=unittest.defaultTestLoader.discover(str(Path(__file__).resolve().parents[1]/'tests'))
    sys.exit(0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1)
