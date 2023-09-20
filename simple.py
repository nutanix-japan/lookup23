from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Define templates folder
templates = Jinja2Templates(directory="templates")

# Define a route to render the form
@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# Define a route to handle form submission
@app.post("/")
async def read_item(request: Request, item: str = Form(...)):
    return templates.TemplateResponse("form.html", {"request": request, "item": item})

# Define a route for the search page
@app.post("/")
# def search():
#     # Get the search parameters from the form submission
#     if request.method == 'POST':
#        search_term = request.form['search_term']
#        # Search the sheet for matching rows
#        spreadsheet_id = '1meMee6yCvtplZCkljknSYtdFECBEPauw8kn-1YB5x7A'
#        sheet_name = 'Sheet1'
#        search_col = 'Email'
#        rows = search_sheet(spreadsheet_id, sheet_name, search_col, search_term)
#        return templates.TemplateResponse('search.html', rows=rows, map=r1_r2_map)
#     else:
#        return templates.TemplateResponse('search.html', rows=None)
    