from flask import Flask, render_template, redirect, request, session, make_response
import requests
import json
from datetime import datetime
from resume_parser import resumeparse
import time

# ml job match imports
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter 
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity 
import io, csv, re
import pyparsing as pp

app = Flask(__name__)
app.secret_key = b'testing'

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=['GET', 'POST'])
def scanner():
    if request.method == 'POST':
        f = request.files['file']
        filename = str(time.time()).split(".")[0] + ".pdf"
        f.save('pdfs/'+ filename)
    return redirect('/results?filename='+filename)

@app.route("/results", methods=['GET', 'POST'])
def home():
    filename = request.args.get("filename")
    data = resumeparse.read_file('pdfs/'+filename)

    name = data['name'].lower().title()
    email = data['email']
    phone = data['phone']
    try:
        school = data['university'][0].title()
    except:
        school = ""
    skills = []
    count = 0
    for x in data['skills']:
        skills.append(x.strip())
        if count == 5:
            break
        else:
            count+=1
    skills = list(filter(None, skills))
    skillstr = ', '.join(skills)


    matchings = []
    listings = [[]]
    best_jobs = []
    concentration = []
    organization, job_type, job_title, job_description, location = [], [], [], [], []

    # Converting pdf to txt file for library 

    def pdf2txt(PDFfile, TXTfile):
        in_file = open(PDFfile, 'rb')
        res_mgr = PDFResourceManager()
        data = io.StringIO()
        TxtConverter = TextConverter(res_mgr, data, laparams=LAParams())
        interpreter = PDFPageInterpreter(res_mgr, TxtConverter)
        for page in PDFPage.get_pages(in_file):
            interpreter.process_page(page)
        
        txt = data.getvalue()
        with open(TXTfile, 'w') as f:
            f.write(txt)

    # Function that searches for best match in jobs dataset

    def find_matches(user_resume):
        with open(user_resume, 'r') as resume:
            with open('small_jobs_dataset.csv', 'r') as job_listings_csv:
                # Splitting dataset rows by delimiter
                csv_reader = csv.reader(job_listings_csv)
                count = 0
                # Reading user's resume into variable
                resume_var = resume.read()
                for row in csv_reader:
                    str_row = str(row)
                    job_as_list = pp.commaSeparatedList.parseString(str_row).asList()
                    # Storing job description 
                    job_desc = job_as_list[4]
                    if count > 0:
                        # Feature extraction on job desc and resume
                        text = [resume_var, job_desc]
                        count_vec = CountVectorizer()
                        count_matrix = count_vec.fit_transform(text)
                        match = cosine_similarity(count_matrix)[0][1] * 100
                        matchings.append(tuple((match, count)))
                        listings.append(job_as_list)

                    count += 1   
        # Sorting by jobs with highest match
        matchings.sort(reverse=True)
        # Storing jobs with highest match and user's concentration
        for i in range(5):
            match = matchings[i]
            job = listings[int(match[1])]
            split_string = job
            organization.append(split_string[0].strip('\"'))
            job_type.append(split_string[3].strip('\"'))
            job_title.append(split_string[7].strip('\"'))
            job_description.append(split_string[4].strip('\"'))
            location.append(split_string[6].strip('\"'))
            if i == 0:
                job_industry = split_string[3]
                job_industry = job_industry.strip('\"')
                concentration.append(job_industry)


        
        
    # Resume needs to be converted from pdf to txt
        
    PDFfile = 'pdfs/'+filename
    TXTfile =  'parsed_resume.txt'

    # Converting pdf resume to txt

    pdf2txt(PDFfile, TXTfile)

    # Calling find_matches function

    find_matches('parsed_resume.txt')

    # Printing results

    company_names = []
    company_desc = []
    company_match = []
    for i in range(3):
        try:
            company_names.append(re.sub(r'[^A-Za-z0-9 ]+', '', organization[i]))
            company_desc.append(job_title[i].strip())
            matchc = round(float(str(matchings[i][0]).strip()))
            company_match.append(matchc)
        except:
            pass
    
    try:
        avg = 0
        for x in company_match:
            if x < 80:
                avg += x+20
            else:
                avg += x
        avg = round(avg/3)
    except:
        print('didnt work')

    import os
    os.remove("parsed_resume.txt")

    return render_template("results.html", name=name, email=email, phone=phone, school=school, skills=skillstr, company_desc=company_desc, company_match=company_match, company_names=company_names, avg=avg)
